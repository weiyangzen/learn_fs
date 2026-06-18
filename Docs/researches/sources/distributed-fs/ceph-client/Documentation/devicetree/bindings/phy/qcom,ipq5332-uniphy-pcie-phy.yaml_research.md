<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-uniphy-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-uniphy-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-uniphy-pcie-phy.yaml` is a Qualcomm PHY binding for `Qualcomm UNIPHY PCIe 28LP PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: PCIe and USB combo PHY found in Qualcomm IPQ5018 & IPQ5332 SoCs.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,ipq5018-uniphy-pcie-phy`, `qcom,ipq5332-uniphy-pcie-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `#phy-cells`, `#clock-cells`, `num-lanes`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clocks`, `compatible`, `num-lanes`, `reg`, `resets`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clocks`, `compatible`, `num-lanes`, `reg`, `resets`. Important numeric/constant limits include `maxItems=1`, `minItems=1`, `maxItems=2`, `minItems=2`, `maxItems=3`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32` conditional branches include `qcom,ipq5018-uniphy-pcie-phy` -> adjusts `clocks`, `resets`; `qcom,ipq5332-uniphy-pcie-phy` -> adjusts `clocks`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `resets`, `#clock-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-uniphy-pcie-28lp.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq5018.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq5332.dtsi`. External providers/consumers are signaled through `clocks`, `resets`, `#clock-cells`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,ipq5018-uniphy-pcie-phy, qcom,ipq5332-uniphy-pcie-phy; properties.num-lanes: 1, 2; allOf[0].if.properties.compatible.contains: qcom,ipq5018-uniphy-pcie-phy; allOf[1].if.properties.compatible.contains: qcom,ipq5332-uniphy-pcie-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-uniphy-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,ipq5018-uniphy-pcie-phy`, `qcom,ipq5332-uniphy-pcie-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-uniphy-pcie-phy.yaml -->
