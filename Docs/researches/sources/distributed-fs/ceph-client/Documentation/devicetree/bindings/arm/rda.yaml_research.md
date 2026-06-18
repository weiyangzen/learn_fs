<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rda.yaml

## Purpose
This root platform schema identifies RDA Micro 8810PL boards, specifically Orange Pi 2G-IoT and Orange Pi i96.

## Important APIs, Types, And Functions
The compatible list is a board enum (`xunlong,orangepi-2g-iot` or `xunlong,orangepi-i96`) followed by `rda,8810pl`.

## Control Flow
Validation enforces the root node name `/` and the ordered two-item compatible list.

## State And Persistence
The schema records immutable platform identity only.

## Dependencies And Integration Points
It integrates with RDA 8810PL DTS files and platform matching.

## Risks
New boards need explicit enum additions. Missing the SoC fallback prevents shared RDA support from matching.

## Test Signals
`dtbs_check` validates root compatible shape; boot-time platform probe confirms runtime use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rda.yaml -->
