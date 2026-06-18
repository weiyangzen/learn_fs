# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.h

Purpose: Defines wl1251 hardware access window constants and inline 32-bit/ELP IO helpers.

Important APIs and types: Defines `HW_ACCESS_MEMORY_MAX_RANGE`, partition control addresses, `HW_ACCESS_PRAM_MAX_RANGE`, `wl1251_read32()`, `wl1251_write32()`, `wl1251_read_elp()`, `wl1251_write_elp()`, memory/register access prototypes, and `wl1251_set_partition()`.

Control flow: Inline read/write helpers directly call `wl->if_ops`. `wl1251_read32()` uses `wl->buffer_32` and converts little-endian data to CPU order; `wl1251_write32()` performs the inverse. ELP helpers call specialized bus hooks when present and fall back to regular bus read/write otherwise.

State and persistence: Uses transient buffers in `struct wl1251` (`buffer_32`) for 32-bit access. ELP access may update bus-private state in SDIO because the SDIO backend caches the last ELP write value.

Dependencies and integration points: Depends on bus implementations filling `wl1251_if_operations`. Included by boot, power-save, RX/TX, command, and main logic.

Risks: Fallback ELP writes pass CPU-endian `u32` directly to bus write, unlike `wl1251_write32()`; this is tied to bus/hardware expectations and should be changed only with hardware validation. Inline helpers assume serialized access to shared buffers, usually via `wl->mutex`.

Test signals: ELP wake/sleep reliability, boot register reads, and interrupt handling are direct indicators for this layer.
