# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/marvell,orion-sata.yaml

## Purpose
Device-tree schema for Marvell Orion SATA. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Andrew Lunn <andrew@lunn.ch>, Gregory Clement <gregory.clement@bootlin.com> and gives dt-schema a canonical contract for nodes matching `marvell,orion-sata`, `marvell,armada-370-sata`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum marvell,orion-sata, marvell,armada-370-sata), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items 1..8), `clock-names` (items 1..?), `phys` (items 1..8), `phy-names` (items 1..?), `nr-ports` (ref uint32; Number of SATA ports in use.). Required properties are `compatible`, `reg`, `interrupts`, `nr-ports`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32, sata-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/marvell,orion-sata.yaml`
- run `make dtbs_check` on DTS files using `marvell,orion-sata`, `marvell,armada-370-sata`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
