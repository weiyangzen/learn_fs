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
