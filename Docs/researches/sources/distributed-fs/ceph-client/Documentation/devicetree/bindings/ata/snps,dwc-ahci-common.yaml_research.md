# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/snps,dwc-ahci-common.yaml

## Purpose
This document defines device tree schema for the generic Synopsys DWC AHCI controller properties. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Serge Semin <fancer.lancer@gmail.com> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items 1..6; Basic DWC AHCI SATA clock sources like application AXI/AHB BIU clock, PM-alive clock, RxOOB detectio), `clock-names` (items 1..6), `resets` (items 1..4; At least basic application and reference clock domains resets are normally supported by the DWC AHCI), `reset-names` (items 1..4). Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), child-node patterns `^sata-port@[0-9a-e]$`, local `$defs` entries `dwc-ahci-port`. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs #/$defs/dwc-ahci-port, /schemas/ata/ahci-common.yaml#/$defs/ahci-port, /schemas/types.yaml#/definitions/uint32, ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/snps,dwc-ahci-common.yaml`
- run `make dtbs_check` on DTS files using `snps,dwc-ahci-common` nodes
- coverage depends on in-tree DTS users because this binding has no embedded example block
