<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml` is a Texas Instruments PHY/control binding for `OMAP USB2 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: OMAP USB2 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 3 accepted compatible forms with values `ti,dra7x-usb2`, `ti,dra7x-usb2-phy2`, `ti,am654-usb2`, `ti,omap-usb2`, `ti,am437x-usb2`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `syscon-phy-power`, `ctrl-module`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `ctrl-module`, `reg`, `syscon-phy-power`. Important numeric/constant limits include `const=ti,am437x-usb2`, `const=ti,omap-usb2`, `maxItems=1`, `const=0`, `minItems=1`, `const=wkupclk`, `const=refclk`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/am437x-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/dra7-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/omap4-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/omap5-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am65-main.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: ti,dra7x-usb2, ti,dra7x-usb2-phy2, ti,am654-usb2; properties.compatible.oneOf[0].items[1]: ti,omap-usb2.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,dra7x-usb2`, `ti,dra7x-usb2-phy2`, `ti,am654-usb2`, `ti,omap-usb2`, `ti,am437x-usb2` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml -->
