# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_spi.c

Purpose: Implements the WFx SPI bus driver and maps SPI transfers, reset GPIO, IRQ, alignment, and PM wakeup into `wfx_hwbus_ops`.

Important APIs and functions: `wfx_spi_copy_from_io()` and `wfx_spi_copy_to_io()` build 16-bit register/length words with read/write markers, optionally byte-swap for 8-bit SPI or big-endian CPUs, and issue `spi_sync()`. IRQ subscription uses a threaded IRQ and calls `wfx_bh_request_rx()`. Probe sets default 16 bits/word, loads platform data from SPI ID, obtains optional reset GPIO, toggles reset, initializes common WFx state, and calls `wfx_probe()`. PM callbacks enable/disable IRQ wake.

Control flow and integration: SPI has no explicit bus lock beyond empty lock/unlock ops; HWIO serializes through the call path and SPI core transfers. Common probe handles firmware loading, IRQ subscription through these ops, and mac80211 registration.

State and persistence: `struct wfx_spi_priv` stores the SPI device, WFx core pointer, optional reset GPIO, and `need_swab` byte-order mode. Platform data provides firmware/PDS names and rising-clock preference.

Dependencies: Depends on Linux SPI, GPIO, IRQ, PM, OF/device IDs, and WFx common code. Compatible strings are matched for OF, while dynamic binding uses stripped modalias IDs.

Risks and test signals: Risks include in-place byte swapping of `const` TX buffers for config writes, unsupported bits-per-word, excessive SPI clock, missing reset GPIO, IRQ trigger mismatch, and byte-order mistakes. Tests should cover 8-bit and 16-bit controllers, big-endian builds, reset GPIO present/absent, IRQ wake suspend/resume, all compatible IDs, and firmware boot over SPI.

Test signals: Source read size: 321 lines, 8377 bytes.
