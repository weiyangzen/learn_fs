# sources/distributed-fs/ceph-client/drivers/phy/cadence/Makefile

Purpose: Maps Cadence PHY Kconfig symbols to their driver objects.

Important APIs and symbols: The file builds `phy-cadence-torrent.o`, `cdns-dphy.o`, `cdns-dphy-rx.o`, `phy-cadence-sierra.o`, and `phy-cadence-salvo.o` behind `CONFIG_PHY_CADENCE_TORRENT`, `CONFIG_PHY_CADENCE_DPHY`, `CONFIG_PHY_CADENCE_DPHY_RX`, `CONFIG_PHY_CADENCE_SIERRA`, and `CONFIG_PHY_CADENCE_SALVO`.

Control flow: There is no runtime control flow. Kbuild includes object files only when their config symbols are built-in or modular.

State and persistence: Build selection persists in generated kernel build artifacts and module outputs. The Makefile itself carries no runtime state.

Dependencies and integration points: Integrated with `drivers/phy/Makefile` and the Cadence `Kconfig`. Object names must match module aliases and source files in this directory.

Risks: A stale object mapping causes selected drivers to disappear from builds or produce unresolved symbols. Since each object is standalone, there are no composite object lists here to hide missing source files.

Test signals: Run targeted `make M=drivers/phy/cadence` or full kernel builds with each `CONFIG_PHY_CADENCE_*` as `m` and `y`, then confirm expected `.o` and `.ko` outputs.
