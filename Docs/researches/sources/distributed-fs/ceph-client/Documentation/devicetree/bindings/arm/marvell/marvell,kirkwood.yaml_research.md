<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,kirkwood.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,kirkwood.yaml

## Purpose
This large root-node schema catalogs Marvell Kirkwood boards across NAS, plug computer, router, and embedded product families.

## Important APIs, Types, And Functions
The schema validates many ordered compatible chains for generic `marvell,kirkwood`, SoC variants `marvell,kirkwood-88f6192`, `88f6281`, `88f6282`, `88f6283`, `88f6702`, and `98DX4122`, plus board-family fallbacks for Synology, D-Link, Globalscale, LaCie, Buffalo, Netgear, Zyxel, and others.

## Control Flow
Each board or product family is represented as a `oneOf` branch. dt-schema enforces exact item counts and ordering, commonly board variant, product family, SoC variant, then `marvell,kirkwood`.

## State And Persistence
The binding represents immutable root identity. Runtime state for SATA, Ethernet, GPIO, and storage devices is described in separate nodes.

## Dependencies And Integration Points
It integrates with many legacy Kirkwood DTS files and platform-specific quirk matching. The fallback strings are used by common Marvell Kirkwood support.

## Risks
The list is long and contains highly similar product names, so duplicate or misordered entries are easy. The `synology,ds212pv10` duplicate-looking chain should be treated carefully when editing to avoid unintended ABI changes.

## Test Signals
`dtbs_check` across Kirkwood DTS files is essential. Hardware or emulator boot confirming SoC variant selection and peripheral probing is the runtime signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,kirkwood.yaml -->
