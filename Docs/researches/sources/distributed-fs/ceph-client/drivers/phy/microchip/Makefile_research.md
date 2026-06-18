# sources/distributed-fs/ceph-client/drivers/phy/microchip/Makefile

Purpose: Connects Microchip PHY Kconfig symbols to their object files.

Important APIs, types, and flow: `obj-$(CONFIG_PHY_SPARX5_SERDES) := sparx5_serdes.o` builds the Sparx5/LAN969x SerDes driver when enabled. `obj-$(CONFIG_PHY_LAN966X_SERDES) := lan966x_serdes.o` builds the LAN966x SerDes driver when enabled.

State, dependencies, and integration points: There is no runtime state; this is a kernel build-system mapping consumed by Kbuild under `drivers/phy/microchip`. The object names match the platform-driver source files.

Risks and test signals: This file is simple, but using `:=` instead of accumulating with `+=` means each symbol maps to one object as intended. Build tests should verify both drivers compile when selected together and independently.
