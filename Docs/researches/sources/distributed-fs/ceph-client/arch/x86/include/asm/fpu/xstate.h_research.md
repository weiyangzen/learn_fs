<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xstate.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xstate.h

## Purpose
XSAVE policy header defining supported/restored/user/supervisor feature masks, XSAVE area constants, xstate size dynamism, and low-level save/restore entry points. The header is 134 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/uaccess.h>`; `#include <linux/types.h>`; `#include <asm/processor.h>`; `#include <asm/fpu/api.h>`; `#include <asm/user.h>`

Notable constants/macros: `#define __ASM_X86_XSAVE_H`; `#define XFEATURE_MASK_EXTEND (~(XFEATURE_MASK_FPSSE | (1ULL << 63)))`; `#define FXSAVE_SIZE 512`; `#define XSAVE_HDR_SIZE 64`; `#define XSAVE_HDR_OFFSET FXSAVE_SIZE`; `#define XSAVE_YMM_SIZE 256`; `#define XSAVE_YMM_OFFSET (XSAVE_HDR_SIZE + XSAVE_HDR_OFFSET)`; `#define XSAVE_ALIGNMENT 64`; `#define XFEATURE_MASK_USER_SUPPORTED (XFEATURE_MASK_FP | \`; `#define XFEATURE_MASK_USER_RESTORE \`; `#define XFEATURE_MASK_USER_DYNAMIC XFEATURE_MASK_XTILE_DATA`; `#define XFEATURE_MASK_GUEST_SUPERVISOR XFEATURE_MASK_CET_KERNEL`; `#define XFEATURE_MASK_SUPERVISOR_SUPPORTED (XFEATURE_MASK_PASID | \`; `#define XFEATURE_MASK_INDEPENDENT (XFEATURE_MASK_LBR)`; `#define XFEATURE_MASK_SUPERVISOR_UNSUPPORTED (XFEATURE_MASK_PT)`; `#define XFEATURE_MASK_SUPERVISOR_ALL (XFEATURE_MASK_SUPERVISOR_SUPPORTED | \`; `#define XFEATURE_MASK_FPSTATE (XFEATURE_MASK_USER_RESTORE | \`; `#define XFEATURE_MASK_SIGFRAME_INITOPT (XFEATURE_MASK_XTILE | \`

Notable declarations and inline helpers: `#define __ASM_X86_XSAVE_H`; `#define XFEATURE_MASK_EXTEND (~(XFEATURE_MASK_FPSSE | (1ULL << 63)))`; `#define FXSAVE_SIZE 512`; `#define XSAVE_HDR_SIZE 64`; `#define XSAVE_HDR_OFFSET FXSAVE_SIZE`; `#define XSAVE_YMM_SIZE 256`; `#define XSAVE_YMM_OFFSET (XSAVE_HDR_SIZE + XSAVE_HDR_OFFSET)`; `#define XSAVE_ALIGNMENT 64`; `#define XFEATURE_MASK_USER_SUPPORTED (XFEATURE_MASK_FP | \`; `#define XFEATURE_MASK_USER_RESTORE \`; `#define XFEATURE_MASK_USER_DYNAMIC XFEATURE_MASK_XTILE_DATA`; `#define XFEATURE_MASK_GUEST_SUPERVISOR XFEATURE_MASK_CET_KERNEL`; `#define XFEATURE_MASK_SUPERVISOR_SUPPORTED (XFEATURE_MASK_PASID | \`; `#define XFEATURE_MASK_INDEPENDENT (XFEATURE_MASK_LBR)`; `#define XFEATURE_MASK_SUPERVISOR_UNSUPPORTED (XFEATURE_MASK_PT)`; `#define XFEATURE_MASK_SUPERVISOR_ALL (XFEATURE_MASK_SUPERVISOR_SUPPORTED | \`; `#define XFEATURE_MASK_FPSTATE (XFEATURE_MASK_USER_RESTORE | \`; `#define XFEATURE_MASK_SIGFRAME_INITOPT (XFEATURE_MASK_XTILE | \`; `extern u64 xstate_fx_sw_bytes[USER_XSTATE_FX_SW_WORDS];`; `extern void __init update_regset_xstate_info(unsigned int size,`; `u64 xstate_mask);`; `int xfeature_size(int xfeature_nr);`; `void xsaves(struct xregs_state *xsave, u64 mask);`; `void xrstors(struct xregs_state *xsave, u64 mask);`

## Control Flow
Code saves/restores selected masks through xsaves()/xrstors(), resolves component addresses with xfeature_size()/get_xsave_addr(), and gates dynamic sizing through static keys.

## State and Persistence
State is boot-computed xstate_fx_sw_bytes, fpu state size configs, XFD-enabled dynamic features, and per-task fpstate masks.

## Dependencies and Integration Points
Depends on uaccess, processor features, fpu API/types, user ABI structures, static keys, and XSAVE instruction support.

## Risks
Risks include exposing unsupported supervisor features, wrong signal-frame init optimization, dynamic-size static-key mistakes, and inconsistent guest/user masks.

## Test Signals
Tests should cover xstate enumeration on varied CPUs, AMX dynamic allocation, supervisor PASID/CET paths, KVM guest masks, sigframe restore masks, and CPUs without XSAVE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xstate.h -->
