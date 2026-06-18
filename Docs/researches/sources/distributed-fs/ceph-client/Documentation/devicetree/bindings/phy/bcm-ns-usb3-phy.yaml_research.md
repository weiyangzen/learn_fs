<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml

## Purpose
Broadcom Northstar USB 3.0 PHY is a physical-layer transceiver binding. Initialization of USB 3.0 PHY depends on Northstar version. There are currently three known series: Ax, Bx and Cx. Known A0: BCM4707 rev 0 Known B0: BCM4707 rev 4, BCM53573 rev 2 Known B1: BCM4707 rev 6 Known C0: BCM47094 rev 0 Maintainers: Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/bcm-ns-usb3-phy.yaml#`. compatible values `brcm,ns-ax-usb3-phy`, `brcm,ns-bx-usb3-phy`. required properties `compatible`, `reg`, `usb3-dmp-syscon`, `#phy-cells`. notable properties `compatible`, `reg`, `#phy-cells`, `usb3-dmp-syscon`. schema refs `phandle`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml -->
