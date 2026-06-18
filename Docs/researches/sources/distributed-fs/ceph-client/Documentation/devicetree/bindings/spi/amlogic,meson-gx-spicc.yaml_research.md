<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson-gx-spicc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson-gx-spicc.yaml

## Purpose
Devicetree binding schema for Amlogic Meson SPI Communication Controller in the Linux SPI subsystem. It documents and validates nodes matched by `amlogic,meson-gx-spicc`, `amlogic,meson-axg-spicc`, `amlogic,meson-g12a-spicc`. The schema description narrows this to: The Meson SPICC is a generic SPI controller for general purpose Full-Duplex communications with dedicated 16 words RX/TX PIO FIFOs.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `interrupts`, `reg`, `resets`, `clocks`, `clock-names`, `pinctrl-0`, `pinctrl-1`, `pinctrl-2`, `pinctrl-names`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 3 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; conditional branches include 2 `if`, 2 `then`, 1 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `interrupts`, `reg`, `resets`, `clocks`, `clock-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Neil Armstrong <neil.armstrong@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/amlogic,meson-gx-spicc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/amlogic,meson-gx-spicc.yaml -->
