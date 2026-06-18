<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml

## Purpose
Amlogic G12A MIPI analog PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Neil Armstrong <narmstrong@baylibre.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,g12a-mipi-dphy-analog.yaml#`. compatible values `amlogic,g12a-mipi-dphy-analog`. required properties `compatible`, `#phy-cells`. notable properties `compatible`, `#phy-cells`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: compatible strings and node topology. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml -->
