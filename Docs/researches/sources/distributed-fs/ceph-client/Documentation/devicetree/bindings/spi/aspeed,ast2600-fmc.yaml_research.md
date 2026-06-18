<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/aspeed,ast2600-fmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/aspeed,ast2600-fmc.yaml

## Purpose
Devicetree binding schema for Aspeed SMC controllers in the Linux SPI subsystem. It documents and validates nodes matched by `aspeed,ast2700-fmc`, `aspeed,ast2700-spi`, `aspeed,ast2600-fmc`, `aspeed,ast2600-spi`, `aspeed,ast2500-fmc`, `aspeed,ast2500-spi`, and 2 more compatible strings. The schema description narrows this to: This binding describes the Aspeed Static Memory Controllers (FMC and SPI) of the AST2400, AST2500, AST2600 and AST2700 SOCs.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Chin-Ting Kuo <chin-ting_kuo@aspeedtech.com>, Cédric Le Goater <clg@kaod.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/aspeed,ast2600-fmc.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/aspeed,ast2600-fmc.yaml -->
