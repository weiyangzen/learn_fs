# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/eswin,eic7700-ahci.yaml

## Purpose
AHCI SATA controller embedded into the EIC7700 SoC is based on the DWC AHCI SATA v5.00a IP core. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Yulin Lu <luyulin@eswincomputing.com>, Huan He <hehuan1@eswincomputing.com> and gives dt-schema a canonical contract for nodes matching `eswin,eic7700-ahci`, `snps,dwc-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `clocks` (items 2..2), `clock-names`, `resets` (items ?..1), `reset-names` (const arst), `ports-implemented` (const 1). Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `ports-implemented`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs snps,dwc-ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/eswin,eic7700-ahci.yaml`
- run `make dtbs_check` on DTS files using `eswin,eic7700-ahci`, `snps,dwc-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
