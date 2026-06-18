<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_test.go

## Purpose
Comprehensive unit tests for lazy remote fetch, remote-aware deletion, and lazy remote directory listing.

## Important APIs and Types
Defines `stubFilerStore`, `stubRemoteClient`, `stubClientMaker`, `countingRemoteClient`, `newTestFiler`, and `registerStubMaker`. Tests target `maybeLazyFetchFromRemote`, `FindEntry`, `DeleteEntryMetaAndData`, `doDeleteEntryMetaAndData`, and `maybeLazyListFromRemote`.

## Control Flow and State
The stub store maintains entries and KV maps with a mutex. Stub remote clients record delete/remove/list calls. Tests register temporary remote client makers by storage type, map directories to remote storage locations, and assert store/remote side effects.

## Persistence Behavior
In-memory store persistence verifies lazy fetch writes local metadata, remote delete failure ordering, local delete failure preservation, lazy listing entry creation/update, and xattr-based TTL caching.

## Dependencies and Integration Points
Exercises `FilerRemoteStorage`, `NewFilerStoreWrapper`, `wdclient.MasterClient`, `log_buffer`, remote storage client registry, and delete/list/fetch methods.

## Risks
Stubs do not model real remote latency, pagination, credentials, or failures beyond configured errors. Several tests share global remote client maker state but restore it with cleanup functions.

## Test Signals
Strong signal for lazy remote behavior: longest-prefix mount matching, recursion guards, fetch-on-miss integration, remote delete skipping for replicated events, keeping metadata on remote/client/local delete failures, not-found tolerance, recursive directory delete, lazy listing TTL, local-only preservation, and remote metadata merge. It does not cover remote listing deletion reconciliation or concurrent singleflight behavior under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_test.go -->
