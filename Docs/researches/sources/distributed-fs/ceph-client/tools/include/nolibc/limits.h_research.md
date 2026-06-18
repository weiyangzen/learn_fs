# sources/distributed-fs/ceph-client/tools/include/nolibc/limits.h

## Purpose
Compatibility entry point for nolibc limits definitions.

## APIs, Types, and Functions
The file includes `nolibc.h`; common path and file constants are provided elsewhere, especially `types.h` for `PATH_MAX` and `MAXPATHLEN`.

## Control Flow, State, and Persistence
There is no runtime behavior. All effect is compile-time inclusion of the broader nolibc surface.

## Dependencies and Integration
Depends on the nolibc umbrella header. It integrates with code that includes `<limits.h>` but only needs constants already defined by the nolibc set.

## Risks and Test Signals
Risks are incomplete libc compatibility for numeric limits such as `INT_MAX` or `CHAR_BIT` if consumers expect a full limits header. Test signals are compiling representative nolibc programs and adding targeted checks for every limit macro they require.
