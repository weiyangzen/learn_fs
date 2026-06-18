<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson6-spifc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson6-spifc.yaml

## Purpose
Devicetree binding schema for Amlogic Meson SPI Flash Controller in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,meson6-spifc`, `amlogic,meson-gxbb-spifc`. The schema description narrows this to: The Meson SPIFC is a controller optimized for communication with SPI NOR memories, without DMA support and a 64-byte unified transmit / receive buffer.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Neil Armstrong <neil.armstrong@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,meson6-spifc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson6-spifc.yaml -->
