# sources/distributed-fs/ceph-client/arch/mips/include/asm/traps.h

## Purpose

`traps.h` declares MIPS trap, exception, NMI, EJTAG, bus-error, cache-error, and page-fault entry points plus board hook pointers.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Macros/constants: `_ASM_TRAPS_H`, `MIPS_BE_DISCARD`, `MIPS_BE_FIXUP`, `MIPS_BE_FATAL`, `VECTORSPACING`, `nmi_notifier`. Types/enums/unions: `pt_regs`, `notifier_block`. Functions/prototypes/helpers: `mips_set_be_handler`, `register_nmi_notifier`, `reserve_exception_space`, `do_ade`, `do_be`, `do_ov`, `do_fpe`, `do_bp`, `do_tr`, `do_ri`, `do_cpu`, `do_msa_fpe`, `do_msa`, `do_mdmx`, `do_watch`, `do_mcheck`, `do_mt`, `do_dsp`, `do_reserved`, `do_ftlb`, `do_gsexc`, `do_daddi_ov`, `do_page_fault`, `cache_parity_error`, `ejtag_exception_handler`, `nmi_exception_handler`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with exception vector setup, notifier chains, fault handling, and board firmware hooks.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 69 lines and 2443 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
