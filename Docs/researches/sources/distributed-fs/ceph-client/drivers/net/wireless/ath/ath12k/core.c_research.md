# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.c

## Purpose
Owns ath12k device lifecycle: module parameters, firmware and board-data loading, QMI firmware-ready handling, CE/DP/WMI/HTC startup, mac80211 group registration, MLO setup, suspend/resume, crash recovery, reset coordination, SMBIOS/DT grouping, panic notification, and final allocation/free.

## Important APIs, Types, And Functions
Exports `ath12k_debug_mask`, `ath12k_ftm_mode`, suspend/resume functions, firmware/board/regdb fetch helpers, peer/station capacity helpers, reserved memory lookup, `ath12k_core_qmi_firmware_ready()`, recovery helpers, group cleanup/unassign, MLO capability setup, firmware stats init/free/reset, memory mode selection, `ath12k_core_pre_init()`, `ath12k_core_init()`, `ath12k_core_deinit()`, `ath12k_core_alloc()`, and `ath12k_core_free()`. Internal work functions handle RFKill, 11d updates, restart, and reset.

## Control Flow
Probe allocates `ath12k_base`, registers panic handling, assigns the device to a hardware group, and once every group member is probed powers up SOCs through QMI/HIF. Firmware-ready starts firmware, initializes CE pipes and common DP, starts WMI/HTC/HIF, waits for service/unified-ready events, initializes REO and HTT, marks the base started, and starts the whole group when all devices are ready. Group start allocates/registers mac80211 hardware, sets up MLO if supported, creates pdev resources, enables IRQs, and configures rfkill. Teardown reverses those layers. Reset collects coredump data, flushes queues/completions, powers devices down, waits for group partners, resets MLO memory, and powers group members back up for restart.

## State And Persistence
Uses global `ath12k_hw_group_list` under `ath12k_hw_group_mutex`. Per-device state lives in `ath12k_base`: flags, completions, workqueues, QMI/WMI/HTC/DP/CE/HAL objects, pdev arrays, regulatory data, firmware files, debug/coredump state, ACPI/SMBIOS data, and group links. Group state tracks number of devices probed/started, registered flags, MLO memory, WSI DT nodes, and mac80211 hardware objects.

## Dependencies And Integration Points
Integrates with Linux module params, firmware loader, remoteproc/devicetree/SMBIOS/ACPI, panic notifiers, HIF bus ops, QMI, HAL, CE, DP, HTC, WMI, mac80211, regulatory, thermal, debugfs, WOW, peer tables, and coredump.

## Risks
Startup and recovery are heavily ordered; missing cleanup on partial failure can leave firmware, IRQs, DP rings, or group refs inconsistent. Grouping by DT WSI nodes and MLO readiness depends on all devices following the same state transitions. Reset throttling protects against infinite recovery but can leave hardware wedged. Board-data matching parses firmware TLVs and must reject malformed lengths. Suspend/resume only proceeds for supported devices with hardware off, so state predicates must remain accurate.

## Test Signals
Probe on single-device and multi-device MLO hardware, firmware API1/API2 board fallback, regdb fallback, rfkill-capable targets, suspend/resume, simulated firmware assert, repeated crash recovery, and module unload are key signals. Lockdep should cover group/core mutex ordering; firmware logs and mac80211 registration indicate successful lifecycle sequencing.
