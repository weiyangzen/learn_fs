<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl-imx-cspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl-imx-cspi.yaml

## Purpose
Devicetree binding schema for Freescale (Enhanced) Configurable Serial Peripheral Interface (CSPI/eCSPI) for i.MX in the Linux SPI subsystem. It documents and validates nodes matched by `fsl,imx1-cspi`, `fsl,imx21-cspi`, `fsl,imx27-cspi`, `fsl,imx31-cspi`, `fsl,imx35-cspi`, `fsl,imx51-ecspi`, and 16 more compatible strings.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `fsl,spi-rdy-drctl`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Shawn Guo <shawnguo@kernel.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl-imx-cspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl-imx-cspi.yaml -->
