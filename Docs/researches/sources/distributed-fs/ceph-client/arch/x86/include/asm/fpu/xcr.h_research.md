<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xcr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xcr.h

## Purpose
Inline wrappers for XGETBV/XSETBV and querying XINUSE state for XSAVE-enabled CPUs. The header is 35 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_FPU_XCR_H`; `#define XCR_XFEATURE_ENABLED_MASK 0x00000000`; `#define XCR_XFEATURE_IN_USE_MASK 0x00000001`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_XCR_H`; `#define XCR_XFEATURE_ENABLED_MASK 0x00000000`; `#define XCR_XFEATURE_IN_USE_MASK 0x00000001`; `static __always_inline u64 xgetbv(u32 index)`; `u32 eax, edx;`; `static inline void xsetbv(u32 index, u64 value)`; `u32 eax = value;`; `u32 edx = value >> 32;`; `static __always_inline u64 xfeatures_in_use(void)`

## Control Flow
xgetbv() and xsetbv() emit raw instructions with 64-bit split registers; xfeatures_in_use() reads XCR_XFEATURE_IN_USE_MASK.

## State and Persistence
No software state; hardware XCR registers persist per CPU and control enabled/in-use xstate components.

## Dependencies and Integration Points
Integrated by FPU initialization, xstate enablement, CPU feature setup, and diagnostics that need XCR0/XINUSE.

## Risks
Risks are executing on unsupported CPUs, writing illegal XCR values, and reading in contexts where xstate is not initialized.

## Test Signals
Tests should boot on XSAVE and non-XSAVE CPUs, validate XCR0 masks during FPU init, and exercise xfeatures_in_use after using extended states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xcr.h -->
