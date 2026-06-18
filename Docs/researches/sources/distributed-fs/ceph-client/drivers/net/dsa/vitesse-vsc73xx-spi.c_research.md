# sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-spi.c

Purpose: this file is the SPI bus frontend for the VSC73xx DSA core. It serializes 32-bit switch register reads and writes into the device's SPI command format and delegates all switch behavior to `vitesse-vsc73xx-core.c`.

Important APIs, types, and functions: `struct vsc73xx_spi` stores the `spi_device`, a mutex protecting SPI traffic, and the embedded core object. `vsc73xx_make_addr()` encodes read/write mode, block, and subblock into the SPI command byte. `vsc73xx_spi_read()` builds a two-transfer message with a 4-byte command and 4-byte receive buffer. `vsc73xx_spi_write()` builds a two-transfer write with a 2-byte command and 4-byte big-endian data payload. `vsc73xx_spi_probe()`, remove, and shutdown wrap the common core lifecycle.

Control flow: probe allocates state, takes a device reference with `spi_dev_get()`, initializes core fields and the SPI mutex, forces SPI mode 0 and 8 bits per word, calls `spi_setup()`, then calls `vsc73xx_probe()`. Each register access validates block/subblock, performs `spi_sync()` under the mutex, and converts values manually between byte arrays and `u32`.

State and persistence: transport state is the SPI device pointer and mutex; common switch state is embedded in `vsc73xx_spi.vsc`. Register caching is not present. Remove unregisters the common switch but does not explicitly drop the `spi_dev_get()` reference in this snapshot, so lifetime management should be reviewed against SPI core expectations.

Dependencies and integration points: it depends on Linux SPI APIs, OF and SPI ID tables for all supported VSC73xx models, and the shared `struct vsc73xx_ops` interface. It exports no switch logic itself.

Risks: SPI command format, mode, and byte order must match the hardware exactly. A missing explicit `spi_dev_put()` after `spi_dev_get()` may be a reference leak unless balanced elsewhere. Because every access is synchronous and mutex-protected, slow SPI buses can stretch DSA operations and polling loops. Invalid register numbers beyond block/subblock validation are not rejected here.

Test signals: SPI probe with `spi_setup()` success, chip-ID detection over SPI, concurrent register operations serialized by the mutex, read/write byte-order tests with known registers, remove/shutdown behavior, and compatibility matching through both OF and SPI ID tables.
