# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cavium,ebt3000-compact-flash.yaml

## Purpose
The Cavium Compact Flash device is connected to the Octeon Boot Bus, and is thus a child of the Boot Bus device. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Rob Herring <robh@kernel.org> and gives dt-schema a canonical contract for nodes matching `cavium,ebt3000-compact-flash`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const cavium,ebt3000-compact-flash), `reg` (The base address of the CF chip select banks.), `cavium,bus-width` (ref uint32; enum 8, 16), `cavium,true-ide` (True IDE mode when present.), `cavium,dma-engine-handle` (ref phandle; A phandle for the DMA Engine connected to this device.). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/cavium,ebt3000-compact-flash.yaml`
- run `make dtbs_check` on DTS files using `cavium,ebt3000-compact-flash`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
