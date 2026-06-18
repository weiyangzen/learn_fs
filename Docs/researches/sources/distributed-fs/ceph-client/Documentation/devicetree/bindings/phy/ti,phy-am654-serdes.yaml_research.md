<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-am654-serdes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-am654-serdes.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-am654-serdes.yaml` is a Texas Instruments PHY/control binding for `TI AM654 SERDES`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This binding describes the TI AM654 SERDES. AM654 SERDES can be configured to be used with either PCIe or USB or SGMII..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `ti,phy-am654-serdes`. Top-level properties are `compatible`, `reg`, `reg-names`, `power-domains`, `clocks`, `#phy-cells`, `ti,serdes-clk`, `#clock-cells`, `mux-controls`, `clock-output-names`. Required properties across the composed schema are `assigned-clock-parents`, `assigned-clocks`, `clock-output-names`, `clocks`, `compatible`, `mux-controls`, `power-domains`, `reg`, `ti,serdes-clk`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-output-names`, `clocks`, `compatible`, `mux-controls`, `power-domains`, `reg`, `reg-names`, `ti,serdes-clk`. Important numeric/constant limits include `maxItems=1`, `const=serdes`, `maxItems=3`, `const=2`, `const=1`, `const=serdes0_cmu_refclk`, `const=serdes0_lo_refclk`, `const=serdes0_ro_refclk`, `const=serdes1_cmu_refclk`, `const=serdes1_lo_refclk`, `const=serdes1_ro_refclk`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `power-domains`, `clocks`, `#clock-cells`, `clock-output-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-am654-serdes.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am65-main.dtsi`. External providers/consumers are signaled through `power-domains`, `clocks`, `#clock-cells`, `clock-output-names`, `ti,serdes-clk`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: ti,phy-am654-serdes.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-am654-serdes.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,phy-am654-serdes` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-am654-serdes.yaml -->
