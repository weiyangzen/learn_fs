# sources/distributed-fs/ceph-client/drivers/net/can/spi/Makefile

Purpose: Kbuild rules for SPI CAN drivers.

Important APIs/types/functions: builds `hi311x.o` for `CONFIG_CAN_HI311X`, `mcp251x.o` for `CONFIG_CAN_MCP251X`, and always descends into `mcp251xfd/` so that subdir Kbuild can decide based on its config.

Control flow: no runtime flow.

State and persistence: build-time only.

Dependencies/integration: ties parent SPI CAN menu to concrete driver objects and MCP251xFD composite module.

Risks: `obj-y += mcp251xfd/` is intentional for recursive kbuild; removing it hides FD driver builds even when configured.

Test signals: kernel build with each config as built-in/module; verify subdirectory objects are considered when `CONFIG_CAN_MCP251XFD` is selected.
