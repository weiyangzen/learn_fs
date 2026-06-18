## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Kconfig

Purpose: this Kconfig file declares the Libertas 8xxx driver core and USB/SDIO/SPI bus frontends.

Important symbols: `LIBERTAS` is the core tristate and depends on at least one bus family (`USB || MMC || SPI`) plus `CFG80211`; it selects `FW_LOADER`. `LIBERTAS_USB`, `LIBERTAS_SDIO`, and `LIBERTAS_SPI` depend on the core and their respective bus subsystems. `LIBERTAS_DEBUG` enables debug output, and `LIBERTAS_MESH` enables mesh support.

Control flow and integration: these options drive `libertas/Makefile`, where the core object is built from common files and bus objects are added as separate modules. Mesh support conditionally adds `mesh.o` and exposes mesh-related callbacks in cfg80211/ethtool paths.

State and persistence: configuration persists in `.config`. Runtime effects include debug macros becoming active under `CONFIG_LIBERTAS_DEBUG` and mesh structures/code being compiled only when `CONFIG_LIBERTAS_MESH` is set.

Risks and tests: dependency mistakes can allow a bus driver without the shared core or firmware loader. Test signals are Kconfig dependency resolution, build coverage for each bus combination, and module autoload behavior with firmware present/missing.
