# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-platform.yaml

## Purpose
SATA nodes are defined to describe on-chip Serial ATA controllers. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Hans de Goede <hdegoede@redhat.com>, Jens Axboe <axboe@kernel.dk> and gives dt-schema a canonical contract for nodes matching `brcm,iproc-ahci`, `marvell,armada-8k-ahci`, `marvell,berlin2-ahci`, `marvell,berlin2q-ahci`, `qcom,apq8064-ahci`, `qcom,ipq806x-ahci`, `socionext,uniphier-pro4-ahci`, `socionext,uniphier-pxs2-ahci`, `socionext,uniphier-pxs3-ahci`, `cavium,octeon-7130-ahci`, plus 3 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items 1..2), `reg-names` (items ?..1), `interrupts` (items ?..1), `clocks` (items 1..5), `clock-names` (items 1..5), `resets` (items 1..3), `power-domains` (items ?..1), `iommus` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 3 conditional `if` branch(es), child-node patterns `^sata-port@[0-9a-f]+$`. Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/ata/ahci-common.yaml#/$defs/ahci-port, ahci-common.yaml#, example includes dt-bindings/ata/ahci.h, dt-bindings/clock/berlin2q.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ahci-platform.yaml`
- run `make dtbs_check` on DTS files using `brcm,iproc-ahci`, `marvell,armada-8k-ahci`, `marvell,berlin2-ahci`, `marvell,berlin2q-ahci`, `qcom,apq8064-ahci`, `qcom,ipq806x-ahci`, `socionext,uniphier-pro4-ahci`, `socionext,uniphier-pxs2-ahci`, `socionext,uniphier-pxs3-ahci`, `cavium,octeon-7130-ahci`, plus 3 more
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
