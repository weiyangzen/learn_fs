<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sa8775p-dwmac-sgmii-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sa8775p-dwmac-sgmii-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sa8775p-dwmac-sgmii-phy.yaml` is a Qualcomm PHY binding for `Qualcomm SerDes/SGMII ethernet PHY controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The SerDes PHY sits between the MAC and the external PHY and provides separate Rx Tx lines..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,qcs8300-dwmac-sgmii-phy`, `qcom,sa8775p-dwmac-sgmii-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `phy-supply`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `phy-supply`, `reg`. Important numeric/constant limits include `const=qcom,sa8775p-dwmac-sgmii-phy`, `maxItems=1`, `const=sgmi_ref`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `phy-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-sgmii-eth.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `phy-supply`, `phy-supply`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,qcs8300-dwmac-sgmii-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sa8775p-dwmac-sgmii-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,qcs8300-dwmac-sgmii-phy`, `qcom,sa8775p-dwmac-sgmii-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sa8775p-dwmac-sgmii-phy.yaml -->
