<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/moxart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/moxart.yaml

## Purpose
This schema identifies the MOXA ART UC-7112-LX embedded computer platform.

## Important APIs, Types, And Functions
The root compatible list is `moxa,moxart-uc-7112-lx`, `moxa,moxart`.

## Control Flow
Validation enforces the ordered two-item compatible list and allows other root properties.

## State And Persistence
It stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with MOXA ART platform code and board DTS files.

## Risks
The schema has no `$nodename` restriction and covers one board, so maintainers must update it for variants.

## Test Signals
`dtbs_check` validates DTS root compatible strings; boot platform matching confirms runtime use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/moxart.yaml -->
