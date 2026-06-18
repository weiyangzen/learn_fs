# sources/distributed-fs/ceph-client/drivers/bluetooth/btmtksdio.c

## Purpose
Implements the MediaTek Bluetooth-over-SDIO HCI transport. It binds MT7663/MT7668/MT7921/MT7902 SDIO functions, manages SDIO ownership and runtime PM, downloads firmware through shared WMT helpers, frames HCI packets with a MediaTek SDIO header, processes interrupt-driven TX/RX, supports wakeup and reset behavior, and configures SCO offload for MT7921-class devices.

## Important APIs, Types, And Functions
- `struct btmtksdio_data` describes per-chip firmware, chip ID, low-power mailbox support, and runtime PM support; `struct btmtksdio_dev` stores live HCI/SDIO state.
- `mtk_hci_wmt_sync` is the SDIO implementation of the shared MediaTek WMT sync callback.
- `btmtksdio_open`/`close` enable the SDIO function, claim IRQs, configure interrupt registers, and transfer ownership between driver and firmware.
- `btmtksdio_txrx_work`, `btmtksdio_interrupt`, `btmtksdio_tx_packet`, and `btmtksdio_rx_packet` implement interrupt-bottom-half TX/RX.
- `mt76xx_setup`, `mt79xx_setup`, and `btmtksdio_setup` drive firmware download, function enablement, runtime PM, SCO, reset pin setup, and HCI quirks.
- PM callbacks `btmtksdio_runtime_suspend`/`resume` and system suspend/resume transfer ownership and mark BT wake state.

## Control Flow
Probe allocates `btmtksdio_dev`, initializes work/queues, allocates an HCI device, wires HCI callbacks, registers the device, normalizes runtime PM state, initializes wakeup, and optionally obtains a reset GPIO. Open enables the SDIO function, claims driver ownership, disables/masks interrupts, claims the SDIO IRQ, sets block size, configures synchronous interrupts and write-one-clear status, enables RX/TX interrupt sources, and enables interrupts. IRQ disables further interrupts and schedules `txrx_work`; the worker gets runtime PM, claims the SDIO host, acknowledges current interrupt status, services mailbox/ownership/TX-ready/RX-done bits, sends one queued skb when hardware is ready, reads complete SDIO packets, then re-enables interrupts. Setup sets TX-ready, performs chip-specific firmware flow, configures SCO/pinmux/reset for MT7921/MT7902, and enables autosuspend policy.

## State And Persistence
Persistent state includes `tx_state` bits for WMT waits, TX readiness, function enabled, patch enabled, reset active, and BT wake; the skb TX queue; an event clone for WMT waiters; optional reset GPIO; chip metadata; and runtime PM state on `bdev->dev`. Firmware-loaded state is represented by `BTMTKSDIO_PATCH_ENABLED` and by controller state after WMT function enablement. No host-side firmware image is retained after setup.

## Dependencies And Integration Points
Depends on SDIO/MMC APIs, PM runtime, GPIO/device tree, HCI core, shared MediaTek helpers in `btmtk.h`, H4 packet metadata, and Bluetooth codec offload hooks. Integrates with SDIO device IDs, system wakeup, HCI non-persistent setup, Microsoft/AOSP vendor capabilities, and eSCO codec offload callbacks.

## Risks And Edge Cases
`btmtksdio_txrx_work` uses `time_is_before_jiffies(txrx_timeout)` in its loop condition, which appears inverted for a "run until timeout" pattern and may affect drain behavior. WMT event parsing assumes `bdev->evt_skb` is present and large enough after the wait. Runtime PM and ownership transitions must not be called recursively while the SDIO host is already claimed; some paths call ownership helpers after claiming the host. Reset handling must restore firmware ownership when reset occurs while the function is closed. Packet padding removal depends on accurate H4 header metadata and SDIO length fields.

## Test Signals
Exercise probe/open/setup/close/remove for each SDIO ID, MT76xx and MT79xx firmware paths, WMT timeouts/wrong events, TX FIFO overflow, RX packet length/type/padding errors, runtime suspend/resume ownership polling, system wakeup interrupt behavior, reset GPIO path on MT7921, SCO codec offload config for CVSD/mSBC, and autosuspend enabled/disabled module parameter.
