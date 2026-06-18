# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.c

Purpose: Provides the SPI bus binding for wl1251, including WSPI reset/wake commands, SPI read/write transactions, GPIO power control, IRQ handling, regulator management, probe/remove, and module registration.

Important APIs and functions: `wl1251_spi_reset()`, `wl1251_spi_wake()`, `wl1251_spi_reset_wake()`, `wl1251_spi_read()`, `wl1251_spi_write()`, IRQ enable/disable, power setter, `wl1251_spi_probe()`, and `wl1251_spi_remove()`. `struct wl1251_spi` stores the SPI device and optional power GPIO.

Control flow: Probe requires an OF node, allocates shared hardware through `wl1251_alloc_hw()`, attaches SPI private data and operations, sets `bits_per_word` to 32, reads `ti,wl1251-has-eeprom`, acquires optional power GPIO and `vio` regulator, requests rising-edge IRQ with `IRQ_NOAUTOEN`, enables regulator, and initializes mac80211. IRQ handler queues core IRQ work. SPI read/write build WSPI command words, perform `spi_sync()`, and transfer busy words/data.

State and persistence: Stores bus-private pointer in `wl->if_priv`, selected operations in `wl->if_ops`, IRQ in `wl->irq`, regulator in `wl->vio`, and optional GPIO. Uses shared command/busy buffers in `struct wl1251`.

Dependencies and integration points: Implements the bus contract consumed by `io.h`/`io.c` and the core driver. Depends on Linux SPI, GPIO descriptor, regulator, OF, CRC7, and byte-swap helpers.

Risks: `spi_sync()` return values are ignored in reset, wake, read, and write paths, so bus transfer failures may be silent. Busy words are read but not validated. Command construction and byte swapping are hardware-specific; changes require WSPI validation. Probe requires OF and will reject non-DT SPI instantiation.

Test signals: Probe with valid DT/regulator/GPIO/IRQ, firmware boot over SPI, ELP wake, sustained RX/TX, and fault injection for failed SPI transfers.
