# sources/distributed-fs/ceph-client/arch/mips/include/asm/vpe.h

## Purpose

`vpe.h` declares MIPS MT VPE loader state, thread-context state, control lists, file operations, notifications, memory allocation, and run/stop APIs.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/init.h`, `linux/list.h`, `linux/smp.h`, `linux/spinlock.h`. Macros/constants: `_ASM_VPE_H`, `VPE_MODULE_NAME`, `VPE_MODULE_MINOR`, `P_SIZE`, `MAX_VPES`. Types/enums/unions: `vpe_state`, `tc_state`, `vpe`, `list_head`, `tc`, `vpe_notifications`, `vpe_control`, `file_operations`. Functions/prototypes/helpers: `aprp_cpu_index`, `vpe_notify`, `get_vpe`, `get_tc`, `alloc_vpe`, `alloc_tc`, `release_vpe`, `release_progmem`, `vpe_run`, `cleanup_tc`, `vpe_module_init`, `vpe_start`, `vpe_stop`, `vpe_free`, `vpe_get_shared`, `alloc_progmem`, `vpe_module_exit`, `vpe_alloc`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with VPE loader device, MIPS MT secondary execution, and module lifecycle.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 131 lines and 2783 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
