# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/utsname.h

## Purpose
Provides `uname` support for nolibc.

## APIs, Types, and Functions
Defines `struct utsname` with Linux `_UTSNAME_LENGTH` fields and `_sys_uname`/`uname` wrappers.

## Control Flow, State, and Persistence
The wrapper fills caller-provided system-name fields from the kernel and translates errors. There is no persistent state.

## Dependencies and Integration
Depends on `../sys.h` and `<linux/utsname.h>`. It integrates with tools that report kernel and machine identity.

## Risks and Test Signals
Risks are structure length/layout mismatch with libc and callers assuming domainname availability semantics beyond this definition. Test signals are uname smoke tests, buffer field NUL termination checks, and comparison with libc `uname` output.
