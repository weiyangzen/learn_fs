# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/rockchip,dwc-ahci.yaml

## Purpose
This document defines device tree bindings for the Synopsys DWC implementation of the AHCI SATA controller found in Rockchip devices. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Serge Semin <fancer.lancer@gmail.com> and gives dt-schema a canonical contract for nodes matching `rockchip,rk3568-dwc-ahci`, `rockchip,rk3576-dwc-ahci`, `rockchip,rk3588-dwc-ahci`, `snps,dwc-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `ports-implemented` (const 1), `power-domains` (items ?..1), `sata-port@0` (ref dwc-ahci-port). Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `ports-implemented`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 2 conditional `if` branch(es), child-node patterns `^sata-port@[1-9a-e]$`. Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/ata/snps,dwc-ahci-common.yaml#/$defs/dwc-ahci-port, snps,dwc-ahci-common.yaml#, example includes dt-bindings/ata/ahci.h, dt-bindings/clock/rockchip,rk3588-cru.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/phy/phy.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/rockchip,dwc-ahci.yaml`
- run `make dtbs_check` on DTS files using `rockchip,rk3568-dwc-ahci`, `rockchip,rk3576-dwc-ahci`, `rockchip,rk3588-dwc-ahci`, `snps,dwc-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
