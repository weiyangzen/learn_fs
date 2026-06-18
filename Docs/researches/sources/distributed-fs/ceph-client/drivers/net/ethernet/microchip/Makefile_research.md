# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Makefile

## Purpose

This Makefile maps Microchip Ethernet Kconfig symbols to objects and subdirectories. It is the build-system counterpart to the local Kconfig file.

## Important Build Rules

`CONFIG_ENC28J60` builds `enc28j60.o`. `CONFIG_ENCX24J600` builds both `encx24j600.o` and `encx24j600-regmap.o`, linking the main driver with its regmap helper. `CONFIG_LAN743X` builds composite `lan743x.o` from `lan743x_main.o`, `lan743x_ethtool.o`, and `lan743x_ptp.o`. Other symbols descend into `lan865x/`, `lan966x/`, `sparx5/`, `vcap/`, and `fdma/`.

## Control Flow, State, And Dependencies

Kbuild expands `obj-y` or `obj-m` based on `.config`, then links composite objects and subdirectories. The file has no runtime state. It depends on symbol names defined by local and sourced Kconfig files and on the listed source files existing with matching names.

## Risks And Test Signals

Risks are stale symbol/object names and incomplete composite object lists. Test with module and built-in builds for `ENC28J60`, `ENCX24J600`, `LAN743X`, and each subdirectory symbol; `make W=1` helps catch missing object references.
