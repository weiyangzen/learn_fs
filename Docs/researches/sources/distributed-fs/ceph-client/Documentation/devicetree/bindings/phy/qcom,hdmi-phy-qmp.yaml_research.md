<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-qmp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-qmp.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-qmp.yaml` is a Qualcomm QMP PHY binding for `Qualcomm Adreno/Snapdragon QMP HDMI phy`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm Adreno/Snapdragon QMP HDMI phy.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,hdmi-phy-8996`, `qcom,hdmi-phy-8998`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `power-domains`, `vcca-supply`, `vddio-supply`, `#clock-cells`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reg-names`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reg-names`, `vcca-supply`, `vddio-supply`. Important numeric/constant limits include `maxItems=6`, `const=hdmi_pll`, `const=hdmi_tx_l0`, `const=hdmi_tx_l1`, `const=hdmi_tx_l2`, `const=hdmi_tx_l3`, `const=hdmi_phy`, `minItems=2`, `maxItems=3`, `const=iface`, `const=ref`, `const=xo`, `maxItems=1`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `vcca-supply`, `vddio-supply`, `#clock-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8996.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8998.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `vcca-supply`, `vddio-supply`, `#clock-cells`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,hdmi-phy-8996, qcom,hdmi-phy-8998.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-qmp.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,hdmi-phy-8996`, `qcom,hdmi-phy-8998` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-qmp.yaml -->
