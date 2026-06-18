# sources/distributed-fs/ceph-client/tools/include/linux/debugfs.h

## Purpose

This is an empty compatibility header for copied kernel code that includes `<linux/debugfs.h>` in tools builds.

## APIs, State, and Dependencies

It defines only an include guard. There are no functions, macros, or state.

## Risks and Test Signals

Code requiring actual debugfs APIs cannot use this stub. Compile tests should identify any consumer that needs more than header presence.
