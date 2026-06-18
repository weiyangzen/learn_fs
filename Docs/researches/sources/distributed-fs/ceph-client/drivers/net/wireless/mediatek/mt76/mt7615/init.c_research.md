# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/init.c

Purpose: common MT7615-family device/PHY initialization, wiphy capability setup, MAC defaults, txpower initialization, LED callbacks, thermal hwmon, and DBDC second-PHY registration.

Important APIs/functions: exports `mt7615_thermal_init()`, `mt7615_wait_for_mcu_init()`, `mt7615_init_txpower()`, `mt7615_init_work()`, `mt7615_reg_map()`, LED blink/brightness callbacks, `mt7615_register_ext_phy()`, `mt7615_unregister_ext_phy()`, and `mt7615_init_device()`. Internal helpers initialize PHY/MAC chains, offload capability, regulatory notifier, wiphy features, and DBDC antenna capabilities.

Control flow: `mt7615_init_device()` wires private PHY pointers, tx worker, PM work, MAC/scan/ROC/coredump work, waitqueues, timers, wiphy defaults, PM timeout, and testmode hooks. `mt7615_init_work()` sends EEPROM to firmware, programs MAC/PHY defaults, clears WTBL, and prunes unsupported offload ops. Starting from regulatory changes or channel changes, txpower is recalculated and sent to firmware when offload is active. DBDC registration can split antenna chains, allocate/register a second mt76 PHY, share queues, install scan/ROC work, and assign a locally administered MAC address.

State and persistence: initializes runtime state for `dev->phy`, `dev->pm`, workqueues, coredump queues, wiphy feature flags, antenna masks, txpower limits, LED registers, and optional second PHY. Thermal reads query firmware and expose millidegree Celsius via hwmon.

Dependencies and integration: ties mac80211 wiphy capabilities to mt76 helpers, MCU commands, EEPROM data, regulatory notifications, LED/hwmon subsystems, and register remapping. `mt7615_reg_map()` programs the PCIe remap register before accessing high physical addresses.

Risks: DBDC registration is refused while running; changing that would require careful queue and interface migration. Offload capability pruning mutates `dev->ops`, so function availability depends on firmware version. Regmap/remap accesses must be serialized. Thermal reads return zero if MCU init has not completed.

Test signals: wiphy reports correct interface combinations, bands, antenna masks, scan limits, and offload features; hwmon `temp1_input` works; regulatory changes update txpower and DFS setup; DBDC debugfs toggling creates/removes a second phy before start; LED callbacks program visible blink/brightness.
