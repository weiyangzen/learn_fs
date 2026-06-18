# sources/distributed-fs/ceph-client/arch/powerpc/kexec/core.c

## Purpose
Provides generic PowerPC kexec entry points, crashkernel reservation, and device-tree properties consumed by userspace and the next kernel.

## Important APIs, Types, And Functions
Defines `machine_crash_shutdown`, `machine_kexec_cleanup`, `machine_kexec`, `arch_reserve_crashkernel`, `kdump_cma_reserve`, `overlaps_crashkernel`, and `kexec_setup`. Internal helpers include `get_crash_base` and `export_crashk_values`.

## Control Flow
`machine_kexec` disables ftrace on the current CPU, calls the platform `machine_kexec` hook or `default_machine_kexec`, restores ftrace if it unexpectedly returns, and falls back to `machine_restart`. Crashkernel reservation parses `crashkernel=`, chooses or aligns a base, rejects overlap with the running kernel, and reserves memory through generic crashkernel helpers. Late init updates `/chosen` with `linux,kernel-end`, crashkernel base/size, and memory limit.

## State And Persistence
Persists crashkernel reservation in resource state, optional crash CMA size, and Open Firmware `/chosen` properties. No data files are written.

## Dependencies And Integration Points
Depends on generic kexec, memblock, ftrace, platform machine descriptors, fadump/kdump, Open Firmware device tree APIs, firmware features, and architecture constants such as `KDUMP_KERNELBASE`.

## Risks And Edge Cases
Crashkernel placement must avoid the running kernel and meet platform expectations, especially nonstatic kernels and LPAR RMA limits. `machine_kexec` is point-of-no-return code and must not allocate or fail. Device-tree property endianness differs by word size.

## Test Signals
Boot with multiple `crashkernel=` forms, inspect `/proc/device-tree/chosen` properties, verify overlap rejection, run normal kexec and crash kexec, and test LPAR/non-LPAR placement behavior.
