# sources/control-plane/longhorn-engine/pkg/replica/replica_test.go

Purpose: broad behavioral test suite for replica disk-chain lifecycle and IO semantics.

Important APIs/types/functions: defines constants `b` and `bs`, `TestBackingFile`, `NewTestBackingFile`, gocheck suite registration, byte/hash comparison helpers, and many `TestSuite` methods. Covered scenarios include create, snapshot metadata, revert graph shape, leaf/middle/root/out-of-chain removal, prepare-remove actions, basic reads/writes, backing file reads, partial write/read, force removal, unmap with removed-chain marking, and unmap alignment.

Control flow: tests create temp replica directories, instantiate replicas, perform snapshots/reverts/writes/unmaps, and assert active disk arrays, metadata maps, children maps, chain output, file sizes, and read data. Some tests sleep one second to create unique timestamps.

State and persistence: creates real disk and metadata files under temp dirs, optionally with backing files. Tests close/remove dirs via defers. Some helper tests print to stdout and use real filesystem sparse behavior.

Dependencies and integration points: exercises `New`, `Snapshot`, `Revert`, `RemoveDiffDisk`, `MarkDiskAsRemoved`, `PrepareRemoveDisk`, `ReadAt`, `WriteAt`, `UnmapAt`, backing-file insertion, and reload behavior.

Risks: tests are time-sensitive due to one-second timestamp sleeps and can be slow. They use real filesystem behavior, so sparse/FIEMAP assumptions can vary by environment. Some cleanup assertions happen in deferred functions and can mask original failures if cleanup also fails.

Test signals: strong coverage for core replica graph invariants and IO edge cases. Missing signals include crash/restart during rollback, multi-digit snapshot/head naming, revision-counter concurrency, and encrypted expansion.
