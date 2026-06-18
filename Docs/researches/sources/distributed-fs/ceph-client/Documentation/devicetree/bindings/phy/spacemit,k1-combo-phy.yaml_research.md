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
