# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-vmem.c

## Purpose

Provides public SPL `vmem_*` allocation wrappers backed by the SPL kmem implementation.

## Functions

- `spl_vmem_alloc(size, flags, func, line)`: validates public kmem flags, adds `KM_VMEM`, then dispatches to normal, debug, or tracking allocation implementation depending on build configuration.
- `spl_vmem_zalloc(size, flags, func, line)`: same as allocation, adding `KM_ZERO`.
- `spl_vmem_free(buf, size)`: frees through normal, debug, or tracking implementation.
- `spl_vmem_init()` / `spl_vmem_fini()`: no-op lifecycle hooks.

## Exports

- `spl_vmem_alloc`
- `spl_vmem_zalloc`
- `spl_vmem_free`

## Notes

This file is a thin compatibility layer. The real allocation behavior lives in the SPL kmem allocator selected by build flags such as `DEBUG_KMEM` and `DEBUG_KMEM_TRACKING`.
