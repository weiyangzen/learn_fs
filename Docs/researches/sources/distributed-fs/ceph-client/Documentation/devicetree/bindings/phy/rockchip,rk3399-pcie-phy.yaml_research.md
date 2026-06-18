<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-pcie-phy.yaml` is a Rockchip PHY binding for `Rockchip RK3399 PCIE PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip RK3399 PCIE PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `rockchip,rk3399-pcie-phy`. Top-level properties are `compatible`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reset-names`, `resets`. Important numeric/constant limits include `const=rockchip,rk3399-pcie-phy`, `const=0`, `const=1`, `maxItems=1`, `const=refclk`, `const=phy`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3399-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-pcie-phy.yaml` should parse this YAML and validate 0 embedded examples. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3399-pcie-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-pcie-phy.yaml -->
