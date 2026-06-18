# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_defs.h

Purpose: supplies the shared preprocessor and bitfield machinery used by all SiByte hardware headers. It also defines the compile-time feature-selection model for chip families and revisions.

Important APIs/types/functions: key feature masks are `SIBYTE_HDR_FMASK_*`, `SIBYTE_HDR_FEATURES`, `SIBYTE_HDR_FEATURE_CHIP`, `SIBYTE_HDR_FEATURE`, `SIBYTE_HDR_FEATURE_EXACT`, `SIBYTE_HDR_FEATURE_UP_TO`, and `SIBYTE_HDR_FEATURE_1250_112x`. Bitfield helpers include `_SB_MAKE64`, `_SB_MAKEMASK1`, `_SB_MAKEMASK`, `_SB_MAKEVALUE`, `_SB_GETVALUE`, and 32-bit variants. On MIPS64 C builds it also defines register access macros `SBWRITECSR(csr, val)` and `SBREADCSR(csr)`.

Control flow: most dependent headers branch at preprocessing time based on `SIBYTE_HDR_FEATURES`, exposing only fields valid for selected chip revisions. Runtime code then uses the bitfield helpers to assemble or decode MMIO register values.

State and persistence: the header has no runtime state. `SBWRITECSR` and `SBREADCSR` are direct volatile MMIO accessors and therefore read/write persistent hardware register state selected by callers.

Dependencies and integration: requires ANSI C89 preprocessing and 64-bit integer support; C users must have `uint32_t` and `uint64_t` defined. It is included by the register, DMA, MAC, memory-controller, generic-bus, interrupt, L2, and LDT headers.

Risks and test signals: incorrect `SIBYTE_HDR_FEATURES` settings can hide needed macros or expose invalid ones, causing either build failures or wrong register programming. The helper macros rely on correct integer widths and should be checked in assembler and C preprocessing contexts. Test signals include compile matrices for all feature masks, macro expansion tests for masks crossing bit 31, and sparse/`-Wshift-*` builds on 32- and 64-bit toolchains.
