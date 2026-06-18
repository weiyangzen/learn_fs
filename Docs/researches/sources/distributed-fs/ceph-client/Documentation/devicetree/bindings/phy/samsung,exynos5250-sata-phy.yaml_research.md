<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos5250-sata-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos5250-sata-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos5250-sata-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung Exynos5250 SoC SATA PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Samsung Exynos5250 SoC SATA PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `samsung,exynos5250-sata-phy`. Top-level properties are `compatible`, `clocks`, `clock-names`, `#phy-cells`, `reg`, `samsung,syscon-phandle`, `samsung,exynos-sataphy-i2c-phandle`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `samsung,exynos-sataphy-i2c-phandle`, `samsung,syscon-phandle`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `samsung,exynos-sataphy-i2c-phandle`, `samsung,syscon-phandle`. Important numeric/constant limits include `const=samsung,exynos5250-sata-phy`, `maxItems=1`, `const=sata_phyctrl`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-sata.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5250.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `samsung,syscon-phandle`, `samsung,exynos-sataphy-i2c-phandle`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos5250-sata-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `samsung,exynos5250-sata-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos5250-sata-phy.yaml -->
