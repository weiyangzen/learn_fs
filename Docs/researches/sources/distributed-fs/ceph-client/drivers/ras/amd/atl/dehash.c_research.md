# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/dehash.c

## Purpose
Reverses Data Fabric address hash bits after denormalization so ATL can produce a system physical address.

## Important APIs, types, and functions
`dehash_address()` dispatches by `ctx->map.intlv_mode`. Family-specific helpers are `df2_dehash_addr()`, `df3_dehash_addr()`, `df3_6chan_dehash_addr()`, `df4_dehash_addr()`, `df4p5_dehash_addr()`, and `mi300_dehash_addr()`. They inspect hash-control fields in `ctx->map.ctl`, compute expected hashed bits from address bits, and toggle interleave bits when needed.

## Control flow
No-hash modes and modes where hashing was already handled during coherent-station ID calculation return immediately. DF2/DF3/DF4 paths progressively fix channel select bits depending on channel count. DF3 six-channel handles three interleave bits with 2M/1G hash controls. DF4.5 builds a rehash vector from total channels and stripe size to decide which address bits need recalculation. MI300 loops over channel and die interleave bits, including 4K/64K/2M/1G/1T hash controls and MI300’s stack bit placement.

## State and persistence
No persistent state. The function mutates `ctx->ret_addr` in place and reads `ctx->map` plus global `df_cfg`-derived map fields populated elsewhere.

## Dependencies and integration
Depends on `internal.h`, bitfield macros, interleave mode definitions, and prior `denormalize_address()` execution. Called from `norm_to_sys_addr()`.

## Risks
Address bit formulas are hardware-specific and difficult to review by inspection. Unsupported modes return `-EINVAL`; newly introduced hardware modes must be added here or explicitly classified. Boolean calculations sometimes use raw `BIT_ULL` truth values, which is intentional but sensitive to type changes. Incorrect total channel/die metadata causes wrong bit toggles.

## Test signals
Golden-vector tests for each interleave/hash-control combination, especially DF3 COD modes, DF3 six-channel, DF4 socket interleaving, DF4.5 1K/2K stripe modes, and MI300 8/16/32 channel plus die interleave cases. Include unknown-mode negative tests.
