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
