# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/debugfs.c

## Purpose
This file exposes MT7921 diagnostics and developer controls through debugfs. It provides register read/write, firmware logging control, TX statistics, TX power table dumps, runtime PM and deep sleep toggles, chip reset triggering, queue views, PM statistics, and SDIO scheduler quota reporting.

## Important APIs, Types, And Functions
The public entry point is `mt7921_init_debugfs()`. Register access is implemented by `mt7921_reg_get()` and `mt7921_reg_set()` through `fops_regval`. Firmware logging uses `mt7921_fw_debug_get/set()` and calls `mt7921_mcu_fw_log_2_host()`. Power controls are `mt7921_pm_get/set()` and `mt7921_deep_sleep_get/set()`. Reset control is `mt7921_chip_reset()`, which either resets directly or asks firmware to collect a coredump/chip config first. `mt7921_txpwr()` prints rate-indexed user/eeprom/TMAC power limits via `mt7921_get_txpwr_info()`.

## Control Flow
Initialization registers the mt76 debugfs root and conditionally chooses MMIO queue dumping (`mt792x_queues_read`) versus generic queues (`mt76_queues_read`). It adds AC queue, TX power, TX stats, firmware debug, runtime PM, idle timeout, chip reset, runtime PM stats, deep sleep, and SDIO-only scheduler quota files. Setters acquire the mt792x mutex before touching hardware or PM state. Runtime PM toggling wakes the chip, updates user policy, calls `mt7921_set_runtime_pm()`, and reschedules power save.

## State And Persistence
Debugfs values modify live driver state: `dev->fw_debug`, `dev->pm.enable_user`, `dev->pm.ds_enable_user`, `pm->enable`, `pm->ds_enable`, PM timestamps, deep sleep firmware state, and the selected `debugfs_reg` inherited from mt76. The files are transient and disappear when the device is unregistered. Reset may trigger firmware coredump state before hardware reset.

## Dependencies And Integration Points
The code depends on Linux debugfs/seq_file helpers, mt76 debugfs registration, mt792x queue and PM helpers, MCU firmware-log/deep-sleep/chip-config commands, and SDIO scheduler state. It is invoked after common device registration in `init.c`.

## Risks
Debugfs controls bypass normal user policy and can reset the chip or disable power saving. Register writes can corrupt live hardware state. PM setters must avoid USB, where runtime/deep sleep controls return `-EOPNOTSUPP`. Monitor mode blocks deep sleep, so debugfs state and actual firmware state can differ intentionally. TX power dump formatting assumes firmware event layout matches `struct mt7921_txpwr`.

## Test Signals
Read/write `regidx`/`regval`, toggle `fw_debug`, `runtime-pm`, `deep-sleep`, and `idle-timeout`, read TX power and queue files on PCI/SDIO/USB variants, trigger chip reset with and without coredump collection, and validate SDIO `sched-quota` appears only for SDIO. Lockdep should not report mutex inversions during debugfs operations.
