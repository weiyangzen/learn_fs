<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gsseg.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/gsseg.h

## Purpose
Helpers for GS-segment based percpu addressing in 32-bit and 64-bit x86 contexts. The header is 66 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`; `#include <asm/asm.h>`; `#include <asm/cpufeature.h>`; `#include <asm/alternative.h>`; `#include <asm/processor.h>`; `#include <asm/nops.h>`

Notable constants/macros: `#define _ASM_X86_GSSEG_H`; `#define LKGS_DI _ASM_BYTES(0xf2,0x0f,0x00,0xf7)`

Notable declarations and inline helpers: `#define _ASM_X86_GSSEG_H`; `extern asmlinkage void asm_load_gs_index(u16 selector);`; `#define LKGS_DI _ASM_BYTES(0xf2,0x0f,0x00,0xf7)`; `static inline void native_lkgs(unsigned int selector)`; `u16 sel = selector;`; `static inline void native_load_gs_index(unsigned int selector)`; `unsigned long flags;`; `static inline void __init lkgs_init(void)`; `static inline void load_gs_index(unsigned int selector)`

## Control Flow
Macros and inline assembly access percpu/current data through GS-relative offsets or alternate segment forms depending on configuration.

## State and Persistence
State is implicit in CPU segment base and percpu layout; callers read/write per-CPU memory rather than file-local state.

## Dependencies and Integration Points
Depends on asm/percpu, segment setup, FSGSBASE/swapgs conventions, and compiler asm constraints.

## Risks
Risks include wrong segment assumption across user/kernel transitions, incorrect offset size, and hard-to-debug percpu corruption.

## Test Signals
Tests should cover percpu access on 32-bit/64-bit, context switches, interrupt entry, and configs with different segment-base mechanisms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gsseg.h -->
