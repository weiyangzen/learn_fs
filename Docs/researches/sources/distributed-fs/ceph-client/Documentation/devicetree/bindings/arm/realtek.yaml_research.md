<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/realtek.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/realtek.yaml

## Purpose
This root platform schema catalogs Realtek RTD multimedia/NAS boards.

## Important APIs, Types, And Functions
It validates board-to-SoC compatible chains for RTD1195, RTD1293, RTD1295, RTD1296, RTD1395, RTD1501s, RTD1619, RTD1861b, and RTD1920s boards from Realtek, Synology, MeLE, ProBox2, Xnano, Zidoo, and Banana Pi.

## Control Flow
`oneOf` selects the SoC family branch and enforces exact compatible ordering.

## State And Persistence
It stores root platform identity only.

## Dependencies And Integration Points
It integrates with Realtek DTS files and platform matching for media and NAS SoCs.

## Risks
Realtek SoC names are close and product boards are varied; incorrect fallback can bind the wrong platform support.

## Test Signals
`dtbs_check` validates DTS root compatible lists; successful boot and media/storage peripheral probing validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/realtek.yaml -->
