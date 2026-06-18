# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/pata-common.yaml

## Purpose
This document defines device tree properties common to most Parallel ATA (PATA, also known as IDE) AT attachment storage devices. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `#address-cells` (const 1), `#size-cells` (const 0). Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^ide-port@[0-1]$`. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/pata-common.yaml`
- run `make dtbs_check` on DTS files using `pata-common` nodes
- coverage depends on in-tree DTS users because this binding has no embedded example block
