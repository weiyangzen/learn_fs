# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_spi.c

Purpose: SPI bus front-end for CW1200 hardware. It adapts CW1200 register accesses to SPI framing, manages GPIO power/reset, IRQ wake, and shared core registration.

Important APIs and functions: Defines `struct hwbus_priv`, `cw1200_spi_memcpy_fromio`, `cw1200_spi_memcpy_toio`, custom lock/unlock functions, threaded IRQ handler, IRQ subscribe/unsubscribe, `cw1200_spi_on/off`, alignment and PM callbacks, `cw1200_spi_probe`, `cw1200_spi_disconnect`, suspend hook, and the `spi_driver`.

Control flow: Probe clamps SPI speed to 1-52 MHz, sets bits-per-word from platform data or defaults to 16, requests GPIOs, powers hardware, calls `spi_setup`, subscribes IRQ, and invokes `cw1200_core_probe`. Register reads/writes build a 16-bit command header and run `spi_sync`. Disconnect unsubscribes IRQ, releases core, and powers off.

State and persistence: Per-SPI-device `hwbus_priv` tracks SPI device, core, platform data, GPIOs, a spinlock-protected claimed flag, and a wait queue used as a sleeping bus mutex.

Dependencies and integration: Depends on SPI, GPIO descriptors, threaded IRQs, platform data, and shared CW1200 core/hwbus APIs.

Risks: `cw1200_spi_memcpy_toio` temporarily byte-swaps the source buffer in place for 8-bit or big-endian transfers, which is risky if callers pass immutable or shared data. Probe does not check `plat_data` for NULL before dereferencing. The consumer name for `powerup` mistakenly uses `self->reset`. IRQ subscription status is overwritten by core probe status. Locking is custom and must not be used in hard IRQ context.

Test signals: SPI transfer tests with 8-bit and 16-bit modes, endian-sensitive register read/write validation, IRQ wake suspend path, missing platform-data failure behavior, and module unload/reload with GPIO state inspection.
