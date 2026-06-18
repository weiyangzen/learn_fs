
# sources/distributed-fs/ceph-client/lib/test_debug_virtual.c

## Purpose

This small module probes `CONFIG_DEBUG_VIRTUAL` behavior by deliberately calling `virt_to_phys()` on representative virtual addresses and printing the resulting physical address. It first uses `VMALLOC_START`, then a dynamically allocated `struct foo`.

## Important APIs, Types, And Functions

The key state is `static struct foo *foo`. `test_debug_virtual_init()` computes and logs physical addresses using `virt_to_phys()`, allocates `foo` with `kzalloc_obj()`, and returns `-ENOMEM` on allocation failure. `test_debug_virtual_exit()` frees the allocation.

## Control Flow And State

On module load, the test performs two conversions and logs both. Only the heap allocation persists until module unload. The module has no sysfs/debugfs interface and no recurring work.

## Dependencies And Integration Points

It includes memory, vmalloc, slab, I/O, page, and module headers. The test is meaningful on architectures that implement `CONFIG_DEBUG_VIRTUAL` checks for invalid virtual-to-physical conversions; MIPS has an additional bootinfo include.

## Risks And Test Signals

The test intentionally touches a suspicious conversion path, so useful signals are WARN splats or diagnostic output from debug virtual checks and the two `pr_info()` address lines. The only cleanup risk is leaked `foo` if init failed after allocation, which does not happen in this straight-line code.
