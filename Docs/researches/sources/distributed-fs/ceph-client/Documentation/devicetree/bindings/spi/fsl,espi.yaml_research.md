<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,espi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,espi.yaml

## Purpose
Devicetree binding schema for Freescale eSPI (Enhanced Serial Peripheral Interface) controller in the Linux SPI subsystem. It documents and validates nodes matched by `fsl,mpc8536-espi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `fsl,espi-num-chipselects`, `fsl,csbef`, `fsl,csaft`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/types.yaml#/definitions/uint32`, `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `fsl,espi-num-chipselects`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/types.yaml#/definitions/uint32`, `spi-controller.yaml#`. Maintainer metadata routes binding review to J. Neuschäfer <j.ne@posteo.net>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `fsl,espi-num-chipselects`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/fsl,espi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/fsl,espi.yaml -->
