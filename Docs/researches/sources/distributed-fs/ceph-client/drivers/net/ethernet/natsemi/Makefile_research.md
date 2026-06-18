# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/Makefile

Purpose: Kbuild mapping from NatSemi-related config symbols to driver objects.

Important declarations: maps `CONFIG_MACSONIC` to `macsonic.o`, `CONFIG_MIPS_JAZZ_SONIC` to `jazzsonic.o`, `CONFIG_NATSEMI` to `natsemi.o`, `CONFIG_NS83820` to `ns83820.o`, and `CONFIG_XTENSA_XT2000_SONIC` to `xtsonic.o`.

Control flow: build-time only.

State and persistence: no runtime state.

Dependencies and integration: paired with `natsemi/Kconfig`.

Risks: object names must match source files and config symbols. Multiple platform SONIC drivers share core code patterns, so build coverage should catch include/arch assumptions.

Test signals: per-symbol kernel builds and module packaging where the symbol is tristate.
