<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,dp-video-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,dp-video-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,dp-video-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung Exynos SoC DisplayPort PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Samsung Exynos SoC DisplayPort PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `samsung,exynos5250-dp-video-phy`, `samsung,exynos5420-dp-video-phy`. Top-level properties are `compatible`, `#phy-cells`, `samsung,pmu-syscon`. Required properties across the composed schema are `#phy-cells`, `compatible`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `samsung,pmu-syscon`. Important numeric/constant limits include `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-dp-video.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5250.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5420.dtsi`. External providers/consumers are signaled through `samsung,pmu-syscon`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: samsung,exynos5250-dp-video-phy, samsung,exynos5420-dp-video-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,dp-video-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `samsung,exynos5250-dp-video-phy`, `samsung,exynos5420-dp-video-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,dp-video-phy.yaml -->
