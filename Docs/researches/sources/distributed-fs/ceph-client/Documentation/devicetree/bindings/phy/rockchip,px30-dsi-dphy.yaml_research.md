<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml` is a Rockchip PHY binding for `Rockchip MIPI DPHY with additional LVDS/TTL modes`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip MIPI DPHY with additional LVDS/TTL modes.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,px30-dsi-dphy`, `rockchip,rk3128-dsi-dphy`, `rockchip,rk3368-dsi-dphy`, `rockchip,rk3506-dsi-dphy`, `rockchip,rk3568-dsi-dphy`, `rockchip,rv1126-dsi-dphy`. Top-level properties are `#phy-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`. Important numeric/constant limits include `const=0`, `maxItems=1`, `const=ref`, `const=pclk`, `const=apb`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-dsidphy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3128.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/px30.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3368.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk356x-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,px30-dsi-dphy, rockchip,rk3128-dsi-dphy, rockchip,rk3368-dsi-dphy, rockchip,rk3506-dsi-dphy, rockchip,rk3568-dsi-dphy, rockchip,rv1126-dsi-dphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,px30-dsi-dphy`, `rockchip,rk3128-dsi-dphy`, `rockchip,rk3368-dsi-dphy`, `rockchip,rk3506-dsi-dphy`, `rockchip,rk3568-dsi-dphy`, `rockchip,rv1126-dsi-dphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml -->
