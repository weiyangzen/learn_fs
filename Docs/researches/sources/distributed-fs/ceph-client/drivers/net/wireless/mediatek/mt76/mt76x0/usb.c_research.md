<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb.c

Purpose: USB bus driver for MT7610U/MT7630U/MT7650U adapters. It binds a vendor/product table, allocates the shared `mt76x02_dev`, wires mac80211 operations to the mt76x02 common helpers, initializes USB queues, firmware, hardware, beacons, and power-management callbacks.

Important APIs/types/functions: `mt76x0u_probe()`, `mt76x0u_register_device()`, `mt76x0u_init_hardware()`, `mt76x0u_start()`, `mt76x0u_stop()`, suspend/resume, and `mt76x0u_ops`. Driver ops point TX/RX, station, channel, survey, and status handling at shared mt76x02 code while using USB-specific `mt76x02u_tx_prepare_skb()` and completion.

Control flow: probe enables and resets USB, initializes MCU transport, disables hardware after hot reboot, validates ASIC/eFUSE, then registers the device. Register allocates USB queues, powers the chip, loads MCU firmware, initializes common hardware and beacon timers, then calls mt76x0 registration. Start enables MAC/RX/TX and schedules calibration/MAC work; stop cancels work, stops USB TX, tears down beacon timers, polls DMA idle, and stops MAC.

State and persistence: persistent state is kernel device state, `mphy.state` bits, USB queue allocation, `no_2ghz` Archer T1U quirk, firmware state, beacon timer state, and calibration work scheduling. No user-space persistence is written.

Dependencies/integration: integrates Linux USB core, mac80211, mt76 USB helpers, mt76x0 chip/PHY code, mt76x02 common TX/RX/beacon/util/debug helpers, and firmware files `mt7610e.bin`/`mt7610u.bin`.

Risks: hot-reboot MCU readiness, DMA busy polling, USB device lifetime balance, unsupported ASIC IDs, quirk-limited bands, and cleanup paths before `MT76_STATE_INITIALIZED`. Test signals include probe/remove cycles, suspend/resume, firmware fallback, USB unplug during init, AP beaconing, calibration work start/stop, and TX/RX under queue teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb.c -->
