<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml

## Purpose
Amlogic Meson8, Meson8b, Meson8m2 and GXBB USB2 PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Martin Blumenstingl <martin.blumenstingl@googlemail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,meson8b-usb2-phy.yaml#`. compatible values `amlogic,meson8-usb2-phy`, `amlogic,meson8b-usb2-phy`, `amlogic,meson8m2-usb2-phy`, `amlogic,meson-mx-usb2-phy`, `amlogic,meson-gxbb-usb2-phy`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `#phy-cells`, `phy-supply`. clock names `usb_general`, `usb`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml -->
