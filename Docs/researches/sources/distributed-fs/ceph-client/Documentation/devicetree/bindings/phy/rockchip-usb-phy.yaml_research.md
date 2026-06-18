<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml` is a Rockchip PHY binding for `Rockchip USB2.0 phy`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip USB2.0 phy.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,rk3066a-usb-phy`, `rockchip,rk3188-usb-phy`, `rockchip,rk3288-usb-phy`. Top-level properties are `compatible`, `#address-cells`, `#size-cells`. Required properties across the composed schema are `#address-cells`, `#phy-cells`, `#size-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#address-cells`, `#clock-cells`, `#phy-cells`, `#size-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vbus-supply`. Important numeric/constant limits include `const=1`, `const=0`, `maxItems=1`, `const=phyclk`, `const=phy-reset`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. pattern child nodes include `usb-phy@[0-9a-f]+$`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3066a.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3188.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3288.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,rk3066a-usb-phy, rockchip,rk3188-usb-phy, rockchip,rk3288-usb-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3066a-usb-phy`, `rockchip,rk3188-usb-phy`, `rockchip,rk3288-usb-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml -->
