
# sources/distributed-fs/ceph-client/drivers/soc/lantiq/Makefile

## Purpose
Always builds the Lantiq FPI bus driver object for this directory.

## Important APIs, Types, and Functions
No runtime APIs. Rule: `obj-y += fpi-bus.o`.

## Control Flow
Build includes the FPI bus driver whenever the directory is part of the kernel build.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with `fpi-bus.c`, which has OF compatible gating.

## Risks
Unconditional object inclusion relies on runtime compatible matching to avoid action on other platforms.

## Test Signals
Build inclusion and nonmatching platform no-op behavior.
