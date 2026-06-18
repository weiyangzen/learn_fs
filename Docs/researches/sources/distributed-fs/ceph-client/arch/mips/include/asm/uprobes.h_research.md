# sources/distributed-fs/ceph-client/arch/mips/include/asm/uprobes.h

## Purpose

`uprobes.h` defines MIPS uprobes instruction storage, break opcodes, XOL slot size, and per-task uprobe state.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `linux/notifier.h`, `linux/types.h`, `asm/break.h`, `asm/inst.h`. Macros/constants: `__ASM_UPROBES_H`, `MAX_UINSN_BYTES`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_BRK_UPROBE`, `UPROBE_BRK_UPROBE_XOL`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`. Types/enums/unions: `mips_instruction`, `arch_uprobe`, `arch_uprobe_task`, `uprobe_opcode_t`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with uprobes breakpoint insertion, branch-delay-slot handling, and trap return.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 46 lines and 1141 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
