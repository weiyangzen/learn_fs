<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/adi,axi-spi-engine.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/adi,axi-spi-engine.yaml

## Purpose
Devicetree binding schema for Analog Devices AXI SPI Engine Controller in the Linux SPI subsystem. It documents and validates nodes matched by `adi,axi-spi-engine-1.00.a`. The schema description narrows this to: The AXI SPI Engine controller is part of the SPI Engine framework[1] and allows memory mapped access to the SPI Engine control bus. This allows it to be used as a general purpose software driven SPI controller as well as some optional advanced acceleration and offloading capabilities. [1] https://wiki.analog.com/resources/fpga/peripherals/spi_engine

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `trigger-sources`, `dmas`, `dma-names`, `spi-rx-bus-width`, `spi-tx-bus-width`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^.*@[0-9a-f]+`.
- External schema APIs: `/schemas/spi/spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`; pattern-matched child/property blocks include `^.*@[0-9a-f]+`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `/schemas/spi/spi-controller.yaml#`. Maintainer metadata routes binding review to Michael Hennerich <Michael.Hennerich@analog.com>, Nuno Sá <nuno.sa@analog.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clocks`, `clock-names`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/adi,axi-spi-engine.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/adi,axi-spi-engine.yaml -->
