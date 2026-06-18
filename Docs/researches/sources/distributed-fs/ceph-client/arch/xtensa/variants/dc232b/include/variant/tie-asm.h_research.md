# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/tie-asm.h

## Purpose
This assembler header saves/restores `dc232b` optional non-coprocessor state.

## Important APIs, types, and functions
`xchal_ncp_store` and `xchal_ncp_load` handle MAC16 `ACCLO/ACCHI` and `M0`-`M3`, `SCOMPARE1`, and `THREADPTR`. The older macro form accepts `continue`, `ofs`, and `select` but not the newer `alloc` parameter. Two temporary registers are required.

## Control flow
Expanded save/load macros align the save-area pointer and conditionally emit special/user register transfers based on `XTHAL_SAS_*` masks. Stores use `rsr`/`rur` plus `s32i`; loads use `l32i` plus `wsr`/`wur`.

## State and persistence behavior
The macros persist 32 bytes of optional state matching `tie.h`. There is no boolean `BR` state for this variant. CP7 `XTIOP` exists but has no context bytes or load/store macro body.

## Dependencies and integration points
The file must match `dc232b` `tie.h` register ordering and `core.h` feature flags. It integrates with common Xtensa assembly save-area helpers.

## Risks and edge cases
Because this header uses the legacy no-`alloc` macro signature, shared assembly must account for variant macro differences. Save and restore `select` masks must match exactly. Misalignment or use on a core without matching MAC16/threadptr support corrupts register state.

## Test signals
Build this variant's assembly, then stress TLS, MAC16, conditional-store code, context switches, and signal return. Compile shared save-area users against both old and new macro signatures.
