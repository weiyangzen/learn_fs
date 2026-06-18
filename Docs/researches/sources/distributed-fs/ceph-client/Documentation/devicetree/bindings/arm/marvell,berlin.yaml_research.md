<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell,berlin.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell,berlin.yaml

## Purpose
This root platform schema catalogs Synaptics/Marvell Berlin multimedia SoC boards, noting the product-line ownership transition to Synaptics.

## Important APIs, Types, And Functions
It validates root compatible fallback chains for Berlin2, Berlin2CD, Berlin2Q, and Berlin4CT boards, always ending in `marvell,berlin`.

## Control Flow
The schema uses `oneOf` to choose the exact board/SoC/family chain and fixes the root node name to `/`.

## State And Persistence
It describes immutable platform identity in the DTB. No runtime state or storage is managed by the schema.

## Dependencies And Integration Points
It integrates with Berlin SoC platform matching and board DTS files for devices such as Chromecast, Steam Link, and Sony NSZ-GS7.

## Risks
Fallback ordering matters for shared family code. The Synaptics/Marvell naming history can cause incompatible additions if maintainers mix vendor prefixes without schema updates.

## Test Signals
`dtbs_check` confirms root compatible strings; boot probing of Berlin platform drivers confirms runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell,berlin.yaml -->
