# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_obj_manifest.h

## Purpose
Defines the serialized object-manifest data model for RGW. A manifest maps logical object byte ranges to head/tail RADOS objects, supports old explicit part maps and newer rule-based implicit layouts, and stores cloud-tier metadata for transitioned objects.

## Important APIs And Types
`rgw_obj_select` stores either a logical `rgw_obj` or a raw `rgw_raw_obj` plus placement rule and can resolve raw locations. `RGWObjManifestPart` records an explicit part location, offset, and size. `RGWObjManifestRule` records implicit layout rule start part, start offset, part size, stripe max size, and optional override prefix. `RGWObjTier` stores tier name, placement, and multipart-upload flag.

`RGWObjManifest` exposes setters/getters for head object, size, prefix, tail placement, tail instance, rules, explicit objects, tier type/config, append operations, rule lookup, object iterators, and a nested `generator`. The nested `obj_iterator` walks stripes/parts and exposes current location, offsets, part id, stripe id, stripe size, and location offset. Encoding version 8 includes placement rules and tier fields while retaining compatibility logic for older structures.

## Control Flow And State
Implicit manifests use ordered `rules` keyed by start offset. Iterators choose the current rule, compute part/stripe ids, and use prefix/override prefix plus tail placement to synthesize locations. Explicit manifests use the `objs` map directly. Decoding handles legacy structures by marking old maps explicit, reconstructing head information, patching issue-16435 old copied head entries, and conditionally decoding tail bucket/instance to avoid redundant serialization.

Cloud-tier methods gate tier config on supported `RGWTierType::CLOUD_S3` and `CLOUD_S3_GLACIER`. `has_tail()` distinguishes single-head objects from objects with tail parts or size beyond head. `set_trivial_rule()` and `set_multipart_part_rule()` are helpers for common layout creation.

## Dependencies And Integration Points
Because this header defines fundamental serialized types, it deliberately avoids includes that require only RGW/OSD contexts beyond placement, bucket, object, and zone type headers. It integrates with object IO, multipart upload, copy/append, lifecycle tiering, admin formatting, and encoding test machinery through `WRITE_CLASS_ENCODER()` and `generate_test_instances()`.

## Risks And Test Signals
Backward-compatible decode paths are sensitive: old manifests without tail instance or placement fields must still map correctly. The mix of explicit and implicit layouts means append/iteration logic must be tested across both representations. Tier setters silently ignore unsupported tier types, which callers must account for. Tests should cover encode/decode versions, iterator seek and increment around rule boundaries, head-only objects, multipart layouts, copied old explicit manifests, tier config round trips, and raw/logical object selection.
