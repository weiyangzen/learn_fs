# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Kconfig

Purpose: Kconfig entries for Microchip MCP251xFD CAN FD controller family.

Important APIs/types/functions: `CAN_MCP251XFD` is a tristate selecting `CAN_RX_OFFLOAD`, `REGMAP`, `WANT_DEV_COREDUMP`, and `GPIOLIB`. `CAN_MCP251XFD_SANITY` enables optional internal counter sanity checks with runtime overhead.

Control flow: build-time configuration only.

State and persistence: selected options persist in kernel config; no runtime state.

Dependencies/integration: SPI parent menu, SocketCAN RX offload, regmap abstraction, devcoredump, and GPIO library are required by the composite driver.

Risks: sanity option can affect runtime cost. The main option pulls in several frameworks, so build dependency changes need care.

Test signals: Kconfig dependency resolution; build with sanity enabled/disabled; verify selected helper frameworks are available for module and built-in builds.
