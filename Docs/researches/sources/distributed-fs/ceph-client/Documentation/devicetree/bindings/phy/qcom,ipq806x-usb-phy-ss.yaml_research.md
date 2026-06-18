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
