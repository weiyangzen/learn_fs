# sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.cc

## Purpose

This file implements the CORTX Motr RGW SAL backend. It maps RGW users, buckets, objects, multipart uploads, metadata caches, and store-driver operations onto Motr indices and Motr objects. The implementation is a proof-of-concept style backend: the main object/user/bucket/multipart paths are present, while many RGW features return success without real work or return not-supported/not-found placeholders.

## Important APIs, Types, and Functions

- `MotrMetaCache::{get,put,remove,invalid}` wraps RGW `ObjectCache` for metadata blobs. Distribution/watch hooks are placeholders.
- `MotrStore::list_buckets()` scans a per-user Motr index named `motr.rgw.user.info.<user>` and fills RGW `BucketList`.
- `MotrUser::{load_user_from_idx,load_user,store_user,remove_user,create_bucket}` persists `MotrUserInfo` in the global users index, manages access-key/email indices, creates per-user bucket-list indices, and creates buckets.
- `MotrBucket::{put_info,load_bucket,link_user,unlink_user,list,remove,create_bucket_index,create_multipart_indices}` persists `MotrBucketInfo`, manages bucket indices, links bucket entries to users, lists objects, and removes bucket structures.
- `MotrObject::{load_obj_state,get_obj_attrs,get_bucket_dir_ent,create_mobj,open_mobj,write_mobj,read_mobj,delete_mobj,update_version_entries}` bridges RGW object metadata with Motr object IO.
- `MotrAtomicWriter` implements normal object PUT by accumulating data, creating/writing a Motr object, and then publishing metadata in the bucket index.
- `MotrMultipartUpload` and `MotrMultipartWriter` implement multipart setup, part writing, part listing, completion, abort, and part deletion using bucket multipart and object parts indices.
- Motr index helpers include `index_name_to_motr_fid()`, `create_motr_idx_by_name()`, `delete_motr_idx_by_name()`, `do_idx_op_by_name()`, `do_idx_op()`, `do_idx_next_op()`, and `next_query_by_name()`.
- `newMotrStore()` is the extern "C" plugin factory that reads Motr config options, initializes `m0_client`, container, UFID generator, and global indices.

## Control Flow

Store creation starts in `newMotrStore()`: a `MotrStore` is allocated, Motr endpoints/fids/profile are read from Ceph config, tracing is configured, `m0_client_init()` opens the Motr client, the uber container is initialized, UFID generation is initialized, and global indices are created.

User creation/update loads the existing user from `motr.rgw.users`, checks optimistic version state, encodes `MotrUserInfo`, writes it back, stores one access key in `motr.rgw.accesskeys`, stores email mapping in `motr.rgw.emails`, creates the per-user bucket index, and updates cache. User lookup by access key/email first reads the secondary index, then loads the user record.

Bucket creation through `MotrUser::create_bucket()` checks existence, fills `RGWBucketInfo`, writes bucket instance metadata to `motr.rgw.bucket.instances`, creates `motr.rgw.bucket.index.<bucket>`, creates `motr.rgw.bucket.<bucket>.multiparts`, and links a `RGWBucketEnt` into the owner index. Bucket listing and object listing use `next_query_by_name()` over Motr sorted index keys with marker/prefix/delim support.

Normal object PUT uses `MotrAtomicWriter`. `prepare()` allocates Motr IO vectors and detects an old object. `process()` accumulates up to 32 MiB before flushing. `write()` creates/opens a Motr object, computes optimal block size from Motr layout/pool attributes, and issues synchronous `M0_OC_WRITE` operations. `complete()` encodes `rgw_bucket_dir_entry`, attrs, and `MotrObject::Meta` into the bucket index and updates metadata cache; versioned writes first clear old current flags through `update_version_entries()`.

GET/read uses `MotrReadOp::prepare()` to load metadata, enforce conditional headers, open the Motr object or multipart part objects, and set attrs/size/mtime. `iterate()` reads object data synchronously via `read_mobj()` or assembled multipart reads. `read()` itself is a stub returning 0.

DELETE loads the bucket-dir entry, removes metadata cache and bucket-index entry, and deletes the Motr object or multipart part objects. Versioning/delete-marker behavior is noted as TODO and not implemented like RADOS.

Multipart init creates a unique upload id and records a metadata entry in the bucket multipart index, then creates `motr.rgw.object.<bucket>.<oid>.parts`. Each part is a separate Motr object and part metadata entry. Completion validates part count/order/etag/min-size, computes multipart ETag, writes a final bucket-index object entry with `MultiMeta` semantics, caches it, and removes the multipart-index entry.

## State and Persistence Behavior

Persistent state is stored mostly in Motr DIX indices:

- Global indices: `motr.rgw.users`, `motr.rgw.bucket.instances`, `motr.rgw.bucket.headers`, `motr.rgw.accesskeys`, `motr.rgw.emails`.
- Per-user bucket lists: `motr.rgw.user.info.<user-id>`.
- Per-bucket object index: `motr.rgw.bucket.index.<bucket-name>`.
- Per-bucket multipart in-progress index: `motr.rgw.bucket.<bucket-name>.multiparts`.
- Per-object multipart parts index: `motr.rgw.object.<bucket-name>.<object>.parts`.

Object payloads are stored as Motr objects. The bucket index value for a normal object encodes `rgw_bucket_dir_entry`, attrs, and `MotrObject::Meta`, where `Meta` contains the Motr object id, pver, and layout id needed to reopen/delete/read the Motr object.

Metadata cache state is local process memory using `ObjectCache`. Cache invalidation is local only because `distribute_cache()` and `watch_cb()` are placeholders. This creates eventual consistency risk across RGW instances.

## Dependencies and Integration Points

The file depends on Motr C headers (`motr/config.h`, `motr/client.h`, `motr/layout.h`, helper UFID APIs), Ceph/RGW SAL types, RGW compression, bucket/object/common utilities, MD5 helpers, Ceph logging, and RGW config values such as `motr_my_endpoint`, `motr_ha_endpoint`, `motr_profile_fid`, and tracing flags.

It integrates with RGW through `StoreDriver`, `StoreUser`, `StoreBucket`, `StoreObject`, `StoreWriter`, `StoreMultipartUpload`, `StoreNotification`, `StoreLuaManager`, placement/zone abstractions, and plugin loading via `newMotrStore()`.

## Risks and Edge Cases

- Many methods are stubs returning 0 or null: stats, usage, quota, lifecycle, restore, append writer, bucket chown, ACL persistence, object attrs mutation, omap, sync policy, metadata listing, notifications, service-map registration, and more. Returning success can mask unsupported behavior.
- Several apparent compile/integration hazards exist in this source as read: `MotrStore::get_lua_manager()` calls a constructor signature not declared in the header, OIDC methods are defined as `DaosStore::...` inside the Motr file, `MotrAtomicWriter::complete()` and `MotrMultipartWriter::complete()` signatures appear inconsistent with the header's checksum-bearing overrides, and multipart completion references identifiers such as `obj_part` and `etag_bl` that are not defined in the shown scope.
- Bucket removal references `forward_to_master`, `bucket_version`, and `req_info` without visible local definitions in the function, suggesting stale code copied from another backend or macro/member assumptions.
- Versioned object updates lack distributed locking, and the code explicitly documents a race that can leave two current versions.
- Cache invalidation is not distributed; multi-RGW deployments can read stale user, bucket, or object metadata.
- Index names are converted to Motr FIDs with MD5, with a comment noting collision risk.
- Several operations are synchronous and block on `M0_TIME_NEVER`; hung Motr operations can hang RGW request paths.
- Object write pads data to optimal block sizes; logical size is tracked separately, so read paths must consistently limit callback length to the requested actual bytes.
- Multipart completion stores a dummy `MotrObject::Meta` for the final composed object and relies on part metadata for reads/deletes.
- Access-key storage only stores the first key from `info.access_keys` during user store, while deletion logic tracks sets; multi-key users may be incomplete.

## Test Signals

No tests are in this file. Nearby DBStore tests do not exercise Motr. Meaningful validation would require a Motr-backed integration environment covering plugin initialization, global/per-user/per-bucket index creation, user lookup by id/email/access key, bucket list pagination, object PUT/GET/DELETE, conditional GET, versioned write races, multipart init/upload/list/complete/read/abort, and unsupported-feature error behavior. Build tests are especially important because several definitions appear inconsistent with declarations or current SAL interfaces.
