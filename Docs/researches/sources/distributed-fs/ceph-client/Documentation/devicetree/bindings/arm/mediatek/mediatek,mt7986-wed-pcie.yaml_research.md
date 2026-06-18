<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7986-wed-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7986-wed-pcie.yaml

## Purpose
This binding documents the MT7986 WED PCIe configuration syscon block.

## Important APIs, Types, And Functions
It requires `compatible = "mediatek,mt7986-wed-pcie", "syscon"` and one `reg` range.

## Control Flow
The schema is strict and fixed-shape; compatible and reg are required and additional properties are rejected.

## State And Persistence
The node describes a small persistent MMIO configuration region. Runtime state is in WED/PCIe syscon users.

## Dependencies And Integration Points
It integrates with MT7986 WED and PCIe controller setup through syscon/regmap.

## Risks
Address or compatible errors prevent WED PCIe configuration. The two-item compatible order must include `syscon`.

## Test Signals
`dtbs_check` validates DTS shape; PCIe-backed wireless offload initialization validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7986-wed-pcie.yaml -->
