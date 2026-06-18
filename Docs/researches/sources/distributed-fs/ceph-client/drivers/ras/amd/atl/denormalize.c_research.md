# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/denormalize.c

## Purpose
Reconstructs address bits removed by AMD Data Fabric normalization, inserting coherent-station/channel/die/socket interleave information before dehashing.

## Important APIs, types, and functions
`denormalize_address()` is the dispatcher. Shared helpers compute destination fabric ID, make address gaps (`make_space_for_coh_st_id_*()`), derive coherent-station IDs (`get_coh_st_id_df2/df4/mi300()` and `calculate_coh_st_id()`), insert IDs, and translate physical-to-logical coherent station IDs including MI300 fixed mapping. Special algorithms are `denorm_addr_df3_6chan()`, `denorm_addr_df4_np2()`, and `denorm_addr_df4p5_np2()` with `struct df4p5_denorm_ctx`.

## Control flow
Power-of-two and common hashed modes convert physical to logical fabric ID, expand address bits to create gaps, calculate interleave/coherent-station ID, then insert it. DF3 six-channel computes high interleave bits and mod3 adjustments based on map size. DF4 non-power-of-two modes rebuild address groups for 3/5/6/10/12 channel interleaves and account for hash bit 8 locally. DF4.5 non-power-of-two modes initialize a context describing lost bits, modulo divisor, base denormalized address, divided high address, and target logical fabric ID; then `check_permutations()` enumerates all dropped remainders and lost-bit combinations, rehashes candidate SPAs, verifies logical fabric ID and re-normalized address, and keeps the highest valid SPA.

## State and persistence
No persistent state. Mutates `ctx->ret_addr` and sometimes `ctx->coh_st_fabric_id`. Temporary `df4p5_denorm_ctx` tracks candidate and resolved SPAs. Reads `df_cfg` masks/shifts and map remap arrays.

## Dependencies and integration
Depends on `internal.h` bit helpers, map metadata from `get_address_map()`, system masks in `df_cfg`, and `add_base_and_hole()`/`remove_base_and_hole()` from `core.c` for DF4.5 candidate verification. Called before `dehash_address()`.

## Risks
This is the highest-complexity ATL logic. DF4.5 permutation search can be expensive but bounded by small modulo/lost-bit counts. Selecting the highest valid SPA is a policy choice that should match hardware expectations. Physical-to-logical remap failures only debug-print and can feed an out-of-range value. Any mismatch in map fields, remap arrays, or hash controls produces silent wrong addresses unless golden vectors catch it.

## Test signals
Golden translations for every supported interleave mode, remap enabled/disabled, socket and die interleaving, MI300 fixed remap, DF3 six-channel edge cases, DF4 3/5/6/10/12 channel modes, DF4.5 1K/2K NP2 modes including multiple valid candidates, and unknown-mode error paths.
