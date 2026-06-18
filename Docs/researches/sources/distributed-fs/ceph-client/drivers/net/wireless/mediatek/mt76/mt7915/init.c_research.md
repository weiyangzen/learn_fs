# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/init.c

Purpose: Main registration and hardware initialization spine for MT7915-family devices. It defines mac80211 capabilities, thermal/hwmon/LED support, txpower initialization, MAC defaults, DBDC/ext-phy registration, WFSYS reset, and device unregister.

Important APIs: `mt7915_init_txpower`, `mt7915_mac_init`, `mt7915_txbf_init`, `mt7915_wfsys_reset`, `mt7915_set_stream_vht_txbf_caps`, `mt7915_set_stream_he_caps`, `mt7915_register_device`, and `mt7915_unregister_device`.

Control flow: register initializes work items/lists/waitqueues/mutexes, determines band/DBDC config, allocates ext phy, initializes DMA/MCU/EEPROM/global WCID, configures wiphy capabilities, registers the main mt76 device, initializes thermal support, registers ext phy if present, queues deferred EEPROM/MAC/TXBF init, enables debugfs and coredump. Hardware init masks interrupts, starts DMA, MCU, EEPROM, optional group calibration, and allocates global WCID. Unregister cancels work, unregisters ext phy/coredump/thermal/mac80211, stops hardware, and frees device.

State and persistence: initializes `dev->phy`, `dbdc_support`, ext phy band index, lists for station rate-control and TWT, reset/coredump work, thermal thresholds/state, MAC/LED registers, chain and txpower state, and recovery readiness.

Dependencies and integration: depends on mac80211, mt76 core registration, DMA/MCU/EEPROM/MAC/debugfs/coredump modules, thermal and hwmon subsystems, LED support, device-tree radar property, and WED capability.

Risks: registration unwind is complex and must mirror initialization order. Ext phy MAC fallback must avoid address collisions. HE/VHT capability generation depends on chip/DBDC stream limits. Thermal threshold validation uses inverted critical/max naming conventions from hardware.

Test signals: build/register/unregister for each chip family, DBDC and single-band modes, ext-phy failure unwind, thermal sysfs and cooling device, LED blink/brightness, HE/VHT capability advertisement, coredump registration failures, and WFSYS reset recovery.
