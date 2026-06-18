# sources/distributed-fs/ceph-client/drivers/net/can/spi/Kconfig

Purpose: Kconfig menu for SPI-connected CAN controllers.

Important APIs/types/functions: menu depends on `SPI`. `CAN_HI311X` enables Holt HI311x driver. `CAN_MCP251X` enables Microchip MCP251x/MCP25625 classic CAN driver. It sources the MCP251xFD subdirectory Kconfig for CAN FD-capable controllers.

Control flow: build-time configuration only.

State and persistence: selected options persist in kernel config; no runtime state.

Dependencies/integration: SPI core is mandatory. Subdrivers integrate with SocketCAN and their own regulators/clocks/DT bindings at runtime.

Risks: users may confuse classic `CAN_MCP251X` with FD `CAN_MCP251XFD`; both are separate drivers. Missing SPI dependency prevents menu visibility.

Test signals: Kconfig visibility under SPI; module/object generation for each selected driver; MCP251xFD options sourced correctly.
