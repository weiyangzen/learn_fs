# sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.hh

## Purpose
`DummyTapeGcMgm.hh` declares the in-memory test implementation of `ITapeGcMgm`. It allows tape-GC unit tests to run without a real XRootD MGM, namespace service, FsView, QuarkDB, or shell command.

## Important APIs, Types, And Functions
The class overrides all `ITapeGcMgm` methods and adds setters `setTapeGcSpaceConfig()`, `setSpaceStats()`, `setStdoutFromShellCmd()`, plus counter getters for config, stats, namespace checks, file-size checks, and eviction calls. Copy/move construction and assignment are deleted.

## Control Flow
Header declarations establish a simple fake: callers configure maps and stdout, then production code paths call the same interface methods they would call on `RealTapeGcMgm`.

## State And Persistence
Private state is guarded by a mutable mutex and includes maps for space config/stats, several counters, and a shell-output string. State is reset only by constructing a new dummy.

## Dependencies And Integration Points
The class depends on `ITapeGcMgm`, `SpaceConfig`, `SpaceStats`, standard maps, and mutexes. It is a core test fixture dependency across `unit_tests/mgm/tgc`.

## Risks And Edge Cases
The fake returns successful values for file existence, file size, and eviction by default; tests that need failure behavior require either changes to the fake or a custom mock. The move constructor is declared as `const DummyTapeGcMgm&&`, which is unusual but still deletes moves for practical purposes.

## Test Signals
The fake itself should be covered by tests that verify default values, setter/getter behavior, thread-safe counters, and stdout retrieval used by `AsyncUint64ShellCmd`.
