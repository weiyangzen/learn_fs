<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-tx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-tx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-tx.yaml` is a PHY binding for `Starfive SoC MIPI D-PHY Tx Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The Starfive SoC uses the MIPI DSI D-PHY based on M31 IP to transfer DSI data..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `starfive,jh7110-dphy-tx`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`. Important numeric/constant limits include `const=starfive,jh7110-dphy-tx`, `maxItems=1`, `const=txesc`, `const=sys`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-tx.c`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-tx.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `starfive,jh7110-dphy-tx` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-tx.yaml -->
