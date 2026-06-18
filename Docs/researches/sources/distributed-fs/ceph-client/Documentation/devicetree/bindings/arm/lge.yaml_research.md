<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/lge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/lge.yaml

## Purpose
This root-node schema catalogs LG Electronics LG1312 and LG1313 reference SoC platforms.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and validates compatible lists `lge,lg1312-ref`, `lge,lg1312` or `lge,lg1313-ref`, `lge,lg1313`.

## Control Flow
Validation is an ordered `oneOf` selection between the two SoC families. Other root properties remain allowed.

## State And Persistence
The schema stores immutable board identity only, with no runtime state.

## Dependencies And Integration Points
It integrates with LG platform/machine matching and SoC-specific driver selection through root compatibles.

## Risks
The binding is small and exact; new boards or incorrect fallback order require updates. It does not validate peripherals beyond root identity.

## Test Signals
`dtbs_check` on LG DTS files validates compatible ordering; boot-time platform selection confirms runtime use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/lge.yaml -->
