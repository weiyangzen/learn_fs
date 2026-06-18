<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/Makefile

Purpose: maps MDIO Kconfig symbols to kernel objects so helper modules, controller drivers, and mux drivers are built when selected.

Important APIs/types/functions: uses standard `obj-$(CONFIG_...) += file.o` entries. It includes firmware helpers (`acpi_mdio.o`, `fwnode_mdio.o`, `of_mdio.o`), controller drivers, library helpers (`mdio-bitbang.o`, `mdio-cavium.o`, `mdio-i2c.o`, `mdio-regmap.o`), and mux drivers.

Control flow: Kbuild includes each object based on resolved tristate state. Silent helper symbols are still built when selected by concrete drivers. The ordering places helper accessors first, individual controllers next, and mux core/drivers last.

State and persistence: no runtime state; this file affects build artifacts and module composition.

Dependencies/integration: depends on the Kconfig file for symbol availability and on source files exporting symbols used by other modules. Mux-specific object mappings must stay aligned with `select MDIO_BUS_MUX` relationships.

Risks and test signals: risks are stale object entries for renamed source files, omitted objects for Kconfig symbols, or building helper libraries in the wrong module linkage mode. Build tests with `allmodconfig`, targeted module builds, and `make M=drivers/net/mdio` catch most issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Makefile -->
