<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spifc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spifc.yaml

## Purpose
Devicetree binding schema for SPI flash controller for Amlogic ARM SoCs in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,a4-spifc`. The schema description narrows this to: The Amlogic SPI flash controller is an extended version of the Amlogic NAND flash controller. It supports SPI Nor Flash and SPI NAND Flash(where the Host ECC HW engine could be enabled).

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `amlogic,rx-adj`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Liang Yang <liang.yang@amlogic.com>, Feng Chen <feng.chen@amlogic.com>, Xianwei Zhao <xianwei.zhao@amlogic.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,a4-spifc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,a4-spifc.yaml -->
