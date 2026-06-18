# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/renesas,rcar-sata.yaml

## Purpose
Device-tree schema for Renesas R-Car Serial-ATA Interface. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Geert Uytterhoeven <geert+renesas@glider.be> and gives dt-schema a canonical contract for nodes matching `renesas,sata-r8a7779`, `renesas,sata-r8a7742`, `renesas,sata-r8a7790-es1`, `renesas,sata-r8a7790`, `renesas,sata-r8a7791`, `renesas,sata-r8a7793`, `renesas,rcar-gen2-sata`, `renesas,sata-r8a774b1`, `renesas,sata-r8a774e1`, `renesas,sata-r8a7795`, plus 2 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `resets` (items ?..1), `iommus` (items ?..1), `power-domains` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/r8a7791-cpg-mssr.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/power/r8a7791-sysc.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/renesas,rcar-sata.yaml`
- run `make dtbs_check` on DTS files using `renesas,sata-r8a7779`, `renesas,sata-r8a7742`, `renesas,sata-r8a7790-es1`, `renesas,sata-r8a7790`, `renesas,sata-r8a7791`, `renesas,sata-r8a7793`, `renesas,rcar-gen2-sata`, `renesas,sata-r8a774b1`, `renesas,sata-r8a774e1`, `renesas,sata-r8a7795`, plus 2 more
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
