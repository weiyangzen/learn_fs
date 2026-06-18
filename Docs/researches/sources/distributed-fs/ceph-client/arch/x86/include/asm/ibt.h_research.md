<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ibt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ibt.h

## Purpose
Indirect Branch Tracking support helpers for ENDBR instruction bytes, validation, sealing, and objtool/runtime integration. The header is 117 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`

Notable constants/macros: `#define _ASM_X86_IBT_H`; `#define HAS_KERNEL_IBT 1`; `#define ASM_ENDBR "endbr64\n\t"`; `#define ASM_ENDBR "endbr32\n\t"`; `#define __noendbr __attribute__((nocf_check))`; `#define IBT_NOSEAL(fname) \`; `#define ENDBR endbr64`; `#define ENDBR endbr32`; `#define HAS_KERNEL_IBT 0`; `#define ASM_ENDBR`; `#define IBT_NOSEAL(name)`; `#define __noendbr`; `#define ENDBR`; `#define ENDBR_INSN_SIZE (4*HAS_KERNEL_IBT)`

Notable declarations and inline helpers: `#define _ASM_X86_IBT_H`; `#define HAS_KERNEL_IBT 1`; `#define ASM_ENDBR "endbr64\n\t"`; `#define ASM_ENDBR "endbr32\n\t"`; `#define __noendbr __attribute__((nocf_check))`; `#define IBT_NOSEAL(fname) \`; `static __always_inline __attribute_const__ u32 gen_endbr(void)`; `u32 endbr;`; `static __always_inline __attribute_const__ u32 gen_endbr_poison(void)`; `static inline bool __is_endbr(u32 val)`; `extern __noendbr bool is_endbr(u32 *val);`; `extern __noendbr u64 ibt_save(bool disable);`; `extern __noendbr void ibt_restore(u64 save);`; `#define ENDBR endbr64`; `#define ENDBR endbr32`; `#define HAS_KERNEL_IBT 0`; `#define ASM_ENDBR`; `#define IBT_NOSEAL(name)`; `#define __noendbr`; `static inline bool is_endbr(u32 *val) { return false; }`; `static inline u64 ibt_save(bool disable) { return 0; }`; `static inline void ibt_restore(u64 save) { }`; `#define ENDBR`; `#define ENDBR_INSN_SIZE (4*HAS_KERNEL_IBT)`

## Control Flow
Helpers detect ENDBR at function entries, let ftrace adjust symbol addresses, and provide macros or stubs depending on CET/IBT config.

## State and Persistence
State is code text contents and metadata used for sealing or validation; no mutable state is stored in the header.

## Dependencies and Integration Points
Depends on CET config, objtool, alternatives/text patching, ftrace, module loading, and compiler-generated ENDBR.

## Risks
Risks include misidentifying function entry addresses, breaking tracing/kprobes on ENDBR-prefixed functions, and weak coverage on non-IBT builds.

## Test Signals
Tests should boot IBT-enabled kernels, load modules, run ftrace/kprobes/livepatch, validate objtool warnings, and ensure non-IBT stubs compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ibt.h -->
