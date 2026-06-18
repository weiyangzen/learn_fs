# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Kconfig

Purpose: Kconfig vendor menu for National Semiconductor Ethernet drivers, including SONIC variants and DP8381x/DP83820 PCI drivers.

Important symbols: `NET_VENDOR_NATSEMI` gates the menu. Driver symbols are `MACSONIC`, `MIPS_JAZZ_SONIC`, `NATSEMI`, `NS83820`, and `XTENSA_XT2000_SONIC`, each with platform or PCI dependencies. `NATSEMI` selects `CRC32`.

Control flow: configuration-only. Platform dependencies expose SONIC drivers only on relevant architectures/boards.

State and persistence: generated `.config` controls compilation and module availability.

Dependencies and integration: consumed by `natsemi/Makefile` and the wider Ethernet Kconfig hierarchy.

Risks: platform dependencies must stay accurate to avoid compiling drivers with unavailable arch headers. Help text references old external URLs but does not affect build.

Test signals: Kconfig builds for MIPS Jazz, Mac, Xtensa XT2000, and PCI configurations; verify unrelated architectures do not expose incompatible platform drivers.
