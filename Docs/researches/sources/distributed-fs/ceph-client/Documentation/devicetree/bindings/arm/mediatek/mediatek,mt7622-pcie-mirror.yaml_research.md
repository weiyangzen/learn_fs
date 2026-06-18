<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-pcie-mirror.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-pcie-mirror.yaml

## Purpose
This schema documents the MT7622 PCIe mirror controller, a small syscon register block used to configure the PCIe controller.

## Important APIs, Types, And Functions
It requires `compatible = "mediatek,mt7622-pcie-mirror", "syscon"` and one `reg` range.

## Control Flow
Validation is a fixed-shape check with no extra properties allowed.

## State And Persistence
The DT describes a persistent MMIO configuration window. Runtime state is managed through syscon/regmap users in PCIe-related code.

## Dependencies And Integration Points
It integrates with MT7622 PCIe controller setup and Linux syscon infrastructure.

## Risks
The register window is tiny, so address or size mistakes can target the wrong system register. Missing `syscon` prevents shared regmap lookup.

## Test Signals
`dtbs_check` catches schema shape errors; PCIe enumeration on MT7622 validates runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-pcie-mirror.yaml -->
