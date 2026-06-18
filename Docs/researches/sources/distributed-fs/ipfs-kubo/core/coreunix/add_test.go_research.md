# sources/distributed-fs/ipfs-kubo/core/coreunix/add_test.go

## Purpose
Tests UnixFS adder safety around concurrent GC and filestore position metadata.

## Important APIs, Types, and Functions
Defines `TestAddMultipleGCLive`, `TestAddGCLive`, `testAddWPosInfo`, `TestAddWPosInfo`, `TestAddWPosInfoAndRawLeafs`, `testBlockstore`, `CheckForPosInfo`, and `dummyFileInfo`.

## Control Flow and State
GC live tests construct mock nodes, use pipe-backed files to pause adds mid-stream, start GC concurrently, assert GC waits for add lock handoff, then ensure newly added hashes are not collected. PosInfo tests wrap blockstore puts and count filestore nodes at offset zero/nonzero for no-copy adds with and without raw leaves.

## Dependencies and Integration Points
Depends on core node/repo mocks, Kubo GC, blockstore, Boxo files/filestore/merkledag, datastore, and add events.

## Risks and Test Signals
Strong signals cover add/GC lock choreography and filestore metadata propagation. The tests use sleeps/timeouts and pipe timing, so failures may indicate either real deadlocks or scheduling sensitivity.
