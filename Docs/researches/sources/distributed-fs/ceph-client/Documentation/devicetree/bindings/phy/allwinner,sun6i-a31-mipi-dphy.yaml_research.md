<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml

## Purpose
Allwinner A31 MIPI D-PHY Controller is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun6i-a31-mipi-dphy.yaml#`. compatible values `allwinner,sun6i-a31-mipi-dphy`, `allwinner,sun50i-a100-mipi-dphy`, `allwinner,sun50i-a64-mipi-dphy`, `allwinner,sun20i-d1-mipi-dphy`. required properties `#phy-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `#phy-cells`, `allwinner,direction`. clock names `bus`, `mod`. schema refs `string`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `string`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml -->
