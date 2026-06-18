# sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-yoga-c630.c

Purpose: core I2C EC driver for Lenovo Yoga C630. It exports serialized register and UCSI helpers, forwards EC events through a notifier chain, and creates auxiliary PSY and UCSI devices.

Important APIs, types, and functions: `struct yoga_c630_ec` stores the I2C client, mutex, and notifier chain. Exported functions include `yoga_c630_ec_read8()`, `yoga_c630_ec_read16()`, `yoga_c630_ec_ucsi_get_version()`, `yoga_c630_ec_ucsi_write()`, `yoga_c630_ec_ucsi_read()`, and notifier register/unregister helpers. `yoga_c630_ec_request()` writes a request block and reads a response block under caller-held lock. `yoga_c630_ec_thread_intr()` retrieves the next event and calls the notifier chain.

Control flow: register reads build command buffers and call the shared request helper while holding `ec->lock`; `read16()` reads adjacent bytes little-endian style and rejects address `0xff`. UCSI data uses dedicated SMBus block read/write commands. Probe allocates state, initializes mutex/notifier, requests threaded IRQ, and creates auxiliary devices for PSY and UCSI via `devm_auxiliary_device_create()`.

State and persistence: all EC-visible state is firmware-owned. Kernel state is limited to serialization and notifier registration. Auxiliary consumers receive the EC pointer.

Dependencies and integration points: uses I2C SMBus block transfers, auxiliary bus, blocking notifiers, and platform data in `linux/platform_data/lenovo-yoga-c630.h`. OF compatible is `lenovo,yoga-c630-ec`.

Risks and edge cases: `yoga_c630_ec_request()` returns raw SMBus block-read byte count rather than checking it equals the requested response length. UCSI write/read similarly normalize only negative errors, not short transfers. Notifier events are untyped bytes and consumers must interpret them consistently. There are no PM hooks in this core file.

Test signals: verify PSY and UCSI auxiliary drivers bind, EC read8/read16 return known registers, UCSI version/read/write work, IRQ notifiers fire, and short-transfer behavior is acceptable on target adapters.
