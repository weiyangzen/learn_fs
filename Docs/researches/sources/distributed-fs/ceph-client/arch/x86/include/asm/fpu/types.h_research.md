<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/types.h

## Purpose
Canonical x86 FPU/xstate data model: legacy FSAVE/FXSAVE/software states, XSAVE feature masks, extended component layouts, task fpstate, permissions, and guest FPU containers. The header is 647 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/page_types.h>`

Notable constants/macros: `#define _ASM_X86_FPU_TYPES_H`; `#define MXCSR_DEFAULT 0x1f80`; `#define MXCSR_AND_FLAGS_SIZE sizeof(u64)`; `#define XFEATURE_MASK_FP (1 << XFEATURE_FP)`; `#define XFEATURE_MASK_SSE (1 << XFEATURE_SSE)`; `#define XFEATURE_MASK_YMM (1 << XFEATURE_YMM)`; `#define XFEATURE_MASK_BNDREGS (1 << XFEATURE_BNDREGS)`; `#define XFEATURE_MASK_BNDCSR (1 << XFEATURE_BNDCSR)`; `#define XFEATURE_MASK_OPMASK (1 << XFEATURE_OPMASK)`; `#define XFEATURE_MASK_ZMM_Hi256 (1 << XFEATURE_ZMM_Hi256)`; `#define XFEATURE_MASK_Hi16_ZMM (1 << XFEATURE_Hi16_ZMM)`; `#define XFEATURE_MASK_PT (1 << XFEATURE_PT_UNIMPLEMENTED_SO_FAR)`; `#define XFEATURE_MASK_PKRU (1 << XFEATURE_PKRU)`; `#define XFEATURE_MASK_PASID (1 << XFEATURE_PASID)`; `#define XFEATURE_MASK_CET_USER (1 << XFEATURE_CET_USER)`; `#define XFEATURE_MASK_CET_KERNEL (1 << XFEATURE_CET_KERNEL)`; `#define XFEATURE_MASK_LBR (1 << XFEATURE_LBR)`; `#define XFEATURE_MASK_XTILE_CFG (1 << XFEATURE_XTILE_CFG)`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_TYPES_H`; `struct fregs_state {`; `u32 cwd; /* FPU Control Word */`; `u32 swd; /* FPU Status Word */`; `u32 twd; /* FPU Tag Word */`; `u32 fip; /* FPU IP Offset */`; `u32 fcs; /* FPU IP Selector */`; `u32 foo; /* FPU Operand Pointer Offset */`; `u32 fos; /* FPU Operand Pointer Selector */`; `u32 st_space[20];`; `u32 status;`; `struct fxregs_state {`; `u16 cwd; /* Control Word */`; `u16 swd; /* Status Word */`; `u16 twd; /* Tag Word */`; `u16 fop; /* Last Instruction Opcode */`; `union {`; `struct {`; `u64 rip; /* Instruction Pointer */`; `u64 rdp; /* Data Pointer */`; `u32 foo; /* FPU Operand Offset */`; `u32 fos; /* FPU Operand Selector */`; `u32 mxcsr; /* MXCSR Register State */`; `u32 mxcsr_mask; /* MXCSR Mask */`

## Control Flow
No executable control flow; structure layout and feature masks drive save/restore, signal, ptrace, prctl, scheduler, and KVM decisions across the FPU subsystem.

## State and Persistence
State is task-local struct fpu and struct fpstate, optional dynamic/vmalloc fpstate buffers, permission bitmaps, guest fpstate, XFD, and boot-time fpu_state_config globals.

## Dependencies and Integration Points
Depends on page sizing, CPU xfeature enumeration, XSAVE UABI, KVM, CET, AMX, APX, PKRU, PASID, LBR, MPX, and memory alignment rules.

## Risks
Risks are severe because layouts are ABI-sensitive: adding fields after dynamic regs, wrong xfeature masks, compacted/non-compacted confusion, or guest/user feature leakage can corrupt context or UABI.

## Test Signals
Tests need compile-time layout checks, ptrace/signal/core-dump ABI validation, context-switch stress for all xfeatures, KVM guest feature negotiation, dynamic AMX/APX permission expansion, and confidential guest paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/types.h -->
