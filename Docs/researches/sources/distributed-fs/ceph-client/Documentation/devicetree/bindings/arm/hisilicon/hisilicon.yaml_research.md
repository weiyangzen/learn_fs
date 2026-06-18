<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/hisilicon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/hisilicon.yaml

## Purpose
This root-node platform schema catalogs supported HiSilicon boards and SoCs, including Hi3660/Hi3670 Hikey boards, Poplar, Hi6220 Hikey, HiP server boards, and SD5203.

## Important APIs, Types, And Functions
The binding constrains the root `$nodename` to `/` and validates `compatible` with `oneOf` board-to-SoC fallback lists such as `hisilicon,hi3660-hikey960`, `hisilicon,hi3660` and `hisilicon,hi6220-hikey`, `hisilicon,hi6220`.

## Control Flow
dt-schema selects exactly one `oneOf` compatible sequence. The exact item order matters because the first string identifies the board and later strings identify the SoC family.

## State And Persistence
The schema carries immutable platform identity in the DTB. It does not describe mutable state or persistence beyond the root compatible string.

## Dependencies And Integration Points
It depends on the core schema and integrates with board matching, machine selection, quirks, and SoC-level driver probing.

## Risks
Adding a board under the wrong SoC fallback can route platform code to incorrect quirks. `additionalProperties: true` intentionally leaves normal root properties to other schemas, so this file only catches compatible-list shape.

## Test Signals
`dtbs_check` on HiSilicon DTBs confirms root compatible ordering. Board boot logs and platform driver matches provide runtime confirmation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/hisilicon.yaml -->
