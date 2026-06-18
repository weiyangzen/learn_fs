# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/init.c

Purpose: MT7925 common hardware/device initialization. It initializes firmware/eeprom/MAC, mac80211 capabilities, work items, PM defaults, debugfs, hwmon thermal reporting, thermal protection, and deferred device registration.

Important APIs/types/functions: `mt7925_mac_init()` programs MDP RX length, enables de-aggregation, clears WTBL admission counters, initializes bands and basic rate table, and clears regulatory alpha2. `mt7925_register_device()` wires mt76/mac80211 state and queues `init_work`. `mt7925_init_work()` runs hardware init, capability setup, MLO setup, `mt76_register_device()`, debugfs, hwmon, thermal protection, and deep sleep. `mt7925_thermal_temp_show()` exposes MCU temperature in millidegrees C.

Control flow: registration initializes `dev->phy`, mt76 private pointers, worker functions, delayed work, waitqueues, locks, scan/coredump queues, reset/ROC/timers, PM defaults, ACPI SAR, WCIDs, wiphy settings, band capabilities, antennas, regulatory notifier, then queues deferred initialization. Hardware init retries MCU/eeprom/MAC setup up to `MT792x_MCU_INIT_RETRY_COUNT`, resetting between attempts.

State/persistence: initializes workqueues, timers, skb queues, PM flags, `MT76_STATE_INITIALIZED`, `hw_init_done`, coredump queues, scan queues, runtime/deep-sleep defaults, wiphy bands/capabilities, thermal hwmon device, and firmware-backed thermal/deep-sleep settings.

Dependencies/integration: uses firmware loading through `mt792x_mcu_init()` and MT7925 MCU helpers, mt76 EEPROM override, mt76 registration/wiphy/WCID helpers, mac80211 capabilities, hwmon, thermal, ACPI SAR, debugfs, regd notifier, coredump, and IPv6 neighbor-solicitation offload work when enabled.

Risks: deferred `init_work` means probe can return before registration completes; failure paths log and stop but do not always unwind already initialized work items. Hardware init retry depends on bus-specific reset working. Thermal and debugfs registration failures prevent later setup but not earlier resource creation.

Test signals: cold probe, firmware init retry after injected failure, debugfs/hwmon availability, thermal readout, PM defaults on USB versus non-USB, MLO capability registration, and successful `mt76_register_device()` with correct HE/EHT/antenna capabilities.
