<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml` is a Socionext UniPhier PHY binding for `Socionext UniPhier USB2 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This describes the devicetree bindings for PHY interface built into USB2 controller implemented on Socionext UniPhier SoCs. Pro4 SoC has both USB2 and USB3 host controllers, however, this USB3 controller doesn't include its own High-Speed PHY. This needs to specify USB2 PHY instead of USB3 HS-PHY..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `socionext,uniphier-pro4-usb2-phy`, `socionext,uniphier-ld11-usb2-phy`. Top-level properties are `compatible`, `#address-cells`, `#size-cells`. Required properties across the composed schema are `#address-cells`, `#phy-cells`, `#size-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#address-cells`, `#phy-cells`, `#size-cells`, `compatible`, `reg`, `vbus-supply`. Important numeric/constant limits include `const=1`, `const=0`, `minimum=0`, `maximum=3`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. pattern child nodes include `^phy@[0-9]+$`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pro4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-ld11.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: socionext,uniphier-pro4-usb2-phy, socionext,uniphier-ld11-usb2-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `socionext,uniphier-pro4-usb2-phy`, `socionext,uniphier-ld11-usb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml -->
