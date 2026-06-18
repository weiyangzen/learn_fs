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
