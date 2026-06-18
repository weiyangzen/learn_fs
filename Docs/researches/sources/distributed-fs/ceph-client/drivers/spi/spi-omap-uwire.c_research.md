# sources/distributed-fs/ceph-client/drivers/spi/spi-omap-uwire.c

Purpose: Legacy OMAP1 MicroWire SPI interface driver using `spi_bitbang`. It maps fixed UWIRE registers, exposes four chip selects on bus 2, supports half-duplex transfers up to 16 bits per word, and computes hardware-specific two-stage clock divisors.

Important APIs, types, and functions: `struct uwire_spi` embeds bitbang and functional clock; `struct uwire_state` stores the per-device `div1_idx` needed because divider 1 is global. Register helpers operate through global `uwire_base`. Key functions are `omap_uwire_configure_mode()`, `wait_uwire_csr_flag()`, `uwire_set_clk1_div()`, `uwire_chipselect()`, `uwire_txrx()`, `uwire_setup_transfer()`, `uwire_setup()`, `uwire_cleanup()`, probe/remove, and init/exit registration.

Control flow: setup allocates per-device controller state and programs mode/dividers. Chip-select waits for controller idle, deselects old CS, restores the device's global divider, sets CPOL in SR4, and asserts `CS_CMD`. Transfers are TX-only or RX-only; TX writes one or two bytes shifted to MSB position, starts a write in CSR, waits for start and final idle. RX starts reads, waits for data-ready, masks received bits, and writes bytes back to the buffer.

State and persistence: per-device state holds only `div1_idx`; hardware state is in UWIRE SR/CSR registers. The global register base and `uwire_idx_shift` reflect platform-specific layout. Remove stops bitbang, clears SR3, disables the clock, and drops the controller.

Dependencies and integration points: depends on OMAP1 SoC headers, fixed physical address `UWIRE_BASE_PHYS`, clock `"fck"`, `spi_bitbang`, and platform device registration via `subsys_initcall`. It advertises `SPI_CONTROLLER_HALF_DUPLEX`, CPOL/CPHA/CS_HIGH, and bits-per-word 1..16.

Risks: fixed physical mapping and global base limit portability and concurrency assumptions. `BUG_ON(wait_uwire_csr_flag(...))` can crash on chipselect timeout. Polling timeouts use one second and return `-EIO` on failure. Comments note DMA and overlap opportunities are not implemented. The code assumes TX and RX are not simultaneous.

Test signals: 1/8/16-bit TX and RX, each SPI mode, CS high/low behavior, divider calculation at boundary rates, timeout behavior with nonresponsive hardware, remove clock cleanup, and multiple devices changing dividers between chip selects.
