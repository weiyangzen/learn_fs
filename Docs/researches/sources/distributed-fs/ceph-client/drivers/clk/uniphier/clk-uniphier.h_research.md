<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier.h -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier.h

## Purpose

This header defines the data model used by Socionext UniPhier clock drivers. It is not a hardware driver by itself; it gives SoC-specific clock-table files a compact way to describe CPU gear clocks, fixed factors, fixed rates, gates, and muxes for later registration.

## Important APIs, Types, And Functions

`enum uniphier_clk_type` selects the registration path. `struct uniphier_clk_data` carries a clock name, DT-visible index, and a union of per-type metadata. The `UNIPHIER_CLK_CPUGEAR`, `UNIPHIER_CLK_FACTOR`, `UNIPHIER_CLK_GATE`, and `UNIPHIER_CLK_DIV*` macros are the table-authoring API. The declared registration functions return `struct clk_hw *` for CPU gear, fixed factor/rate, gate, and mux instances. The extern arrays name platform clock inventories for LD4, Pro4, SLD8, Pro5, PXS2, LD11, LD20, PXS3, NX1, MIO, SD, peripheral, and SG domains.

## Control Flow

There is no executable control flow in this file. Control flow is imposed by UniPhier common probe code that iterates a `struct uniphier_clk_data` array, switches on `type`, and passes the corresponding union member to one of the declared register helpers.

## State And Persistence Behavior

The header stores no runtime state. Persistent state belongs to the registered CCF clock objects and their backing registers. `idx = -1` in generated divider helper entries indicates intermediate clocks that are not exported as indexed consumer IDs.

## Dependencies And Integration Points

It forward-declares `struct clk_hw`, `struct device`, and `struct regmap`, so consumers integrate with Linux CCF and regmap without pulling implementation details into table files.

## Risks And Test Signals

Risks are table-shape errors: too many parents for the fixed arrays, wrong DT index values, or mismatched mux masks/values. Build coverage should catch type/name mistakes; boot tests should verify UniPhier DT clock IDs resolve and `clk_summary` contains the expected table names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier.h -->
