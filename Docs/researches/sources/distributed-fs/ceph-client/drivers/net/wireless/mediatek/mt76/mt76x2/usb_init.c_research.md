# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_init.c

Purpose: Hardware bring-up and registration path for MT76x2U. It powers WLAN/RF blocks, reads EEPROM over USB vendor register space, loads firmware and MCU state, resets MAC tables, allocates USB queues, and registers the device with mac80211.

Important APIs: `mt76x2u_init_hardware`, `mt76x2u_register_device`, `mt76x2u_stop_hw`, and `mt76x2u_cleanup`. Internal helpers configure USB DMA, RF power patches, WLAN MTCMOS, and EEPROM extraction.

Control flow: initialization resets WLAN, powers both RF units, waits for MAC readiness, loads ROM patch/firmware, waits for DMA idle, initializes USB DMA, starts MCU radio state, resets MAC, sets MAC address and rx filter, clears WCID/shared-key tables, initializes beacon config, loads CR tables, configures PHY paths, then stops the MAC until mac80211 start. Registration layers mt76 device init, EEPROM init, MCU response buffer allocation, USB queue allocation, hardware init, VHT capability selection, mac80211 registration, debugfs, and txpower setup.

State and persistence: EEPROM bytes are copied into devm-allocated `mt76.eeprom.data`; `dev->mt76.rxfilter`, revision-dependent VHT capability, work items, queue allocation, and `MT76_STATE_INITIALIZED` are runtime state.

Dependencies and integration: depends on mt76 USB queue helpers, mt76x02 EEPROM/MAC/PHY helpers, USB MCU loader in `usb_mcu.c`, MAC reset/stop in `usb_mac.c`, and txpower helpers from `phy.c`.

Risks: bring-up is timing-sensitive and uses many magic vendor registers. EEPROM read size and endian handling must match hardware. Registration failure paths rely on `mt76x2u_cleanup` being safe before full initialization. Disabling RX bulk aggregation is a deliberate copy-avoidance tradeoff.

Test signals: firmware load success, MAC wait timeouts, EEPROM MAC address correctness, VHT-disabled revision behavior, table reset after reinit, interface start after stopped MAC, and cleanup on each injected failure point.
