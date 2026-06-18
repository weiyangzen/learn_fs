# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme2_rtr_regs.h

## Purpose

`mme2_rtr_regs.h` is an auto-generated Goya ASIC register-offset header for the `MME2_RTR` block, whose prototype is `MME_RTR`. It gives C preprocessor names to MMIO addresses in the MME2 router block. The router is part of the internal fabric around the matrix-math engine path and exposes arbitration, credit, split, range-match, range-base, register-lane, and scrambler control registers.

## Important APIs, types, and data

There are no functions, structs, enums, or inline helpers. The only API is the macro namespace `mmMME2_RTR_*`. Important groups are HBW read/write request and response arbitration registers, LBW read/write request and response arbitration registers, per-direction arbitration maxima, HBW and LBW credit limits, debug arbitration controls, ten `SPLIT_COEF_*` registers, split read/write saturation and timeout controls, HBW range hit/mask/base registers, LBW range hit/mask/base registers, `RGLTR` read/write-result registers, and `SCRAMB_EN`/`NON_LIN_SCRAMB`.

The address span starts at `0x80100` and ends at `0x80604`, with the implicit block base around `0x80000`. HBW range state uses eight mask/base slots split into low and high halves; LBW range state uses sixteen mask/base slots. The same register layout appears in the sibling MME router headers with a different base address.

## Control flow

The file has no executable control flow. Runtime control flow appears in consumers that include generated Goya register headers and pass these constants to `RREG32()`/`WREG32()`-style MMIO helpers. Typical sequences configure fabric credits and arbitration before engine traffic is enabled, install range masks before exposing address windows, read range-hit/debug state during fault handling, and update scrambler controls during device initialization or low-level diagnostics.

## State and persistence behavior

The macros are compile-time constants and persist only through compiled code. Writes to the named registers change volatile device hardware state. Router range registers and scrambler controls can affect all subsequent traffic through this router until a reset or reprogramming; debug and hit registers are hardware-observable state rather than host persistence. The header itself does not allocate memory, store host state, or serialize configuration.

## Dependencies and integration points

The header depends only on normal C preprocessing and its include guard. It is generated from the Goya register database and is consumed by Goya device code, low-level security/range programming, coresight/performance plumbing, and any diagnostic path that needs direct router MMIO offsets. It integrates with sibling generated headers that provide masks for related fields and with common HabanaLabs register access helpers.

## Risks and edge cases

The main risk is address drift between this generated file and the hardware spec. A single wrong offset can cause writes to another router register or to an adjacent block. HBW masks are split across low/high registers while LBW masks are not, so code must not mechanically reuse LBW programming for HBW. Range endpoints and split timeouts are fabric-sensitive; overbroad masks can route or block unintended traffic. `WPLIT_WR_TST_TOLEN` appears with a likely generator spelling anomaly and should be treated as an ABI macro name, not corrected by hand.

## Test signals

Static signals are successful compilation of all Goya code that includes generated register headers and grep-based checks that the MME2 router namespace remains unique. Runtime signals include successful Goya probe/reset, no unexpected router protection or range-hit errors during MME workloads, expected values when debugfs or low-level diagnostic code reads these offsets, and correct behavior after programming LBW/HBW ranges around restricted regions.
