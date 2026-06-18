# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-divider.h

## Purpose
Declares the regmap divider descriptor used by `clk-regmap-divider.c`.

## Important APIs, Types, And Functions
`struct clk_regmap_div` stores register offset, shift, width, and embedded `clk_regmap`. The header exports writable and read-only divider ops.

## Control Flow
Clock controller data fills the descriptor and registers it with `clk_regmap_div_ops` or `clk_regmap_div_ro_ops`. Runtime operations are implemented in the C file.

## State And Persistence
Static descriptor state defines the hardware field. Actual divider state persists in the MMIO register.

## Dependencies And Integration Points
Includes CCF provider APIs and `clk-regmap.h`. It is used by Qualcomm SoC clock controller tables for compact divider definitions.

## Risks And Edge Cases
The descriptor has no parent map or custom table support, so callers needing nonstandard encodings must use another clock type.

## Test Signals
Build coverage and basic divider rate tests validate the header.
