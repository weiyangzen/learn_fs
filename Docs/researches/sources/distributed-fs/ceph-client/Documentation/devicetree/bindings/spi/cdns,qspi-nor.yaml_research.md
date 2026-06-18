<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor.yaml

## Purpose
Devicetree binding schema for Cadence Quad/Octal SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `amd,pensando-elba-qspi`, `amd,versal2-ospi`, `intel,lgm-qspi`, `intel,socfpga-qspi`, `mobileye,eyeq5-ospi`, `starfive,jh7110-qspi`, and 6 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `cdns,fifo-depth`, `cdns,fifo-width`, `cdns,trigger-address`, `cdns,is-decoded-cs`, `cdns,rclk-en`, `power-domains`, `resets`, `reset-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^flash@[0-9a-f]+$`.
- External schema APIs: `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `cdns,qspi-nor-peripheral-props.yaml`.

## Control flow
The schema control flow is declarative: validation first composes 5 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `#address-cells`, `#size-cells`; pattern-matched child/property blocks include `^flash@[0-9a-f]+$`; conditional branches include 2 `oneOf`, 4 `if`, 4 `then`, 3 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `cdns,qspi-nor-peripheral-props.yaml`. Maintainer metadata routes binding review to Vaishnav Achath <vaishnav.a@ti.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `#address-cells`, `#size-cells`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/cdns,qspi-nor.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/cdns,qspi-nor.yaml -->
