<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,npcm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,npcm.yaml

## Purpose
This root platform schema catalogs Nuvoton WPCM450 and NPCM BMC evaluation/server boards.

## Important APIs, Types, And Functions
It validates root compatible chains for `supermicro,x9sci-ln4f-bmc`, `nuvoton,wpcm450`, for `nuvoton,npcm750-evb`, `nuvoton,npcm750`, and for `nuvoton,npcm845-evb`, `nuvoton,npcm845`.

## Control Flow
`oneOf` selects the BMC SoC family branch and enforces ordered board-to-SoC fallback strings.

## State And Persistence
The binding records immutable BMC platform identity only.

## Dependencies And Integration Points
It integrates with Nuvoton NPCM/WPCM DTS files and BMC platform driver matching.

## Risks
Server BMC board compatibles must remain exact for platform quirks. New NPCM boards need explicit enum additions.

## Test Signals
`dtbs_check` validates root compatible strings; BMC boot and platform device probing confirm runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,npcm.yaml -->
