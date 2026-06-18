# sources/distributed-fs/ceph-client/drivers/edac/mce_amd.h Research

## Purpose
`mce_amd.h` is the internal/public header for the AMD EDAC MCE decoder. It defines bitfield macros for AMD MCA error-code interpretation, enums for decoded field IDs, the per-family decoder-ops structure, and exported registration APIs for DRAM ECC decoders.

## Important APIs, Types, and Functions
Macros `EC()`, `LOW_SYNDROME()`, and `HIGH_SYNDROME()` extract generic status fields. `TLB_ERROR()`, `MEM_ERROR()`, `BUS_ERROR()`, and `INT_ERROR()` classify MCA error codes. `TT()`, `II()`, `LL()`, `TO()`, `PP()`, `UU()`, and `R4()` extract transaction, memory/IO, cache-level, timeout, participating-processor, internal-error, and memory-transaction fields; the corresponding `_MSG()` macros index message tables defined in `mce_amd.c`.

The enums `tt_ids`, `ll_ids`, `ii_ids`, and `rrrr_ids` name the encoded values used by the decoder logic. `struct amd_decoder_ops` carries function pointers for family-specific MC0/MC1/MC2 decoding. `amd_register_ecc_decoder()` and `amd_unregister_ecc_decoder()` let AMD memory-controller EDAC drivers attach a DRAM ECC decoder callback. `pp_msgs` is declared for external use.

## Control Flow
This header has no runtime control flow. It shapes the control flow in `mce_amd.c` and companion AMD EDAC drivers by providing classification predicates and callback declarations.

## State and Persistence
The header defines no storage except external declarations. State lives in the implementation file and consumers.

## Dependencies and Integration Points
It depends on Linux notifier declarations and `asm/mce.h` for `struct mce` and MCE bit definitions. It integrates the generic AMD MCE decoder with memory-controller-specific DRAM ECC decoding modules.

## Risks and Edge Cases
The macros assume AMD MCA encoding layouts. Using them for non-AMD/Hygon records or future encodings without updates can misclassify errors. `_MSG()` macros do not bounds-check except `R4_MSG()`, so callers rely on masked field widths matching message table lengths. Callback signatures expose only node ID and raw MCE, so richer topology must be derived by consumers.

## Test Signals
Header-level test signals are compile coverage across `mce_amd.c` and AMD EDAC users, correct macro expansion for representative status values, exported symbol availability for callback registration, and static analysis confirming enum/macro values align with decoder tables.
