# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.h

## Purpose
`core.h` is the shared ath11k object model. It defines global constants, enums, skb control blocks, vif/sta/radio/SoC state, firmware stats, debug state, PCI ops, MSI config, PM policy, and prototypes for core lifecycle and firmware helpers.

## Important APIs, Types, And Functions
Major enums cover supported bandwidth, BDF search mode, WME ACs, crypto mode, skb flags, hardware revisions, firmware modes, scan/11d states, device flags, monitor flags, packet/stat counters, ath11k radio state, and PM policy. Core types include `ath11k_skb_cb`, `ath11k_skb_rxcb`, `ath11k_ext_irq_grp`, `ath11k_smbios_bdf`, `ath11k_he`, `ath11k_vif`, `ath11k_sta`, `ath11k`, `ath11k_pdev`, `ath11k_board_data`, `ath11k_pci_ops`, MSI structs, and `ath11k_base`. Inline helpers map TID to AC, convert mac80211 private objects, map MAC ID to radio, build firmware paths, stringify bus and scan states, and expose skb control blocks.

## Control Flow
The header enables all ath11k modules to share a common state graph. Bus drivers allocate `ath11k_base`; core creates per-radio `ath11k`; MAC code stores `ath11k_vif` and `ath11k_sta` in mac80211 private areas; CE/DP/WMI/QMI/debug/coredump modules read or update fields under documented locks and completions. Firmware path creation consults device tree `firmware-name`, usecase firmware mapping, and hardware firmware directories.

## State And Persistence
`ath11k_base` holds SoC-wide state: HIF bus/ops, QMI/WMI/HTC/DP/CE/HAL state, IRQ arrays, ext IRQ groups, hardware params, firmware data, coredump buffer, peer tables, regulatory domains, workqueues, reset/recovery counters, direct-buffer capabilities, MSI data, and private transport storage. `ath11k` holds per-radio mac80211 state, scan/vdev/peer/key completions, locks, tx management IDR, survey/regulatory work, WoW, debug, spectral, thermal, CFR, firmware stats, and power-save fields. State is volatile except firmware files requested through the kernel firmware loader.

## Dependencies And Integration Points
The header pulls in QMI, HTC, WMI, HAL, DP, CE, MAC, HW, RX, regulatory, thermal, DBRing, spectral, WoW, firmware, coredump, and CFR headers. That makes it a high-fanout integration point and a source of compile coupling across the driver.

## Risks And Test Signals
Risk comes from structure size/layout expectations, lock ownership comments that implementations must honor, feature-guarded fields, and helper assumptions such as skb control-block size. Changes need broad build coverage across config combinations (`DEBUGFS`, `SPECTRAL`, `CFR`, testmode), runtime smoke on PCI/AHB buses, mac80211 attach/detach tests, and lockdep/KASAN coverage for peer/vif/radio lifetimes.
