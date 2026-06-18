<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Kconfig

## Purpose
Kconfig menu for Allwinner/Sunxi power-domain drivers in this folder.

## Important APIs, Types, And Functions
Defines tristate symbols `SUN20I_PPU`, `SUN50I_H6_PRCM_PPU`, and `SUN55I_PCK600`, each depending on Sunxi or compile-test platforms and PM, and selecting generic PM domains.

## Control Flow
Enabled symbols select matching objects from the Sunxi Makefile.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Integrates with Allwinner platform configs and distinct DT compatibles for D1/V853/A523 PPU, H6/H616 PRCM PPU, and A523 PCK-600.

## Risks
The requested file batch only includes `sun20i-ppu.c`; the Makefile also builds H6 and PCK-600 drivers when configured. Missing PM_GENERIC_DOMAINS selection would break providers, so each option selects it.

## Test Signals
Sunxi and COMPILE_TEST builds should compile selected objects. DT systems using display/video engines should verify required domains are powered.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Kconfig -->
