<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml` is a Rockchip PHY binding for `Rockchip EMMC PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip EMMC PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `rockchip,rk3399-emmc-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `drive-impedance-ohm`, `rockchip,enable-strobe-pulldown`, `rockchip,output-tapdelay-select`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `drive-impedance-ohm`, `reg`, `rockchip,enable-strobe-pulldown`, `rockchip,output-tapdelay-select`. Important numeric/constant limits include `const=rockchip,rk3399-emmc-phy`, `maxItems=1`, `const=emmcclk`, `maximum=15`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-emmc.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3399-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `rockchip,enable-strobe-pulldown`, `rockchip,output-tapdelay-select`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.drive-impedance-ohm: 33, 40, 50, 66, 100.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3399-emmc-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml -->
