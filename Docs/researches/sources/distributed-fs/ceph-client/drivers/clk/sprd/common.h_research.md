# sources/distributed-fs/ceph-client/drivers/clk/sprd/common.h

## Purpose
Defines the common data contracts shared by all Spreadtrum clock classes and SoC descriptors.

## Important APIs, Types, And Functions
`struct sprd_clk_common` embeds the regmap pointer, register offset, and `struct clk_hw`. `struct sprd_clk_desc` groups the mutable common-clock array with the public `clk_hw_onecell_data`. `hw_to_sprd_clk_common` converts a `clk_hw` back to its Spreadtrum common container. Prototypes expose `sprd_clk_regmap_init` and `sprd_clk_probe`.

## Control Flow
This header has no runtime control flow, but its container layout is used by every clk op implementation to recover register metadata from generic CCF callbacks.

## State And Persistence
The common structure stores persistent per-clock register metadata and the regmap pointer filled during platform probe.

## Dependencies And Integration Points
Includes CCF, OF platform, and regmap headers. It is included by all Spreadtrum gate, mux, divider, composite, PLL, and SoC table files.

## Risks And Edge Cases
Changing the embedded layout or conversion helper would break all `hw_to_*` wrappers. Descriptor arrays must include every clock with register-backed ops so `sprd_clk_regmap_init` can fill `regmap`.

## Test Signals
The strongest signal is successful build and boot probe of multiple Spreadtrum clock classes. Sparse or CFI-like checks would catch invalid container assumptions only indirectly.
