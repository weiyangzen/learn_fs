<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/can/Kconfig

Purpose: this Kconfig file defines the top-level CAN device-driver menu. It enables the common CAN netdevice support, virtual interfaces, serial adapters, platform/PCI/SPI/USB controller families, bit-timing calculation, RX offload support, and debug logging.

Important APIs, types, and functions: the main symbols are `CAN_DEV`, `CAN_NETLINK`, `CAN_CALC_BITTIMING`, and internal `CAN_RX_OFFLOAD`. Driver symbols covered by this subset include `CAN_AT91`, `CAN_BXCAN`, `CAN_CAN327`, `CAN_C_CAN` via a sourced sub-Kconfig, and `CAN_CC770` via another sourced sub-Kconfig. It also sources the rest of the CAN driver family Kconfig files.

Control flow: once `CAN_DEV` is enabled, virtual drivers can be selected immediately. Hardware drivers are nested under `CAN_NETLINK`, which defaults to enabled and provides shared bittiming, restart, and error-state infrastructure needed by most CAN netdev drivers. Individual drivers add architecture, bus, and memory dependencies and select common helpers such as `CAN_RX_OFFLOAD`.

State and persistence: Kconfig state is build-time configuration. It determines whether drivers are built in, modular, or omitted, and whether debug builds add verbose device logging through the Makefile.

Dependencies and integration points: this file integrates with the kernel CAN core (`CAN`), TTY for serial line-discipline drivers, platform architecture symbols such as `ARCH_AT91` and `ARCH_STM32`, PCI for PCIe drivers, MFD dependencies for some board drivers, and `HAS_IOMEM` or `HAS_DMA` where MMIO or DMA is mandatory.

Risks: dependency mistakes can expose non-buildable drivers under `COMPILE_TEST` or hide valid hardware on supported architectures. `CAN_NETLINK` controls common behavior required by hardware drivers, so disabling it drops most physical controller options. Help text and module names need to stay aligned with actual Makefile targets.

Test signals: run Kconfig dependency checks for all relevant architecture combinations, verify modular names match built objects, confirm `CAN_RX_OFFLOAD` is selected by drivers that call rx-offload helpers, and test `CONFIG_CAN_DEBUG_DEVICES` adding `-DDEBUG` through the top-level Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Kconfig -->
