# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ceva,ahci-1v84.yaml

## Purpose
The Ceva SATA controller mostly conforms to the AHCI interface with some special extensions to add functionality, is a high-performance dual-port SATA host controller with an AHCI compliant command layer which supports advanced features such as native command  It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Radhey Shyam Pandey <radhey.shyam.pandey@amd.com> and gives dt-schema a canonical contract for nodes matching `ceva,ahci-1v84`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const ceva,ahci-1v84), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `resets` (items ?..1), `phys` (items ?..1), `phy-names`, `dma-coherent`, `iommus` (items ?..4), `power-domains` (items ?..1), plus 2 more. Required properties are `compatible`, `reg`, `clocks`, `interrupts`, `ceva,p0-cominit-params`, `ceva,p0-comwake-params`, `ceva,p0-burst-params`, `ceva,p0-retry-params`, `ceva,p1-cominit-params`, `ceva,p1-comwake-params`, `ceva,p1-burst-params`, `ceva,p1-retry-params`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/flag, /schemas/types.yaml#/definitions/uint16-array, /schemas/types.yaml#/definitions/uint8-array, example includes dt-bindings/interrupt-controller/irq.h, dt-bindings/phy/phy.h, dt-bindings/power/xlnx-zynqmp-power.h, dt-bindings/reset/xlnx-zynqmp-resets.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ceva,ahci-1v84.yaml`
- run `make dtbs_check` on DTS files using `ceva,ahci-1v84`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
