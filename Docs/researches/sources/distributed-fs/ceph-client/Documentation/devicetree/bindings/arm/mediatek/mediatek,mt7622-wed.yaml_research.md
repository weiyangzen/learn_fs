<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-wed.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-wed.yaml

## Purpose
This schema describes MediaTek Wireless Ethernet Dispatch controllers, which offload Ethernet-to-WLAN traffic and interact with WLAN DMA queues and PCIe interrupts.

## Important APIs, Types, And Functions
Compatible strings cover `mediatek,mt7622-wed`, `mt7981-wed`, `mt7986-wed`, and `mt7988-wed`, each followed by `syscon`. Required properties are `reg` and `interrupts`; newer variants may use five `memory-region` phandles with matching `memory-region-names` and a `mediatek,wo-ccif` phandle.

## Control Flow
An `allOf` conditional forbids firmware memory-region and WO CCIF properties for MT7622. The schema otherwise validates exact memory-region name ordering.

## State And Persistence
The DT stores MMIO, interrupt, reserved firmware memory, and controller-interface links. Runtime state is in WED networking, firmware, and PCIe/WLAN drivers.

## Dependencies And Integration Points
It depends on reserved-memory phandles, interrupt controllers, syscon, and MediaTek wireless offload infrastructure.

## Risks
Variant differences are significant: applying MT7986 firmware-memory properties to MT7622 is invalid, while omitting them on newer designs can break firmware-assisted offload.

## Test Signals
`dtbs_check` validates variant conditionals. Runtime signals include WED driver probe, interrupt handling, reserved-memory mapping, and WLAN offload operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-wed.yaml -->
