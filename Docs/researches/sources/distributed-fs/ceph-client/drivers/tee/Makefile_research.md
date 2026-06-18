# sources/distributed-fs/ceph-client/drivers/tee/Makefile

## Purpose
Defines the build composition for the generic TEE core and provider backends.

## Important APIs, Types, and Functions
`obj-$(CONFIG_TEE) += tee.o` builds the generic aggregate object from `tee_core.o`, `tee_heap.o`, `tee_shm.o`, and `tee_shm_pool.o`. Provider directories are included through `obj-$(CONFIG_OPTEE)`, `obj-$(CONFIG_AMDTEE)`, `obj-$(CONFIG_ARM_TSTEE)`, and `obj-$(CONFIG_QCOMTEE)`.

## Control Flow and State
No runtime flow. Kbuild links generic TEE support and selected provider drivers according to Kconfig.

## Dependencies and Integration Points
Depends on the source files in `drivers/tee/` and provider subdirectories. The generic object supplies shared device, heap, shared-memory, and pool services consumed by backends.

## Risks and Test Signals
Omitting a generic object would break backend linkage or user ABI support. Test signals include all selected providers linking against `tee.o`, module/built-in combinations for `CONFIG_TEE=m/y`, and no orphan provider object when TEE core is disabled.
