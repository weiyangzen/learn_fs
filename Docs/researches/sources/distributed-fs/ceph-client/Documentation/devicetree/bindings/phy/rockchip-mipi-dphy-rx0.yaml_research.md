<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-mipi-dphy-rx0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-mipi-dphy-rx0.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-mipi-dphy-rx0.yaml` is a Rockchip PHY binding for `Rockchip SoC MIPI RX0 D-PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The Rockchip SoC has a MIPI D-PHY bus with an RX0 entry which connects to the ISP1 (Image Signal Processing unit v1.0) for CSI cameras..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `rockchip,rk3399-mipi-dphy-rx0`. Top-level properties are `compatible`, `clocks`, `clock-names`, `#phy-cells`, `power-domains`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`. Important numeric/constant limits include `const=rockchip,rk3399-mipi-dphy-rx0`, `const=dphy-ref`, `const=dphy-cfg`, `const=grf`, `const=0`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dphy-rx0.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3399-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-mipi-dphy-rx0.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3399-mipi-dphy-rx0` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-mipi-dphy-rx0.yaml -->
