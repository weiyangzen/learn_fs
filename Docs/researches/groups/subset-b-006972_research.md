# subset-b-006972 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_putobj_processor.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_putobj_processor.cc

## Purpose
`rgw_putobj_processor.cc` implements the RADOS-backed object-write processors used by RGW put-object paths. It turns streamed `bufferlist` input into head and tail RADOS object writes, builds the `RGWObjManifest` that describes where object data lives, and commits the final visible metadata for ordinary atomic puts, multipart part uploads, and appendable objects. The file owns the concrete lifecycle behind the declarations in `rgw_putobj_processor.h`: prepare placement and striping, stream data through first-head-chunk handling, drain asynchronous writes, then atomically update bucket/object metadata or multipart metadata.

It also contains `read_cloudtier_info_from_attrs()`, a helper for restore/cloud-tier uploads that consumes internal attributes, stores tier configuration into the manifest, and updates an OLH epoch for restored versioned objects.

## Important APIs, Types, and Functions
`read_cloudtier_info_from_attrs()` scans the caller's attribute map for `RGW_ATTR_CLOUD_TIER_TYPE`, `RGW_ATTR_CLOUD_TIER_CONFIG`, `RGW_ATTR_RESTORE_VERSIONED_EPOCH`, and `RGW_ATTR_RESTORE_TYPE`. Supported tier types mark the object category as `CloudTiered`, move decoded tier config into `RGWObjManifest`, and erase internal replication-only attributes. Restore epoch decoding may override the passed `olh_epoch`, with temporary restores retaining the epoch attribute for later reset behavior.

`HeadObjectProcessor::process()` is the front door for streamed object data. It buffers the first `head_chunk_size` bytes, calls subclass-specific `process_first_chunk()`, then forwards all remaining data to the processor returned by that subclass. A zero-length input acts as a flush for a partial first chunk.

`RadosWriter` methods translate processor writes into librados operations. `process()` writes a chunk to the current stripe object using `write_full()` at offset zero or `write()` for later offsets. `write_exclusive()` creates the current stripe/head object with `op.create(true)` and drains AIO immediately so multipart and append paths can react to `-EEXIST`. `drain()` consumes outstanding AIO completions. The destructor drains and deletes written raw objects unless `clear_written()` was called after a successful commit.

`ManifestObjectProcessor::next()` implements `StripeGenerator`. It asks `RGWObjManifest::generator` for the next stripe object, resolves pool chunk size, points `RadosWriter` at the raw stripe object, resets the `ChunkProcessor`, and returns the maximum size of the current stripe.

`AtomicObjectProcessor::{prepare,process_first_chunk,complete}` implement ordinary put/copy/restore writes. `prepare()` chooses head and tail placement, inline head capacity, chunk size, aligned stripe size, and a trivial manifest rule. `process_first_chunk()` keeps the first head bytes in memory for the final metadata write. `complete()` drains tail writes, closes the manifest at the actual data size, configures `RGWRados::Object::Write::meta`, applies cloud-tier/restore attributes, and writes the head metadata through `write_meta()`.

`MultipartObjectProcessor::{prepare,prepare_head,process_first_chunk,complete}` implement one multipart part. `prepare()` prefixes part data by object name and upload id. `prepare_head()` builds a multipart-part manifest, converts the first stripe raw object into the part head object, and configures the writer. `process_first_chunk()` writes the first chunk as an exclusive create; on `-EEXIST`, it randomizes the multipart oid prefix, rebuilds the manifest/head, and retries. `complete()` writes part head metadata, builds `RGWUploadPartInfo`, extracts compression metadata, and updates the multipart meta object's omap using `cls_rgw_mp_upload_part_info_update()` with an older `omap_set()` fallback for `-EOPNOTSUPP`.

`AppendObjectProcessor::{prepare,process_first_chunk,complete}` implement appendable object writes. `prepare()` reads existing object state, validates that the caller's append position matches the current accounted size, reads and increments `RGW_ATTR_APPEND_PART_NUM`, preserves storage class and manifest prefix for existing appendable objects, or creates a random prefix for new objects. `complete()` appends the new manifest to the old manifest when present, marks metadata as appendable, updates the append part number attribute, composes a multipart-style ETag from the previous ETag and new ETag, then writes total size/accounted size metadata.

## Control Flow
All processor variants follow the same high-level sequence. A caller constructs the processor, calls `prepare()`, repeatedly calls `process()` with object data, and calls `complete()` after the request body is consumed. `prepare()` initializes manifest generation, the active stripe object, the head chunk threshold, `ChunkProcessor`, and `StripeProcessor`. `HeadObjectProcessor::process()` captures the first head chunk before any general tail streaming happens; the subclass decides whether that first chunk is retained for atomic head metadata or written immediately as an exclusive RADOS object.

For normal atomic writes, data up to the inline head limit is buffered in memory. Tail data goes through `StripeProcessor`, which observes stripe boundaries, and `ChunkProcessor`, which breaks writes into pool-appropriate chunk sizes. Completion drains all AIO, advances the manifest generator to the actual byte count, and performs one `write_meta()` operation on the head object with manifest, owner, tags, mtime, conditional headers, delete-at time, zone trace, and operation logging flags.

For multipart parts, the first chunk is not retained until final metadata. It is written with an exclusive create to make racing uploads of the same upload id and part number visible. If the initial part head already exists, the processor chooses a random oid prefix, regenerates the manifest and head mapping, and submits the exclusive write again. Final completion separately writes the part head metadata and then registers the completed part in the multipart meta object's omap, detecting abort races with `assert_exists()`.

For appends, `prepare()` first reads current object state. Nonexistent objects are only valid at append position zero. Existing objects must have `RGW_ATTR_APPEND_PART_NUM`; otherwise they are rejected as non-appendable. The new write is represented as another multipart-part-style manifest segment, and completion either writes that manifest directly or appends it into the current manifest before replacing head metadata.

## State and Persistence Behavior
The file coordinates several layers of state. In-memory processor state includes current head object, target object, manifest, manifest generator, buffered first chunk, active chunk/stripe processors, writer cleanup set, object owner, placement rules, append counters, and multipart upload identifiers. Persistent state is written to RADOS data objects, RGW head object metadata, bucket index transactions, and multipart meta object omap entries.

`RadosWriter::written` is a cleanup ledger of raw objects whose writes have completed. If a processor is destroyed before successful completion, the destructor drains remaining AIO and removes those raw objects. It handles head objects specially: raw tail objects are deleted directly, while the head object is deleted through `store->delete_obj()` so bucket index prepare/complete rules are respected. Successful completion calls `clear_written()` so committed data is not removed. On `-ETIMEDOUT` during a commit that may still succeed, the code also clears the cleanup ledger to avoid deleting objects that a late success could expose, accepting possible orphaning as the crash-equivalent failure mode.

Manifest persistence is variant-specific. Atomic puts use a trivial rule that may inline data into the head depending on placement and zone inline-data settings. Multipart parts use a multipart-part rule and store part metadata in the multipart meta object. Appends reuse the existing manifest prefix and append a new manifest segment, with `keep_tail` telling metadata write logic to preserve old tail data.

Attribute mutation is part of persistence behavior. Cloud-tier config attributes are consumed into the manifest and removed from the head attrs. Append completion mutates `RGW_ATTR_APPEND_PART_NUM` and sometimes `RGW_ATTR_ETAG`. Multipart completion records checksum and compression information in `RGWUploadPartInfo` rather than only in the part head.

## Dependencies and Integration Points
The implementation depends on librados write operations, RGW AIO throttling, `RGWRados`, `RGWObjectCtx`, `RGWBucketInfo`, placement and zone services, `RGWObjManifest`, `RGWObjManifest::generator`, `RGWMPObj`, multipart cls helpers, cls version incrementing, compression attribute parsing, request context tracing, Ceph encoding/decoding, MD5 helpers, and RGW error codes.

Direct call sites include SAL writer wrappers (`RadosAtomicWriter`, `RadosAppendWriter`, and `RadosMultipartWriter`) and several RADOS copy/fetch/restore paths that instantiate `AtomicObjectProcessor` directly. The class contracts connect the generic `rgw::sal::ObjectProcessor` and `DataProcessor` streaming interfaces to the RADOS-specific persistence backend.

## Risks
The first-chunk state machine is sensitive to zero-sized flushes and `head_chunk_size` values. It intentionally calls `process_first_chunk()` when `data_offset == 0`, so empty-object and zero-inline-head writes must continue to initialize the downstream processor correctly.

Cleanup is deliberately conservative around timeouts. Clearing `written` on `-ETIMEDOUT` prevents data loss after a late successful metadata update, but it can leave orphaned tail objects if the commit never completes. Conversely, missing a successful write in `written` would bypass destructor cleanup and leak data after failed requests.

Multipart race handling depends on exclusive creation of the first stripe/head and a correct prefix rebuild after `-EEXIST`. Any mismatch between `target_obj`, randomized `RGWMPObj`, manifest prefix, and `head_obj.index_hash_source` could make completed part metadata point at the wrong data. Multipart meta updates also need the cls call and omap fallback to remain semantically compatible.

Append correctness depends on current object state being fresh, position checks using accounted size rather than raw size, and `keep_tail` preserving previous data. ETag composition assumes old and new ETags are MD5 hex strings of the expected length. Cloud-tier attr decoding mutates caller attrs, so callers must not expect those internal attrs to survive a successful atomic completion.

## Test Signals
Useful tests include empty object puts, puts smaller than the head chunk, exact head-chunk boundary writes, multi-stripe writes, tail placement different from head placement, inline-data enabled and disabled zones, AIO write error cleanup, destructor cleanup after failed completion, and timeout behavior that avoids destructive cleanup.

Multipart coverage should exercise racing same-part uploads that return `-EEXIST`, randomized prefix retry, sorted and unsorted omap keys, cls unsupported fallback, upload abort race returning `-ERR_NO_SUCH_UPLOAD`, checksum propagation, compression info extraction, and part manifest correctness. Append tests should cover new appendable object creation at position zero, nonzero append to nonexistent object rejection, non-appendable existing object rejection, position mismatch, storage-class preservation, manifest append behavior, append part number encoding, and ETag recomputation. Restore/cloud-tier tests should verify manifest tier fields, attr erasure, temporary restore epoch retention, and decode error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_putobj_processor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_putobj_processor.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_putobj_processor.h

## Purpose
`rgw_putobj_processor.h` declares the RADOS implementation of RGW put-object processors. It defines a small hierarchy that adapts RGW's generic streaming `ObjectProcessor`/`DataProcessor` interfaces to RADOS object layout, manifest generation, bucket-index-aware head object commits, multipart part registration, and appendable object updates.

The header separates the reusable pipeline pieces from the three concrete write modes. `HeadObjectProcessor` handles first-head-chunk buffering. `RadosWriter` is the RADOS data sink. `ManifestObjectProcessor` combines first-chunk handling with `StripeGenerator` and `RGWObjManifest`. `AtomicObjectProcessor`, `MultipartObjectProcessor`, and `AppendObjectProcessor` implement the operation-specific `prepare()` and `complete()` contracts.

## Important APIs, Types, and Members
`HeadObjectProcessor` derives from `rgw::sal::ObjectProcessor`. It stores `head_chunk_size`, buffered `head_data`, the downstream `DataProcessor*`, and `data_offset`, exposing `set_head_chunk_size()` and `get_actual_size()`. Subclasses implement `process_first_chunk(bufferlist&&, DataProcessor**)`, while `process()` is final so all variants share the same first-chunk and forwarding behavior.

`RawObjSet` is a `std::set<rgw_raw_obj>` used by `RadosWriter` to remember successfully written raw RADOS objects for later cleanup if the higher-level operation is canceled or fails.

`RadosWriter` derives from `rgw::sal::DataProcessor`. It owns references to `Aio`, `RGWRados`, `RGWBucketInfo`, `RGWObjectCtx`, the current head object, the active stripe object reference, the written-object cleanup set, logging/yield context, and tracing context. Public methods set the head object, set the active stripe object, stream data into that stripe, perform an exclusive create for first chunks, drain AIO, add allocation hints, clear cleanup state after success, and expose the trace context for metadata writes.

`ManifestObjectProcessor` derives from both `HeadObjectProcessor` and `StripeGenerator`. It stores the RADOS store, bucket info, tail placement, owner, object context, head object, `RadosWriter`, `RGWObjManifest`, manifest generator, `ChunkProcessor`, `StripeProcessor`, and logging provider. Its `next()` implementation supplies stripe transitions to `StripeProcessor`; its constructor wires writer, chunk, and stripe placeholders before a concrete `prepare()` method configures sizes and placement.

`AtomicObjectProcessor` adds `olh_epoch`, `unique_tag`, and `first_chunk`. It prepares a trivial manifest and completes with an atomic head object metadata write in a bucket index transaction. Its completion signature carries accounted size, ETag, mtime controls, attributes, optional checksum, delete-at, conditional headers, user data, zone trace, cancellation output, request context, and flags.

`MultipartObjectProcessor` adds target object identity, upload id, part number, part number string, and `RGWMPObj`. It prepares a multipart manifest, writes the part head with exclusive create semantics, and completes by writing part metadata and registering the part in the multipart meta object.

`AppendObjectProcessor` adds current append part number, requested append position, current object size, an output pointer for current accounted size, previous ETag, unique tag, `keep_tail`, and a pointer to the current manifest. It validates append state in `prepare()` and completes by writing combined append metadata while updating the caller-visible accounted size.

## Control Flow
The declared API establishes a common lifecycle for callers: construct one of the concrete processors, call `prepare(optional_yield)`, stream request data through `process(bufferlist&&, offset)`, then call `complete(...)`. `HeadObjectProcessor::process()` intercepts the first head-sized chunk and delegates variant-specific first-chunk behavior. After `process_first_chunk()` returns a downstream processor, later data flows through `StripeProcessor`, then `ChunkProcessor`, then `RadosWriter`.

`ManifestObjectProcessor` is the shared bridge between logical object offsets and physical RADOS stripes. The concrete `prepare()` methods initialize the manifest generator and the first stripe, then configure head chunk size and processor sizes. When `StripeProcessor` reaches a stripe boundary, it calls `ManifestObjectProcessor::next()` to allocate or identify the next manifest object and reset the writer/chunker for that stripe.

Completion methods are intentionally not abstracted further because visibility rules differ. Atomic puts expose the object by committing the head object metadata. Multipart parts first commit part head metadata and then update the multipart meta object. Appends modify existing object metadata, usually retaining old tail data and extending the old manifest.

## State and Persistence Behavior
The header shows which state is durable-facing and which is transient. `RadosWriter::written` is transient cleanup state for raw objects. `head_obj`, `stripe_obj`, `manifest`, `manifest_gen`, `tail_placement_rule`, owner, object context, and bucket info determine persistent placement and metadata. The concrete processors store operation tags, upload identifiers, append positions, OLH epoch, and first chunk buffers needed to make the final metadata operation consistent with the streamed data.

`clear_written()` is the explicit success boundary for data-object cleanup ownership. Until completion calls it, the writer destructor treats completed raw writes as provisional and eligible for deletion. `get_actual_size()` returns the maximum byte offset accepted by the head processor, which completion uses as the persisted object or part size after compression/filtering effects.

## Dependencies and Integration Points
The header includes `rgw_putobj.h` for `ChunkProcessor`, `StripeProcessor`, and `StripeGenerator`; `services/svc_tier_rados.h`; `rgw_sal.h`; and `rgw_obj_manifest.h`. It forward declares `rgw::sal::RadosStore` and `rgw::Aio`, and uses many RGW/RADOS types supplied by included headers: `RGWRados`, `RGWBucketInfo`, `RGWObjectCtx`, `rgw_obj`, `rgw_raw_obj`, `rgw_rados_ref`, `rgw_placement_rule`, `ACLOwner`, `RGWObjManifest`, `RGWMPObj`, `DoutPrefixProvider`, `optional_yield`, `jspan_context`, request context, checksum, and zone trace types.

The concrete processors are embedded by RADOS SAL store writers, including atomic, append, and multipart writer wrappers. Direct RADOS copy and restore paths also instantiate the atomic processor. The interfaces are therefore part of the RGW backend contract between HTTP/S3 request handling, optional data filters such as compression, and durable RADOS object layout.

## Risks
Because `HeadObjectProcessor::process()` is final, all subclasses rely on the same first-chunk behavior. Bugs in `head_chunk_size` setup affect every put mode. A subclass must set `*processor` in `process_first_chunk()` before any remaining data is forwarded; failing to do so trips assertions or drops data.

`RadosWriter` is non-owning for important collaborators (`Aio`, `RGWRados`, bucket info, object context, trace), so callers must keep those objects alive for the writer and processor lifetime. Its destructor has side effects in RADOS, making object lifetime and success/failure signaling critical.

`AppendObjectProcessor` stores `cur_accounted_size` as an external pointer and `cur_manifest` as a pointer returned through object state lookup, so stale state or premature owner destruction would corrupt completion semantics. `set_tail_placement(const rgw_placement_rule&&)` takes an rvalue reference but copies it into the member; callers should not infer move-only semantics.

## Test Signals
Header-level coverage should instantiate each concrete processor through the SAL writer wrappers and verify that `prepare/process/complete` signatures remain compatible with filters and request code. Behavioral tests should check that `process_first_chunk()` is invoked for empty, partial, exact, and oversized first chunks; that `ManifestObjectProcessor::next()` is called at stripe boundaries; and that `RadosWriter` cleanup is triggered only on unsuccessful lifetimes.

Integration tests should cover ordinary put/copy/restore atomic paths, multipart part upload registration and retry, appendable object creation and extension, different head/tail placement rules, object versioning or OLH epoch interactions, conditional headers, delete-at metadata, zones trace propagation, and optional checksum handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_putobj_processor.h -->
