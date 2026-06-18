<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Makefile

## Purpose
Kbuild mapping for Allwinner/Sunxi power-domain drivers.

## Important APIs, Types, And Functions
Maps `SUN20I_PPU` to `sun20i-ppu.o`, `SUN50I_H6_PRCM_PPU` to `sun50i-h6-prcm-ppu.o`, and `SUN55I_PCK600` to `sun55i-pck600.o`.

## Control Flow
Kbuild includes each driver according to the selected tristate symbol.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on Sunxi Kconfig symbols and source object names.

## Risks
Because the folder has multiple providers, Makefile drift can make one Kconfig option appear functional while the object is not compiled.

## Test Signals
Build each symbol as built-in and module where allowed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Makefile -->
