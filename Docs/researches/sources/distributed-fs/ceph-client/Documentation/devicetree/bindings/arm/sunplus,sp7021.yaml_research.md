<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunplus,sp7021.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunplus,sp7021.yaml

## Purpose
This root platform binding identifies Sunplus SP7021 boards.

## Important APIs, Types, And Functions
It validates board strings `sunplus,sp7021-achip` and `sunplus,sp7021-demo-v3` followed by `sunplus,sp7021`.

## Control Flow
The root node name is `/`; validation selects the single SP7021 board branch and enforces compatible ordering.

## State And Persistence
It stores immutable board/SoC identity only.

## Dependencies And Integration Points
It integrates with Sunplus SP7021 DTS files and platform matching.

## Risks
New board variants require schema additions. Missing the SoC fallback can break shared SP7021 code.

## Test Signals
`dtbs_check` validates compatible chains; boot-time platform match confirms integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunplus,sp7021.yaml -->
