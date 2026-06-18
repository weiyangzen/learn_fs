<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek.yaml

## Purpose
This large root platform schema catalogs MediaTek SoC based boards across mobile, router, Chromebook, IoT, and evaluation platforms.

## Important APIs, Types, And Functions
It fixes the root node to `/` and validates many `compatible` chains sorted by final SoC compatible. Covered SoCs include MT2701, MT762x, MT798x router SoCs, MT81xx/MT82xx Chromebook and tablet SoCs, MT83xx/MT839x Genio-style platforms, and MT8516. Board chains include Banana Pi, Google Chromebook revisions/SKUs, MediaTek EVBs, Sony phones, and other vendors.

## Control Flow
dt-schema selects a single `oneOf` branch and checks exact compatible ordering. Many Chromebook entries encode revision and SKU fallback chains, so the list acts as an ABI catalog.

## State And Persistence
The schema records immutable platform identity in the DTB. Device state and resources are represented by downstream peripheral nodes.

## Dependencies And Integration Points
It integrates with MediaTek platform matching, board DTS files, and SoC-specific driver probing. `additionalProperties: true` leaves non-root properties to generic schemas.

## Risks
The file is high-churn because every new board or SKU needs an entry. Risks include ordering mistakes, placing a board under the wrong SoC, and accidentally changing ChromeOS revision fallback semantics.

## Test Signals
`dtbs_check` over MediaTek DTS files is the primary signal. Boot logs showing expected SoC and board quirks, especially for Chromebook SKUs, provide runtime confirmation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek.yaml -->
