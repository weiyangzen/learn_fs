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
