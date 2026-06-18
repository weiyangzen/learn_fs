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
