<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada-370-xp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada-370-xp.yaml

## Purpose
This schema catalogs root compatibles for Marvell Armada 370 and Armada XP boards, including NAS, router, switch, and development platforms.

## Important APIs, Types, And Functions
It validates board-specific compatibles followed by SoC fallbacks such as `marvell,armada370`, `marvell,armadaxp-98dx3236`, `marvell,armadaxp-mv78230`, `marvell,armadaxp-mv78260`, or `marvell,armadaxp-mv78460`, all ending at `marvell,armada-370-xp` where appropriate.

## Control Flow
`oneOf` chooses the board/SoC chain and requires exact ordering. The root node name is fixed to `/`.

## State And Persistence
The binding stores immutable board and SoC identity. Runtime platform state belongs to drivers matched by that identity.

## Dependencies And Integration Points
It integrates with Armada 370/XP DTS files and common Marvell platform code, especially for legacy NAS and switch boards.

## Risks
Board families have similar marketing names but different SoC fallbacks. Incorrect fallback can apply wrong CPU, switch, or peripheral assumptions.

## Test Signals
`dtbs_check` validates compatible chains; boot-time machine match and peripheral enumeration are runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada-370-xp.yaml -->
