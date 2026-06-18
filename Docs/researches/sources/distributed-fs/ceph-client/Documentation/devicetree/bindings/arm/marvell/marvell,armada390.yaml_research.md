<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada390.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada390.yaml

## Purpose
This schema catalogs Marvell Armada 39x platform root compatibles for A390, A395, and A398 boards.

## Important APIs, Types, And Functions
It validates chains for `marvell,a390-db`, `marvell,armada390`, for A398 boards falling back to `marvell,armada398`, `marvell,armada390`, and for A395 boards falling back to `marvell,armada395`, `marvell,armada390`.

## Control Flow
`oneOf` enforces the exact SoC variant branch and compatible order.

## State And Persistence
Only root platform identity is represented. Device state is in other DT nodes and runtime drivers.

## Dependencies And Integration Points
It integrates with Armada 39x DTS files and shared Armada platform matching.

## Risks
Variant fallback errors can select the wrong SoC-level support. New boards require schema updates.

## Test Signals
`dtbs_check` validates root compatible lists; hardware boot validates correct platform matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada390.yaml -->
