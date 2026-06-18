<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore.go

## Purpose
Defines the storage backend interface for filer metadata and common backend capability/error contracts.

## Important APIs and Types
`FilerStore` requires initialization, CRUD, recursive child deletion, paged listing, prefixed listing, transactions, KV operations, and shutdown. `ListEachEntryFunc` is the listing callback. `BucketAware` adds bucket lifecycle callbacks and whole-bucket drop capability. `Debuggable` adds debug output. Constants/errors include `CountEntryChunksForGzip`, `ErrUnsupportedListDirectoryPrefixed`, `ErrUnsupportedSuperLargeDirectoryListing`, `ErrKvNotImplemented`, and `ErrKvNotFound`.

## Control Flow and State
This file has no implementation logic; it defines contracts implemented by backend packages and wrapped by `FilerStoreWrapper`.

## Persistence Behavior
Backends implementing this interface own metadata and KV persistence. KV is also used for filer store ID and hard-link state.

## Dependencies and Integration Points
All filer metadata operations depend on this interface. Store wrappers add metrics, path routing, hard-link handling, and context behavior.

## Risks
Interface semantics are broader than Go types express: `FindEntry` should return `filer_pb.ErrNotFound`, listings should be sorted/paged consistently, transaction behavior should match backend guarantees, and KV support is expected for some features.

## Test Signals
Wrapper tests and stubs exercise selected interface behavior. Backend-specific correctness is outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore.go -->
