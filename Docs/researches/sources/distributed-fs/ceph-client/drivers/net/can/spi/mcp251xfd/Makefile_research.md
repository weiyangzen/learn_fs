# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Makefile

Purpose: Kbuild composition for the MCP251xFD CAN FD driver.

Important APIs/types/functions: builds `mcp251xfd.o` when `CONFIG_CAN_MCP251XFD` is enabled. The module links chip FIFO, core, CRC, ethtool, RAM, regmap, ring, RX, TEF, timestamp, and TX objects; `mcp251xfd-dump.o` is added when `CONFIG_DEV_COREDUMP` is enabled.

Control flow: no runtime flow. Object list defines functional decomposition of the driver.

State and persistence: build-time only.

Dependencies/integration: relies on the parent SPI Makefile descending into this directory. Conditional dump object corresponds to devcoredump support selected in Kconfig.

Risks: missing one object can break runtime paths or unresolved symbols because the driver is highly split. Conditional dump linkage must match config.

Test signals: module link for MCP251xFD with and without devcoredump; modpost symbol resolution across all listed objects.
