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
