# sources/distributed-fs/ceph-client/drivers/tee/amdtee/Makefile

## Purpose
Defines the AMDTEE backend aggregate object and its component source files.

## Important APIs, Types, and Functions
`obj-$(CONFIG_AMDTEE) += amdtee.o` builds the backend, and `amdtee-objs` includes `core.o`, `call.o`, and `shm_pool.o`.

## Control Flow and State
No runtime flow. Kbuild composes one AMDTEE module/built-in object from core registration, secure calls, and shared-memory pool support.

## Dependencies and Integration Points
Depends on the generic TEE core build and AMD PSP/CCP services selected by Kconfig. The component split maps to driver lifecycle, command invocation, and shared memory handling.

## Risks and Test Signals
Missing any component would break provider registration or command/shared-memory operations. Test signals include module link success and `modinfo`/built-in symbol presence for all three implementation areas.
