# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/init.c

## Purpose
Handles MT7601U device allocation, hardware power-on/reset, firmware/MCU/DMA/MAC/BBP/RF initialization, MAC start/stop, cleanup, supported band/rate registration, and mac80211 hardware registration.

## Important APIs, Types, And Functions
Exports `mt7601u_mac_start()`, `mt7601u_mac_stop()`, `mt7601u_init_hardware()`, `mt7601u_cleanup()`, `mt7601u_alloc_device()`, and `mt7601u_register_device()`. Internal helpers control WLAN power/reset, USB DMA configuration, BBP/MAC initval writes, beacon offsets, WCID/key memory initialization, counter reset, MAC stop hardware drain, and supported-band setup.

## Control Flow
Hardware init powers on WLAN, waits ASIC ready, initializes MCU, waits DMA idle, resets CSR/BBP, configures USB DMA, initializes MCU command path and DMA, writes MAC/BBP init values, clears WCID/key memories, disables beacon timing, reads EEPROM, initializes PHY, and sets default channel bandwidth/path state. Error paths unwind DMA, MCU command, and power state. Registration reserves WCID 0, creates monitor WCID, sets mac80211 capabilities, exposes 2 GHz channels/rates from EEPROM region, initializes work items, registers hardware, and creates debugfs.

## State And Persistence
Persistent state includes device locks, workqueues, WCID mask, beacon offsets, EEPROM pointer, macaddr, supported bands/rates, mac80211 hw flags, work items, DMA/MCU state, WLAN running/initialized bits, RX filter, and hardware registers programmed by init tables.

## Dependencies And Integration Points
Depends on mac80211 allocation/registration, MCU, DMA, EEPROM, PHY, MAC, debugfs, init tables, USB DMA registers, and MT7601U register definitions. It is the central probe/register path called by the USB driver.

## Risks
Initialization order is strict: MCU must be loaded before command register access, DMA before RX, EEPROM before band setup, and PHY after calibration data. MAC stop waits for several busy/page counters; timeout warnings indicate possible stale DMA state. Cleanup must be idempotent through `MT7601U_STATE_INITIALIZED`.

## Test Signals
Probe/register/unregister, init error injection at MCU/DMA/EEPROM/PHY steps, MAC start/stop with queues active, 2 GHz channel list matching EEPROM region, debugfs creation, and no busy warnings during normal stop.
