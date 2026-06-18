<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml

## Purpose
Broadcom STB USB PHY is a physical-layer transceiver binding. Broadcom's PHY that handles EHCI/OHCI and/or XHCI Maintainers: Al Cooper <alcooperx@gmail.com>, Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/brcm,brcmstb-usb-phy.yaml#`. compatible values `brcm,bcm4908-usb-phy`, `brcm,bcm7211-usb-phy`, `brcm,bcm7216-usb-phy`, `brcm,bcm74110-usb-phy`, `brcm,brcmstb-usb-phy`. required properties `reg`, `#phy-cells`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, and 7 more. register names `ctrl`, `xhci_ec`, `xhci_gbl`, `usb_phy`, `usb_mdio`, `bdc_ec`. clock names `sw_usb`, `sw_usb3`. interrupt names `wake`. schema refs `phandle`, `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 3 `allOf` layer(s); 3 conditional branch(es); 0 `oneOf` and 2 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle`, `uint32`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, interrupt map/name mistakes hide link, MSI, or error events, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 2 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml -->
