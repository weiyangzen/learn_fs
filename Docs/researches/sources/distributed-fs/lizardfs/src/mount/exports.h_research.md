# sources/distributed-fs/lizardfs/src/mount/exports.h

## Purpose
`exports.h` exposes a single mutable process-local flag controlling whether non-root users may use a filesystem mounted in meta mode.

## Important APIs, Types, And Functions
- `inline bool& nonRootAllowedToUseMeta()` returns a reference to a function-local static bool.

## Control Flow
Callers read or assign through the returned reference. The static defaults to `false`.

## State And Persistence
The function-local static bool is process-local runtime state. It is not persisted.

## Dependencies And Integration Points
It includes `common/platform.h`. Mount authorization code can use this flag to gate meta-mode access for non-root users.

## Risks
- Returning a mutable global reference allows any includer to change policy without central auditing.
- Thread-safety is limited to C++ static initialization; reads/writes to the bool are not synchronized.

## Test Signals
Tests should verify default false value and policy behavior in code that consults the flag. Multi-threaded mutation should be avoided or synchronized by callers.
