# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/debugfs.c

Purpose: debugfs interface for MT7615/MT7663 runtime inspection and low-level control.

Important APIs/functions: provides debugfs attributes for register read/write (`regval` via mt76 core), radar pattern trigger, chip config, SCS, runtime PM, idle timeout, DBDC toggling, firmware debug logs, reset-test injection, AMPDU stats, radio sensitivity/false CCA, AC queue depth, TX queue status, RF register access, extra MAC address table manipulation, and SDIO scheduler quota. Entry point is `mt7615_init_debugfs()`.

Control flow: most setters first check MCU readiness with `mt7615_wait_for_mcu_init()`, then acquire the driver mutex before sending MCU commands or touching hardware. Runtime PM toggling refuses unsupported firmware/bus combinations and AP beacon activity, wakes the chip, flips `pm->enable`, and reschedules power-save work. DBDC debugfs dynamically registers/unregisters the second PHY. `reset_test` injects a tiny raw skb to exercise reset paths. Read handlers snapshot hardware queues, MIB-derived AMPDU stats, RF registers, or MUAR entries.

State and persistence: writes alter live driver and hardware state: `dev->fw_debug`, `dev->pm.enable`, `dev->pm.idle_timeout`, `dev->muar_mask`, radar test pattern fields, RF register selector fields, and possibly second-PHY registration. Changes are not persistent across driver reload unless firmware or external config preserves them.

Dependencies and integration: uses Linux debugfs/seq_file helpers, mt76 debugfs registration, MCU helpers, MAC SCS controls, RF accessors, PM state, and SDIO scheduler structures. Debugfs files are installed under the mt76 PHY debugfs directory.

Risks: low-level register/RF writes can destabilize hardware. `ext_mac_addr` accepts user-provided entries and programs MUAR hardware directly. Runtime PM and DBDC toggles are constrained but still race-sensitive with running interfaces if external callers bypass expected mac80211 state. Some file operations are unsafe by design (`debugfs_create_file_unsafe`).

Test signals: presence of debugfs files after registration; `regval` read/write against benign registers; `runtime_pm_stats` showing awake/doze transitions; `xmit-queues` and `acq` changing under traffic; `fw_debug` enabling firmware log events; DBDC file registering a secondary PHY only while the device is stopped.
