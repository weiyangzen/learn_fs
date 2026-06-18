# sources/distributed-fs/ceph-client/tools/include/asm/rwonce.h

## Purpose

This file is intentionally empty in this source snapshot. It reserves the tools include path for architecture-specific `rwonce` content while the active `READ_ONCE` and `WRITE_ONCE` definitions come from `linux/compiler.h`.

## APIs, State, and Dependencies

There are no macros, functions, includes, or state in the file.

## Risks and Test Signals

Consumers must not rely on this header to provide APIs directly. Tests are compile checks for code that includes `<asm/rwonce.h>` indirectly and gets actual access macros from the proper compiler headers.
