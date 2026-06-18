# sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.hh

## Purpose
`ITapeGcMgm.hh` declares the tape-GC subsystem's abstraction over EOS MGM services. It isolates GC logic from concrete FsView, namespace, QuarkDB, shell-command, and eviction implementations.

## Important APIs, Types, And Functions
The interface declares config/stats methods, `FailedToGetFileSize`, file-size and namespace-state methods, `evictAsRoot()`, `getFsIdToSpaceMap()`, `getSpaceToDiskReplicasMap()`, and `getStdoutFromShellCmd()`. Nested `FileIdAndCtime` stores a file ID and creation time and defines ordering by ctime seconds then nanoseconds.

## Control Flow
Space-specific and multi-space GC classes call this interface for all external operations: read config, read space stats, map namespace replicas to spaces, validate files, evict files, and run optional free-byte scripts. The sorted set of `FileIdAndCtime` lets initial population feed LRUs oldest-first.

## State And Persistence
The interface owns no state. Concrete implementations may read live MGM state or test maps. `FileIdAndCtime` is a value type used in temporary maps.

## Dependencies And Integration Points
It depends on EOS filesystem IDs, namespace file metadata IDs, QuarkDB contact details, `SpaceConfig`, and `SpaceStats`. `RealTapeGcMgm`, `DummyTapeGcMgm`, `MultiSpaceTapeGc`, `TapeGc`, `SmartSpaceStats`, and `AsyncUint64ShellCmd` integrate through it.

## Risks And Edge Cases
`FileIdAndCtime::operator<()` ignores file ID when ctime is exactly equal, so two files with identical `timespec` compare equivalent in `std::set` and one can be lost. Interface methods mix throwing and non-throwing expectations; callers need careful error handling to avoid stopping GC on transient namespace failures.

## Test Signals
Tests should cover derived implementation substitution, duplicate ctime ordering behavior, file-size exception propagation, replica-map stop handling, and shell-output length/error semantics.
