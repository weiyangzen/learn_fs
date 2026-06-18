# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/sata_highbank.yaml

## Purpose
The Calxeda SATA controller mostly conforms to the AHCI interface with some special extensions to add functionality, to map GPIOs for activity LEDs and for mapping the ComboPHYs. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Andre Przywara <andre.przywara@arm.com> and gives dt-schema a canonical contract for nodes matching `calxeda,hb-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const calxeda,hb-ahci), `reg` (items ?..1), `interrupts` (items ?..1), `dma-coherent`, `calxeda,pre-clocks` (ref uint32; Indicates the number of additional clock cycles to transmit before sending an SGPIO pattern.), `calxeda,post-clocks` (ref uint32; Indicates the number of additional clock cycles to transmit after sending an SGPIO pattern.), `calxeda,led-order` (ref uint32-array; items 1..8), `calxeda,port-phys` (ref phandle-array; items 1..8), `calxeda,tx-atten` (ref uint32-array; items 1..8), `calxeda,sgpio-gpio` (items ?..3; phandle-gpio bank, bit offset, and default on or off, which indicates that the driver supports SGPIO). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/sata_highbank.yaml`
- run `make dtbs_check` on DTS files using `calxeda,hb-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
