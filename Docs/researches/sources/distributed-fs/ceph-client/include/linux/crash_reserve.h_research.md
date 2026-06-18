<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_reserve.h -->
# sources/distributed-fs/ceph-client/include/linux/crash_reserve.h

## Purpose

`crash_reserve.h` declares crashkernel reservation resources, command-line parsing, optional CMA-backed crash ranges, and generic architecture reservation defaults. The source was read as a complete 66-line file.

## Important APIs, Types, and Functions

Global resources include `crashk_res`, `crashk_low_res`, `crashk_cma_ranges[]`, and optionally `crashk_cma_cnt`. `parse_crashkernel()` parses crashkernel command-line sizing, base, low memory, CMA size, and high/low mode. `reserve_crashkernel_cma()` handles CMA reservation. With generic crashkernel reservation support, defaults include `arch_add_crash_res_to_iomem()`, `DEFAULT_CRASH_KERNEL_LOW_SIZE`, `CRASH_ALIGN`, `CRASH_ADDR_LOW_MAX`, `CRASH_ADDR_HIGH_MAX`, and `reserve_crashkernel_generic()`.

## Control Flow

Early boot parses crashkernel parameters, chooses crash/high/low/CMA sizes, reserves resources, and optionally reports them in iomem. Generic reservation code is used when the architecture opts in, otherwise the generic function is a no-op.

## State and Persistence Behavior

Crashkernel memory is represented by global `struct resource` objects and optional CMA ranges for the boot lifetime. These reservations protect memory for the capture kernel.

## Dependencies and Integration Points

It depends on linkage, ELF core definitions, optional architecture crash reservation headers, resources, ranges, memblock, and CMA configuration. It integrates with boot command-line parsing, iomem resources, kexec/kdump, and architecture memory layout constraints.

## Risks and Edge Cases

Crashkernel sizing must respect low-memory requirements, high-memory limits, alignment, and reserved resource overlap. CMA crash ranges only exist with both CMA and generic architecture support. Architecture defaults may be overridden and must match platform addressing.

## Test Signals

Signals include boot tests for `crashkernel=` variants, resource tree inspection, low/high reservation boundary tests, CMA crashkernel reservation tests, architecture override builds, and kdump load/boot validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_reserve.h -->
