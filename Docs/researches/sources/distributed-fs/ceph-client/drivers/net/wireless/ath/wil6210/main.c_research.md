# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/main.c

## Purpose
`main.c` is the central lifecycle and hardware-control file for wil6210. It defines module parameters, 32-bit MMIO copy helpers, reset/up/down flows, firmware recovery, connection teardown, TX ring allocation, broadcast ring management, private-state initialization, boot-loader interaction, firmware capability refresh, scan abort, power-save update, and HALP voting.

## Important APIs, Types, And Functions
Public functions include `wil_memcpy_fromio_32()`, `wil_memcpy_toio_32()`, `wil_mem_access_lock()`, `wil_ring_init_tx()`, `wil_bcast_init()`, `wil_bcast_fini_all()`, `wil_priv_init()`, `wil6210_disconnect()`, `wil6210_disconnect_complete()`, `wil_priv_deinit()`, `wil_refresh_fw_capabilities()`, `wil_mbox_ring_le2cpus()`, `wil_get_board_file()`, `wil_clear_fw_log_addr()`, `wil_reset()`, `wil_fw_error_recovery()`, `__wil_up()`, `wil_up()`, `__wil_down()`, `wil_down()`, `wil_find_cid()`, `wil_halp_vote()`, `wil_halp_unvote()`, and `wil_init_txrx_ops()`.

## Control Flow
The primary control path is reset. `wil_reset()` requires `wil->mutex`, blocks device memory access through `mem_lock`, aborts scans, disconnects VIFs, disables LEDs, masks/flushed IRQ/WMI/service work, resets hardware, reloads firmware and board data when requested, releases CPUs, waits for WMI ready, checks `wmi_echo()`, configures interrupt moderation, restores VIF ports, refreshes firmware-derived capabilities, and notifies platform firmware-ready. `__wil_up()` calls reset with firmware load, initializes RX/TX, sets interface type, programs MAC, enables NAPI, and requests bus bandwidth. `__wil_down()` disables NAPI/IRQ activity, stops radio operations and scans, then resets without firmware load.

## State And Persistence
The file initializes core `wil6210_priv` state: station table locks, ring metadata, mutexes, completions, workqueues, WMI queues, PM/suspend counters, EDMA defaults, aggregation limits, wake triggers, VIF limits, and recovery counters. Reset mutates firmware version, firmware capabilities, hardware status bits, station/ring state, VIF connection flags, and device registers.

## Dependencies And Integration Points
It integrates with WMI, cfg80211, netdev, TX/RX backend ops, firmware loading, boot-loader register layouts, platform operations, interrupts, PM, P2P, and debugfs recovery controls. The 32-bit IO helpers are used across firmware, mailbox, debugfs, and PMC paths.

## Risks
Reset/recovery is high blast radius. Lock ordering among `wil->mutex`, `vif_mutex`, `wmi_mutex`, `mem_lock`, NAPI synchronization, and workqueue flushes must remain consistent. Firmware recovery has retry limits and manual mode via `no_fw_recovery`. Hardware generation branches for Sparrow/Talyn/Talyn-MB must not drift. Early returns in secured-boot or load failures must release `mem_lock` and clear status bits correctly.

## Test Signals
Test cold probe reset, up/down cycles, firmware reload failures, no-flash OTP MAC paths, boot-loader MAC paths, WMI-only/debug-fw modes, firmware crash recovery, manual recovery through debugfs, scan/connect timeouts, VIF restore after reset, HALP timeout, and lockdep during concurrent suspend/remove/reset.
