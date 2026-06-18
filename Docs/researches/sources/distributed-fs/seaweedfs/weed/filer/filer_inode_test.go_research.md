<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_inode_test.go

## Purpose
Tests inode derivation and persistence behavior for filer entries, parents, updates, and hard links.

## Important APIs and Functions
Tests call `ensureEntryInode`, `CreateEntry`, and `UpdateEntry`. `newTestFilerWithStubStore` creates a filer with the shared stub store from lazy remote tests.

## Control Flow and State
The tests validate deterministic path/crtime derivation, hard-link ID hashing, assignment during creation, recursive parent auto-creation, update rejection when changing file to directory, preservation of existing inode, and backfilling legacy zero inode.

## Persistence Behavior
The stub store persists entries in memory, allowing assertions on stored inode values after create/update.

## Dependencies and Integration Points
Uses `NewFiler`, `NewFilerStoreWrapper`, the stub store, `util.FullPath`, `pb.ServerDiscovery`, and testify assertions. It connects inode code to the real create/update paths rather than only testing the helper.

## Risks
Relies on stub store behavior from another test file in the same package; changes to that stub can affect this test. Does not cover rename inode preservation.

## Test Signals
Strong coverage for inode assignment and preservation. Missing coverage for concurrent creates, hard-link KV updates, and rename/move paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode_test.go -->
