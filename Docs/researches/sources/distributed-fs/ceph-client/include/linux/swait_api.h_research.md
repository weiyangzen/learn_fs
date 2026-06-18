<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait_api.h -->
# sources/distributed-fs/ceph-client/include/linux/swait_api.h

## Purpose

`swait_api.h` is a one-line compatibility or layering header that includes `linux/swait.h`. It provides an alternate include name for code that wants the simple waitqueue API without depending directly on the main header name.

## Important APIs, types, and functions

It exports no independent symbols. All visible API comes from `swait.h`: simple waitqueue heads, wait entries, wake functions, prepare/finish helpers, and wait-event macros.

## Control flow

There is no local control flow. Inclusion delegates preprocessing entirely to `swait.h`.

## State and persistence behavior

There is no local state. State behavior is exactly that of `swait.h` consumers.

## Dependencies and integration points

It depends solely on `linux/swait.h` and integrates as an include shim for kernel files that use simple wait queues.

## Risks and test signals

Risk is minimal, but duplicate or inconsistent include paths can hide dependency mistakes. Tests are compile-time only: ensure consumers including `swait_api.h` receive the same declarations as `swait.h` and do not rely on this header for any extra definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait_api.h -->
