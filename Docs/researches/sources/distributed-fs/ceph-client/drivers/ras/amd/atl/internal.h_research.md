# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/internal.h

## Purpose
Private header for AMD ATL. It defines Data Fabric revision/mode enums, global configuration structures, address-map and translation context structures, cross-file prototypes, PRM hooks, bit manipulation helpers, debug helpers, and MI300 MCA address fields.

## Important APIs, types, and functions
Defines `enum df_revisions`, extensive `enum intlv_modes`, `struct df4p5_denorm_ctx`, `struct df_flags`, `struct df_config`, `struct dram_addr_map`, `struct addr_ctx_inputs`, and `struct addr_ctx`. Declares DF indirect access, system info, node determination, MI300 UMC info, address map lookup, denormalization, dehashing, UMC conversion, base/hole helpers, and optional `prm_umc_norm_to_sys_addr()`. Inline helpers `expand_bits()` and `remove_bits()` are central to address reconstruction.

## Control flow
No top-level runtime flow. Inline `expand_bits()` inserts a gap of `num_bits` at `bit_num`; `remove_bits()` removes an inclusive bit range. PRM fallback returns `-ENODEV` when `CONFIG_AMD_ATL_PRM` is disabled. Debug helpers standardize context-rich messages.

## State and persistence
Declares external global `df_cfg`, which persists for module lifetime and carries DF revision, masks, shifts, map count, hole base, and flags. Structures defined here hold per-map and per-translation transient state.

## Dependencies and integration
Includes Linux bitfield/bitops/RAS headers, AMD northbridge/node headers, and `reg_fields.h`. Used by every ATL compilation unit in the Makefile.

## Risks
Enums encode hardware-visible values and special software values; changes must preserve dispatch assumptions. `expand_bits()` and `remove_bits()` warn but do not fail on invalid bit ranges. Returning negative errno through unsigned address APIs appears in prototypes and must be handled consistently by callers. Cross-file prototypes need to track object composition in the Makefile.

## Test signals
Compile all ATL variants, unit-test `expand_bits()`/`remove_bits()` boundaries, validate enum dispatch coverage in denormalize/dehash/map code, test PRM disabled fallback, and verify structure fields are initialized before translation use.
