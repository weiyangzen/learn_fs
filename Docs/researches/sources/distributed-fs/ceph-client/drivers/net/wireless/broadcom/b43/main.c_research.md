# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.c

## Purpose
`main.c` is the central Broadcom b43 mac80211 driver implementation. It registers the BCMA, SSB, and SDIO-facing driver entry points, builds the mac80211 `ieee80211_ops` table, manages firmware loading and upload, initializes and resets wireless cores, services interrupts, handles TX/RX queueing, programs shared memory and template RAM, manages hardware keys, and coordinates common PHY operations through the `struct b43_phy_operations` vtable.

## Important APIs, Types, and Functions
- Module parameters control runtime behavior: firmware postfix, hardware power control, hardware crypto/TKIP, QoS, Bluetooth coexistence, verbosity, PIO forcing, and broad hardware support gating.
- Device tables `b43_bcma_tbl` and `b43_ssb_tbl` match 802.11 cores by BCMA/SSB revision.
- Shared-memory and timing helpers include `b43_shm_read16/32`, `b43_shm_write16/32`, `b43_hf_read`, `b43_hf_write`, `b43_tsf_read`, and `b43_tsf_write`.
- Core and MAC lifecycle functions include `b43_wireless_core_reset`, `b43_wireless_core_init`, `b43_wireless_core_start`, `b43_wireless_core_stop`, `b43_wireless_core_exit`, `b43_mac_suspend`, `b43_mac_enable`, and `b43_controller_restart`.
- Firmware paths include `b43_do_request_fw`, `b43_try_request_fw`, `b43_request_firmware`, `b43_upload_microcode`, `b43_write_initvals`, and the release helpers.
- mac80211 entry points are gathered in `b43_hw_ops`: TX, interface add/remove, config, BSS changes, filter configuration, key setup, TSF, start/stop, scan notifications, survey, and rfkill polling.
- Interrupt handling is split between `b43_do_interrupt` top-half collection/ACK and `b43_do_interrupt_thread` threaded work, with an SDIO process-context variant.
- Hardware encryption helpers program key table memory, RCMTA MAC slots, default RX/TX keys, and TKIP phase-1 state.
- Static channel/rate tables publish 2.4 GHz, 5 GHz A-PHY, full N-PHY 5 GHz, and limited channel variants to mac80211.

## Control Flow
Module init initializes debugfs and SDIO support, then registers BCMA and/or SSB bus drivers. Probe allocates a `b43_bus_dev`, creates the mac80211 `ieee80211_hw`, attaches one wireless core, and schedules asynchronous firmware loading. Firmware loading first tries proprietary firmware, then open firmware, maps core revision and PHY type to microcode/initvals filenames, validates firmware headers, registers the mac80211 hardware, registers LEDs, and optionally registers an hwrng.

Attach-time core discovery powers the bus, resets the core enough to read PHY/radio versioning, determines supported bands, allocates the PHY-specific private state, validates chip access, sets band tables, disables analog, and powers down. Runtime start clears per-instance state, initializes the wireless core if needed, requests IRQs, enables MAC/data flow, starts periodic work, then reloads mac80211 configuration. Stop cancels beacon/TX/txpower work, disables IRQs, frees IRQs, drains TX queues, suspends MAC, releases LED state, exits the PHY/chip, disables the core, and lets the bus power down.

Interrupt flow disables device IRQs in the top half after reading and ACKing generic and DMA reason registers. The thread handles fatal DMA fallback to PIO, firmware debug/panic IRQs, TBTT/ATIM/PMQ/beacon/noise interrupts, RX processing through DMA or PIO, TX status completion, and finally restores the current IRQ mask.

## State and Persistence
Persistent driver state lives in `struct b43_wl` and `struct b43_wldev`: current core, status, interface mode, BSSID/MAC, beacon templates, TX queues, filter flags, QoS parameters, firmware metadata, key slots, IRQ masks/reasons, PHY state, noise samples, and statistics. Firmware blobs are cached in `dev->fw` until core detach, not re-requested on every init. Hardware state is persisted into MMIO registers, shared memory, template RAM, key table memory, and RCMTA. The file uses `wl->mutex` for most lifecycle and mac80211 state, `hardirq_lock` for non-SDIO interrupt top halves, and `beacon_lock` around the current beacon skb.

## Dependencies and Integration Points
- Integrates with mac80211/cfg80211 through `ieee80211_alloc_hw`, `ieee80211_register_hw`, queue control, beacon generation, key callbacks, channel configuration, and survey reporting.
- Depends on b43 subsystems: PHY modules, DMA, PIO, xmit, debugfs, sysfs, LEDs, SDIO, local oscillator, and firmware/initvals definitions.
- Integrates with Linux firmware loading APIs, BCMA/SSB bus control, optional hwrng, rfkill polling, workqueues, SKB queues, and IRQ threading.
- Shares register and SHM contracts with firmware; many helpers write fixed offsets such as host flags, channel cookie, QoS parameter blocks, beacon template metadata, and microcode status registers.

## Risks and Edge Cases
- Firmware filename selection is a large matrix of core revision and PHY type; unsupported or newly added hardware fails with `-EOPNOTSUPP` unless this mapping and versioning logic are updated.
- Hardware key programming differs between old and new key-index APIs; pairwise, default RX, and TKIP phase-1 slots must stay synchronized or decryption can silently fail.
- IRQ stop/start code deliberately unlocks `wl->mutex` around work cancellation and IRQ freeing, so it revalidates `wl->current_dev`; regressions here can race device removal or restart.
- Fatal DMA errors permanently set `dev->use_pio = true` and restart the controller, so repeated DMA faults shift the data path and should be visible in performance and logs.
- Beacon template updates are asynchronous and double-buffered; incorrect valid-bit or IRQ-mask handling can upload partial beacons while firmware is transmitting.
- Power saving is partly stubbed and currently forces awake with hardware power save off, so future power-save work must revisit assumptions in TBTT, PHY locking, and `b43_power_saving_ctl_bits`.
- AC-PHY hardware is accepted by versioning, but the companion AC ops are skeletal; null callbacks used by common init paths are a high-risk integration gap if AC support is enabled.

## Test Signals
- Build coverage should compile BCMA, SSB, SDIO, DMA, PIO, hardware crypto, and each enabled PHY variant.
- Probe/start/stop smoke tests should cover firmware absence, proprietary and open firmware, initvals format errors, IRQ request/free, DMA-to-PIO fallback, and suspend/resume-like stop/start cycles.
- mac80211 tests should exercise add/remove interface, AP/mesh/IBSS beacon updates, channel/band changes, retry limits, QoS parameter updates, hardware key setup/removal, TKIP key refresh, scan start/complete, and rfkill polling.
- Runtime signals include firmware version logs, "Microcode not responding", firmware watchdog/panic, fatal DMA messages, unsupported PHY/radio logs, and survey noise updates.
