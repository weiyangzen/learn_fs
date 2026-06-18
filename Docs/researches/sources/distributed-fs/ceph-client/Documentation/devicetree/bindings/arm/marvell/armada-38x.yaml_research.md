<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-38x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-38x.yaml

## Purpose
This root-node schema documents Marvell Armada 380/385/388 boards, including Netgear, Marvell development boards, SolidRun Clearfog systems, and Kobol Helios4.

## Important APIs, Types, And Functions
It validates ordered compatible chains ending in `marvell,armada380`, with intermediate fallbacks for `marvell,armada385`, `marvell,armada388`, and `solidrun,clearfog-a1` where appropriate.

## Control Flow
Each board family is a `oneOf` branch. dt-schema requires exact order and branch-specific item counts.

## State And Persistence
The schema records immutable platform identity only; peripherals and memory state are validated elsewhere.

## Dependencies And Integration Points
It integrates with Armada 38x board DTS files and common SoC/platform code using the compatible chain.

## Risks
The 385/388 fallback hierarchy is important for shared support. Incorrect board grouping can select the wrong quirks for NAS or switch boards.

## Test Signals
`dtbs_check` validates compatible order for Armada 38x DTBs. Runtime signals include successful platform match and peripheral initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-38x.yaml -->
