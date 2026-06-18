<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_8xx.h

## Purpose
`cpu_specs_8xx.h` provides the CPU descriptor for classic 8xx PowerPC processors. It is the minimal cputable input for kernels targeting the 8xx MMU and cache model.

## Important APIs, Types, And Functions
The file defines `static struct cpu_spec cpu_specs[] __initdata` with one 8xx entry. The descriptor uses `PVR_8xx`, `CPU_FTRS_8XX`, `MMU_FTR_TYPE_8xx`, 16-byte I/D cache line sizes, `machine_check_8xx`, and platform string `ppc823`.

## Control Flow
There is a single high-16-bit PVR match. Unlike other tables, there is no explicit zero-mask default in this file, so unsupported PVRs should fail identification rather than silently booting as generic 8xx.

## State And Persistence
Only init-time metadata is defined here. The selected descriptor is copied to `cur_cpu_spec` and then drives runtime feature checks.

## Dependencies And Integration Points
It integrates with `cputable.c`, 8xx MMU initialization, cache maintenance, machine-check handling, and userspace HWCAP generation. The comment notes possible doze support if the 8xx code is present.

## Risks
The lack of a fallback is intentional but means any new 8xx PVR must be added explicitly. Cache-line size or MMU feature errors would affect low-level memory management and DMA/cache coherency assumptions.

## Test Signals
Successful 8xx boot should identify the CPU as `8xx`, expose 32-bit MMU HWCAPs, use 16-byte cache blocks, and route machine checks through `machine_check_8xx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_8xx.h -->
