# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,pq-sata.yaml

## Purpose
SATA nodes are defined to describe on-chip Serial ATA controllers. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by J. Neuschfer <j.ne@posteo.net> and gives dt-schema a canonical contract for nodes matching `fsl,mpc8377-sata`, `fsl,mpc8536-sata`, `fsl,mpc8315-sata`, `fsl,mpc8379-sata`, `fsl,pq-sata`, `fsl,pq-sata-v2`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `cell-index` (ref uint32; enum 1, 2, 3, 4). Required properties are `compatible`, `interrupts`, `cell-index`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32, example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/fsl,pq-sata.yaml`
- run `make dtbs_check` on DTS files using `fsl,mpc8377-sata`, `fsl,mpc8536-sata`, `fsl,mpc8315-sata`, `fsl,mpc8379-sata`, `fsl,pq-sata`, `fsl,pq-sata-v2`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
