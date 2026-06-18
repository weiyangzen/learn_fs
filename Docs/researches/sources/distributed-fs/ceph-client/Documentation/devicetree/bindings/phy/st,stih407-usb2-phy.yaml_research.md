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
