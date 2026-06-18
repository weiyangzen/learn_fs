<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/altera.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/altera.h

Purpose: This header defines platform data, controller private state, and shared entry points for the Altera SPI controller driver.

Important APIs/types/functions: `ALTERA_SPI_MAX_CS` caps chip selects. `altera_spi_platform_data` provides mode bits, chip-select count, bits-per-word mask, and optional child `spi_board_info` entries. `struct altera_spi` stores IRQ, transfer length/count, bytes-per-word, interrupt mask, TX/RX pointers, regmap, register offset, and device pointer. Shared functions are `altera_spi_irq()` and `altera_spi_init_host()`.

Control flow: Platform code supplies controller capabilities and child devices. The controller driver initializes a `spi_controller` through `altera_spi_init_host()`, then interrupt-driven transfers use `altera_spi_irq()` to advance TX/RX buffers and counters.

State and persistence: Per-controller state persists in `altera_spi`; in-flight transfer state is `len`, `count`, `bytes_per_word`, `tx`, and `rx`, while `imr` caches interrupt-mask state.

Dependencies/integration: Depends on interrupt handling, regmap, SPI core, device model, and board-info registration.

Risks and test signals: Risks include count/length underflow, regmap offset errors, unsupported word sizes, and registering too many chip selects. Test PIO/IRQ transfers, different bits-per-word, child enumeration, interrupt masking, and full-duplex data integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/altera.h -->
