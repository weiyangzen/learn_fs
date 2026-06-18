# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.c

## Purpose
`core.c` is the central ath11k lifecycle and hardware-parameter implementation. It defines module parameters, the hardware revision table, firmware/board-data lookup, SoC and pdev creation/destruction, firmware boot handoff, suspend/resume policy, crash recovery, reset orchestration, and allocation of the top-level `ath11k_base`.

## Important APIs, Types, And Functions
Exported functions include `ath11k_core_pre_init()`, `ath11k_core_init()`, `ath11k_core_deinit()`, `ath11k_core_alloc()`, `ath11k_core_free()`, `ath11k_core_qmi_firmware_ready()`, firmware/board-data helpers, suspend/resume hooks, recovery preconfiguration, PM notifier unregister, firmware usecase lookup, and fw stats helpers. The `ath11k_hw_params[]` table maps each hardware revision to firmware directory, CE configs, QMI service ID, ring masks, HAL ops, interface modes, monitor/suspend/regdb/CFR capabilities, memory model, and platform quirks. Module parameters include `debug_mask`, `crypto_mode`, `frame_mode`, and `ftm_mode`.

## Control Flow
Bus drivers allocate `ath11k_base`, set `hw_rev` and HIF ops, then call `ath11k_core_pre_init()` to copy matching hardware params and pre-init firmware metadata. `ath11k_core_init()` sets PM policy from DMI quirks, registers a PM notifier, creates QMI/debugfs SoC state, and powers up HIF. When QMI reports firmware ready, `ath11k_core_qmi_firmware_ready()` applies crypto/raw mode flags, starts firmware, initializes CE pipes, allocates DP, starts WMI/HTC/HIF/HTT, waits for service/unified ready events, allocates MAC objects, initializes REO rings, sends WMI init, creates pdev facilities, and enables HIF IRQs. Deinit reverses pdev, core, HIF power, MAC, SoC, and notifier setup.

## State And Persistence
Persistent-on-disk firmware and board data are requested through Linux firmware APIs; runtime state lives in `ath11k_base` and per-radio `ath11k` objects. Board-data resolution tries API2 names with variant, fallback without variant, chip ID, then legacy `board.bin`; regdb lookup has similar API2 then legacy fallback. Suspend state is mediated by `pm_policy` and `actual_pm_policy`. Recovery uses flags, completions, counters, workqueues, and vdev/peer reset state; no driver state persists across unload.

## Dependencies And Integration Points
`core.c` integrates nearly every subsystem: HIF, QMI, WMI, HTC, DP TX/RX, HAL, MAC/mac80211, debugfs, thermal, spectral, CFR, WoW, firmware loader, DMI, OF, regulatory, coredump, and workqueue/completion primitives. It is called by bus modules such as AHB/PCI and in turn calls feature modules during pdev creation and cleanup.

## Risks And Test Signals
The highest risks are ordering-sensitive startup/teardown, hardware param drift, firmware file lookup regressions, crash recovery races, and suspend/resume corner cases. Error labels often unwind partially initialized subsystems; tests should exercise failure injection at WMI attach, HIF start, service ready, DP allocation, pdev create, and firmware start. Runtime signals include clean boot on each hw revision, board/regdb fallback logs, mac80211 registration, WoW/default suspend resume, repeated firmware crash recovery without wedging, coredump collection, and lockdep checks for `core_lock`, `conf_mutex`, and base/data locks.
