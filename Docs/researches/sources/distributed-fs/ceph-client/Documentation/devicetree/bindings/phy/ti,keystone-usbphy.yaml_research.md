<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml` is a Texas Instruments PHY/control binding for `TI Keystone USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The main purpose of this PHY driver is to enable the USB PHY reference clock gate on the Keystone SOC for both the USB2 and USB3 PHY. Otherwise it is just an NOP PHY driver. Hence this node is referenced as both the usb2 and usb3 phy node in the USB Glue layer driver node..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `ti,keystone-usbphy`. Top-level properties are `compatible`, `reg`. Required properties across the composed schema are `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `compatible`, `reg`. Important numeric/constant limits include `const=ti,keystone-usbphy`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/keystone-k2e.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/keystone.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,keystone-usbphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml -->
