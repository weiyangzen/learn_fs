<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper.go

## Purpose
Adds routing, metrics, hard-link handling, MIME normalization, context policy, bucket callbacks, and prefix-list fallback around a `FilerStore`.

## Important APIs and Types
`VirtualFilerStore` extends `FilerStore` with hard-link, direct-delete, path-specific store, bucket, and store-comparison methods. `FilerStoreWrapper` stores a default backend, path prefix trie, store ID map, and fast-path flag. Methods implement CRUD/list/KV/transaction wrappers plus `AddPathSpecificStore`, `getActualStore`, `SameActualStore`, `normalizeEntryMimeForStore`, and `prefixFilterEntries`.

## Control Flow and State
Writes first check `ctx.Err()`, then strip cancellation before backend calls so active writes are not interrupted after admission. Reads strip cancellation without rejecting, allowing cleanup/recovery reads to complete. Insert/update serialize chunks, normalize file MIME, update hard-link KV, record metrics, and call actual store. Find/list hydrate hard links and deserialize chunks. Prefix-list fallback scans ordinary listing and filters names when a backend lacks native prefix listing.

## Persistence Behavior
Persists entries through selected actual store. Hard-link data and filer store ID KV go through the default store. Path-specific stores persist translated paths via `FilerStorePathTranslator`.

## Dependencies and Integration Points
Used by `Filer.SetStore` and most filer metadata operations. Integrates with stats, `ptrie`, hard-link helpers, protobuf chunk serialization hooks, and `BucketAware` stores.

## Risks
Context policy is subtle: canceled writes are rejected, but backend operations ignore later cancellation. Hard-link errors during delete are logged but deletion continues to prevent undeletable directories. Prefix fallback can scan extra pages and depends on sorted listing. `FindEntry` converts some missing table errors to not-found only for bucket-droppable stores.

## Test Signals
`filerstore_wrapper_test.go` covers MIME normalization, write rejection on canceled/deadline contexts, active write success, read success with canceled contexts, and rollback success with canceled contexts. Path-specific routing, metrics, prefix fallback, and hard-link KV are not directly tested here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper.go -->
