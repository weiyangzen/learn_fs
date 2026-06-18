# subset-b-000600 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-7nm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-7nm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-7nm.yaml` is a Qualcomm PHY binding for `Qualcomm Display DSI 7nm PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm Display DSI 7nm PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 3 accepted compatible forms with values `qcom,dsi-phy-7nm`, `qcom,dsi-phy-7nm-8150`, `qcom,kaanapali-dsi-phy-3nm`, `qcom,sa8775p-dsi-phy-5nm`, `qcom,sar2130p-dsi-phy-5nm`, `qcom,sc7280-dsi-phy-7nm`, `qcom,sm6375-dsi-phy-7nm`, `qcom,sm8350-dsi-phy-5nm`, `qcom,sm8450-dsi-phy-5nm`, `qcom,sm8550-dsi-phy-4nm`, `qcom,sm8650-dsi-phy-4nm`, `qcom,sm8750-dsi-phy-3nm`, `qcom,eliza-dsi-phy-4nm`, `qcom,qcs8300-dsi-phy-5nm`, `qcom,sc8280xp-dsi-phy-5nm`. Top-level properties are `compatible`, `reg`, `reg-names`, `vdds-supply`, `phy-type`. Required properties across the composed schema are `compatible`, `reg`, `reg-names`. All discovered property names, including nested child-node contracts, include `compatible`, `phy-type`, `reg`, `reg-names`, `vdds-supply`. Important numeric/constant limits include `const=qcom,sm8650-dsi-phy-4nm`, `const=qcom,sa8775p-dsi-phy-5nm`, `const=dsi_phy`, `const=dsi_phy_lane`, `const=dsi_pll`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `qcom,dsi-phy-common.yaml#`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `vdds-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `qcom,dsi-phy-common.yaml#`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kodiak.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8180x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8150.dtsi`, and 2 more. External providers/consumers are signaled through `vdds-supply`, `phy-type`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: composition is closed by `unevaluatedProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,dsi-phy-7nm, qcom,dsi-phy-7nm-8150, qcom,kaanapali-dsi-phy-3nm, qcom,sa8775p-dsi-phy-5nm, qcom,sar2130p-dsi-phy-5nm, qcom,sc7280-dsi-phy-7nm, qcom,sm6375-dsi-phy-7nm, qcom,sm8350-dsi-phy-5nm, qcom,sm8450-dsi-phy-5nm, qcom,sm8550-dsi-phy-4nm, qcom,sm8650-dsi-phy-4nm, qcom,sm8750-dsi-phy-3nm; properties.compatible.oneOf[1].items[0]: qcom,eliza-dsi-phy-4nm; properties.compatible.oneOf[2].items[0]: qcom,qcs8300-dsi-phy-5nm, qcom,sc8280xp-dsi-phy-5nm; properties.phy-type: 10, 11.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-7nm.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,dsi-phy-7nm`, `qcom,dsi-phy-7nm-8150`, `qcom,kaanapali-dsi-phy-3nm`, `qcom,sa8775p-dsi-phy-5nm`, `qcom,sar2130p-dsi-phy-5nm`, `qcom,sc7280-dsi-phy-7nm`, and 9 more against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-7nm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-common.yaml` is a Qualcomm PHY binding for `Qualcomm Display DSI PHY Common Properties`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Common properties for Qualcomm Display DSI PHY..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is no explicit compatible schema with values none listed. Top-level properties are `#clock-cells`, `#phy-cells`, `clocks`, `clock-names`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`. Important numeric/constant limits include `const=1`, `const=0`, `const=iface`, `const=ref`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `#clock-cells`, `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. No direct driver filename reference was found by the bounded compatible-string search; integration may be through generic data tables, newer code outside this checkout, or DTS-only schema coverage. External providers/consumers are signaled through `#clock-cells`, `clocks`, `clock-names`.

## Risks And Edge Cases
ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are allowed. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-common.yaml` should parse this YAML and validate 0 embedded examples. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,dsi-phy-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,edp-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,edp-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,edp-phy.yaml` is a Qualcomm PHY binding for `Qualcomm eDP PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The Qualcomm eDP PHY is found in a number of Qualcomm platform and provides the physical interface for Embedded Display Port..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,glymur-dp-phy`, `qcom,sa8775p-edp-phy`, `qcom,sc7280-edp-phy`, `qcom,sc8180x-edp-phy`, `qcom,sc8280xp-dp-phy`, `qcom,sc8280xp-edp-phy`, `qcom,x1e80100-dp-phy`, `qcom,qcs8300-edp-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#phy-cells`, `power-domains`, `vdda-phy-supply`, `vdda-pll-supply`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `vdda-phy-supply`, `vdda-pll-supply`. Important numeric/constant limits include `const=qcom,sa8775p-edp-phy`, `minItems=2`, `maxItems=3`, `const=aux`, `const=cfg_ahb`, `const=ref`, `const=1`, `const=0`, `maxItems=1`, `minItems=3`, `maxItems=2`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `qcom,glymur-dp-phy`, `qcom,x1e80100-dp-phy` -> adjusts `clock-names`, `clocks`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `#clock-cells`, `power-domains`, `vdda-phy-supply`, `vdda-pll-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-edp.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kodiak.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8180x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp-crd.dts`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp-lenovo-thinkpad-x13s.dts`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `#clock-cells`, `power-domains`, `vdda-phy-supply`, `vdda-pll-supply`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0]: qcom,glymur-dp-phy, qcom,sa8775p-edp-phy, qcom,sc7280-edp-phy, qcom,sc8180x-edp-phy, qcom,sc8280xp-dp-phy, qcom,sc8280xp-edp-phy, qcom,x1e80100-dp-phy; properties.compatible.oneOf[1].items[0]: qcom,qcs8300-edp-phy; allOf[0].if.properties.compatible: qcom,glymur-dp-phy, qcom,x1e80100-dp-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,edp-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,glymur-dp-phy`, `qcom,sa8775p-edp-phy`, `qcom,sc7280-edp-phy`, `qcom,sc8180x-edp-phy`, `qcom,sc8280xp-dp-phy`, `qcom,sc8280xp-edp-phy`, and 2 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,edp-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-other.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-other.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-other.yaml` is a Qualcomm PHY binding for `Qualcomm Adreno/Snapdragon HDMI phy`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm Adreno/Snapdragon HDMI phy.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,hdmi-phy-8660`, `qcom,hdmi-phy-8960`, `qcom,hdmi-phy-8974`, `qcom,hdmi-phy-8084`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `power-domains`, `core-vdda-supply`, `vddio-supply`, `#clock-cells`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clocks`, `compatible`, `reg`, `reg-names`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `core-vdda-supply`, `power-domains`, `reg`, `reg-names`, `vddio-supply`. Important numeric/constant limits include `maxItems=2`, `const=hdmi_phy`, `const=hdmi_pll`, `minItems=1`, `maxItems=1`, `const=0`, `const=slave_iface`, `const=pxo`, `const=iface`, `const=alt_iface`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `qcom,hdmi-phy-8660` -> adjusts `clock-names`, `clocks`, `vddio-supply`; `qcom,hdmi-phy-8960` -> adjusts `clock-names`, `clocks`, `vddio-supply`; `qcom,hdmi-phy-8084`, `qcom,hdmi-phy-8974` -> adjusts `clock-names`, `clocks`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `core-vdda-supply`, `vddio-supply`, `#clock-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-apq8064.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `core-vdda-supply`, `vddio-supply`, `#clock-cells`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,hdmi-phy-8660, qcom,hdmi-phy-8960, qcom,hdmi-phy-8974, qcom,hdmi-phy-8084; allOf[0].if.properties.compatible.contains: qcom,hdmi-phy-8660; allOf[1].if.properties.compatible.contains: qcom,hdmi-phy-8960; allOf[2].if.properties.compatible.contains: qcom,hdmi-phy-8084, qcom,hdmi-phy-8974.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-other.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,hdmi-phy-8660`, `qcom,hdmi-phy-8960`, `qcom,hdmi-phy-8974`, `qcom,hdmi-phy-8084` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,hdmi-phy-other.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-usb-hsphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-usb-hsphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-usb-hsphy.yaml` is a Qualcomm PHY binding for `M31 USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: USB M31 PHY (https://www.m31tech.com) found in Qualcomm IPQ5018, IPQ5332 SoCs..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is ordered fallback `items` sequence with values `qcom,ipq5018-usb-hsphy`, `qcom,ipq5332-usb-hsphy`. Top-level properties are `compatible`, `#phy-cells`, `reg`, `clocks`, `clock-names`, `resets`, `vdd-supply`. Required properties across the composed schema are none. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `resets`, `vdd-supply`. Important numeric/constant limits include `const=0`, `maxItems=1`, `const=cfg_ahb`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `vdd-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq5018.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq5332.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `vdd-supply`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.items[0]: qcom,ipq5018-usb-hsphy, qcom,ipq5332-usb-hsphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-usb-hsphy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,ipq5018-usb-hsphy`, `qcom,ipq5332-usb-hsphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq5332-usb-hsphy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-hs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-hs.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-hs.yaml` is a Qualcomm PHY binding for `Qualcomm ipq806x usb DWC3 HS PHY CONTROLLER`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: DWC3 PHY nodes are defined to describe on-chip Synopsis Physical layer controllers used in ipq806x. Each DWC3 PHY controller should have its own node..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `qcom,ipq806x-usb-phy-hs`. Top-level properties are `compatible`, `#phy-cells`, `reg`, `clocks`, `clock-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. Important numeric/constant limits include `const=qcom,ipq806x-usb-phy-hs`, `const=0`, `maxItems=1`, `minItems=1`, `maxItems=2`, `const=ref`, `const=xo`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-ipq8064.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-hs.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,ipq806x-usb-phy-hs` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-hs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-ss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-ss.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-ss.yaml` is a Qualcomm PHY binding for `Qualcomm ipq806x usb DWC3 SS PHY CONTROLLER`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: DWC3 PHY nodes are defined to describe on-chip Synopsis Physical layer controllers used in ipq806x. Each DWC3 PHY controller should have its own node..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `qcom,ipq806x-usb-phy-ss`. Top-level properties are `compatible`, `#phy-cells`, `reg`, `clocks`, `clock-names`, `qcom,rx-eq`, `qcom,tx-deamp-3_5db`, `qcom,mpll`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `qcom,mpll`, `qcom,rx-eq`, `qcom,tx-deamp-3_5db`, `reg`. Important numeric/constant limits include `const=qcom,ipq806x-usb-phy-ss`, `const=0`, `maxItems=1`, `minItems=1`, `maxItems=2`, `const=ref`, `const=xo`, `maximum=7`, `maximum=63`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-ipq8064.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `qcom,rx-eq`, `qcom,tx-deamp-3_5db`, `qcom,mpll`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-ss.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,ipq806x-usb-phy-ss` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq806x-usb-phy-ss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq8074-qmp-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq8074-qmp-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq8074-qmp-pcie-phy.yaml` is a Qualcomm QMP PCIe PHY binding for `Qualcomm QMP PHY controller (PCIe, IPQ8074)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: QMP PHY controller supports physical layer functionality for a number of controllers on Qualcomm chipsets, such as, PCIe, UFS, and USB..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 3 accepted compatible forms with values `qcom,ipq6018-qmp-pcie-phy`, `qcom,ipq8074-qmp-gen3-pcie-phy`, `qcom,ipq8074-qmp-pcie-phy`, `qcom,ipq9574-qmp-gen3x1-pcie-phy`, `qcom,ipq9574-qmp-gen3x2-pcie-phy`, `qcom,ipq5424-qmp-gen3x1-pcie-phy`, `qcom,ipq5424-qmp-gen3x2-pcie-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `#clock-cells`, `clock-output-names`, `#phy-cells`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. Important numeric/constant limits include `const=qcom,ipq9574-qmp-gen3x1-pcie-phy`, `const=qcom,ipq9574-qmp-gen3x2-pcie-phy`, `maxItems=3`, `const=aux`, `const=cfg_ahb`, `const=pipe`, `maxItems=2`, `const=phy`, `const=common`, `const=0`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `#clock-cells`, `clock-output-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq5424.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq6018.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq8074.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq9574.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `#clock-cells`, `clock-output-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0]: qcom,ipq6018-qmp-pcie-phy, qcom,ipq8074-qmp-gen3-pcie-phy, qcom,ipq8074-qmp-pcie-phy, qcom,ipq9574-qmp-gen3x1-pcie-phy, qcom,ipq9574-qmp-gen3x2-pcie-phy; properties.compatible.oneOf[1].items[0]: qcom,ipq5424-qmp-gen3x1-pcie-phy; properties.compatible.oneOf[2].items[0]: qcom,ipq5424-qmp-gen3x2-pcie-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq8074-qmp-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,ipq6018-qmp-pcie-phy`, `qcom,ipq8074-qmp-gen3-pcie-phy`, `qcom,ipq8074-qmp-pcie-phy`, `qcom,ipq9574-qmp-gen3x1-pcie-phy`, `qcom,ipq9574-qmp-gen3x2-pcie-phy`, `qcom,ipq5424-qmp-gen3x1-pcie-phy`, and 1 more against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,ipq8074-qmp-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,m31-eusb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,m31-eusb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,m31-eusb2-phy.yaml` is a Qualcomm PHY binding for `Qualcomm M31 eUSB2 phy`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: M31 based eUSB2 controller, which supports LS/FS/HS usb connectivity on Qualcomm chipsets. It is paired with a eUSB2 repeater..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,glymur-m31-eusb2-phy`, `qcom,kaanapali-m31-eusb2-phy`, `qcom,sm8750-m31-eusb2-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `phys`, `vdd-supply`, `vdda12-supply`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `resets`, `vdd-supply`, `vdda12-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `phys`, `reg`, `resets`, `vdd-supply`, `vdda12-supply`. Important numeric/constant limits include `const=qcom,sm8750-m31-eusb2-phy`, `maxItems=1`, `const=0`, `const=ref`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `vdd-supply`, `vdda12-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31-eusb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8750.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `vdd-supply`, `vdda12-supply`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,glymur-m31-eusb2-phy, qcom,kaanapali-m31-eusb2-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,m31-eusb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,glymur-m31-eusb2-phy`, `qcom,kaanapali-m31-eusb2-phy`, `qcom,sm8750-m31-eusb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,m31-eusb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8996-qmp-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8996-qmp-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8996-qmp-pcie-phy.yaml` is a Qualcomm QMP PCIe PHY binding for `Qualcomm QMP PHY controller (MSM8996 PCIe)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: QMP PHY controller supports physical layer functionality for a number of controllers on Qualcomm chipsets, such as, PCIe, UFS, and USB..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `qcom,msm8996-qmp-pcie-phy`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `vddp-ref-clk-supply`. Required properties across the composed schema are `#address-cells`, `#clock-cells`, `#phy-cells`, `#size-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `ranges`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#address-cells`, `#clock-cells`, `#phy-cells`, `#size-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `ranges`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`, `vddp-ref-clk-supply`. Important numeric/constant limits include `const=qcom,msm8996-qmp-pcie-phy`, `maxItems=3`, `const=aux`, `const=cfg_ahb`, `const=ref`, `const=phy`, `const=common`, `const=cfg`, `const=0`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. pattern child nodes include `^phy@[0-9a-f]+$`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `vddp-ref-clk-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-msm8996.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8996.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `vddp-ref-clk-supply`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.#address-cells: 1, 2; properties.#size-cells: 1, 2; patternProperties.^phy@[0-9a-f]+$.properties.clock-names.items[0]: pipe0, pipe1, pipe2; patternProperties.^phy@[0-9a-f]+$.properties.reset-names.items[0]: lane0, lane1, lane2.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8996-qmp-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,msm8996-qmp-pcie-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8996-qmp-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-pcie-phy.yaml` is a Qualcomm QMP PCIe PHY binding for `Qualcomm QMP PHY controller (PCIe, MSM8998)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The QMP PHY controller supports physical layer functionality for a number of controllers on Qualcomm chipsets, such as, PCIe, UFS, and USB..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `qcom,msm8998-qmp-pcie-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `clock-output-names`, `#phy-cells`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. Important numeric/constant limits include `const=qcom,msm8998-qmp-pcie-phy`, `maxItems=4`, `const=aux`, `const=cfg_ahb`, `const=ref`, `const=pipe`, `maxItems=2`, `const=phy`, `const=common`, `const=0`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `clock-output-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8998.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `clock-output-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,msm8998-qmp-pcie-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-usb3-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-usb3-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-usb3-phy.yaml` is a Qualcomm QMP USB/DisplayPort PHY binding for `Qualcomm QMP PHY controller (USB, MSM8998)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The QMP PHY controller supports physical layer functionality for USB-C on several Qualcomm chipsets..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,msm8998-qmp-usb3-phy`, `qcom,qcm2290-qmp-usb3-phy`, `qcom,qcs615-qmp-usb3-phy`, `qcom,sdm660-qmp-usb3-phy`, `qcom,sm6115-qmp-usb3-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `clock-output-names`, `#phy-cells`, `orientation-switch`, `qcom,tcsr-reg`, `ports`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `qcom,tcsr-reg`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `orientation-switch`, `port@0`, `port@1`, `ports`, `qcom,tcsr-reg`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. Important numeric/constant limits include `maxItems=1`, `maxItems=4`, `maxItems=2`, `const=phy`, `const=phy_phy`, `const=0`, `const=aux`, `const=ref`, `const=cfg_ahb`, `const=pipe`, `const=com_aux`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle-array` conditional branches include `qcom,msm8998-qmp-usb3-phy`, `qcom,qcs615-qmp-usb3-phy`, `qcom,sdm660-qmp-usb3-phy` -> adjusts `clock-names`, `clocks`; `qcom,qcm2290-qmp-usb3-phy`, `qcom,sm6115-qmp-usb3-phy` -> adjusts `clock-names`, `clocks`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `clock-output-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usbc.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/agatti.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8998.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sdm630.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm6115.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `clock-output-names`, `qcom,tcsr-reg`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,msm8998-qmp-usb3-phy, qcom,qcm2290-qmp-usb3-phy, qcom,qcs615-qmp-usb3-phy, qcom,sdm660-qmp-usb3-phy, qcom,sm6115-qmp-usb3-phy; allOf[0].if.properties.compatible.contains: qcom,msm8998-qmp-usb3-phy, qcom,qcs615-qmp-usb3-phy, qcom,sdm660-qmp-usb3-phy; allOf[1].if.properties.compatible.contains: qcom,qcm2290-qmp-usb3-phy, qcom,sm6115-qmp-usb3-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-usb3-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,msm8998-qmp-usb3-phy`, `qcom,qcm2290-qmp-usb3-phy`, `qcom,qcs615-qmp-usb3-phy`, `qcom,sdm660-qmp-usb3-phy`, `qcom,sm6115-qmp-usb3-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,msm8998-qmp-usb3-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,pcie2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,pcie2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,pcie2-phy.yaml` is a Qualcomm PHY binding for `Qualcomm PCIe2 PHY controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The Qualcomm PCIe2 PHY is a Synopsys based phy found in a number of Qualcomm platforms..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is ordered fallback `items` sequence with values `qcom,qcs404-pcie2-phy`, `qcom,pcie2-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-output-names`, `#clock-cells`, `#phy-cells`, `vdda-vp-supply`, `vdda-vph-supply`, `resets`, `reset-names`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-output-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vdda-vp-supply`, `vdda-vph-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-output-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vdda-vp-supply`, `vdda-vph-supply`. Important numeric/constant limits include `const=qcom,qcs404-pcie2-phy`, `const=qcom,pcie2-phy`, `maxItems=1`, `const=0`, `maxItems=2`, `const=phy`, `const=pipe`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-output-names`, `#clock-cells`, `vdda-vp-supply`, `vdda-vph-supply`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-pcie2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/qcs404.dtsi`. External providers/consumers are signaled through `clocks`, `clock-output-names`, `#clock-cells`, `vdda-vp-supply`, `vdda-vph-supply`, `resets`, `reset-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,pcie2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,qcs404-pcie2-phy`, `qcom,pcie2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,pcie2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qcs615-qmp-usb3dp-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qcs615-qmp-usb3dp-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qcs615-qmp-usb3dp-phy.yaml` is a Qualcomm QMP USB/DisplayPort PHY binding for `Qualcomm QMP USB3-DP PHY controller (DP, QCS615)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The QMP PHY controller supports physical layer functionality for both USB3 and DisplayPort over USB-C. While it enables mode switching between USB3 and DisplayPort, but does not support combo mode..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,qcs615-qmp-usb3-dp-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `#phy-cells`, `qcom,tcsr-reg`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `qcom,tcsr-reg`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `qcom,tcsr-reg`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. Important numeric/constant limits include `maxItems=1`, `maxItems=4`, `const=aux`, `const=ref`, `const=cfg_ahb`, `const=pipe`, `maxItems=2`, `const=phy_phy`, `const=dp_phy`, `const=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usbc.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `qcom,tcsr-reg`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,qcs615-qmp-usb3-dp-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qcs615-qmp-usb3dp-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,qcs615-qmp-usb3-dp-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qcs615-qmp-usb3dp-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qusb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qusb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qusb2-phy.yaml` is a Qualcomm PHY binding for `Qualcomm QUSB2 phy controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: QUSB2 controller supports LS/FS/HS usb connectivity on Qualcomm chipsets..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,ipq5424-qusb2-phy`, `qcom,ipq6018-qusb2-phy`, `qcom,ipq8074-qusb2-phy`, `qcom,ipq9574-qusb2-phy`, `qcom,msm8953-qusb2-phy`, `qcom,msm8996-qusb2-phy`, `qcom,msm8998-qusb2-phy`, `qcom,qcm2290-qusb2-phy`, `qcom,qcs615-qusb2-phy`, `qcom,sdm660-qusb2-phy`, `qcom,sm4250-qusb2-phy`, `qcom,sm6115-qusb2-phy`, `qcom,sc7180-qusb2-phy`, `qcom,sdm670-qusb2-phy`, `qcom,sdm845-qusb2-phy`, `qcom,sm6350-qusb2-phy`, `qcom,qusb2-v2-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `vdd-supply`, `vdda-pll-supply`, `vdda-phy-dpdm-supply`, `resets`, `nvmem-cells`, `qcom,tcsr-syscon`, `qcom,imp-res-offset-value`, `qcom,bias-ctrl-value`, `qcom,charge-ctrl-value`, `qcom,hstx-trim-value`, `qcom,preemphasis-level`, `qcom,preemphasis-width`, `qcom,hsdisc-trim-value`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `resets`, `vdd-supply`, `vdda-phy-dpdm-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `nvmem-cells`, `qcom,bias-ctrl-value`, `qcom,charge-ctrl-value`, `qcom,hsdisc-trim-value`, `qcom,hstx-trim-value`, `qcom,imp-res-offset-value`, `qcom,preemphasis-level`, `qcom,preemphasis-width`, `qcom,tcsr-syscon`, `reg`, `resets`, `vdd-supply`, `vdda-phy-dpdm-supply`, `vdda-pll-supply`. Important numeric/constant limits include `const=qcom,qusb2-v2-phy`, `maxItems=1`, `const=0`, `minItems=2`, `const=cfg_ahb`, `const=ref`, `const=iface`, `minimum=0`, `maximum=63`, `maximum=3`, `maximum=15`, `maximum=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32` conditional branches include `qcom,qusb2-v2-phy` -> adjusts `qcom,bias-ctrl-value`, `qcom,charge-ctrl-value`, `qcom,hsdisc-trim-value`, `qcom,hstx-trim-value`, `qcom,imp-res-offset-value`, `qcom,preemphasis-level`, `qcom,preemphasis-width`

## State And Persistence
State is static firmware description rather than runtime persistence. NVMEM cells provide board/fuse trim data consumed by the driver; regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `vdd-supply`, `vdda-pll-supply`, `vdda-phy-dpdm-supply`, `resets` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qusb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/agatti.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq5424.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq6018.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq8074.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq9574.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8953.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8996.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8998.dtsi`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `vdd-supply`, `vdda-pll-supply`, `vdda-phy-dpdm-supply`, `resets`, `nvmem-cells`, `qcom,tcsr-syscon`, `qcom,imp-res-offset-value`, `qcom,bias-ctrl-value`, `qcom,charge-ctrl-value`, `qcom,hstx-trim-value`, `qcom,preemphasis-level`, `qcom,preemphasis-width`, `qcom,hsdisc-trim-value`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,ipq5424-qusb2-phy, qcom,ipq6018-qusb2-phy, qcom,ipq8074-qusb2-phy, qcom,ipq9574-qusb2-phy, qcom,msm8953-qusb2-phy, qcom,msm8996-qusb2-phy, qcom,msm8998-qusb2-phy, qcom,qcm2290-qusb2-phy, qcom,qcs615-qusb2-phy, qcom,sdm660-qusb2-phy, qcom,sm4250-qusb2-phy, qcom,sm6115-qusb2-phy; properties.compatible.oneOf[1].items[0]: qcom,sc7180-qusb2-phy, qcom,sdm670-qusb2-phy, qcom,sdm845-qusb2-phy, qcom,sm6350-qusb2-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qusb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,ipq5424-qusb2-phy`, `qcom,ipq6018-qusb2-phy`, `qcom,ipq8074-qusb2-phy`, `qcom,ipq9574-qusb2-phy`, `qcom,msm8953-qusb2-phy`, `qcom,msm8996-qusb2-phy`, and 11 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,qusb2-phy.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sata-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sata-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sata-phy.yaml` is a Qualcomm PHY binding for `Qualcomm SATA PHY Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The Qualcomm SATA PHY describes on-chip SATA Physical layer controllers..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,ipq806x-sata-phy`, `qcom,apq8064-sata-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. Important numeric/constant limits include `maxItems=1`, `const=cfg`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-apq8064-sata.c`, `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-sata.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-apq8064.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-ipq8064.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,ipq806x-sata-phy, qcom,apq8064-sata-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sata-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,ipq806x-sata-phy`, `qcom,apq8064-sata-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sata-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-pcie-phy.yaml` is a Qualcomm QMP PCIe PHY binding for `Qualcomm QMP PHY controller (PCIe, SC8280XP)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The QMP PHY controller supports physical layer functionality for a number of controllers on Qualcomm chipsets, such as, PCIe, UFS, and USB..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,glymur-qmp-gen4x2-pcie-phy`, `qcom,glymur-qmp-gen5x4-pcie-phy`, `qcom,kaanapali-qmp-gen3x2-pcie-phy`, `qcom,qcs615-qmp-gen3x1-pcie-phy`, `qcom,qcs8300-qmp-gen4x2-pcie-phy`, `qcom,sa8775p-qmp-gen4x2-pcie-phy`, `qcom,sa8775p-qmp-gen4x4-pcie-phy`, `qcom,sar2130p-qmp-gen3x2-pcie-phy`, `qcom,sc8180x-qmp-pcie-phy`, `qcom,sc8280xp-qmp-gen3x1-pcie-phy`, `qcom,sc8280xp-qmp-gen3x2-pcie-phy`, `qcom,sc8280xp-qmp-gen3x4-pcie-phy`, `qcom,sdm845-qhp-pcie-phy`, `qcom,sdm845-qmp-pcie-phy`, `qcom,sdx55-qmp-pcie-phy`, `qcom,sdx65-qmp-gen4x2-pcie-phy`, `qcom,sm8150-qmp-gen3x1-pcie-phy`, `qcom,sm8150-qmp-gen3x2-pcie-phy`, `qcom,sm8250-qmp-gen3x1-pcie-phy`, `qcom,sm8250-qmp-gen3x2-pcie-phy`, `qcom,sm8250-qmp-modem-pcie-phy`, `qcom,sm8350-qmp-gen3x1-pcie-phy`, `qcom,sm8350-qmp-gen3x2-pcie-phy`, `qcom,sm8450-qmp-gen3x1-pcie-phy`, and 11 more. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `vdda-qref-supply`, `qcom,4ln-config-sel`, `#clock-cells`, `clock-output-names`, `#phy-cells`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `qcom,4ln-config-sel`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `power-domains`, `qcom,4ln-config-sel`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`, `vdda-qref-supply`. Important numeric/constant limits include `minItems=1`, `maxItems=2`, `minItems=5`, `maxItems=6`, `const=aux`, `const=cfg_ahb`, `const=ref`, `const=pipe`, `const=pipediv2`, `maxItems=1`, `const=phy`, `const=phy_nocsr`, `const=0`, `maxItems=5`, `minItems=6`, `minItems=2`, `const=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array` conditional branches include `qcom,sc8280xp-qmp-gen3x4-pcie-phy`, `qcom,x1e80100-qmp-gen4x4-pcie-phy`, `qcom,x1p42100-qmp-gen4x4-pcie-phy` -> adjusts `reg`, requires `qcom,4ln-config-sel`; `qcom,kaanapali-qmp-gen3x2-pcie-phy`, `qcom,qcs615-qmp-gen3x1-pcie-phy`, `qcom,sar2130p-qmp-gen3x2-pcie-phy`, `qcom,sc8180x-qmp-pcie-phy`, `qcom,sdm845-qhp-pcie-phy`, `qcom,sdm845-qmp-pcie-phy`, `qcom,sdx55-qmp-pcie-phy`, `qcom,sm8150-qmp-gen3x1-pcie-phy`, `qcom,sm8150-qmp-gen3x2-pcie-phy`, `qcom,sm8250-qmp-gen3x1-pcie-phy`, and 11 more -> adjusts `clock-names`, `clocks`; `q...

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `vdda-qref-supply`, `#clock-cells`, `clock-output-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx55.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx65.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kodiak.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `vdda-qref-supply`, `#clock-cells`, `clock-output-names`, `qcom,4ln-config-sel`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,glymur-qmp-gen4x2-pcie-phy, qcom,glymur-qmp-gen5x4-pcie-phy, qcom,kaanapali-qmp-gen3x2-pcie-phy, qcom,qcs615-qmp-gen3x1-pcie-phy, qcom,qcs8300-qmp-gen4x2-pcie-phy, qcom,sa8775p-qmp-gen4x2-pcie-phy, qcom,sa8775p-qmp-gen4x4-pcie-phy, qcom,sar2130p-qmp-gen3x2-pcie-phy, qcom,sc8180x-qmp-pcie-phy, qcom,sc8280xp-qmp-gen3x1-pcie-phy, qcom,sc8280xp-qmp-gen3x2-pcie-phy, qcom,sc8280xp-qmp-gen3x4-pcie-phy, and 23 more; properties.clock-names.items[3]: rchng, refgen; allOf[0].if.properties.compatible.contains: qcom,sc8280xp-qmp-gen3x4-pcie-phy, qcom,x1e80100-qmp-gen4x4-pcie-phy, qcom,x1p42100-q....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,glymur-qmp-gen4x2-pcie-phy`, `qcom,glymur-qmp-gen5x4-pcie-phy`, `qcom,kaanapali-qmp-gen3x2-pcie-phy`, `qcom,qcs615-qmp-gen3x1-pcie-phy`, `qcom,qcs8300-qmp-gen4x2-pcie-phy`, `qcom,sa8775p-qmp-gen4x2-pcie-phy`, and 29 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-ufs-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-ufs-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-ufs-phy.yaml` is a Qualcomm QMP UFS PHY binding for `Qualcomm QMP PHY controller (UFS, SC8280XP)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The QMP PHY controller supports physical layer functionality for a number of controllers on Qualcomm chipsets, such as, PCIe, UFS, and USB..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 6 accepted compatible forms with values `qcom,qcs8300-qmp-ufs-phy`, `qcom,sa8775p-qmp-ufs-phy`, `qcom,qcs615-qmp-ufs-phy`, `qcom,sm6115-qmp-ufs-phy`, `qcom,x1e80100-qmp-ufs-phy`, `qcom,sm8550-qmp-ufs-phy`, `qcom,eliza-qmp-ufs-phy`, `qcom,sm8650-qmp-ufs-phy`, `qcom,kaanapali-qmp-ufs-phy`, `qcom,sm8750-qmp-ufs-phy`, `qcom,milos-qmp-ufs-phy`, `qcom,msm8996-qmp-ufs-phy`, `qcom,msm8998-qmp-ufs-phy`, `qcom,sc7180-qmp-ufs-phy`, `qcom,sc7280-qmp-ufs-phy`, `qcom,sc8180x-qmp-ufs-phy`, `qcom,sc8280xp-qmp-ufs-phy`, `qcom,sdm845-qmp-ufs-phy`, `qcom,sm6125-qmp-ufs-phy`, `qcom,sm6350-qmp-ufs-phy`, `qcom,sm7150-qmp-ufs-phy`, `qcom,sm8150-qmp-ufs-phy`, `qcom,sm8250-qmp-ufs-phy`, `qcom,sm8350-qmp-ufs-phy`, and 2 more. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. Important numeric/constant limits include `const=qcom,sa8775p-qmp-ufs-phy`, `const=qcom,sm6115-qmp-ufs-phy`, `const=qcom,sm8550-qmp-ufs-phy`, `const=qcom,sm8650-qmp-ufs-phy`, `const=qcom,sm8750-qmp-ufs-phy`, `maxItems=1`, `minItems=2`, `maxItems=3`, `const=ufsphy`, `const=1`, `const=0`, `minItems=3`, `const=ref`, `const=ref_aux`, `const=qref`, `maxItems=2`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `qcom,milos-qmp-ufs-phy`, `qcom,msm8998-qmp-ufs-phy`, `qcom,sa8775p-qmp-ufs-phy`, `qcom,sc7180-qmp-ufs-phy`, `qcom,sc7280-qmp-ufs-phy`, `qcom,sc8180x-qmp-ufs-phy`, `qcom,sc8280xp-qmp-ufs-phy`, `qcom,sdm845-qmp-ufs-phy`, `qcom,sm6115-qmp-ufs-phy`, `qcom,sm6125-qmp-ufs-phy`, and 10 more -> adjusts `clock-names`, `clocks`; `qcom,msm8996-qmp-ufs-phy` -> adjusts `clock-names`, `clocks`; `qcom,msm8996-qmp-ufs-phy`, `qcom,msm8998-qmp-ufs-phy` -> adjusts `power-domains`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-ufs.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/eliza.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kodiak.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/milos.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8996.dtsi`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `#clock-cells`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,qcs8300-qmp-ufs-phy; properties.compatible.oneOf[1].items[0]: qcom,qcs615-qmp-ufs-phy; properties.compatible.oneOf[2].items[0]: qcom,x1e80100-qmp-ufs-phy; properties.compatible.oneOf[3].items[0]: qcom,eliza-qmp-ufs-phy; properties.compatible.oneOf[4].items[0]: qcom,kaanapali-qmp-ufs-phy; properties.compatible.oneOf[5]: qcom,milos-qmp-ufs-phy, qcom,msm8996-qmp-ufs-phy, qcom,msm8998-qmp-ufs-phy, qcom,sa8775p-qmp-ufs-phy, qcom,sc7180-qmp-ufs-phy, qcom,sc7280-qmp-ufs-phy, qcom,sc8180x-qmp-ufs-phy, qcom,sc8280xp-qmp-ufs-phy, qcom,sdm845-qmp-ufs-phy, qcom,sm6115-qmp-ufs-....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-ufs-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,qcs8300-qmp-ufs-phy`, `qcom,sa8775p-qmp-ufs-phy`, `qcom,qcs615-qmp-ufs-phy`, `qcom,sm6115-qmp-ufs-phy`, `qcom,x1e80100-qmp-ufs-phy`, `qcom,sm8550-qmp-ufs-phy`, and 20 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-ufs-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb3-uni-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb3-uni-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb3-uni-phy.yaml` is a Qualcomm QMP USB/DisplayPort PHY binding for `Qualcomm QMP PHY controller (USB, SC8280XP)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The QMP PHY controller supports physical layer functionality for a number of controllers on Qualcomm chipsets, such as, PCIe, UFS, and USB..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,glymur-qmp-usb3-uni-phy`, `qcom,ipq5424-qmp-usb3-phy`, `qcom,ipq6018-qmp-usb3-phy`, `qcom,ipq8074-qmp-usb3-phy`, `qcom,ipq9574-qmp-usb3-phy`, `qcom,msm8996-qmp-usb3-phy`, `qcom,qcs8300-qmp-usb3-uni-phy`, `qcom,qdu1000-qmp-usb3-uni-phy`, `qcom,sa8775p-qmp-usb3-uni-phy`, `qcom,sc8180x-qmp-usb3-uni-phy`, `qcom,sc8280xp-qmp-usb3-uni-phy`, `qcom,sdm845-qmp-usb3-uni-phy`, `qcom,sdx55-qmp-usb3-uni-phy`, `qcom,sdx65-qmp-usb3-uni-phy`, `qcom,sdx75-qmp-usb3-uni-phy`, `qcom,sm8150-qmp-usb3-uni-phy`, `qcom,sm8250-qmp-usb3-uni-phy`, `qcom,sm8350-qmp-usb3-uni-phy`, `qcom,x1e80100-qmp-usb3-uni-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `refgen-supply`, `#clock-cells`, `clock-output-names`, `#phy-cells`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `power-domains`, `refgen-supply`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `power-domains`, `refgen-supply`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. Important numeric/constant limits include `maxItems=1`, `minItems=4`, `maxItems=5`, `maxItems=2`, `const=phy`, `const=phy_phy`, `const=0`, `maxItems=4`, `const=aux`, `const=ref`, `const=cfg_ahb`, `const=pipe`, `const=com_aux`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `qcom,ipq5424-qmp-usb3-phy`, `qcom,ipq6018-qmp-usb3-phy`, `qcom,ipq8074-qmp-usb3-phy`, `qcom,ipq9574-qmp-usb3-phy`, `qcom,msm8996-qmp-usb3-phy`, `qcom,sdx55-qmp-usb3-uni-phy`, `qcom,sdx65-qmp-usb3-uni-phy`, `qcom,sdx75-qmp-usb3-uni-phy` -> adjusts `clock-names`, `clocks`; `qcom,glymur-qmp-usb3-uni-phy`, `qcom,qcs8300-qmp-usb3-uni-phy`, `qcom,qdu1000-qmp-usb3-uni-phy`, `qcom,sa8775p-qmp-usb3-uni-phy`, `qcom,sc8180x-qmp-usb3-uni-phy`, `qcom,sc8280xp-qmp-usb3-uni-phy`, `qcom,sm8150-qmp-usb3-uni-phy`, `qcom,sm8250-qmp-usb3-uni-phy`, `q...

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `refgen-supply`, `#clock-cells`, `clock-output-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx55.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx65.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq5424.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq6018.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq8074.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/ipq9574.dtsi`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `refgen-supply`, `#clock-cells`, `clock-output-names`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,glymur-qmp-usb3-uni-phy, qcom,ipq5424-qmp-usb3-phy, qcom,ipq6018-qmp-usb3-phy, qcom,ipq8074-qmp-usb3-phy, qcom,ipq9574-qmp-usb3-phy, qcom,msm8996-qmp-usb3-phy, qcom,qcs8300-qmp-usb3-uni-phy, qcom,qdu1000-qmp-usb3-uni-phy, qcom,sa8775p-qmp-usb3-uni-phy, qcom,sc8180x-qmp-usb3-uni-phy, qcom,sc8280xp-qmp-usb3-uni-phy, qcom,sdm845-qmp-usb3-uni-phy, and 7 more; allOf[0].if.properties.compatible.contains: qcom,ipq5424-qmp-usb3-phy, qcom,ipq6018-qmp-usb3-phy, qcom,ipq8074-qmp-usb3-phy, qcom,ipq9574-qmp-usb3-phy, qcom,msm8996-qmp-usb3-phy, qcom,sdx55-qmp-usb3-uni-phy, qcom,sdx65-qmp-usb3-uni....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb3-uni-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,glymur-qmp-usb3-uni-phy`, `qcom,ipq5424-qmp-usb3-phy`, `qcom,ipq6018-qmp-usb3-phy`, `qcom,ipq8074-qmp-usb3-phy`, `qcom,ipq9574-qmp-usb3-phy`, `qcom,msm8996-qmp-usb3-phy`, and 13 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb3-uni-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb43dp-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb43dp-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb43dp-phy.yaml` is a Qualcomm QMP USB/DisplayPort PHY binding for `Qualcomm QMP USB4-USB3-DP PHY controller (SC8280XP)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The QMP PHY controller supports physical layer functionality for a number of controllers on Qualcomm chipsets, such as, PCIe, UFS and USB..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,kaanapali-qmp-usb3-dp-phy`, `qcom,sm8750-qmp-usb3-dp-phy`, `qcom,glymur-qmp-usb3-dp-phy`, `qcom,sar2130p-qmp-usb3-dp-phy`, `qcom,sc7180-qmp-usb3-dp-phy`, `qcom,sc7280-qmp-usb3-dp-phy`, `qcom,sc8180x-qmp-usb3-dp-phy`, `qcom,sc8280xp-qmp-usb43dp-phy`, `qcom,sdm845-qmp-usb3-dp-phy`, `qcom,sm6350-qmp-usb3-dp-phy`, `qcom,sm8150-qmp-usb3-dp-phy`, `qcom,sm8250-qmp-usb3-dp-phy`, `qcom,sm8350-qmp-usb3-dp-phy`, `qcom,sm8450-qmp-usb3-dp-phy`, `qcom,sm8550-qmp-usb3-dp-phy`, `qcom,sm8650-qmp-usb3-dp-phy`, `qcom,x1e80100-qmp-usb3-dp-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `refgen-supply`, `#clock-cells`, `#phy-cells`, `mode-switch`, `orientation-switch`, `ports`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `data-lanes`, `power-domains`, `refgen-supply`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `data-lanes`, `endpoint`, `endpoint@0`, `endpoint@1`, `mode-switch`, `orientation-switch`, `port@0`, `port@1`, `port@2`, `ports`, `power-domains`, `refgen-supply`, `reg`, `reset-names`, `resets`, `vdda-phy-supply`, `vdda-pll-supply`. Important numeric/constant limits include `const=qcom,sm8750-qmp-usb3-dp-phy`, `maxItems=1`, `minItems=4`, `maxItems=5`, `const=aux`, `const=ref`, `const=com_aux`, `const=usb3_pipe`, `const=cfg_ahb`, `maxItems=2`, `const=phy`, `const=common`, `const=1`, `minItems=2`, `maxItems=4`, `const=3`, `const=0`, `const=2`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/usb/usb-switch.yaml#` conditional branches include `qcom,sc7180-qmp-usb3-dp-phy`, `qcom,sdm845-qmp-usb3-dp-phy` -> adjusts `clock-names`, `clocks`; `qcom,glymur-qmp-usb3-dp-phy`, `qcom,sar2130p-qmp-usb3-dp-phy`, `qcom,sc8280xp-qmp-usb43dp-phy`, `qcom,sm6350-qmp-usb3-dp-phy`, `qcom,sm8550-qmp-usb3-dp-phy`, `qcom,sm8650-qmp-usb3-dp-phy`, `qcom,sm8750-qmp-usb3-dp-phy`, `qcom,x1e80100-qmp-usb3-dp-phy` -> requires `power-domains`; `qcom,glymur-qmp-usb3-dp-phy` -> requires `refgen-supply`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `refgen-supply`, `#clock-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/usb/usb-switch.yaml#`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-combo.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kodiak.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc7180.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8180x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sdm845.dtsi`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `vdda-phy-supply`, `vdda-pll-supply`, `refgen-supply`, `#clock-cells`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,kaanapali-qmp-usb3-dp-phy; properties.compatible.oneOf[1]: qcom,glymur-qmp-usb3-dp-phy, qcom,sar2130p-qmp-usb3-dp-phy, qcom,sc7180-qmp-usb3-dp-phy, qcom,sc7280-qmp-usb3-dp-phy, qcom,sc8180x-qmp-usb3-dp-phy, qcom,sc8280xp-qmp-usb43dp-phy, qcom,sdm845-qmp-usb3-dp-phy, qcom,sm6350-qmp-usb3-dp-phy, qcom,sm8150-qmp-usb3-dp-phy, qcom,sm8250-qmp-usb3-dp-phy, qcom,sm8350-qmp-usb3-dp-phy, qcom,sm8450-qmp-usb3-dp-phy, and 4 more; allOf[1].if.properties.compatible: qcom,sc7180-qmp-usb3-dp-phy, qcom,sdm845-qmp-usb3-dp-phy; allOf[2].if.properties.compatible.contains: qcom,glymu....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb43dp-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,kaanapali-qmp-usb3-dp-phy`, `qcom,sm8750-qmp-usb3-dp-phy`, `qcom,glymur-qmp-usb3-dp-phy`, `qcom,sar2130p-qmp-usb3-dp-phy`, `qcom,sc7180-qmp-usb3-dp-phy`, `qcom,sc7280-qmp-usb3-dp-phy`, and 11 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,sc8280xp-qmp-usb43dp-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml` is a Qualcomm PHY binding for `Qualcomm SNPS eUSB2 phy controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: eUSB2 controller supports LS/FS/HS usb connectivity on Qualcomm chipsets..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,milos-snps-eusb2-phy`, `qcom,sar2130p-snps-eusb2-phy`, `qcom,sdx75-snps-eusb2-phy`, `qcom,sm8650-snps-eusb2-phy`, `qcom,x1e80100-snps-eusb2-phy`, `qcom,sm8550-snps-eusb2-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `phys`, `vdd-supply`, `vdda12-supply`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `resets`, `vdd-supply`, `vdda12-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `phys`, `reg`, `resets`, `vdd-supply`, `vdda12-supply`. Important numeric/constant limits include `const=qcom,sm8550-snps-eusb2-phy`, `maxItems=1`, `const=0`, `const=ref`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `vdd-supply`, `vdda12-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/phy-snps-eusb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/milos.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sdx75.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8650.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `vdd-supply`, `vdda12-supply`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,milos-snps-eusb2-phy, qcom,sar2130p-snps-eusb2-phy, qcom,sdx75-snps-eusb2-phy, qcom,sm8650-snps-eusb2-phy, qcom,x1e80100-snps-eusb2-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,milos-snps-eusb2-phy`, `qcom,sar2130p-snps-eusb2-phy`, `qcom,sdx75-snps-eusb2-phy`, `qcom,sm8650-snps-eusb2-phy`, `qcom,x1e80100-snps-eusb2-phy`, `qcom,sm8550-snps-eusb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-repeater.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-repeater.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-repeater.yaml` is a Qualcomm PHY binding for `Qualcomm Synopsis eUSB2 to USB 2.0 repeater`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: eUSB2 repeater converts between eUSB2 and USB 2.0 signaling levels and allows a eUSB2 PHY to connect to legacy USB 2.0 products.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,pm7550ba-eusb2-repeater`, `qcom,pm8550b-eusb2-repeater`, `qcom,pmiv0104-eusb2-repeater`, `qcom,smb2360-eusb2-repeater`, `qcom,smb2370-eusb2-repeater`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `vdd18-supply`, `vdd3-supply`, `qcom,tune-usb2-disc-thres`, `qcom,tune-usb2-amplitude`, `qcom,tune-usb2-preem`, `qcom,tune-res-fsdif`, `qcom,squelch-detector-bp`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `qcom,squelch-detector-bp`, `qcom,tune-res-fsdif`, `qcom,tune-usb2-amplitude`, `qcom,tune-usb2-disc-thres`, `qcom,tune-usb2-preem`, `reg`, `vdd18-supply`, `vdd3-supply`. Important numeric/constant limits include `const=qcom,pm8550b-eusb2-repeater`, `maxItems=1`, `const=0`, `minimum=0`, `maximum=7`, `maximum=15`, `minimum=-6000`, `maximum=1000`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint8`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `vdd18-supply`, `vdd3-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint8`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-eusb2-repeater.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa-pmics.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/pm7550ba.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/pm8550b.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/pmih0108-kaanapali.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/pmih0108.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/pmiv0104.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/smb2370.dtsi`. External providers/consumers are signaled through `vdd18-supply`, `vdd3-supply`, `qcom,tune-usb2-disc-thres`, `qcom,tune-usb2-amplitude`, `qcom,tune-usb2-preem`, `qcom,tune-res-fsdif`, `qcom,squelch-detector-bp`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,pm7550ba-eusb2-repeater; properties.compatible.oneOf[1]: qcom,pm8550b-eusb2-repeater, qcom,pmiv0104-eusb2-repeater, qcom,smb2360-eusb2-repeater, qcom,smb2370-eusb2-repeater.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-repeater.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,pm7550ba-eusb2-repeater`, `qcom,pm8550b-eusb2-repeater`, `qcom,pmiv0104-eusb2-repeater`, `qcom,smb2360-eusb2-repeater`, `qcom,smb2370-eusb2-repeater` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,snps-eusb2-repeater.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-28nm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-28nm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-28nm.yaml` is a Qualcomm PHY binding for `Qualcomm Synopsys DesignWare Core 28nm High-Speed PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm Low-Speed, Full-Speed, Hi-Speed 28nm USB PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,usb-hs-28nm-femtophy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `vdd-supply`, `vdda1p8-supply`, `vdda3p3-supply`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vdd-supply`, `vdda1p8-supply`, `vdda3p3-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vdd-supply`, `vdda1p8-supply`, `vdda3p3-supply`. Important numeric/constant limits include `maxItems=1`, `const=0`, `const=ref`, `const=ahb`, `const=sleep`, `const=phy`, `const=por`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `vdd-supply`, `vdda1p8-supply`, `vdda3p3-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs-28nm.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8917.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8937.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8976.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/qcs404.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `vdd-supply`, `vdda1p8-supply`, `vdda3p3-supply`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,usb-hs-28nm-femtophy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-28nm.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,usb-hs-28nm-femtophy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-28nm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-phy.yaml` is a Qualcomm PHY binding for `Qualcomm's USB HS PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm's USB HS PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is ordered fallback `items` sequence with values `qcom,usb-hs-phy-apq8064`, `qcom,usb-hs-phy-msm8226`, `qcom,usb-hs-phy-msm8660`, `qcom,usb-hs-phy-msm8916`, `qcom,usb-hs-phy-msm8960`, `qcom,usb-hs-phy-msm8974`, `qcom,usb-hs-phy`. Top-level properties are `compatible`, `clocks`, `clock-names`, `resets`, `reset-names`, `v1p8-supply`, `v3p3-supply`, `extcon`, `#phy-cells`, `qcom,init-seq`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `extcon`, `qcom,init-seq`, `reset-names`, `resets`, `v1p8-supply`, `v3p3-supply`. Important numeric/constant limits include `maxItems=1`, `const=por`, `minItems=2`, `maxItems=2`, `const=phy`, `const=qcom,usb-hs-phy`, `const=ref`, `const=sleep`, `const=0`, `maxItems=32`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint8-matrix` conditional branches include `qcom,usb-hs-phy-apq8064`, `qcom,usb-hs-phy-msm8660`, `qcom,usb-hs-phy-msm8960` -> adjusts `reset-names`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `v1p8-supply`, `v3p3-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint8-matrix`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-apq8064.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-msm8226.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-msm8960.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-msm8974.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8916.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8939.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `v1p8-supply`, `v3p3-supply`, `qcom,init-seq`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: if.properties.compatible.contains: qcom,usb-hs-phy-apq8064, qcom,usb-hs-phy-msm8660, qcom,usb-hs-phy-msm8960; properties.compatible.items[0]: qcom,usb-hs-phy-apq8064, qcom,usb-hs-phy-msm8226, qcom,usb-hs-phy-msm8660, qcom,usb-hs-phy-msm8916, qcom,usb-hs-phy-msm8960, qcom,usb-hs-phy-msm8974.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,usb-hs-phy-apq8064`, `qcom,usb-hs-phy-msm8226`, `qcom,usb-hs-phy-msm8660`, `qcom,usb-hs-phy-msm8916`, `qcom,usb-hs-phy-msm8960`, `qcom,usb-hs-phy-msm8974`, and 1 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hs-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hsic-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hsic-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hsic-phy.yaml` is a Qualcomm PHY binding for `Qualcomm USB HSIC PHY Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm USB HSIC PHY Controller.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is ordered fallback `items` sequence with values `qcom,usb-hsic-phy-mdm9615`, `qcom,usb-hsic-phy-msm8974`, `qcom,usb-hsic-phy`. Top-level properties are `compatible`, `clocks`, `clock-names`, `#phy-cells`, `pinctrl-0`, `pinctrl-1`, `pinctrl-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `pinctrl-0`, `pinctrl-1`, `pinctrl-names`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `pinctrl-0`, `pinctrl-1`, `pinctrl-names`. Important numeric/constant limits include `const=qcom,usb-hsic-phy`, `maxItems=3`, `const=phy`, `const=cal`, `const=cal_sleep`, `const=0`, `const=init`, `const=default`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hsic.c`, `sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_msm.c`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.items[0]: qcom,usb-hsic-phy-mdm9615, qcom,usb-hsic-phy-msm8974.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hsic-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,usb-hsic-phy-mdm9615`, `qcom,usb-hsic-phy-msm8974`, `qcom,usb-hsic-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-hsic-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-snps-femto-v2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-snps-femto-v2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-snps-femto-v2.yaml` is a Qualcomm PHY binding for `Qualcomm Synopsys Femto High-Speed USB PHY V2`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm High-Speed USB PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `qcom,sa8775p-usb-hs-phy`, `qcom,sc8280xp-usb-hs-phy`, `qcom,usb-snps-hs-5nm-phy`, `qcom,qcs8300-usb-hs-phy`, `qcom,qdu1000-usb-hs-phy`, `qcom,sc7280-usb-hs-phy`, `qcom,sc8180x-usb-hs-phy`, `qcom,sdx55-usb-hs-phy`, `qcom,sdx65-usb-hs-phy`, `qcom,sm6375-usb-hs-phy`, `qcom,sm8150-usb-hs-phy`, `qcom,sm8250-usb-hs-phy`, `qcom,sm8350-usb-hs-phy`, `qcom,sm8450-usb-hs-phy`, `qcom,usb-snps-hs-7nm-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `vdda-pll-supply`, `vdda18-supply`, `vdda33-supply`, `qcom,hs-disconnect-bp`, `qcom,squelch-detector-bp`, `qcom,hs-amplitude-bp`, `qcom,pre-emphasis-duration-bp`, `qcom,pre-emphasis-amplitude-bp`, `qcom,hs-rise-fall-time-bp`, `qcom,hs-crossover-voltage-microvolt`, `qcom,hs-output-impedance-micro-ohms`, `qcom,ls-fs-output-impedance-bp`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `resets`, `vdda-pll-supply`, `vdda18-supply`, `vdda33-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `qcom,hs-amplitude-bp`, `qcom,hs-crossover-voltage-microvolt`, `qcom,hs-disconnect-bp`, `qcom,hs-output-impedance-micro-ohms`, `qcom,hs-rise-fall-time-bp`, `qcom,ls-fs-output-impedance-bp`, `qcom,pre-emphasis-amplitude-bp`, `qcom,pre-emphasis-duration-bp`, `qcom,squelch-detector-bp`, `reg`, `resets`, `vdda-pll-supply`, `vdda18-supply`, `vdda33-supply`. Important numeric/constant limits include `const=qcom,usb-snps-hs-5nm-phy`, `const=qcom,usb-snps-hs-7nm-phy`, `maxItems=1`, `const=0`, `const=ref`, `minimum=-272`, `maximum=2156`, `minimum=-2090`, `maximum=1590`, `minimum=-660`, `maximum=2670`, `minimum=10000`, `maximum=20000`, `maximum=40000`, `minimum=-4100`, `maximum=5430`, `minimum=-31000`, `maximum=28000`, and 4 more.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `vdda-pll-supply`, `vdda18-supply`, `vdda33-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-snps-femto-v2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx55.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx65.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kodiak.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/qdu1000.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8180x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp.dtsi`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `vdda-pll-supply`, `vdda18-supply`, `vdda33-supply`, `qcom,hs-disconnect-bp`, `qcom,squelch-detector-bp`, `qcom,hs-amplitude-bp`, `qcom,pre-emphasis-duration-bp`, `qcom,pre-emphasis-amplitude-bp`, `qcom,hs-rise-fall-time-bp`, `qcom,hs-crossover-voltage-microvolt`, `qcom,hs-output-impedance-micro-ohms`, `qcom,ls-fs-output-impedance-bp`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: qcom,sa8775p-usb-hs-phy, qcom,sc8280xp-usb-hs-phy; properties.compatible.oneOf[1].items[0]: qcom,qcs8300-usb-hs-phy, qcom,qdu1000-usb-hs-phy, qcom,sc7280-usb-hs-phy, qcom,sc8180x-usb-hs-phy, qcom,sdx55-usb-hs-phy, qcom,sdx65-usb-hs-phy, qcom,sm6375-usb-hs-phy, qcom,sm8150-usb-hs-phy, qcom,sm8250-usb-hs-phy, qcom,sm8350-usb-hs-phy, qcom,sm8450-usb-hs-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-snps-femto-v2.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,sa8775p-usb-hs-phy`, `qcom,sc8280xp-usb-hs-phy`, `qcom,usb-snps-hs-5nm-phy`, `qcom,qcs8300-usb-hs-phy`, `qcom,qdu1000-usb-hs-phy`, `qcom,sc7280-usb-hs-phy`, and 9 more against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-snps-femto-v2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-ss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-ss.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-ss.yaml` is a Qualcomm PHY binding for `Qualcomm Synopsys 1.0.0 SuperSpeed USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcomm Synopsys 1.0.0 SuperSpeed USB PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,usb-ss-28nm-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `vdd-supply`, `vdda1p8-supply`, `resets`, `reset-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `vdd-supply`, `vdda1p8-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vdd-supply`, `vdda1p8-supply`. Important numeric/constant limits include `maxItems=1`, `const=0`, `const=ref`, `const=ahb`, `const=pipe`, `const=com`, `const=phy`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `vdd-supply`, `vdda1p8-supply`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-ss.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/qcs404.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `vdd-supply`, `vdda1p8-supply`, `resets`, `reset-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,usb-ss-28nm-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-ss.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,usb-ss-28nm-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom,usb-ss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom-usb-ipq4019-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom-usb-ipq4019-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom-usb-ipq4019-phy.yaml` is a Qualcomm PHY binding for `Qualcom IPQ40xx Dakota HS/SS USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Qualcom IPQ40xx Dakota HS/SS USB PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `qcom,usb-ss-ipq4019-phy`, `qcom,usb-hs-ipq4019-phy`. Top-level properties are `compatible`, `reg`, `resets`, `reset-names`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `reg`, `reset-names`, `resets`. Important numeric/constant limits include `maxItems=1`, `maxItems=2`, `const=por_rst`, `const=srif_rst`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq4019-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-ipq4019.dtsi`. External providers/consumers are signaled through `resets`, `reset-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: qcom,usb-ss-ipq4019-phy, qcom,usb-hs-ipq4019-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom-usb-ipq4019-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `qcom,usb-ss-ipq4019-phy`, `qcom,usb-hs-ipq4019-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/qcom-usb-ipq4019-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb2phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb2phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb2phy.yaml` is a Realtek USB PHY binding for `Realtek DHC SoCs USB 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Realtek USB 2.0 PHY support the digital home center (DHC) RTD series SoCs. The USB 2.0 PHY driver is designed to support the XHCI controller. The SoCs support multiple XHCI controllers. One PHY device node maps to one XHCI controller. RTD1295/RTD1619 SoCs USB The USB architecture includes three XHCI controllers. Each XHCI maps to one USB 2.0 PHY and map one USB 3.0 PHY on some controllers. XHCI controller#0 -- usb2phy -- phy#0 |- usb3phy -- phy#0 XHCI controller#1 -- usb2phy -- phy#0 XHCI controller#2 -- usb2phy -- phy#0 |- usb3phy -- phy#0 RTD1395 SoCs USB The USB architecture includes two XHCI controllers. The controller#0 has one USB 2.0 PHY. The controller#1 includes two USB 2.0 PHY. XHCI controller#0 -- usb2phy -- phy#0 XHCI controller#1 -- u....

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `realtek,rtd1295-usb2phy`, `realtek,rtd1312c-usb2phy`, `realtek,rtd1315e-usb2phy`, `realtek,rtd1319-usb2phy`, `realtek,rtd1319d-usb2phy`, `realtek,rtd1395-usb2phy`, `realtek,rtd1395-usb2phy-2port`, `realtek,rtd1619-usb2phy`, `realtek,rtd1619b-usb2phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `nvmem-cells`, `nvmem-cell-names`, `realtek,inverse-hstx-sync-clock`, `realtek,driving-level`, `realtek,driving-level-compensate`, `realtek,disconnection-compensate`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `nvmem-cell-names`, `nvmem-cells`, `realtek,disconnection-compensate`, `realtek,driving-level`, `realtek,driving-level-compensate`, `realtek,inverse-hstx-sync-clock`, `reg`. Important numeric/constant limits include `const=0`, `maxItems=2`, `const=usb-dc-cal`, `const=usb-dc-dis`, `minimum=0`, `maximum=31`, `minimum=-8`, `maximum=8`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/uint32` conditional branches include `realtek,rtd1619b-usb2phy` -> adjusts `realtek,inverse-hstx-sync-clock`; `realtek,rtd1315e-usb2phy` -> adjusts `realtek,driving-level-compensate`

## State And Persistence
State is static firmware description rather than runtime persistence. NVMEM cells provide board/fuse trim data consumed by the driver. Named resources such as `realtek,inverse-hstx-sync-clock` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb2.c`. External providers/consumers are signaled through `realtek,inverse-hstx-sync-clock`, `nvmem-cells`, `nvmem-cell-names`, `realtek,inverse-hstx-sync-clock`, `realtek,driving-level`, `realtek,driving-level-compensate`, `realtek,disconnection-compensate`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: realtek,rtd1295-usb2phy, realtek,rtd1312c-usb2phy, realtek,rtd1315e-usb2phy, realtek,rtd1319-usb2phy, realtek,rtd1319d-usb2phy, realtek,rtd1395-usb2phy, realtek,rtd1395-usb2phy-2port, realtek,rtd1619-usb2phy, realtek,rtd1619b-usb2phy; allOf[0].if.not.properties.compatible.contains: realtek,rtd1619b-usb2phy; allOf[1].if.not.properties.compatible.contains: realtek,rtd1315e-usb2phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb2phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `realtek,rtd1295-usb2phy`, `realtek,rtd1312c-usb2phy`, `realtek,rtd1315e-usb2phy`, `realtek,rtd1319-usb2phy`, `realtek,rtd1319d-usb2phy`, `realtek,rtd1395-usb2phy`, and 3 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb2phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb3phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb3phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb3phy.yaml` is a Realtek USB PHY binding for `Realtek DHC SoCs USB 3.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Realtek USB 3.0 PHY support the digital home center (DHC) RTD series SoCs. The USB 3.0 PHY driver is designed to support the XHCI controller. The SoCs support multiple XHCI controllers. One PHY device node maps to one XHCI controller. RTD1295/RTD1619 SoCs USB The USB architecture includes three XHCI controllers. Each XHCI maps to one USB 2.0 PHY and map one USB 3.0 PHY on some controllers. XHCI controller#0 -- usb2phy -- phy#0 |- usb3phy -- phy#0 XHCI controller#1 -- usb2phy -- phy#0 XHCI controller#2 -- usb2phy -- phy#0 |- usb3phy -- phy#0 RTD1319/RTD1619b SoCs USB The USB architecture includes three XHCI controllers. Each XHCI maps to one USB 2.0 PHY and map one USB 3.0 PHY on controllers#2. XHCI controller#0 -- usb2phy -- phy#0 XHCI controller#....

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `realtek,rtd1295-usb3phy`, `realtek,rtd1319-usb3phy`, `realtek,rtd1319d-usb3phy`, `realtek,rtd1619-usb3phy`, `realtek,rtd1619b-usb3phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `nvmem-cells`, `nvmem-cell-names`, `realtek,amplitude-control-coarse-tuning`, `realtek,amplitude-control-fine-tuning`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `nvmem-cell-names`, `nvmem-cells`, `realtek,amplitude-control-coarse-tuning`, `realtek,amplitude-control-fine-tuning`, `reg`. Important numeric/constant limits include `maxItems=1`, `const=0`, `const=usb_u3_tx_lfps_swing_trim`, `minimum=0`, `maximum=255`, `maximum=65535`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. NVMEM cells provide board/fuse trim data consumed by the driver. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb3.c`. External providers/consumers are signaled through `nvmem-cells`, `nvmem-cell-names`, `realtek,amplitude-control-coarse-tuning`, `realtek,amplitude-control-fine-tuning`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: realtek,rtd1295-usb3phy, realtek,rtd1319-usb3phy, realtek,rtd1319d-usb3phy, realtek,rtd1619-usb3phy, realtek,rtd1619b-usb3phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb3phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `realtek,rtd1295-usb3phy`, `realtek,rtd1319-usb3phy`, `realtek,rtd1319d-usb3phy`, `realtek,rtd1619-usb3phy`, `realtek,rtd1619b-usb3phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/realtek,usb3phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,r8a779f0-ether-serdes.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,r8a779f0-ether-serdes.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,r8a779f0-ether-serdes.yaml` is a Renesas PHY binding for `Renesas Ethernet SERDES`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Renesas Ethernet SERDES.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `renesas,r8a779f0-ether-serdes`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `power-domains`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. Important numeric/constant limits include `const=renesas,r8a779f0-ether-serdes`, `maxItems=1`, `const=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `resets`, `power-domains` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/renesas/r8a779f0-ether-serdes.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a779f0.dtsi`. External providers/consumers are signaled through `clocks`, `resets`, `power-domains`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,r8a779f0-ether-serdes.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `renesas,r8a779f0-ether-serdes` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,r8a779f0-ether-serdes.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen2-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen2-usb-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen2-usb-phy.yaml` is a Renesas PHY binding for `Renesas R-Car Gen2 USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Renesas R-Car Gen2 USB PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is ordered fallback `items` sequence with values `renesas,usb-phy-r8a7742`, `renesas,usb-phy-r8a7743`, `renesas,usb-phy-r8a7744`, `renesas,usb-phy-r8a7745`, `renesas,usb-phy-r8a77470`, `renesas,usb-phy-r8a7790`, `renesas,usb-phy-r8a7791`, `renesas,usb-phy-r8a7794`, `renesas,rcar-gen2-usb-phy`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `power-domains`, `resets`. Required properties across the composed schema are `#address-cells`, `#phy-cells`, `#size-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`, `usb-phy@0`, `usb-phy@2`. All discovered property names, including nested child-node contracts, include `#address-cells`, `#phy-cells`, `#size-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`, `usb-phy@2`. Important numeric/constant limits include `const=renesas,rcar-gen2-usb-phy`, `maxItems=1`, `const=1`, `const=0`, `const=usbhs`, `const=renesas,usb-phy-r8a77470`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `renesas,usb-phy-r8a77470` -> adjusts `usb-phy@2` pattern child nodes include `^usb-phy@[02]$`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a7742.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a7743.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a7744.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a7745.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a77470.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a7790.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a7791.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a7794.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.items[0]: renesas,usb-phy-r8a7742, renesas,usb-phy-r8a7743, renesas,usb-phy-r8a7744, renesas,usb-phy-r8a7745, renesas,usb-phy-r8a77470, renesas,usb-phy-r8a7790, renesas,usb-phy-r8a7791, renesas,usb-phy-r8a7794; patternProperties.^usb-phy@[02]$.properties.reg: 0, 2.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen2-usb-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `renesas,usb-phy-r8a7742`, `renesas,usb-phy-r8a7743`, `renesas,usb-phy-r8a7744`, `renesas,usb-phy-r8a7745`, `renesas,usb-phy-r8a77470`, `renesas,usb-phy-r8a7790`, and 3 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen2-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen3-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen3-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen3-pcie-phy.yaml` is a Renesas PHY binding for `Renesas R-Car Generation 3 PCIe PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Renesas R-Car Generation 3 PCIe PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `renesas,r8a77980-pcie-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `power-domains`, `resets`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. Important numeric/constant limits include `const=renesas,r8a77980-pcie-phy`, `maxItems=1`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `power-domains`, `resets` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a77980.dtsi`. External providers/consumers are signaled through `clocks`, `power-domains`, `resets`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen3-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `renesas,r8a77980-pcie-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,rcar-gen3-pcie-phy.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb2-phy.yaml` is a Renesas PHY binding for `Renesas R-Car generation 3 USB 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Renesas R-Car generation 3 USB 2.0 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 6 accepted compatible forms with values `renesas,usb2-phy-r8a77470`, `renesas,usb2-phy-r9a08g045`, `renesas,usb2-phy-r9a09g057`, `renesas,usb2-phy-r7s9210`, `renesas,usb2-phy-r8a774a1`, `renesas,usb2-phy-r8a774b1`, `renesas,usb2-phy-r8a774c0`, `renesas,usb2-phy-r8a774e1`, `renesas,usb2-phy-r8a7795`, `renesas,usb2-phy-r8a7796`, `renesas,usb2-phy-r8a77961`, `renesas,usb2-phy-r8a77965`, `renesas,usb2-phy-r8a77990`, `renesas,usb2-phy-r8a77995`, `renesas,rcar-gen3-usb2-phy`, `renesas,usb2-phy-r9a07g043`, `renesas,usb2-phy-r9a07g044`, `renesas,usb2-phy-r9a07g054`, `renesas,rzg2l-usb2-phy`, `renesas,usb2-phy-r9a09g047`, `renesas,usb2-phy-r9a09g056`, `renesas,usb2-phy-r9a09g077`, `renesas,usb2-phy-r9a09g087`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`, `interrupts`, `power-domains`, `resets`, `vbus-supply`, `vbus-regulator`, `renesas,no-otg-pins`, `dr_mode`, `mux-states`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `dr_mode`, `interrupts`, `mux-states`, `power-domains`, `reg`, `renesas,no-otg-pins`, `resets`, `vbus-regulator`, `vbus-supply`. Important numeric/constant limits include `const=renesas,rcar-gen3-usb2-phy`, `const=renesas,rzg2l-usb2-phy`, `const=renesas,usb2-phy-r9a09g057`, `const=renesas,usb2-phy-r9a09g077`, `const=renesas,usb2-phy-r9a09g087`, `maxItems=1`, `minItems=1`, `maxItems=2`, `const=fck`, `const=usb_x1`, `const=renesas,usb2-phy-r7s9210`, `minItems=2`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/regulator/regulator.yaml#`, `/schemas/types.yaml#/definitions/flag` conditional branches include `renesas,usb2-phy-r7s9210` -> requires `clock-names`; `renesas,usb2-phy-r9a09g057`, `renesas,usb2-phy-r9a08g045`, `renesas,rzg2l-usb2-phy` -> adjusts `clocks`, requires `resets`; `renesas,usb2-phy-r9a09g077` -> adjusts `clocks`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `vbus-supply`, `interrupts` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/regulator/regulator.yaml#`, `/schemas/types.yaml#/definitions/flag`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r7s9210.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/r8a77470.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a774a1.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a774b1.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a774c0.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a774e1.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a77951.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a77960.dtsi`, and 2 more. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `vbus-supply`, `interrupts`, `renesas,no-otg-pins`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: renesas,usb2-phy-r8a77470, renesas,usb2-phy-r9a08g045, renesas,usb2-phy-r9a09g057; properties.compatible.oneOf[1].items[0]: renesas,usb2-phy-r7s9210, renesas,usb2-phy-r8a774a1, renesas,usb2-phy-r8a774b1, renesas,usb2-phy-r8a774c0, renesas,usb2-phy-r8a774e1, renesas,usb2-phy-r8a7795, renesas,usb2-phy-r8a7796, renesas,usb2-phy-r8a77961, renesas,usb2-phy-r8a77965, renesas,usb2-phy-r8a77990, renesas,usb2-phy-r8a77995; properties.compatible.oneOf[2].items[0]: renesas,usb2-phy-r9a07g043, renesas,usb2-phy-r9a07g044, renesas,usb2-phy-r9a07g054; properties.compatible.oneOf[3].it....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `renesas,usb2-phy-r8a77470`, `renesas,usb2-phy-r9a08g045`, `renesas,usb2-phy-r9a09g057`, `renesas,usb2-phy-r7s9210`, `renesas,usb2-phy-r8a774a1`, `renesas,usb2-phy-r8a774b1`, and 17 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb3-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb3-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb3-phy.yaml` is a Renesas PHY binding for `Renesas R-Car generation 3 USB 3.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Renesas R-Car generation 3 USB 3.0 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is ordered fallback `items` sequence with values `renesas,r8a774a1-usb3-phy`, `renesas,r8a774b1-usb3-phy`, `renesas,r8a774e1-usb3-phy`, `renesas,r8a7795-usb3-phy`, `renesas,r8a7796-usb3-phy`, `renesas,r8a77961-usb3-phy`, `renesas,r8a77965-usb3-phy`, `renesas,rcar-gen3-usb3-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`, `power-domains`, `resets`, `renesas,ssc-range`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `renesas,ssc-range`, `resets`. Important numeric/constant limits include `const=renesas,rcar-gen3-usb3-phy`, `maxItems=1`, `minItems=2`, `maxItems=3`, `const=usb3-if`, `const=usb3s_clk`, `const=usb_extal`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb3.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a774a1.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a774b1.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a774e1.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a77951.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a77960.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a77961.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/r8a77965.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `renesas,ssc-range`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.items[0]: renesas,r8a774a1-usb3-phy, renesas,r8a774b1-usb3-phy, renesas,r8a774e1-usb3-phy, renesas,r8a7795-usb3-phy, renesas,r8a7796-usb3-phy, renesas,r8a77961-usb3-phy, renesas,r8a77965-usb3-phy; properties.renesas,ssc-range: 0, 4003, 4492, 4980.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb3-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `renesas,r8a774a1-usb3-phy`, `renesas,r8a774b1-usb3-phy`, `renesas,r8a774e1-usb3-phy`, `renesas,r8a7795-usb3-phy`, `renesas,r8a7796-usb3-phy`, `renesas,r8a77961-usb3-phy`, and 2 more against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/renesas,usb3-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,inno-usb2phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,inno-usb2phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,inno-usb2phy.yaml` is a Rockchip PHY binding for `Rockchip USB2.0 phy with inno IP block`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip USB2.0 phy with inno IP block.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,px30-usb2phy`, `rockchip,rk3036-usb2phy`, `rockchip,rk3128-usb2phy`, `rockchip,rk3228-usb2phy`, `rockchip,rk3308-usb2phy`, `rockchip,rk3328-usb2phy`, `rockchip,rk3366-usb2phy`, `rockchip,rk3399-usb2phy`, `rockchip,rk3562-usb2phy`, `rockchip,rk3568-usb2phy`, `rockchip,rk3576-usb2phy`, `rockchip,rk3588-usb2phy`, `rockchip,rv1108-usb2phy`. Top-level properties are `compatible`, `reg`, `clock-output-names`, `#clock-cells`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `extcon`, `interrupts`, `resets`, `reset-names`, `rockchip,usbgrf`, `host-port`, `otg-port`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-output-names`, `compatible`, `host-port`, `interrupt-names`, `interrupts`, `otg-port`, `reg`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `assigned-clock-parents`, `assigned-clocks`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `extcon`, `host-port`, `interrupt-names`, `interrupts`, `otg-port`, `phy-supply`, `reg`, `reset-names`, `resets`, `rockchip,usbgrf`. Important numeric/constant limits include `maxItems=1`, `const=0`, `minItems=1`, `maxItems=3`, `const=phyclk`, `const=aclk`, `const=aclk_slv`, `maxItems=2`, `const=phy`, `const=apb`, `const=linestate`, `const=otg-mux`, `const=otg-bvalid`, `const=otg-id`, `minItems=3`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle` conditional branches include `rockchip,rk3568-usb2phy`, `rockchip,rk3588-usb2phy` -> adjusts `host-port`, `interrupts`, `otg-port`, requires `interrupts`; `rockchip,px30-usb2phy`, `rockchip,rk3036-usb2phy`, `rockchip,rk3128-usb2phy`, `rockchip,rk3228-usb2phy`, `rockchip,rk3308-usb2phy`, `rockchip,rk3328-usb2phy`, `rockchip,rk3366-usb2phy`, `rockchip,rk3399-usb2phy`, `rockchip,rk3562-usb2phy`, `rockchip,rk3568-usb2phy`, and 2 more -> adjusts `clock-names`, `clocks`; `rockchip,rk3576-usb2phy` -> adjusts `clock-names`, `clocks`

## State And Persistence
State is static firmware description rather than runtime persistence. assigned-clock properties persist boot-time clock parent/rate choices. Named resources such as `clock-output-names`, `#clock-cells`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `resets`, `reset-names`, `interrupts` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3036.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3128.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk322x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rv1108.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/px30.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3308.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3328.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3399-base.dtsi`, and 2 more. External providers/consumers are signaled through `clock-output-names`, `#clock-cells`, `clocks`, `clock-names`, `assigned-clocks`, `assigned-clock-parents`, `resets`, `reset-names`, `interrupts`, `rockchip,usbgrf`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,px30-usb2phy, rockchip,rk3036-usb2phy, rockchip,rk3128-usb2phy, rockchip,rk3228-usb2phy, rockchip,rk3308-usb2phy, rockchip,rk3328-usb2phy, rockchip,rk3366-usb2phy, rockchip,rk3399-usb2phy, rockchip,rk3562-usb2phy, rockchip,rk3568-usb2phy, rockchip,rk3576-usb2phy, rockchip,rk3588-usb2phy, and 1 more; allOf[0].if.properties.compatible.contains: rockchip,rk3568-usb2phy, rockchip,rk3588-usb2phy; allOf[1].if.properties.compatible.contains: rockchip,px30-usb2phy, rockchip,rk3036-usb2phy, rockchip,rk3128-usb2phy, rockchip,rk3228-usb2phy, rockchip,rk3308-usb2phy, rockchip,rk3328-usb2phy....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,inno-usb2phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,px30-usb2phy`, `rockchip,rk3036-usb2phy`, `rockchip,rk3128-usb2phy`, `rockchip,rk3228-usb2phy`, `rockchip,rk3308-usb2phy`, `rockchip,rk3328-usb2phy`, and 7 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,inno-usb2phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,pcie3-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,pcie3-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,pcie3-phy.yaml` is a Rockchip PHY binding for `Rockchip PCIe v3 phy`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip PCIe v3 phy.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,rk3568-pcie3-phy`, `rockchip,rk3588-pcie3-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `data-lanes`, `#phy-cells`, `resets`, `reset-names`, `phy-supply`, `rockchip,phy-grf`, `rockchip,pipe-grf`, `rockchip,rx-common-refclk-mode`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`, `rockchip,phy-grf`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `data-lanes`, `phy-supply`, `reg`, `reset-names`, `resets`, `rockchip,phy-grf`, `rockchip,pipe-grf`, `rockchip,rx-common-refclk-mode`. Important numeric/constant limits include `maxItems=1`, `minItems=1`, `maxItems=3`, `minItems=2`, `maxItems=16`, `minimum=0`, `maximum=16`, `const=0`, `const=phy`, `maximum=1`, `const=pclk`, `minItems=3`, `const=refclk_m`, `const=refclk_n`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array` conditional branches include `rockchip,rk3588-pcie3-phy` -> adjusts `clock-names`, `clocks`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `phy-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-snps-pcie3.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3568.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3588-extra.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `phy-supply`, `phy-supply`, `rockchip,phy-grf`, `rockchip,pipe-grf`, `rockchip,rx-common-refclk-mode`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,rk3568-pcie3-phy, rockchip,rk3588-pcie3-phy; allOf[0].if.properties.compatible: rockchip,rk3588-pcie3-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,pcie3-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3568-pcie3-phy`, `rockchip,rk3588-pcie3-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,pcie3-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml` is a Rockchip PHY binding for `Rockchip MIPI DPHY with additional LVDS/TTL modes`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip MIPI DPHY with additional LVDS/TTL modes.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,px30-dsi-dphy`, `rockchip,rk3128-dsi-dphy`, `rockchip,rk3368-dsi-dphy`, `rockchip,rk3506-dsi-dphy`, `rockchip,rk3568-dsi-dphy`, `rockchip,rv1126-dsi-dphy`. Top-level properties are `#phy-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`. Important numeric/constant limits include `const=0`, `maxItems=1`, `const=ref`, `const=pclk`, `const=apb`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-dsidphy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3128.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/px30.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3368.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk356x-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,px30-dsi-dphy, rockchip,rk3128-dsi-dphy, rockchip,rk3368-dsi-dphy, rockchip,rk3506-dsi-dphy, rockchip,rk3568-dsi-dphy, rockchip,rv1126-dsi-dphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,px30-dsi-dphy`, `rockchip,rk3128-dsi-dphy`, `rockchip,rk3368-dsi-dphy`, `rockchip,rk3506-dsi-dphy`, `rockchip,rk3568-dsi-dphy`, `rockchip,rv1126-dsi-dphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,px30-dsi-dphy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3228-hdmi-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3228-hdmi-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3228-hdmi-phy.yaml` is a Rockchip PHY binding for `Rockchip HDMI PHY with Innosilicon IP block`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip HDMI PHY with Innosilicon IP block.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,rk3228-hdmi-phy`, `rockchip,rk3328-hdmi-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `clock-output-names`, `#clock-cells`, `interrupts`, `nvmem-cells`, `nvmem-cell-names`, `#phy-cells`. Required properties across the composed schema are `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `interrupts`, `reg`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `interrupts`, `nvmem-cell-names`, `nvmem-cells`, `reg`. Important numeric/constant limits include `maxItems=1`, `maxItems=3`, `const=sysclk`, `const=refoclk`, `const=refpclk`, `const=0`, `const=cpu-version`, `const=rockchip,rk3228-hdmi-phy`, `const=rockchip,rk3328-hdmi-phy`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `rockchip,rk3228-hdmi-phy` -> adjusts `interrupts`; `rockchip,rk3328-hdmi-phy` -> requires `interrupts`

## State And Persistence
State is static firmware description rather than runtime persistence. NVMEM cells provide board/fuse trim data consumed by the driver. Named resources such as `clocks`, `clock-names`, `clock-output-names`, `#clock-cells`, `interrupts` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-hdmi.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk322x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3328.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `clock-output-names`, `#clock-cells`, `interrupts`, `nvmem-cells`, `nvmem-cell-names`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,rk3228-hdmi-phy, rockchip,rk3328-hdmi-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3228-hdmi-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3228-hdmi-phy`, `rockchip,rk3328-hdmi-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3228-hdmi-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3288-dp-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3288-dp-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3288-dp-phy.yaml` is a Rockchip PHY binding for `Rockchip specific extensions to the Analogix Display Port PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip specific extensions to the Analogix Display Port PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `rockchip,rk3288-dp-phy`. Top-level properties are `compatible`, `clocks`, `clock-names`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`. Important numeric/constant limits include `const=rockchip,rk3288-dp-phy`, `maxItems=1`, `const=24m`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dp.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3288.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3288-dp-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3288-dp-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3288-dp-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml` is a Rockchip PHY binding for `Rockchip EMMC PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip EMMC PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `rockchip,rk3399-emmc-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `drive-impedance-ohm`, `rockchip,enable-strobe-pulldown`, `rockchip,output-tapdelay-select`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `drive-impedance-ohm`, `reg`, `rockchip,enable-strobe-pulldown`, `rockchip,output-tapdelay-select`. Important numeric/constant limits include `const=rockchip,rk3399-emmc-phy`, `maxItems=1`, `const=emmcclk`, `maximum=15`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-emmc.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3399-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `rockchip,enable-strobe-pulldown`, `rockchip,output-tapdelay-select`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.drive-impedance-ohm: 33, 40, 50, 66, 100.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3399-emmc-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-emmc-phy.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-typec-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-typec-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-typec-phy.yaml` is a Rockchip PHY binding for `Rockchip Type-C PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip Type-C PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `rockchip,rk3399-typec-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `extcon`, `power-domains`, `resets`, `reset-names`, `rockchip,grf`, `dp-port`, `usb3-port`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `dp-port`, `reg`, `reset-names`, `resets`, `usb3-port`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `dp-port`, `extcon`, `orientation-switch`, `port`, `power-domains`, `reg`, `reset-names`, `resets`, `rockchip,grf`, `usb3-port`. Important numeric/constant limits include `const=rockchip,rk3399-typec-phy`, `maxItems=1`, `maxItems=2`, `const=tcpdcore`, `const=tcpdphy-ref`, `maxItems=3`, `const=uphy`, `const=uphy-pipe`, `const=uphy-tcphy`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-typec.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3399-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `rockchip,grf`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-typec-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3399-typec-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3399-typec-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-hdptx-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-hdptx-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-hdptx-phy.yaml` is a Rockchip PHY binding for `Rockchip SoC HDMI/eDP Transmitter Combo PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip SoC HDMI/eDP Transmitter Combo PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `rockchip,rk3588-hdptx-phy`, `rockchip,rk3576-hdptx-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#phy-cells`, `resets`, `reset-names`, `rockchip,grf`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `rockchip,grf`. All discovered property names, including nested child-node contracts, include `#clock-cells`, `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `rockchip,grf`. Important numeric/constant limits include `const=rockchip,rk3588-hdptx-phy`, `maxItems=1`, `const=ref`, `const=apb`, `const=0`, `minItems=4`, `maxItems=7`, `maxItems=4`, `const=init`, `const=cmn`, `const=lane`, `minItems=7`, `const=phy`, `const=ropll`, `const=lcpll`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle` conditional branches include `rockchip,rk3576-hdptx-phy` -> adjusts `reset-names`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `#clock-cells`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-samsung-hdptx.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3576.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3588-base.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3588-extra.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `#clock-cells`, `resets`, `reset-names`, `rockchip,grf`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0]: rockchip,rk3588-hdptx-phy; properties.compatible.oneOf[1].items[0]: rockchip,rk3576-hdptx-phy; allOf[0].if.properties.compatible.contains: rockchip,rk3576-hdptx-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-hdptx-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3588-hdptx-phy`, `rockchip,rk3576-hdptx-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-hdptx-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-mipi-dcphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-mipi-dcphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-mipi-dcphy.yaml` is a Rockchip PHY binding for `Rockchip MIPI D-/C-PHY with Samsung IP block`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip MIPI D-/C-PHY with Samsung IP block.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,rk3576-mipi-dcphy`, `rockchip,rk3588-mipi-dcphy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `rockchip,grf`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `rockchip,grf`. Important numeric/constant limits include `maxItems=1`, `const=1`, `maxItems=2`, `const=pclk`, `const=ref`, `maxItems=4`, `const=m_phy`, `const=apb`, `const=grf`, `const=s_phy`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-samsung-dcphy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3576.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3588-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `rockchip,grf`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,rk3576-mipi-dcphy, rockchip,rk3588-mipi-dcphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-mipi-dcphy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3576-mipi-dcphy`, `rockchip,rk3588-mipi-dcphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip,rk3588-mipi-dcphy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-inno-csi-dphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-inno-csi-dphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-inno-csi-dphy.yaml` is a Rockchip PHY binding for `Rockchip SoC MIPI RX0 D-PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The Rockchip SoC has a MIPI CSI D-PHY based on an Innosilicon IP which connects to the ISP1 (Image Signal Processing unit v1.0) for CSI cameras..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,px30-csi-dphy`, `rockchip,rk1808-csi-dphy`, `rockchip,rk3326-csi-dphy`, `rockchip,rk3368-csi-dphy`, `rockchip,rk3568-csi-dphy`, `rockchip,rk3588-csi-dphy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`, `power-domains`, `resets`, `reset-names`, `rockchip,grf`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`, `rockchip,grf`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reset-names`, `resets`, `rockchip,grf`. Important numeric/constant limits include `maxItems=1`, `const=pclk`, `const=0`, `minItems=1`, `const=apb`, `const=phy`, `minItems=2`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle` conditional branches include `rockchip,px30-csi-dphy`, `rockchip,rk1808-csi-dphy`, `rockchip,rk3326-csi-dphy`, `rockchip,rk3368-csi-dphy` -> requires `power-domains`; `rockchip,px30-csi-dphy`, `rockchip,rk1808-csi-dphy`, `rockchip,rk3326-csi-dphy`, `rockchip,rk3368-csi-dphy`, `rockchip,rk3568-csi-dphy` -> adjusts `reset-names`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-csidphy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/px30.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk356x-base.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk3588-base.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `rockchip,grf`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,px30-csi-dphy, rockchip,rk1808-csi-dphy, rockchip,rk3326-csi-dphy, rockchip,rk3368-csi-dphy, rockchip,rk3568-csi-dphy, rockchip,rk3588-csi-dphy; allOf[0].if.properties.compatible.contains: rockchip,px30-csi-dphy, rockchip,rk1808-csi-dphy, rockchip,rk3326-csi-dphy, rockchip,rk3368-csi-dphy; allOf[1].if.properties.compatible.contains: rockchip,px30-csi-dphy, rockchip,rk1808-csi-dphy, rockchip,rk3326-csi-dphy, rockchip,rk3368-csi-dphy, rockchip,rk3568-csi-dphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-inno-csi-dphy.yaml` should parse this YAML and validate 2 embedded examples. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,px30-csi-dphy`, `rockchip,rk1808-csi-dphy`, `rockchip,rk3326-csi-dphy`, `rockchip,rk3368-csi-dphy`, `rockchip,rk3568-csi-dphy`, `rockchip,rk3588-csi-dphy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-inno-csi-dphy.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml` is a Rockchip PHY binding for `Rockchip USB2.0 phy`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Rockchip USB2.0 phy.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `rockchip,rk3066a-usb-phy`, `rockchip,rk3188-usb-phy`, `rockchip,rk3288-usb-phy`. Top-level properties are `compatible`, `#address-cells`, `#size-cells`. Required properties across the composed schema are `#address-cells`, `#phy-cells`, `#size-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#address-cells`, `#clock-cells`, `#phy-cells`, `#size-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vbus-supply`. Important numeric/constant limits include `const=1`, `const=0`, `maxItems=1`, `const=phyclk`, `const=phy-reset`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. pattern child nodes include `usb-phy@[0-9a-f]+$`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3066a.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3188.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/rk3288.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: rockchip,rk3066a-usb-phy, rockchip,rk3188-usb-phy, rockchip,rk3288-usb-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `rockchip,rk3066a-usb-phy`, `rockchip,rk3188-usb-phy`, `rockchip,rk3288-usb-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/rockchip-usb-phy.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-hdmi-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-hdmi-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-hdmi-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung Exynos SoC HDMI PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Samsung Exynos SoC HDMI PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 2 accepted compatible forms with values `samsung,exynos4210-hdmiphy`, `samsung,exynos4212-hdmiphy`, `samsung,exynos5-hdmiphy`. Top-level properties are `compatible`, `reg`. Required properties across the composed schema are `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `compatible`, `reg`. Important numeric/constant limits include `const=samsung,exynos5-hdmiphy`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_hdmi.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5250.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0]: samsung,exynos4210-hdmiphy, samsung,exynos4212-hdmiphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-hdmi-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `samsung,exynos4210-hdmiphy`, `samsung,exynos4212-hdmiphy`, `samsung,exynos5-hdmiphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-hdmi-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-pcie-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung SoC series PCIe PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Samsung SoC series PCIe PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `samsung,exynos5433-pcie-phy`. Top-level properties are `#phy-cells`, `compatible`, `reg`, `samsung,pmu-syscon`, `samsung,fsys-sysreg`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`, `samsung,fsys-sysreg`, `samsung,pmu-syscon`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `reg`, `samsung,fsys-sysreg`, `samsung,pmu-syscon`. Important numeric/constant limits include `const=0`, `const=samsung,exynos5433-pcie-phy`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos5433.dtsi`. External providers/consumers are signaled through `samsung,pmu-syscon`, `samsung,fsys-sysreg`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `samsung,exynos5433-pcie-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos2200-eusb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos2200-eusb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos2200-eusb2-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung Exynos2200 eUSB2 phy controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Samsung Exynos2200 eUSB2 phy, based on Synopsys eUSB2 IP block, supports LS/FS/HS usb connectivity..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `samsung,exynos2200-eusb2-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `phys`, `vdd-supply`, `vdda12-supply`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `vdd-supply`, `vdda12-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `phys`, `reg`, `resets`, `vdd-supply`, `vdda12-supply`. Important numeric/constant limits include `maxItems=1`, `const=0`, `const=ref`, `const=bus`, `const=ctrl`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `vdd-supply`, `vdda12-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/phy-snps-eusb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos2200.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `vdd-supply`, `vdda12-supply`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: samsung,exynos2200-eusb2-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos2200-eusb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `samsung,exynos2200-eusb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,exynos2200-eusb2-phy.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,mipi-video-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,mipi-video-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,mipi-video-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung S5P/Exynos SoC MIPI CSIS/DSIM DPHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: For samsung,s5pv210-mipi-video-phy compatible PHYs the second cell in the PHY specifier identifies the PHY and its meaning is as follows:: 0 - MIPI CSIS 0, 1 - MIPI DSIM 0, 2 - MIPI CSIS 1, 3 - MIPI DSIM 1. samsung,exynos5420-mipi-video-phy and samsung,exynos5433-mipi-video-phy support additional fifth PHY:: 4 - MIPI CSIS 2..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `samsung,s5pv210-mipi-video-phy`, `samsung,exynos5420-mipi-video-phy`, `samsung,exynos5433-mipi-video-phy`, `samsung,exynos7870-mipi-video-phy`. Top-level properties are `compatible`, `#phy-cells`, `syscon`, `samsung,pmu-syscon`, `samsung,disp-sysreg`, `samsung,cam0-sysreg`, `samsung,cam1-sysreg`. Required properties across the composed schema are `#phy-cells`, `compatible`, `samsung,cam0-sysreg`, `samsung,cam1-sysreg`, `samsung,disp-sysreg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `samsung,cam0-sysreg`, `samsung,cam1-sysreg`, `samsung,disp-sysreg`, `samsung,pmu-syscon`, `syscon`. Important numeric/constant limits include `const=1`, `const=samsung,exynos5433-mipi-video-phy`, `const=samsung,exynos7870-mipi-video-phy`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle` conditional branches include `samsung,s5pv210-mipi-video-phy`, `samsung,exynos5420-mipi-video-phy` -> adjusts `samsung,cam0-sysreg`, `samsung,cam1-sysreg`, `samsung,disp-sysreg`, `samsung,pmu-syscon`; `samsung,exynos5433-mipi-video-phy` -> adjusts `syscon`, requires `samsung,cam0-sysreg`, `samsung,cam1-sysreg`, `samsung,disp-sysreg`; `samsung,exynos7870-mipi-video-phy` -> adjusts `samsung,cam1-sysreg`, `syscon`, requires `samsung,cam0-sysreg`, `samsung,disp-sysreg`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-mipi-video.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos3250.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5250.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5420.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos5433.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos7870.dtsi`. External providers/consumers are signaled through `samsung,pmu-syscon`, `samsung,disp-sysreg`, `samsung,cam0-sysreg`, `samsung,cam1-sysreg`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: samsung,s5pv210-mipi-video-phy, samsung,exynos5420-mipi-video-phy, samsung,exynos5433-mipi-video-phy, samsung,exynos7870-mipi-video-phy; allOf[0].if.properties.compatible.contains: samsung,s5pv210-mipi-video-phy, samsung,exynos5420-mipi-video-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,mipi-video-phy.yaml` should parse this YAML and validate 2 embedded examples. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `samsung,s5pv210-mipi-video-phy`, `samsung,exynos5420-mipi-video-phy`, `samsung,exynos5433-mipi-video-phy`, `samsung,exynos7870-mipi-video-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,mipi-video-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,ufs-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,ufs-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,ufs-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung SoC series UFS PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Samsung SoC series UFS PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `google,gs101-ufs-phy`, `samsung,exynos7-ufs-phy`, `samsung,exynosautov9-ufs-phy`, `samsung,exynosautov920-ufs-phy`, `tesla,fsd-ufs-phy`. Top-level properties are `#phy-cells`, `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `power-domains`, `samsung,pmu-syscon`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reg-names`, `samsung,pmu-syscon`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `reg-names`, `samsung,pmu-syscon`. Important numeric/constant limits include `const=0`, `maxItems=1`, `const=phy-pma`, `minItems=1`, `maxItems=4`, `const=samsung,exynos7-ufs-phy`, `const=ref_clk`, `const=rx1_symbol_clk`, `const=rx0_symbol_clk`, `const=tx0_symbol_clk`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array` conditional branches include `samsung,exynos7-ufs-phy` -> adjusts `clock-names`, `clocks`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos7.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynosautov9.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynosautov920.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/gs101.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/fsd.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `samsung,pmu-syscon`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: google,gs101-ufs-phy, samsung,exynos7-ufs-phy, samsung,exynosautov9-ufs-phy, samsung,exynosautov920-ufs-phy, tesla,fsd-ufs-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,ufs-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `google,gs101-ufs-phy`, `samsung,exynos7-ufs-phy`, `samsung,exynosautov9-ufs-phy`, `samsung,exynosautov920-ufs-phy`, `tesla,fsd-ufs-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,ufs-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb2-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung S5P/Exynos SoC USB 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The first phandle argument in the PHY specifier identifies the PHY, its meaning is compatible dependent. For the currently supported SoCs (Exynos4210 and Exynos4212) it is as follows:: 0 - USB device ("device"), 1 - USB host ("host"), 2 - HSIC0 ("hsic0"), 3 - HSIC1 ("hsic1"), Exynos3250 has only USB device phy available as phy 0. Exynos4210 and Exynos4212 use mode switching and require that mode switch register is supplied..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `samsung,exynos3250-usb2-phy`, `samsung,exynos4210-usb2-phy`, `samsung,exynos4x12-usb2-phy`, `samsung,exynos5250-usb2-phy`, `samsung,exynos5420-usb2-phy`, `samsung,s5pv210-usb2-phy`. Top-level properties are `compatible`, `clocks`, `clock-names`, `#phy-cells`, `reg`, `samsung,pmureg-phandle`, `samsung,sysreg-phandle`, `vbus-supply`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `samsung,pmureg-phandle`, `samsung,sysreg-phandle`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `samsung,pmureg-phandle`, `samsung,sysreg-phandle`, `vbus-supply`. Important numeric/constant limits include `const=phy`, `const=ref`, `const=1`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle` conditional branches include `samsung,exynos4x12-usb2-phy`, `samsung,exynos5250-usb2-phy`, `samsung,exynos5420-usb2-phy` -> requires `samsung,sysreg-phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `vbus-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos3250.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos4x12.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5250.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos54xx.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s5pv210.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `vbus-supply`, `samsung,pmureg-phandle`, `samsung,sysreg-phandle`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: samsung,exynos3250-usb2-phy, samsung,exynos4210-usb2-phy, samsung,exynos4x12-usb2-phy, samsung,exynos5250-usb2-phy, samsung,exynos5420-usb2-phy, samsung,s5pv210-usb2-phy; allOf[0].if.properties.compatible.contains: samsung,exynos4x12-usb2-phy, samsung,exynos5250-usb2-phy, samsung,exynos5420-usb2-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `samsung,exynos3250-usb2-phy`, `samsung,exynos4210-usb2-phy`, `samsung,exynos4x12-usb2-phy`, `samsung,exynos5250-usb2-phy`, `samsung,exynos5420-usb2-phy`, `samsung,s5pv210-usb2-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb3-drd-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb3-drd-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb3-drd-phy.yaml` is a Samsung/Exynos PHY binding for `Samsung Exynos SoC USB 3.0 DRD PHY USB 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: For samsung,exynos5250-usbdrd-phy and samsung,exynos5420-usbdrd-phy compatible PHYs, the second cell in the PHY specifier identifies the PHY id, which is interpreted as follows:: 0 - UTMI+ type phy, 1 - PIPE3 type phy. For SoCs like Exynos5420 having multiple USB 3.0 DRD PHY controllers, 'usbdrd_phy' nodes should have numbered alias in the aliases node, in the form of usbdrdphyN, N = 0, 1... (depending on number of controllers)..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `google,gs101-usb31drd-phy`, `samsung,exynos2200-usb32drd-phy`, `samsung,exynos5250-usbdrd-phy`, `samsung,exynos5420-usbdrd-phy`, `samsung,exynos5433-usbdrd-phy`, `samsung,exynos7-usbdrd-phy`, `samsung,exynos7870-usbdrd-phy`, `samsung,exynos850-usbdrd-phy`, `samsung,exynos990-usbdrd-phy`, `samsung,exynosautov920-usb31drd-combo-ssphy`, `samsung,exynosautov920-usbdrd-combo-hsphy`, `samsung,exynosautov920-usbdrd-phy`. Top-level properties are `compatible`, `clocks`, `clock-names`, `power-domains`, `#phy-cells`, `phys`, `phy-names`, `port`, `reg`, `reg-names`, `samsung,pmu-syscon`, `vbus-supply`, `vbus-boost-supply`, `pll-supply`, `dvdd-usb20-supply`, `vddh-usb20-supply`, `vdd33-usb20-supply`, `vdda-usbdp-supply`, `vddh-usbdp-supply`, `dvdd-supply`, `vdd18-supply`, `vdd33-supply`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `dvdd-supply`, `dvdd-usb20-supply`, `orientation-switch`, `phy-names`, `phys`, `pll-supply`, `port`, `reg`, `reg-names`, `samsung,pmu-syscon`, `vdd18-supply`, `vdd33-supply`, `vdd33-usb20-supply`, `vdda-usbdp-supply`, `vddh-usb20-supply`, `vddh-usbdp-supply`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `dvdd-supply`, `dvdd-usb20-supply`, `phy-names`, `phys`, `pll-supply`, `port`, `power-domains`, `reg`, `reg-names`, `samsung,pmu-syscon`, `vbus-boost-supply`, `vbus-supply`, `vdd18-supply`, `vdd33-supply`, `vdd33-usb20-supply`, `vdda-usbdp-supply`, `vddh-usb20-supply`, `vddh-usbdp-supply`. Important numeric/constant limits include `minItems=1`, `maxItems=5`, `maxItems=1`, `const=1`, `const=hs`, `maxItems=3`, `const=phy`, `const=pcs`, `const=pma`, `const=google,gs101-usb31drd-phy`, `const=ref`, `const=ctrl_aclk`, `const=ctrl_pclk`, `const=scl_pclk`, `minItems=3`, `minItems=5`, `const=phy_utmi`, `const=phy_pipe`, and 3 more.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-switch-ports.yaml#`, `/schemas/usb/usb-switch.yaml#` conditional branches include `google,gs101-usb31drd-phy` -> adjusts `clock-names`, `clocks`, `reg`, `reg-names`, requires `dvdd-usb20-supply`, `orientation-switch`, `pll-supply`, `port`, `reg-names`, `vdd33-usb20-supply`, `vdda-usbdp-supply`, `vddh-usb20-supply`, `vddh-usbdp-supply`; `samsung,exynos2200-usb32drd-phy` -> adjusts `clock-names`, `clocks`, `reg`, `reg-names`, requires `phy-names`, `phys`; `samsung,exynos5433-usbdrd-phy`, `samsung,exynos7-usbdrd-phy` -> adjusts `clock-names`, `clocks`, `reg`, `reg-names`; `samsung,exynos5250-usbdrd-phy`, `samsung,e...

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology; power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `power-domains`, `vbus-supply`, `vbus-boost-supply`, `pll-supply`, `dvdd-usb20-supply`, `vddh-usb20-supply`, `vdd33-usb20-supply`, `vdda-usbdp-supply`, `vddh-usbdp-supply`, `dvdd-supply`, `vdd18-supply`, `vdd33-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/graph.yaml#/properties/port`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/usb/usb-switch-ports.yaml#`, `/schemas/usb/usb-switch.yaml#`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5-usbdrd.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos5250.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos54xx.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos2200.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos5433.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos7.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos7870.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos850.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos990.dtsi`, and 1 more. External providers/consumers are signaled through `clocks`, `clock-names`, `power-domains`, `vbus-supply`, `vbus-boost-supply`, `pll-supply`, `dvdd-usb20-supply`, `vddh-usb20-supply`, `vdd33-usb20-supply`, `vdda-usbdp-supply`, `vddh-usbdp-supply`, `dvdd-supply`, `vdd18-supply`, `vdd33-supply`, `phy-names`, `samsung,pmu-syscon`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: composition is closed by `unevaluatedProperties: false`. Representative enum constraints: properties.compatible: google,gs101-usb31drd-phy, samsung,exynos2200-usb32drd-phy, samsung,exynos5250-usbdrd-phy, samsung,exynos5420-usbdrd-phy, samsung,exynos5433-usbdrd-phy, samsung,exynos7-usbdrd-phy, samsung,exynos7870-usbdrd-phy, samsung,exynos850-usbdrd-phy, samsung,exynos990-usbdrd-phy, samsung,exynosautov920-usb31drd-combo-ssphy, samsung,exynosautov920-usbdrd-combo-hsphy, samsung,exynosautov920-usbdrd-phy; allOf[1].if.properties.compatible.contains: samsung,exynos2200-usb32drd-phy; allOf[2].if.properties.compatible.contains: samsung,exynos5433-usbdrd-phy, samsung,exynos7-usbdrd-phy; allOf[3].if.propert....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb3-drd-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `google,gs101-usb31drd-phy`, `samsung,exynos2200-usb32drd-phy`, `samsung,exynos5250-usbdrd-phy`, `samsung,exynos5420-usbdrd-phy`, `samsung,exynos5433-usbdrd-phy`, `samsung,exynos7-usbdrd-phy`, and 6 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/samsung,usb3-drd-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-ahci-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-ahci-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-ahci-phy.yaml` is a Socionext UniPhier PHY binding for `Socionext UniPhier AHCI PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This describes the deivcetree bindings for PHY interfaces built into AHCI controller implemented on Socionext UniPhier SoCs..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `socionext,uniphier-pro4-ahci-phy`, `socionext,uniphier-pxs2-ahci-phy`, `socionext,uniphier-pxs3-ahci-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. Important numeric/constant limits include `maxItems=1`, `const=0`, `minItems=1`, `maxItems=2`, `maxItems=6`, `minItems=2`, `const=socionext,uniphier-pro4-ahci-phy`, `const=link`, `const=gio`, `minItems=6`, `const=phy`, `const=pm`, `const=tx`, `const=rx`, `const=socionext,uniphier-pxs2-ahci-phy`, `const=socionext,uniphier-pxs3-ahci-phy`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `socionext,uniphier-pro4-ahci-phy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`; `socionext,uniphier-pxs2-ahci-phy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`; `socionext,uniphier-pxs3-ahci-phy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-ahci.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pro4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pxs2.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-pxs3.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: socionext,uniphier-pro4-ahci-phy, socionext,uniphier-pxs2-ahci-phy, socionext,uniphier-pxs3-ahci-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-ahci-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `socionext,uniphier-pro4-ahci-phy`, `socionext,uniphier-pxs2-ahci-phy`, `socionext,uniphier-pxs3-ahci-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-ahci-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-pcie-phy.yaml` is a Socionext UniPhier PHY binding for `Socionext UniPhier PCIe PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This describes the devicetree bindings for PHY interface built into PCIe controller implemented on Socionext UniPhier SoCs..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `socionext,uniphier-pro5-pcie-phy`, `socionext,uniphier-ld20-pcie-phy`, `socionext,uniphier-pxs3-pcie-phy`, `socionext,uniphier-nx1-pcie-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `socionext,syscon`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `socionext,syscon`. Important numeric/constant limits include `maxItems=1`, `const=0`, `minItems=1`, `maxItems=2`, `const=socionext,uniphier-pro5-pcie-phy`, `minItems=2`, `const=gio`, `const=link`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle` conditional branches include `socionext,uniphier-pro5-pcie-phy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pro5.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-ld20.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-pxs3.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `socionext,syscon`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: socionext,uniphier-pro5-pcie-phy, socionext,uniphier-ld20-pcie-phy, socionext,uniphier-pxs3-pcie-phy, socionext,uniphier-nx1-pcie-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `socionext,uniphier-pro5-pcie-phy`, `socionext,uniphier-ld20-pcie-phy`, `socionext,uniphier-pxs3-pcie-phy`, `socionext,uniphier-nx1-pcie-phy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml` is a Socionext UniPhier PHY binding for `Socionext UniPhier USB2 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This describes the devicetree bindings for PHY interface built into USB2 controller implemented on Socionext UniPhier SoCs. Pro4 SoC has both USB2 and USB3 host controllers, however, this USB3 controller doesn't include its own High-Speed PHY. This needs to specify USB2 PHY instead of USB3 HS-PHY..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `socionext,uniphier-pro4-usb2-phy`, `socionext,uniphier-ld11-usb2-phy`. Top-level properties are `compatible`, `#address-cells`, `#size-cells`. Required properties across the composed schema are `#address-cells`, `#phy-cells`, `#size-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#address-cells`, `#phy-cells`, `#size-cells`, `compatible`, `reg`, `vbus-supply`. Important numeric/constant limits include `const=1`, `const=0`, `minimum=0`, `maximum=3`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. pattern child nodes include `^phy@[0-9]+$`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pro4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-ld11.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: socionext,uniphier-pro4-usb2-phy, socionext,uniphier-ld11-usb2-phy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `socionext,uniphier-pro4-usb2-phy`, `socionext,uniphier-ld11-usb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3hs-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3hs-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3hs-phy.yaml` is a Socionext UniPhier PHY binding for `Socionext UniPhier USB3 High-Speed (HS) PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This describes the devicetree bindings for PHY interfaces built into USB3 controller implemented on Socionext UniPhier SoCs. Although the controller includes High-Speed PHY and Super-Speed PHY, this describes about High-Speed PHY..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `socionext,uniphier-pro5-usb3-hsphy`, `socionext,uniphier-pxs2-usb3-hsphy`, `socionext,uniphier-ld20-usb3-hsphy`, `socionext,uniphier-pxs3-usb3-hsphy`, `socionext,uniphier-nx1-usb3-hsphy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `vbus-supply`, `nvmem-cells`, `nvmem-cell-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `nvmem-cell-names`, `nvmem-cells`, `reg`, `reset-names`, `resets`, `vbus-supply`. Important numeric/constant limits include `maxItems=1`, `const=0`, `minItems=2`, `maxItems=3`, `maxItems=2`, `const=rterm`, `const=sel_t`, `const=hs_i`, `const=socionext,uniphier-pro5-usb3-hsphy`, `const=gio`, `const=link`, `const=phy`, `const=phy-ext`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `socionext,uniphier-pro5-usb3-hsphy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`; `socionext,uniphier-pxs2-usb3-hsphy`, `socionext,uniphier-ld20-usb3-hsphy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`; `socionext,uniphier-pxs3-usb3-hsphy`, `socionext,uniphier-nx1-usb3-hsphy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. NVMEM cells provide board/fuse trim data consumed by the driver; regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `vbus-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3hs.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pro5.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pxs2.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-ld20.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-pxs3.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `vbus-supply`, `nvmem-cells`, `nvmem-cell-names`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: socionext,uniphier-pro5-usb3-hsphy, socionext,uniphier-pxs2-usb3-hsphy, socionext,uniphier-ld20-usb3-hsphy, socionext,uniphier-pxs3-usb3-hsphy, socionext,uniphier-nx1-usb3-hsphy; allOf[1].if.properties.compatible.contains: socionext,uniphier-pxs2-usb3-hsphy, socionext,uniphier-ld20-usb3-hsphy; allOf[2].if.properties.compatible.contains: socionext,uniphier-pxs3-usb3-hsphy, socionext,uniphier-nx1-usb3-hsphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3hs-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `socionext,uniphier-pro5-usb3-hsphy`, `socionext,uniphier-pxs2-usb3-hsphy`, `socionext,uniphier-ld20-usb3-hsphy`, `socionext,uniphier-pxs3-usb3-hsphy`, `socionext,uniphier-nx1-usb3-hsphy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3hs-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3ss-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3ss-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3ss-phy.yaml` is a Socionext UniPhier PHY binding for `Socionext UniPhier USB3 Super-Speed (SS) PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This describes the devicetree bindings for PHY interfaces built into USB3 controller implemented on Socionext UniPhier SoCs. Although the controller includes High-Speed PHY and Super-Speed PHY, this describes about Super-Speed PHY..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `socionext,uniphier-pro4-usb3-ssphy`, `socionext,uniphier-pro5-usb3-ssphy`, `socionext,uniphier-pxs2-usb3-ssphy`, `socionext,uniphier-ld20-usb3-ssphy`, `socionext,uniphier-pxs3-usb3-ssphy`, `socionext,uniphier-nx1-usb3-ssphy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `vbus-supply`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `vbus-supply`. Important numeric/constant limits include `maxItems=1`, `const=0`, `minItems=2`, `maxItems=3`, `maxItems=2`, `const=gio`, `const=link`, `const=phy`, `const=phy-ext`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `socionext,uniphier-pro4-usb3-ssphy`, `socionext,uniphier-pro5-usb3-ssphy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`; `socionext,uniphier-pxs2-usb3-ssphy`, `socionext,uniphier-ld20-usb3-ssphy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`; `socionext,uniphier-pxs3-usb3-ssphy`, `socionext,uniphier-nx1-usb3-ssphy` -> adjusts `clock-names`, `clocks`, `reset-names`, `resets`

## State And Persistence
State is static firmware description rather than runtime persistence. regulator phandles persist the board power topology. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `vbus-supply` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3ss.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pro4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pro5.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/uniphier-pxs2.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-ld20.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/uniphier-pxs3.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `vbus-supply`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples missing or swapped regulator supplies can pass compile-time phandle syntax but break analog bring-up wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: socionext,uniphier-pro4-usb3-ssphy, socionext,uniphier-pro5-usb3-ssphy, socionext,uniphier-pxs2-usb3-ssphy, socionext,uniphier-ld20-usb3-ssphy, socionext,uniphier-pxs3-usb3-ssphy, socionext,uniphier-nx1-usb3-ssphy; allOf[0].if.properties.compatible.contains: socionext,uniphier-pro4-usb3-ssphy, socionext,uniphier-pro5-usb3-ssphy; allOf[1].if.properties.compatible.contains: socionext,uniphier-pxs2-usb3-ssphy, socionext,uniphier-ld20-usb3-ssphy; allOf[2].if.properties.compatible.contains: socionext,uniphier-pxs3-usb3-ssphy, socionext,uniphier-nx1-usb3-ssphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3ss-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `socionext,uniphier-pro4-usb3-ssphy`, `socionext,uniphier-pro5-usb3-ssphy`, `socionext,uniphier-pxs2-usb3-ssphy`, `socionext,uniphier-ld20-usb3-ssphy`, `socionext,uniphier-pxs3-usb3-ssphy`, `socionext,uniphier-nx1-usb3-ssphy` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/socionext,uniphier-usb3ss-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sophgo,cv1800b-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sophgo,cv1800b-usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sophgo,cv1800b-usb2-phy.yaml` is a PHY binding for `Sophgo CV18XX/SG200X USB 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Sophgo CV18XX/SG200X USB 2.0 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `sophgo,cv1800b-usb2-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `resets`. Important numeric/constant limits include `const=sophgo,cv1800b-usb2-phy`, `maxItems=1`, `const=0`, `const=app`, `const=stb`, `const=lpm`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/sophgo/phy-cv1800-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/cv180x.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sophgo,cv1800b-usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `sophgo,cv1800b-usb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sophgo,cv1800b-usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-combo-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-combo-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-combo-phy.yaml` is a PHY binding for `SpacemiT K1 PCIe/USB3 Combo PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Of the three PHYs on the SpacemiT K1 SoC capable of being used for PCIe, one is a combo PHY that can also be configured for use by a USB 3 controller. Using PCIe or USB 3 is a board design decision. The combo PHY is also the only PCIe PHY that is able to determine PCIe calibration values to use, and this must be determined before the other two PCIe PHYs can be used. This calibration must be performed with the combo PHY in PCIe mode, and is this is done when the combo PHY is probed. The combo PHY uses an external oscillator as a reference clock. During normal operation, the PCIe or USB port driver is responsible for ensuring all other clocks needed by a PHY are enabled, and all resets affecting the PHY are deasserted. However, for the combo PHY to....

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `spacemit,k1-combo-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `spacemit,apmu`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `spacemit,apmu`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`, `spacemit,apmu`. Important numeric/constant limits include `const=spacemit,k1-combo-phy`, `const=refclk`, `const=dbi`, `const=mstr`, `const=slv`, `const=phy`, `const=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/riscv/boot/dts/spacemit/k1.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `spacemit,apmu`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-combo-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `spacemit,k1-combo-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-combo-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-pcie-phy.yaml` is a PHY binding for `SpacemiT K1 PCIe PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Two PHYs on the SpacemiT K1 SoC used for only for PCIe. These PHYs must be configured using calibration values that are determined by a third "combo PHY". The combo PHY determines these calibration values during probe so they can be used for the two PCIe-only PHYs. The PHY uses an external oscillator as a reference clock. During normal operation, the PCIe host driver is responsible for ensuring all other clocks needed by a PHY are enabled, and all resets affecting the PHY are deasserted..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `spacemit,k1-pcie-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. Important numeric/constant limits include `const=spacemit,k1-pcie-phy`, `const=refclk`, `const=phy`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/riscv/boot/dts/spacemit/k1.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `spacemit,k1-pcie-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,k1-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,usb2-phy.yaml` is a PHY binding for `SpacemiT K1 SoC USB 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: SpacemiT K1 SoC USB 2.0 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `spacemit,k1-usb2-phy`. Top-level properties are `compatible`, `reg`, `clocks`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clocks`, `compatible`, `reg`. Important numeric/constant limits include `const=spacemit,k1-usb2-phy`, `maxItems=1`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/riscv/boot/dts/spacemit/k1.dtsi`. External providers/consumers are signaled through `clocks`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `spacemit,k1-usb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/spacemit,usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,spear1310-miphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,spear1310-miphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,spear1310-miphy.yaml` is a PHY binding for `ST SPEAr miphy`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: ST Microelectronics SPEAr miphy is a phy controller supporting PCIe and SATA..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `st,spear1310-miphy`, `st,spear1340-miphy`. Top-level properties are `compatible`, `reg`, `misc`, `#phy-cells`, `phy-id`. Required properties across the composed schema are `#phy-cells`, `compatible`, `misc`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `misc`, `phy-id`, `reg`. Important numeric/constant limits include `maxItems=1`, `const=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1310-miphy.c`, `sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1340-miphy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/spear1310.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/spear1340.dtsi`. External providers/consumers are signaled through `phy-id`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: st,spear1310-miphy, st,spear1340-miphy.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,spear1310-miphy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `st,spear1310-miphy`, `st,spear1340-miphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,spear1310-miphy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stih407-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stih407-usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stih407-usb2-phy.yaml` is a PHY binding for `STMicroelectronics STiH407 USB PHY controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The USB picoPHY device is the PHY for both USB2 and USB3 host controllers (when controlling usb2/1.1 devices) available on STiH407 SoC family from STMicroelectronics..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `st,stih407-usb2-phy`. Top-level properties are `compatible`, `st,syscfg`, `resets`, `reset-names`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reset-names`, `resets`, `st,syscfg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `reset-names`, `resets`, `st,syscfg`. Important numeric/constant limits include `const=st,stih407-usb2-phy`, `const=global`, `const=port`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `resets`, `reset-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/st/phy-stih407-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih407-family.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih410.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/stih418.dtsi`. External providers/consumers are signaled through `resets`, `reset-names`, `st,syscfg`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stih407-usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `st,stih407-usb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stih407-usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml` is a PHY binding for `STMicroelectronics STM32MP25 USB3/PCIe COMBOPHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Single lane PHY shared (exclusive) between the USB3 and PCIe controllers. Supports 5Gbit/s for USB3 and PCIe gen2 or 2.5Gbit/s for PCIe gen1..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `st,stm32mp25-combophy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `wakeup-source`, `interrupts`, `access-controllers`, `st,ssc-on`, `st,rx-equalizer`, `st,output-micro-ohms`, `st,output-vswing-microvolt`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reset-names`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `access-controllers`, `clock-names`, `clocks`, `compatible`, `interrupts`, `power-domains`, `reg`, `reset-names`, `resets`, `st,output-micro-ohms`, `st,output-vswing-microvolt`, `st,rx-equalizer`, `st,ssc-on`, `wakeup-source`. Important numeric/constant limits include `const=st,stm32mp25-combophy`, `maxItems=1`, `const=1`, `minItems=2`, `const=apb`, `const=ker`, `const=pad`, `const=phy`, `minimum=0`, `maximum=7`, `minimum=3999000`, `maximum=6090000`, `minimum=442000`, `maximum=803000`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `interrupts` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-combophy.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/st/stm32mp251.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `interrupts`, `st,ssc-on`, `st,rx-equalizer`, `st,output-micro-ohms`, `st,output-vswing-microvolt`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `st,stm32mp25-combophy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/st,stm32mp25-combophy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-rx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-rx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-rx.yaml` is a PHY binding for `StarFive SoC JH7110 MIPI D-PHY Rx Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: StarFive SoCs contain a MIPI CSI D-PHY based on M31 IP, used to transfer CSI camera data..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `starfive,jh7110-dphy-rx`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `power-domains`, `#phy-cells`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `power-domains`, `reg`, `resets`. Important numeric/constant limits include `const=starfive,jh7110-dphy-rx`, `maxItems=1`, `const=cfg`, `const=ref`, `const=tx`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `clocks`, `clock-names`, `resets`, `power-domains` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-rx.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `resets`, `power-domains`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-rx.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `starfive,jh7110-dphy-rx` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-dphy-rx.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-pcie-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-pcie-phy.yaml` is a PHY binding for `StarFive JH7110 PCIe 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: StarFive JH7110 PCIe 2.0 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `starfive,jh7110-pcie-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `starfive,sys-syscon`, `starfive,stg-syscon`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `reg`, `starfive,stg-syscon`, `starfive,sys-syscon`. Important numeric/constant limits include `const=starfive,jh7110-pcie-phy`, `maxItems=1`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle-array`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-pcie.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110.dtsi`. External providers/consumers are signaled through `starfive,sys-syscon`, `starfive,stg-syscon`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-pcie-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `starfive,jh7110-pcie-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-usb-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-usb-phy.yaml` is a PHY binding for `StarFive JH7110 USB 2.0 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: StarFive JH7110 USB 2.0 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `starfive,jh7110-usb-phy`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. Important numeric/constant limits include `const=starfive,jh7110-usb-phy`, `maxItems=1`, `const=0`, `const=125m`, `const=app_125m`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-usb-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `starfive,jh7110-usb-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/starfive,jh7110-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sunplus,sp7021-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sunplus,sp7021-usb2-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sunplus,sp7021-usb2-phy.yaml` is a PHY binding for `Sunplus SP7021 USB 2.0 PHY Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Sunplus SP7021 USB 2.0 PHY Controller.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `sunplus,sp7021-usb2-phy`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `resets`, `#phy-cells`, `nvmem-cell-names`, `nvmem-cells`, `sunplus,disc-vol-addr-off`. Required properties across the composed schema are `#phy-cells`, `clocks`, `compatible`, `nvmem-cell-names`, `nvmem-cells`, `reg`, `reg-names`, `resets`, `sunplus,disc-vol-addr-off`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clocks`, `compatible`, `nvmem-cell-names`, `nvmem-cells`, `reg`, `reg-names`, `resets`, `sunplus,disc-vol-addr-off`. Important numeric/constant limits include `const=sunplus,sp7021-usb2-phy`, `const=phy`, `const=moon4`, `maxItems=1`, `const=0`, `const=disc_vol`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`

## State And Persistence
State is static firmware description rather than runtime persistence. NVMEM cells provide board/fuse trim data consumed by the driver. Named resources such as `clocks`, `resets` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/sunplus/phy-sunplus-usb2.c`. External providers/consumers are signaled through `clocks`, `resets`, `nvmem-cell-names`, `nvmem-cells`, `sunplus,disc-vol-addr-off`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sunplus,sp7021-usb2-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `sunplus,sp7021-usb2-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/sunplus,sp7021-usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,control-phy-otghs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,control-phy-otghs.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,control-phy-otghs.yaml` is a Texas Instruments PHY/control binding for `TI OMAP Control PHY Module`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The TI OMAP Control PHY module is a hardware block within the system control module (SCM) of Texas Instruments OMAP SoCs. It provides centralized control over power, configuration, and auxiliary features for multiple on-chip PHYs. This module is essential for proper PHY operation in power-constrained embedded systems..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `ti,control-phy-otghs`, `ti,control-phy-pcie`, `ti,control-phy-pipe3`, `ti,control-phy-usb2`, `ti,control-phy-usb2-am437`, `ti,control-phy-usb2-dra7`. Top-level properties are `$nodename`, `compatible`, `reg`, `reg-names`. Required properties across the composed schema are `compatible`, `reg`, `reg-names`. All discovered property names, including nested child-node contracts, include `$nodename`, `compatible`, `reg`, `reg-names`. Important numeric/constant limits include `minItems=1`, `maxItems=3`, `const=otghs_control`, `minItems=3`, `const=power`, `const=pcie_pcs`, `const=control_sma`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `ti,control-phy-otghs` -> adjusts `reg-names`; `ti,control-phy-pcie` -> adjusts `reg`, `reg-names`; `ti,control-phy-usb2`, `ti,control-phy-usb2-dra7`, `ti,control-phy-usb2-am437`, `ti,control-phy-pipe3` -> adjusts `reg-names`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-control.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/omap4-l4.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: composition is closed by `unevaluatedProperties: false`. Representative enum constraints: properties.compatible: ti,control-phy-otghs, ti,control-phy-pcie, ti,control-phy-pipe3, ti,control-phy-usb2, ti,control-phy-usb2-am437, ti,control-phy-usb2-dra7; properties.reg-names.items: otghs_control, power, pcie_pcs, control_sma; allOf[0].if.properties.compatible.contains: ti,control-phy-otghs; allOf[1].if.properties.compatible.contains: ti,control-phy-pcie; allOf[2].if.properties.compatible.contains: ti,control-phy-usb2, ti,control-phy-usb2-dra7, ti,control-phy-usb2-am437, ti,control-phy-pipe3.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,control-phy-otghs.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,control-phy-otghs`, `ti,control-phy-pcie`, `ti,control-phy-pipe3`, `ti,control-phy-usb2`, `ti,control-phy-usb2-am437`, `ti,control-phy-usb2-dra7` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,control-phy-otghs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,da830-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,da830-usb-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,da830-usb-phy.yaml` is a Texas Instruments PHY/control binding for `TI DA8xx/OMAP-L1xx/AM18xx USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This device controls the PHY for both the USB 1.1 OHCI and USB 2.0 OTG controllers on DA8xx SoCs. It also requires a "syscon" node with compatible = "ti,da830-cfgchip", "syscon" to access the CFGCHIP2 register..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is ordered fallback `items` sequence with values `ti,da830-usb-phy`. Top-level properties are `compatible`, `#phy-cells`, `clocks`, `clock-names`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`. Important numeric/constant limits include `const=ti,da830-usb-phy`, `const=1`, `maxItems=2`, `const=usb0_clk48`, `const=usb1_clk48`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/clk/davinci/da8xx-cfgchip.c`, `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-da8xx-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/davinci/da850.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,da830-usb-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,da830-usb-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,da830-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,dm8168-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,dm8168-usb-phy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,dm8168-usb-phy.yaml` is a Texas Instruments PHY/control binding for `TI DM8168 USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: TI DM8168 USB PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `ti,dm8168-usb-phy`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `#phy-cells`, `syscon`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reg-names`, `syscon`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reg-names`, `syscon`. Important numeric/constant limits include `const=ti,dm8168-usb-phy`, `maxItems=1`, `const=phy`, `const=refclk`, `const=0`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-dm816x-usb.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/dm816x.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,dm8168-usb-phy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,dm8168-usb-phy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,dm8168-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml` is a Texas Instruments PHY/control binding for `TI Keystone USB PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The main purpose of this PHY driver is to enable the USB PHY reference clock gate on the Keystone SOC for both the USB2 and USB3 PHY. Otherwise it is just an NOP PHY driver. Hence this node is referenced as both the usb2 and usb3 phy node in the USB Glue layer driver node..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `ti,keystone-usbphy`. Top-level properties are `compatible`, `reg`. Required properties across the composed schema are `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `compatible`, `reg`. Important numeric/constant limits include `const=ti,keystone-usbphy`, `maxItems=1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape.

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/keystone-k2e.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/keystone.dtsi`. External providers/consumers are signaled through standard schema properties.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: none beyond compatible or referenced schemas.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,keystone-usbphy` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,keystone-usbphy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml` is a Texas Instruments PHY/control binding for `OMAP USB2 PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: OMAP USB2 PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 3 accepted compatible forms with values `ti,dra7x-usb2`, `ti,dra7x-usb2-phy2`, `ti,am654-usb2`, `ti,omap-usb2`, `ti,am437x-usb2`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `clocks`, `clock-names`, `syscon-phy-power`, `ctrl-module`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `ctrl-module`, `reg`, `syscon-phy-power`. Important numeric/constant limits include `const=ti,am437x-usb2`, `const=ti,omap-usb2`, `maxItems=1`, `const=0`, `minItems=1`, `const=wkupclk`, `const=refclk`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-usb2.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/am437x-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/dra7-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/omap4-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/omap5-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am65-main.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: ti,dra7x-usb2, ti,dra7x-usb2-phy2, ti,am654-usb2; properties.compatible.oneOf[0].items[1]: ti,omap-usb2.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,dra7x-usb2`, `ti,dra7x-usb2-phy2`, `ti,am654-usb2`, `ti,omap-usb2`, `ti,am437x-usb2` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,omap-usb2.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-gmii-sel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-gmii-sel.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-gmii-sel.yaml` is a Texas Instruments PHY/control binding for `CPSW Port's Interface Mode Selection PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: TI am335x/am437x/dra7(am5)/dm814x CPSW3G Ethernet Subsystem supports two 10/100/1000 Ethernet ports with selectable G/MII, RMII, and RGMII interfaces. The interface mode is selected by configuring the MII mode selection register(s) (GMII_SEL) in the System Control Module chapter (SCM). GMII_SEL register(s) and bit fields placement in SCM are different between SoCs while fields meaning is the same. +--------------+ +-------------------------------+ |SCM | | CPSW | | +---------+ | | +--------------------------------+gmii_sel | | | | | | +---------+ | | +----v---+ +--------+ | +--------------+ | |Port 1..<--+-->GMII/MII<-------> | | | | | | | | +--------+ | +--------+ | | | | | | +--------+ | | | | RMII <-------> | +--> | | | | +--------+ | | | | | |....

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `ti,am3352-phy-gmii-sel`, `ti,dra7xx-phy-gmii-sel`, `ti,am43xx-phy-gmii-sel`, `ti,dm814-phy-gmii-sel`, `ti,am654-phy-gmii-sel`, `ti,j7200-cpsw5g-phy-gmii-sel`, `ti,j721e-cpsw9g-phy-gmii-sel`, `ti,j784s4-cpsw9g-phy-gmii-sel`. Top-level properties are `compatible`, `reg`, `#phy-cells`, `ti,qsgmii-main-ports`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `compatible`, `reg`, `ti,qsgmii-main-ports`. Important numeric/constant limits include `maxItems=1`, `minItems=1`, `maxItems=2`, `minimum=1`, `maximum=8`, `const=1`, `maximum=4`, `minItems=2`, `const=2`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32-array` conditional branches include `ti,dra7xx-phy-gmii-sel`, `ti,dm814-phy-gmii-sel`, `ti,am654-phy-gmii-sel`, `ti,j7200-cpsw5g-phy-gmii-sel`, `ti,j721e-cpsw9g-phy-gmii-sel`, `ti,j784s4-cpsw9g-phy-gmii-sel` -> adjusts `#phy-cells`; `ti,j7200-cpsw5g-phy-gmii-sel` -> adjusts `ti,qsgmii-main-ports`; `ti,j721e-cpsw9g-phy-gmii-sel`, `ti,j784s4-cpsw9g-phy-gmii-sel` -> adjusts `ti,qsgmii-main-ports`; `ti,j7200-cpsw5g-phy-gmii-sel`, `ti,j721e-cpsw9g-phy-gmii-sel`, `ti,j784s4-cpsw9g-phy-gmii-sel` -> adjusts `ti,qsgmii-main-ports`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as none must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-gmii-sel.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/am33xx-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/am437x-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/dm814x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/dra7-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am62-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am62a-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am62l-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am62p-j722s-common-main.dtsi`, and 2 more. External providers/consumers are signaled through `ti,qsgmii-main-ports`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: ti,am3352-phy-gmii-sel, ti,dra7xx-phy-gmii-sel, ti,am43xx-phy-gmii-sel, ti,dm814-phy-gmii-sel, ti,am654-phy-gmii-sel, ti,j7200-cpsw5g-phy-gmii-sel, ti,j721e-cpsw9g-phy-gmii-sel, ti,j784s4-cpsw9g-phy-gmii-sel; allOf[0].if.properties.compatible.contains: ti,dra7xx-phy-gmii-sel, ti,dm814-phy-gmii-sel, ti,am654-phy-gmii-sel, ti,j7200-cpsw5g-phy-gmii-sel, ti,j721e-cpsw9g-phy-gmii-sel, ti,j784s4-cpsw9g-phy-gmii-sel; allOf[1].if.properties.compatible.contains: ti,j7200-cpsw5g-phy-gmii-sel; allOf[2].if.properties.compatible.contains: ti,j721e-cpsw9g-phy-gmii-sel, ti,j784s4-cpsw9g-phy-gmii-sel; a....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-gmii-sel.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,am3352-phy-gmii-sel`, `ti,dra7xx-phy-gmii-sel`, `ti,am43xx-phy-gmii-sel`, `ti,dm814-phy-gmii-sel`, `ti,am654-phy-gmii-sel`, `ti,j7200-cpsw5g-phy-gmii-sel`, and 2 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-gmii-sel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-j721e-wiz.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-j721e-wiz.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-j721e-wiz.yaml` is a Texas Instruments PHY/control binding for `TI J721E WIZ (SERDES Wrapper)`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: TI J721E WIZ (SERDES Wrapper).

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `ti,j721e-wiz-16g`, `ti,j721e-wiz-10g`, `ti,j721s2-wiz-10g`, `ti,am64-wiz-10g`, `ti,j7200-wiz-10g`, `ti,j784s4-wiz-10g`. Top-level properties are `compatible`, `power-domains`, `clocks`, `clock-names`, `num-lanes`, `#address-cells`, `#size-cells`, `#reset-cells`, `#clock-cells`, `ranges`, `typec-dir-gpios`, `typec-dir-debounce-ms`, `refclk-dig`, `ti,scm`. Required properties across the composed schema are `#address-cells`, `#clock-cells`, `#reset-cells`, `#size-cells`, `assigned-clock-parents`, `assigned-clocks`, `clock-names`, `clocks`, `compatible`, `num-lanes`, `power-domains`, `ranges`, `ti,scm`. All discovered property names, including nested child-node contracts, include `#address-cells`, `#clock-cells`, `#reset-cells`, `#size-cells`, `assigned-clock-parents`, `assigned-clocks`, `clock-names`, `clock-output-names`, `clocks`, `compatible`, `num-lanes`, `power-domains`, `ranges`, `refclk-dig`, `ti,scm`, `typec-dir-debounce-ms`, `typec-dir-gpios`. Important numeric/constant limits include `maxItems=1`, `minItems=3`, `maxItems=4`, `const=fck`, `const=core_ref_clk`, `const=ext_ref_clk`, `const=core_ref1_clk`, `minimum=1`, `maximum=4`, `const=1`, `minimum=100`, `maximum=1000`, `minItems=2`, `const=0`, `maxItems=2`, `const=ti,j7200-wiz-10g`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle` conditional branches include `ti,j7200-wiz-10g` -> requires `ti,scm` pattern child nodes include `^cmn-refclk1?-dig-div$`, `^pll[0|1]-refclk$`, `^serdes@[0-9a-f]+$`

## State And Persistence
State is static firmware description rather than runtime persistence. power-domain phandles persist the SoC power-island relationship. Named resources such as `power-domains`, `clocks`, `clock-names`, `#clock-cells`, `typec-dir-gpios` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-j721e-wiz.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-am64-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-j7200-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-j721e-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-j721s2-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-j722s-main.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-j784s4-j742s2-main-common.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-j784s4-main.dtsi`. External providers/consumers are signaled through `power-domains`, `clocks`, `clock-names`, `#clock-cells`, `typec-dir-gpios`, `ti,scm`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: ti,j721e-wiz-16g, ti,j721e-wiz-10g, ti,j721s2-wiz-10g, ti,am64-wiz-10g, ti,j7200-wiz-10g, ti,j784s4-wiz-10g.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-j721e-wiz.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,j721e-wiz-16g`, `ti,j721e-wiz-10g`, `ti,j721s2-wiz-10g`, `ti,am64-wiz-10g`, `ti,j7200-wiz-10g`, `ti,j784s4-wiz-10g` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-j721e-wiz.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-usb3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-usb3.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-usb3.yaml` is a Texas Instruments PHY/control binding for `TI PIPE3 PHY Module`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The TI PIPE3 PHY is a high-speed SerDes (Serializer/Deserializer) transceiver integrated in OMAP5, DRA7xx/AM57xx, and similar SoCs. It supports multiple protocols (USB3, SATA, PCIe) using the PIPE3 interface standard, which defines a common physical layer for high-speed serial interfaces..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `ti,omap-usb3`, `ti,phy-pipe3-pcie`, `ti,phy-pipe3-sata`, `ti,phy-usb3`. Top-level properties are `$nodename`, `compatible`, `reg`, `reg-names`, `#phy-cells`, `clocks`, `clock-names`, `syscon-phy-power`, `syscon-pllreset`, `syscon-pcs`, `ctrl-module`. Required properties across the composed schema are `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reg-names`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `$nodename`, `clock-names`, `clocks`, `compatible`, `ctrl-module`, `reg`, `reg-names`, `syscon-pcs`, `syscon-phy-power`, `syscon-pllreset`. Important numeric/constant limits include `minItems=2`, `maxItems=3`, `const=phy_rx`, `const=phy_tx`, `const=pll_ctrl`, `const=0`, `maxItems=7`, `maxItems=1`, `const=ti,phy-pipe3-sata`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array` conditional branches include `ti,phy-pipe3-sata` -> adjusts `syscon-pllreset`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/ti/phy-ti-pipe3.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/dra7-l4.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/omap5-l4.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: composition is closed by `unevaluatedProperties: false`. Representative enum constraints: properties.compatible: ti,omap-usb3, ti,phy-pipe3-pcie, ti,phy-pipe3-sata, ti,phy-usb3; properties.clock-names.items: wkupclk, sysclk, refclk, dpll_ref, dpll_ref_m2, phy-div, div-clk.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-usb3.yaml` should parse this YAML and validate 2 embedded examples. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `ti,omap-usb3`, `ti,phy-pipe3-pcie`, `ti,phy-pipe3-sata`, `ti,phy-usb3` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,phy-usb3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,tcan104x-can.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,tcan104x-can.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,tcan104x-can.yaml` is a Texas Instruments PHY/control binding for `TCAN104x CAN TRANSCEIVER PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: TCAN104x CAN TRANSCEIVER PHY.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `oneOf` with 3 accepted compatible forms with values `microchip,ata6561`, `ti,tcan1051`, `ti,tcan1042`, `ti,tcan1046`, `nxp,tja1048`, `ti,tcan1043`, `nxp,tja1051`, `nxp,tja1057`, `nxp,tjr1443`. Top-level properties are `$nodename`, `compatible`, `#phy-cells`, `silent-gpios`, `standby-gpios`, `enable-gpios`, `max-bitrate`, `mux-states`. Required properties across the composed schema are `#phy-cells`, `compatible`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `$nodename`, `compatible`, `enable-gpios`, `max-bitrate`, `mux-states`, `silent-gpios`, `standby-gpios`. Important numeric/constant limits include `const=ti,tcan1042`, `const=ti,tcan1046`, `const=nxp,tja1048`, `maxItems=1`, `minItems=1`, `maxItems=2`, `minimum=1`, `const=0`, `const=1`, `minItems=2`, `const=nxp,tja1051`, `const=nxp,tja1057`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. Referenced schemas include `/schemas/types.yaml#/definitions/uint32` conditional branches include `nxp,tjr1443`, `ti,tcan1042`, `ti,tcan1043` -> adjusts `#phy-cells`, `silent-gpios`, `standby-gpios`; `nxp,tja1048` -> adjusts `#phy-cells`, `enable-gpios`, `silent-gpios`, `standby-gpios`; `nxp,tja1051` -> adjusts `#phy-cells`, `standby-gpios`; `nxp,tja1057` -> adjusts `#phy-cells`, `enable-gpios`, `standby-gpios`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `silent-gpios`, `standby-gpios`, `enable-gpios` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/phy-can-transceiver.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-evk.dts`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-tx8p-ml81-moduline-display-106.dts`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx91-11x11-frdm-s.dts`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx91-11x11-frdm.dts`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx91-phyboard-segin.dts`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx93-11x11-evk-common.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx93-11x11-frdm.dts`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx93-9x9-qsb-can1.dtso`, and 2 more. External providers/consumers are signaled through `silent-gpios`, `standby-gpios`, `enable-gpios`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible.oneOf[0].items[0]: microchip,ata6561, ti,tcan1051; properties.compatible.oneOf[2]: ti,tcan1042, ti,tcan1043, nxp,tja1048, nxp,tja1051, nxp,tja1057, nxp,tjr1443; properties.#phy-cells: 0, 1; allOf[0].if.properties.compatible: nxp,tjr1443, ti,tcan1042, ti,tcan1043.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,tcan104x-can.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `microchip,ata6561`, `ti,tcan1051`, `ti,tcan1042`, `ti,tcan1046`, `nxp,tja1048`, `ti,tcan1043`, and 3 more against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/ti,tcan104x-can.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/xlnx,zynqmp-psgtr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/xlnx,zynqmp-psgtr.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/xlnx,zynqmp-psgtr.yaml` is a Qualcomm QMP PHY binding for `Xilinx ZynqMP Gigabit Transceiver PHY`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: This binding describes the Xilinx ZynqMP Gigabit Transceiver (GTR) PHY. The GTR provides four lanes and is used by USB, SATA, PCIE, Display port and Ethernet SGMII controllers..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is `enum` list with values `xlnx,zynqmp-psgtr-v1.1`, `xlnx,zynqmp-psgtr`. Top-level properties are `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `xlnx,tx-termination-fix`. Required properties across the composed schema are `#phy-cells`, `compatible`, `reg`, `reg-names`. All discovered property names, including nested child-node contracts, include `#phy-cells`, `clock-names`, `clocks`, `compatible`, `reg`, `reg-names`, `xlnx,tx-termination-fix`. Important numeric/constant limits include `const=4`, `minItems=1`, `maxItems=4`, `const=serdes`, `const=siou`, `const=xlnx,zynqmp-psgtr-v1.1`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after the matching PHY driver probes: it maps registers, enables clocks and supplies, deasserts resets, registers a PHY provider, and lets host controllers acquire the PHY by phandle using the declared `#phy-cells` shape. conditional branches include `xlnx,zynqmp-psgtr-v1.1` -> adjusts `xlnx,tx-termination-fix`

## State And Persistence
State is static firmware description rather than runtime persistence. the binding itself has no mutable state; it constrains static devicetree data. Named resources such as `clocks`, `clock-names` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux generic PHY framework and the consuming USB, PCIe, UFS, SATA, HDMI, DP, DSI, Ethernet, or CAN controller drivers. Schema dependencies are none beyond the core/meta schema. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/phy/xilinx/phy-zynqmp.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/zynqmp.dtsi`. External providers/consumers are signaled through `clocks`, `clock-names`, `xlnx,tx-termination-fix`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately ordered clock/reset names must match the driver data table and DTS examples wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: properties.compatible: xlnx,zynqmp-psgtr-v1.1, xlnx,zynqmp-psgtr.

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/xlnx,zynqmp-psgtr.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `xlnx,zynqmp-psgtr-v1.1`, `xlnx,zynqmp-psgtr` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/xlnx,zynqmp-psgtr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s500-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s500-pinctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s500-pinctrl.yaml` is a Actions Semi S-series pin controller binding for `Actions Semi S500 SoC pinmux & GPIO controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Pinmux & GPIO controller manages pin multiplexing & configuration including GPIO function selection & GPIO attributes configuration. Please refer to pinctrl-bindings.txt in this directory for common binding part and usage..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `actions,s500-pinctrl`. Top-level properties are `compatible`, `reg`, `clocks`, `gpio-controller`, `gpio-ranges`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`. Required properties across the composed schema are `#gpio-cells`, `#interrupt-cells`, `clocks`, `compatible`, `function`, `gpio-controller`, `gpio-ranges`, `groups`, `interrupt-controller`, `interrupts`, `reg`. All discovered property names, including nested child-node contracts, include `#gpio-cells`, `#interrupt-cells`, `bias-pull-down`, `bias-pull-up`, `clocks`, `compatible`, `drive-strength`, `function`, `gpio-controller`, `gpio-ranges`, `groups`, `input-schmitt-disable`, `input-schmitt-enable`, `interrupt-controller`, `interrupts`, `pins`, `reg`. Important numeric/constant limits include `const=actions,s500-pinctrl`, `minItems=1`, `maxItems=1`, `const=2`, `minItems=5`, `maxItems=5`, `maxItems=32`, `maxItems=64`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after a matching pinctrl driver probes: validated child nodes are consumed as state definitions, and client devices select those states through standard `pinctrl-*` properties. Referenced schemas include `pincfg-node.yaml#`, `pinctrl.yaml#`, `pinmux-node.yaml#` pattern child nodes include `-pins$`

## State And Persistence
State is static firmware description rather than runtime persistence. pinctrl child nodes persist mux, bias, drive, and GPIO/IRQ configuration selected by consumers. Named resources such as `clocks`, `gpio-controller`, `gpio-ranges`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux pinctrl, gpiolib, and irqchip/irqdomain frameworks. Schema dependencies are `pincfg-node.yaml#`, `pinctrl.yaml#`, `pinmux-node.yaml#`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s500.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm/boot/dts/actions/owl-s500.dtsi`. External providers/consumers are signaled through `clocks`, `gpio-controller`, `gpio-ranges`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.

## Risks And Edge Cases
strict property closure makes spelling and resource-name drift fail validation immediately wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block function/group enum mistakes can silently route board pins to the wrong peripheral if schema and driver tables diverge Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: patternProperties.-pins$.patternProperties.^(.*-)?pinmux$.properties.groups.items.oneOf[0]: lcd0_d18_mfp, rmii_crs_dv_mfp, rmii_txd0_mfp, rmii_txd1_mfp, rmii_txen_mfp, rmii_rxen_mfp, rmii_rxd1_mfp, rmii_rxd0_mfp, rmii_ref_clk_mfp, i2s_d0_mfp, i2s_pcm1_mfp, i2s0_pcm0_mfp, and 49 more; patternProperties.-pins$.patternProperties.^(.*-)?pinmux$.properties.function: nor, eth_rmii, eth_smii, spi0, spi1, spi2, spi3, sens0, sens1, uart0, uart1, uart2, and 32 more; patternProperties.-pins$.patternProperties.^(.*-)?pinconf$.properties.groups.items.oneOf[0]: sirq_drv, rmii_txd01_txen_drv, rmii_rxer_drv, rmii_crs_drv, rmi....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s500-pinctrl.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `actions,s500-pinctrl` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s500-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s700-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s700-pinctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s700-pinctrl.yaml` is a Actions Semi S-series pin controller binding for `Actions Semi S700 Pin Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Actions Semi S700 Pin Controller.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `actions,s700-pinctrl`. Top-level properties are `compatible`, `reg`, `clocks`, `gpio-controller`, `gpio-line-names`, `gpio-ranges`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`. Required properties across the composed schema are `#gpio-cells`, `#interrupt-cells`, `clocks`, `compatible`, `function`, `gpio-controller`, `gpio-ranges`, `groups`, `interrupt-controller`, `interrupts`, `pinconf`, `pinmux`, `pins`, `reg`. All discovered property names, including nested child-node contracts, include `#gpio-cells`, `#interrupt-cells`, `bias-pull-down`, `bias-pull-up`, `clocks`, `compatible`, `drive-strength`, `function`, `gpio-controller`, `gpio-line-names`, `gpio-ranges`, `groups`, `input-schmitt-disable`, `input-schmitt-enable`, `interrupt-controller`, `interrupts`, `pinconf`, `pinmux`, `pins`, `reg`. Important numeric/constant limits include `const=actions,s700-pinctrl`, `maxItems=1`, `maxItems=136`, `const=2`, `maxItems=5`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after a matching pinctrl driver probes: validated child nodes are consumed as state definitions, and client devices select those states through standard `pinctrl-*` properties. Referenced schemas include `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`

## State And Persistence
State is static firmware description rather than runtime persistence. pinctrl child nodes persist mux, bias, drive, and GPIO/IRQ configuration selected by consumers. Named resources such as `clocks`, `gpio-controller`, `gpio-ranges`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux pinctrl, gpiolib, and irqchip/irqdomain frameworks. Schema dependencies are `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s700.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/actions/s700.dtsi`. External providers/consumers are signaled through `clocks`, `gpio-controller`, `gpio-ranges`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.

## Risks And Edge Cases
wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block function/group enum mistakes can silently route board pins to the wrong peripheral if schema and driver tables diverge Closure rule: additional top-level properties are constrained by a nested schema. Representative enum constraints: additionalProperties.properties.pinmux.properties.groups.items: rgmii_txd23_mfp, rgmii_rxd2_mfp, rgmii_rxd3_mfp, lcd0_d18_mfp, rgmii_txd01_mfp, rgmii_txd0_mfp, rgmii_txd1_mfp, rgmii_txen_mfp, rgmii_rxen_mfp, rgmii_rxd1_mfp, rgmii_rxd0_mfp, rgmii_ref_clk_mfp, and 55 more; additionalProperties.properties.pinmux.properties.function.items: nor, eth_rgmii, eth_sgmii, spi0, spi1, spi2, spi3, seNs0, sens1, uart0, uart1, uart2, and 36 more; additionalProperties.properties.pinconf.properties.groups.items: sirq_drv, rgmii_txd23_drv, rgmii_rxd23_drv, rgmii_txd01_txen_drv, rgmii_rxer_drv, rgmii_crs_drv, rgmii_rxd10_drv, r....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s700-pinctrl.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `actions,s700-pinctrl` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s700-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s900-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s900-pinctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s900-pinctrl.yaml` is a Actions Semi S-series pin controller binding for `Actions Semi S900 Pin Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: Actions Semi S900 Pin Controller.

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `actions,s900-pinctrl`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `clocks`, `gpio-controller`, `gpio-line-names`, `gpio-ranges`, `#gpio-cells`. Required properties across the composed schema are `#gpio-cells`, `#interrupt-cells`, `clocks`, `compatible`, `function`, `gpio-controller`, `gpio-ranges`, `groups`, `interrupt-controller`, `interrupts`, `pins`, `reg`. All discovered property names, including nested child-node contracts, include `#gpio-cells`, `#interrupt-cells`, `bias-bus-hold`, `bias-high-impedance`, `bias-pull-down`, `bias-pull-up`, `clocks`, `compatible`, `drive-strength`, `function`, `gpio-controller`, `gpio-line-names`, `gpio-ranges`, `groups`, `input-schmitt-disable`, `input-schmitt-enable`, `interrupt-controller`, `interrupts`, `pinconf`, `pinmux`, `pins`, `reg`, `slew-rate`. Important numeric/constant limits include `const=actions,s900-pinctrl`, `maxItems=1`, `maxItems=6`, `const=2`, `maxItems=146`.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after a matching pinctrl driver probes: validated child nodes are consumed as state definitions, and client devices select those states through standard `pinctrl-*` properties. Referenced schemas include `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`

## State And Persistence
State is static firmware description rather than runtime persistence. pinctrl child nodes persist mux, bias, drive, and GPIO/IRQ configuration selected by consumers. Named resources such as `clocks`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `gpio-ranges`, `#gpio-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux pinctrl, gpiolib, and irqchip/irqdomain frameworks. Schema dependencies are `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s900.c`. Observed DTS references include `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/actions/s900.dtsi`. External providers/consumers are signaled through `clocks`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `gpio-ranges`, `#gpio-cells`.

## Risks And Edge Cases
wrong register ranges can point the driver at the wrong PHY lane, PLL, or mux block function/group enum mistakes can silently route board pins to the wrong peripheral if schema and driver tables diverge Closure rule: additional top-level properties are constrained by a nested schema. Representative enum constraints: additionalProperties.properties.pinmux.properties.groups.items: lvds_oxx_uart4_mfp, rmii_mdc_mfp, rmii_mdio_mfp, sirq0_mfp, sirq1_mfp, rmii_txd0_mfp, rmii_txd1_mfp, rmii_txen_mfp, rmii_rxer_mfp, rmii_crs_dv_mfp, rmii_rxd1_mfp, rmii_rxd0_mfp, and 49 more; additionalProperties.properties.pinmux.properties.function.items: eram, eth_rmii, eth_smii, spi0, spi1, spi2, spi3, sens0, uart0, uart1, uart2, uart3, and 37 more; additionalProperties.properties.pinconf.properties.groups.items: sgpio3_drv, sgpio2_drv, sgpio1_drv, sgpio0_drv, rmii_tx_d0_d1_drv, rmii_txen_rxer_drv, rmii_crs_dv_drv, rmii_rx_d1_d0_drv, rmii_ref_c....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s900-pinctrl.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `actions,s900-pinctrl` against matching driver OF tables and DTS examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/actions,s900-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,an7583-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,an7583-pinctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,an7583-pinctrl.yaml` is a Airoha AN7583 pin controller binding for `Airoha AN7583 Pin Controller`. It preserves the devicetree ABI for this hardware by constraining compatible matching, provider cells, required board resources, child nodes, and examples. Description signal: The Airoha's AN7583 Pin controller is used to control SoC pins..

## Important APIs, Types, And Functions
The effective API is the schema contract. `compatible` is single `const` with values `airoha,an7583-pinctrl`. Top-level properties are `compatible`, `interrupts`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupt-controller`, `#interrupt-cells`. Required properties across the composed schema are `#gpio-cells`, `#interrupt-cells`, `compatible`, `function`, `gpio-controller`, `groups`, `interrupt-controller`, `interrupts`, `pins`. All discovered property names, including nested child-node contracts, include `#gpio-cells`, `#interrupt-cells`, `bias-disable`, `bias-pull-down`, `bias-pull-up`, `compatible`, `drive-open-drain`, `drive-strength`, `function`, `gpio-controller`, `gpio-ranges`, `groups`, `input-enable`, `interrupt-controller`, `interrupts`, `output-enable`, `output-high`, `output-low`, `pins`. Important numeric/constant limits include `const=airoha,an7583-pinctrl`, `maxItems=1`, `const=2`, `const=pon`, `const=tod_1pps`, `const=sipo`, `const=mdio`, `const=uart`, `maxItems=2`, `const=i2c`, `const=jtag`, `const=pcm`, `const=spi`, `const=pcm_spi`, `maxItems=7`, `const=emmc`, `const=pnand`, `const=pcie_reset`, and 6 more.

## Control Flow
Control flow is declarative JSON-schema evaluation, not imperative code. `dt-doc-validate` and `dt_binding_check` load the YAML, resolve `$ref` links, apply `allOf`/`oneOf`/`if`/`then` composition, validate embedded examples, and `dtbs_check` later applies the same rules to compiled board DTS. Runtime behavior begins after a matching pinctrl driver probes: validated child nodes are consumed as state definitions, and client devices select those states through standard `pinctrl-*` properties. Referenced schemas include `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`, `pinctrl.yaml#` conditional branches include `pon` -> adjusts `groups`; `tod_1pps` -> adjusts `groups`; `sipo` -> adjusts `groups`; `mdio` -> adjusts `groups` pattern child nodes include `-pins$`

## State And Persistence
State is static firmware description rather than runtime persistence. pinctrl child nodes persist mux, bias, drive, and GPIO/IRQ configuration selected by consumers. Named resources such as `interrupts`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupt-controller`, `#interrupt-cells` must stay stable because driver probe, suspend/resume, and board DTS validation depend on their order and names.

## Dependencies And Integration Points
Integrates with Linux pinctrl, gpiolib, and irqchip/irqdomain frameworks. Schema dependencies are `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`, `pinctrl.yaml#`. Observed driver-side references include `sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-airoha.c`. External providers/consumers are signaled through `interrupts`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupt-controller`, `#interrupt-cells`.

## Risks And Edge Cases
conditional compatible branches can reject valid boards or admit invalid resource counts if a new SoC is added to the wrong enum strict property closure makes spelling and resource-name drift fail validation immediately function/group enum mistakes can silently route board pins to the wrong peripheral if schema and driver tables diverge Closure rule: top-level unknown properties are rejected by `additionalProperties: false`. Representative enum constraints: patternProperties.-pins$.patternProperties.^mux(-|$).properties.function: pon, tod_1pps, sipo, mdio, uart, i2c, jtag, pcm, spi, pcm_spi, i2s, emmc, and 11 more; patternProperties.-pins$.patternProperties.^mux(-|$).allOf[0].then.properties.groups: pon; patternProperties.-pins$.patternProperties.^mux(-|$).allOf[1].then.properties.groups: pon_tod_1pps, gsw_tod_1pps; patternProperties.-pins$.patternProperties.^mux(-|$).allOf[2].then.properties.groups: sipo, sipo_rclk; patternProperties.-pins$.patternProperties.^mux(-|$).allOf[3].then.properties.groups: mdio; patternProperties.-pins$.patternProperties.^mux(-|$).all....

## Test Signals
`make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,an7583-pinctrl.yaml` should parse this YAML and validate 1 embedded example. `make dtbs_check` should validate board DTS nodes using the compatible strings and resource names from this schema. spot-check representative compatibles such as `airoha,an7583-pinctrl` against matching driver OF tables and DTS examples. exercise both sides of the conditional branches by validating DTS snippets for the affected SoC compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,an7583-pinctrl.yaml -->
