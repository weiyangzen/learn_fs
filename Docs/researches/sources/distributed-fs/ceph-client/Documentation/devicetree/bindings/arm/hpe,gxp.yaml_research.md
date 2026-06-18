<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hpe,gxp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hpe,gxp.yaml

## Purpose
This root platform binding identifies HPE GXP BMC boards, currently the DL360 Gen10 BMC platform.

## Important APIs, Types, And Functions
The root `compatible` must be a two-item list with a board string such as `hpe,gxp-dl360gen10` followed by the SoC family fallback `hpe,gxp`.

## Control Flow
The schema uses a single `oneOf` branch for GXP boards and requires `compatible`. Other root-node properties remain validated by generic schemas because `additionalProperties` is true.

## State And Persistence
It stores immutable board/SoC identity in the DTB; no runtime state or persistent storage is created.

## Dependencies And Integration Points
It integrates with HPE GXP platform setup and any driver or machine matching keyed by the root compatible.

## Risks
The schema is narrow: new GXP boards must be added explicitly or `dtbs_check` will fail. Wrong fallback ordering can prevent shared SoC code from matching.

## Test Signals
`dtbs_check` validates GXP DTS root compatibles; boot logs should show expected platform and BMC device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hpe,gxp.yaml -->
