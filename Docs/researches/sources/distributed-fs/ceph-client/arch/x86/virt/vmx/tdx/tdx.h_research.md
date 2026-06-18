# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx.h

Purpose: Defines the local TDX host architecture constants and private data structures used by `tdx.c`. It separates hardware-defined TDX ABI values from Linux-only helper state.

Important APIs/types/functions: The header enumerates TDH.* SEAMCALL leaf IDs, `TDX_VERSION_SHIFT`, TDX physical page types `PT_NDA` and `PT_RSVD`, TDMR alignment constants, `struct tdmr_reserved_area`, packed/aligned `struct tdmr_info`, `TDX_FEATURES0_NO_RBP_MOD`, `struct tdx_memblock`, `TDMR_NR_WARN`, and `struct tdmr_info_list`.

Control flow and state: This file has no executable control flow, but its layout definitions control how `tdx.c` builds the physical TDMR array passed to TDH.SYS.CONFIG. `tdmr_info` uses a flexible reserved-area tail whose size is calculated from TDX module metadata. `tdx_memblock` records source memory PFN ranges and NUMA node IDs, while `tdmr_info_list` records the contiguous TDMR allocation, element size, maximum count, and consumed count.

Dependencies and integration points: It includes `linux/bits.h` and is included by the TDX host implementation. Its constants must match the TDX module ABI and the generic `asm/tdx.h` structures used for SEAMCALL arguments.

Risks and test signals: Because these structures are consumed by firmware/module code, packing, alignment, leaf IDs, and page type values are ABI-sensitive. Regression signals are TDX module initialization failures, unexpected TDH.SYS.CONFIG errors, reserved-area exhaustion warnings, or KVM TDX wrapper calls targeting the wrong leaf.
