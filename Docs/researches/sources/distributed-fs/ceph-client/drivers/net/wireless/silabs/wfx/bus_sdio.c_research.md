# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bus_sdio.c

Purpose: Implements the WFx SDIO bus driver and maps SDIO register/IRQ/PM operations into `wfx_hwbus_ops`.

Important APIs and functions: `wfx_sdio_copy_from_io()` and `wfx_sdio_copy_to_io()` access SDIO register IDs shifted by two and use queue-mode buffer IDs for `WFX_REG_IN_OUT_QUEUE`. `wfx_sdio_irq_subscribe()` supports both SDIO function IRQ and out-of-band DT IRQ; `wfx_sdio_irq_unsubscribe()` tears them down. Probe validates function 1, matches DT platform data, enables the function, sets 64-byte block size, initializes common WFx state, and calls `wfx_probe()`. PM callbacks keep power and enable IRQ wake for WoWLAN-capable devices.

Control flow and integration: On IRQ, the handler calls `wfx_bh_request_rx()`. Probe stores `struct wfx_sdio_priv` as SDIO drvdata, passes `wfx_sdio_hwbus_ops` to `wfx_init_common()`, then lets common probe load firmware and register mac80211. Remove calls `wfx_release()` and disables the SDIO function.

State and persistence: `struct wfx_sdio_priv` tracks function pointer, core device, TX/RX queue buffer IDs, and optional OF IRQ. Queue buffer IDs wrap independently across RX modulo 4 and TX modulo 32.

Dependencies: Depends on Linux MMC/SDIO, OF IRQ parsing, device PM, WFx HWIO/BH/main, and Device Tree compatible data selecting firmware/PDS names.

Risks and test signals: Risks include wrong function number, missing DT compatible, out-of-band IRQ cleanup calling both free IRQ and `sdio_release_irq()`, queue buffer ID wrap bugs, alignment assumptions, and suspend without wake capability. Tests should cover DT compatibles, SDIO-only IRQ and external IRQ, PM keep-power/wake flags, block-size behavior, probe failure cleanup, and remove while BH work may be active.

Test signals: Source read size: 326 lines, 7985 bytes.
