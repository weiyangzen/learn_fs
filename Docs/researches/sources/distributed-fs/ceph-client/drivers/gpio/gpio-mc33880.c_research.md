# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mc33880.c

Purpose: exposes the Freescale MC33880 high-side/low-side SPI switch as an 8-output GPIO chip. It is a simple output-latch driver with no input, direction, or IRQ support.

Important APIs/types/functions: `struct mc33880` stores a mutex, cached `port_config` byte, `gpio_chip`, and `spi_device`. `mc33880_write_config()` writes the cached byte to SPI, `__mc33880_set()` mutates one bit and writes it, and `mc33880_set()` wraps that with the mutex. Probe and remove are standard SPI driver callbacks.

Control flow: probe requires legacy `struct mc33880_platform_data` with a nonzero `base`, sets `spi->bits_per_word = 8`, runs `spi_setup()`, allocates state, initializes the mutex, assigns a fixed-base sleepable GPIO chip with only `.set`, writes an all-zero configuration twice, and registers the chip. Remove unregisters the GPIO chip and destroys the mutex.

State and persistence behavior: the output latch state is cached in `port_config` and mirrored to the SPI device on every `set`. No suspend/resume hook exists, so cached state is not explicitly replayed after system power loss. The mutex serializes simultaneous SPI updates and protects the byte cache.

Dependencies and integration points: depends on SPI core, legacy `linux/spi/mc33880.h` platform data, and gpiolib. It uses `subsys_initcall()` so the GPIO chip is available before later subsystem users that may rely on board GPIOs.

Risks: no `.get`, `.direction_output`, or `.get_direction` callbacks means consumers mostly use it as an output-only settable GPIO and cannot read back state through normal callbacks. Requiring platform data and fixed `base` limits firmware-description support. The initial double write is needed by the device behavior; a failed SPI write prevents chip registration.

Test signals: board-level or SPI mock tests should verify `bits_per_word` setup, two zero writes during probe, bit updates for offsets 0-7, mutex-serialized concurrent sets, failure on missing platform data, and successful `gpiochip_add_data()` with `can_sleep = true`.
