# sources/distributed-fs/lizardfs/src/master/metadata_dumper.h

## Purpose

`metadata_dumper.h` declares the `MetadataDumper` class used by the master to orchestrate foreground/background metadata dumping and optional metarestore-assisted dumping. The source was read as a complete 88-line header.

## Important APIs, Types, and Functions

The class exposes `DumpType` (`kForegroundDump`, `kBackgroundDump`), construction with metadata/tmp filenames, status getters, setters for metarestore path/use, `start`, poll hooks `pollDesc`/`pollServe`, and blocking waits. Protected state includes dump success flags, child pipe fd, poll index, output-empty flag, metarestore path, and metadata paths.

## Control Flow

The header documents the class API but has no implementation flow. Callers invoke `start` before a metadata store and then use poll or wait helpers to observe the background process.

## State and Persistence Behavior

The class stores runtime process-monitoring state only. It names metadata files but does not define their format or write them directly in the header.

## Dependencies and Integration Points

It includes polling, logging, time utilities, and standard path/string/vector support. It integrates with the master event loop and filesystem metadata store logic.

## Risks and Edge Cases

Callers must respect the special child-return case from `start`: true means execution continues in the child and `dumpType` has been changed to foreground. Poll hooks support at most one fd per dumper instance.

## Test Signals

Compile coverage, API tests for state transitions, and integration tests that run background dump flows through event-loop polling or timeout waits.
