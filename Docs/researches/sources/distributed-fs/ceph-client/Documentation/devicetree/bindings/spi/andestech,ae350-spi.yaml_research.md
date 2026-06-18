<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/andestech,ae350-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/andestech,ae350-spi.yaml

## Purpose
Devicetree binding schema for Andes ATCSPI200 SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `andestech,qilai-spi`, `andestech,ae350-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `num-cs`, `dmas`, `dma-names`, `spi-rx-bus-width`, `spi-tx-bus-width`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `@[0-9a-f]+$`.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `dmas`, `dma-names`; pattern-matched child/property blocks include `@[0-9a-f]+$`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to CL Wang <cl634@andestech.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `dmas`, `dma-names`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files; chip-select numbering and child-node address cells must match controller hardware and SPI core expectations.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/andestech,ae350-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/andestech,ae350-spi.yaml -->
