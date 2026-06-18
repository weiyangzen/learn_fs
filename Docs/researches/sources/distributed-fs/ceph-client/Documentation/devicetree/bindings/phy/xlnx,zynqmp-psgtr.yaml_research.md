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
