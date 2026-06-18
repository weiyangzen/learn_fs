<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel-ixp4xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel-ixp4xx.yaml

## Purpose
This root-node schema catalogs Intel IXP4xx network/NAS/router platforms for the IXP42x and IXP43x SoC families.

## Important APIs, Types, And Functions
The root compatible is validated as one of two fallback chains: a board string followed by `intel,ixp42x`, or selected boards followed by `intel,ixp43x`.

## Control Flow
dt-schema chooses a `oneOf` branch and enforces exact compatible ordering. The root node name is fixed to `/`.

## State And Persistence
The binding stores platform identity only. It has no mutable state; the compatible list controls machine and driver matching.

## Dependencies And Integration Points
It depends on the core schema and integrates with IXP4xx platform code, board-specific DTS files, and SoC-level driver matching.

## Risks
Many legacy boards are enumerated; misspelling or using the wrong SoC fallback silently changes platform match behavior. New boards must be added before validation passes.

## Test Signals
`dtbs_check` validates compatible chains for affected IXP4xx DTS files; successful boot and peripheral enumeration confirm the selected SoC family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel-ixp4xx.yaml -->
