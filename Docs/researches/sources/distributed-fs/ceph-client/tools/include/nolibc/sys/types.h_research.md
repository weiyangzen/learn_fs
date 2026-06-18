# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/types.h

## Purpose
Compatibility shim for `<sys/types.h>` under nolibc.

## APIs, Types, and Functions
Includes `../types.h` and defines no additional APIs.

## Control Flow, State, and Persistence
No runtime control flow or state exists. It exposes nolibc's POSIX-ish typedefs and structs through the conventional include path.

## Dependencies and Integration
Depends on `types.h`. It integrates with portable code that includes system type definitions before other headers.

## Risks and Test Signals
Risks are incomplete typedef coverage compared with glibc and include-order conflicts if mixed with system libc headers. Test signals are compiling representative portable sources and checking every required typedef is present.
