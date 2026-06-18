# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-common.yaml

## Purpose
This document defines device tree properties for a common AHCI SATA controller implementation. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Hans de Goede <hdegoede@redhat.com>, Damien Le Moal <dlemoal@kernel.org> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `reg` (Generic AHCI registers space conforming to the Serial ATA AHCI specification.), `reg-names` (CSR space IDs), `interrupts` (items 1..32; Generic AHCI state change interrupt.), `phys` (items ?..1; Reference to the SATA PHY node), `phy-names` (const sata-phy), `ports-implemented` (ref uint32; Mask that indicates which ports the HBA supports.), `hba-cap` (ref uint32; Bitfield of the HBA generic platform capabilities like Staggered Spin-up or Mechanical Presence Swit), `ahci-supply` (Power regulator for AHCI controller), `target-supply` (Power regulator for SATA target device), `phy-supply` (Power regulator for SATA PHY). Required properties are `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), child-node patterns `^sata-port@[0-9a-f]+$`, local `$defs` entries `ahci-port`. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs #/$defs/ahci-port, /schemas/ata/sata-common.yaml#/$defs/sata-port, /schemas/types.yaml#/definitions/uint32, sata-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ahci-common.yaml`
- run `make dtbs_check` on DTS files using `ahci-common` nodes
- coverage depends on in-tree DTS users because this binding has no embedded example block
