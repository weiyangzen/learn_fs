# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/st,ahci.yaml

## Purpose
Device-tree schema for STMicroelectronics STi SATA controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Patrice Chotard <patrice.chotard@foss.st.com> and gives dt-schema a canonical contract for nodes matching `st,ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const st,ahci), `clocks` (items ?..1), `clock-names`, `resets`, `reset-names`, `interrupt-names`. Required properties are `compatible`, `interrupt-names`, `phys`, `phy-names`, `clocks`, `clock-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs ahci-common.yaml#, example includes dt-bindings/clock/stih407-clks.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/phy/phy.h, dt-bindings/reset/stih407-resets.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/st,ahci.yaml`
- run `make dtbs_check` on DTS files using `st,ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
