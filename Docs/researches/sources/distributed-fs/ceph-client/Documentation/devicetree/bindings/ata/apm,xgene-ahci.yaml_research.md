# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/apm,xgene-ahci.yaml

## Purpose
Device-tree schema for APM X-Gene 6.0 Gb/s SATA host controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Rob Herring <robh@kernel.org> and gives dt-schema a canonical contract for nodes matching `apm,xgene-ahci`, `apm,xgene-ahci-v2`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum apm,xgene-ahci, apm,xgene-ahci-v2), `reg` (items 4..?), `interrupts` (items ?..1), `clocks` (items ?..1). Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/apm,xgene-ahci.yaml`
- run `make dtbs_check` on DTS files using `apm,xgene-ahci`, `apm,xgene-ahci-v2`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
