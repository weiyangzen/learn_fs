# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus.h

Purpose: Defines the WFx common bus abstraction used by the core driver to share SDIO and SPI implementations.

Important APIs and types: Register IDs cover config, control, in/out queue, AHB/SRAM data ports, base address, generic read/write, and frame-out registers. `struct wfx_hwbus_ops` supplies `copy_from_io`, `copy_to_io`, IRQ subscribe/unsubscribe, bus lock/unlock, transfer alignment, and wakeup enable hooks. It declares external `wfx_sdio_driver` and `wfx_spi_driver`.

Control flow and integration: `wfx_init_common()` stores these ops in `wdev`; HWIO, firmware loading, BH, and PM paths call them without knowing the physical bus. `main.c` registers the external SPI/SDIO drivers depending on Kconfig.

State and persistence: The abstraction itself has no state; bus-private state is passed as `hwbus_priv`.

Dependencies: Includes Linux SDIO and SPI type declarations because both bus driver symbols are declared here.

Risks and test signals: Risks include bus ops with incompatible locking/alignment semantics and missing driver symbols in build variants. Test both bus paths for identical register/data semantics, IRQ subscribe/unsubscribe lifecycle, and wakeup enable behavior.

Test signals: Source read size: 37 lines, 1078 bytes.
