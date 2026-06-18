<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rzg3e-usb3-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rzg3e-usb3-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rzg3e-usb3-phy.yaml` is a Renesas PHY binding for `Renesas RZ/G3E USB 3.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Renesas RZ/G3E USB 3.0 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `renesas,r9a09g047-usb3-phy`, `renesas,r9a09g056-usb3-phy`, `renesas,r9a09g057-usb3-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. Important numeric/constant limits include `const=renesas,r9a09g047-usb3-phy`, `maxItems=1`, `const=pclk`, `const=core`, `const=ref_alt_clk_p`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rzg3e-usb3.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r9a09g047.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r9a09g056.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r9a09g057.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[1].items[0]: renesas,r9a09g056-usb3-phy, renesas,r9a09g057-usb3-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rzg3e-usb3-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `renesas,r9a09g047-usb3-phy`, `renesas,r9a09g056-usb3-phy`, `renesas,r9a09g057-usb3-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rzg3e-usb3-phy.yaml -->
