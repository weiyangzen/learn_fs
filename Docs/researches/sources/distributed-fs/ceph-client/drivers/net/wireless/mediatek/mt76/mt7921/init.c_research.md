# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/init.c

## Purpose
This file initializes MT7921 common hardware and mac80211 registration. It handles thermal hwmon exposure, regulatory domain updates, MAC hardware setup, firmware/eeprom init retry, asynchronous common device registration, power-save defaults, wiphy capability tweaks, workqueue setup, and stream capability publication.

## Important APIs, Types, And Functions
The exported registration function is `mt7921_register_device()`. It initializes `struct mt792x_dev` and `struct mt792x_phy` members, work items, wait queues, PM state, ACPI SAR, WCID table, wiphy, regulatory notifier, HT/VHT/HE capabilities, antenna availability, and queues `mt7921_init_work()`.

Hardware helpers include `mt7921_mac_init()`, `__mt7921_init_hardware()`, and `mt7921_init_hardware()`. Regulatory helpers are `mt7921_regd_update()`, `mt7921_regd_notifier()`, and `mt7921_regd_channel_update()`. Thermal support is implemented by `mt7921_thermal_temp_show()` and `mt7921_thermal_init()`.

## Control Flow
Transport probe calls `mt7921_register_device()`, which prepares software state and queues asynchronous init work. `mt7921_init_work()` retries firmware/eeprom/MAC initialization through `mt7921_init_hardware()`, sets stream and HE capabilities, configures MAC addresses, registers the mt76 device with mac80211, initializes debugfs, registers hwmon temperature input, marks `hw_init_done`, and applies initial deep sleep state.

Hardware init forces `MT_SWDEF_MODE` to normal, runs bus-specific MCU init through `mt792x_mcu_init()`, applies EEPROM overrides, sends EEPROM mode to firmware, and initializes MAC registers. Regulatory notifications update alpha2/DFS/environment, optionally set country-IE ignore behavior, skip work while suspended, then push CLC, channel-domain, and SAR power changes under the driver mutex.

## State And Persistence
The file initializes persistent driver state: PM work and flags, reset/init/scan/coredump/ROC work, IPv6 NS queue, scan/coredump queues, wait queues, `pm.idle_timeout`, country/region fields, `regd_in_progress`, thermal hwmon device, and hardware initialization state. Regulatory channel-disable decisions persist in wiphy channel flags until rebuilt. Firmware state includes EEPROM buffer mode, MDP/MAC config, channel domain, CLC, SAR power, and deep sleep.

## Dependencies And Integration Points
It depends on mac80211/cfg80211, hwmon, firmware, ACPI SAR, mt792x common helpers, mt76 EEPROM override, MCU helpers from `mcu.c`, MAC helpers from `mac.c`, debugfs, coredump, and transport-specific HIF ops installed before registration.

## Risks
Registration is asynchronous, so remove paths must cancel `init_work`. Hardware init retry relies on transport reset hooks being safe before full registration. Regulatory updates race with suspend and are guarded by `regd_in_progress`; suspend paths wait for that flag. Channel disabling combines CLC firmware data and device tree power-limit nodes, so missing or wrong DT entries can disable bands. hwmon temperature reads call firmware under the mutex and may fail during reset/suspend.

## Test Signals
Probe on PCI/SDIO/USB, firmware init retry after injected failure, mac80211 registration, debugfs/hwmon creation, temperature reads, regulatory alpha2 changes, country IE handling, 5/6 GHz channel disabling, SAR updates, and suspend while regulatory update is in flight. `hw_init_done` should become true only after full registration and debugfs/thermal setup.
