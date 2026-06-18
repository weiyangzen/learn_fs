# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/arasan,cf-spear1340.yaml

## Purpose
Device-tree schema for Arasan PATA Compact Flash Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Viresh Kumar <viresh.kumar@linaro.org> and gives dt-schema a canonical contract for nodes matching `arasan,cf-spear1340`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const arasan,cf-spear1340), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `dmas` (items ?..1), `dma-names`, `arasan,broken-udma` (UDMA mode is unusable), `arasan,broken-mwdma` (MWDMA mode is unusable), `arasan,broken-pio` (PIO mode is unusable). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/arasan,cf-spear1340.yaml`
- run `make dtbs_check` on DTS files using `arasan,cf-spear1340`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
