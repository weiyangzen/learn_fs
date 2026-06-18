# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/init.c

## Purpose
MT7603 device initialization and registration. It defines mt76 driver callbacks, initializes scheduler/PHY/MAC hardware, wraps bus ops for register remapping, sets LED behavior, computes initial txpower, registers with mac80211, and tears down the device.

## Important APIs, Types, And Functions
- `mt7603_drv_ops` connects common mt76 callbacks to MT7603 implementations for TX prepare/complete, RX dispatch, survey, channel setting, station events, and PS.
- `mt7603_dma_sched_init()`, `mt7603_phy_init()`, and `mt7603_mac_init()` program PSE scheduler quotas, stream counts, AGC snapshots, aggregation, DMA RX/TX selection, WTBL defaults, security, MBSSID, retry, and beacon timing offsets.
- `mt7603_init_hardware()` orders EEPROM init, DMA init, MAC DMA start, WTBL reset, MCU firmware init, scheduler, EEPROM upload, PHY init, and MAC init.
- LED callbacks `mt7603_led_set_config()`, `mt7603_led_set_blink()`, and `mt7603_led_set_brightness()` program LED registers through the remap window.
- `mt7603_rr()`, `mt7603_wr()`, and `mt7603_rmw()` wrap parent bus ops to remap addresses above the direct window.
- `mt7603_regd_notifier()` stores DFS region and enables ED monitor only for ETSI when user-enabled.
- `mt7603_init_txpower()` derives initial target power from EEPROM, external PA fields, rate offsets, and antenna count, then updates channel max/original power.
- `mt7603_register_device()` performs full runtime registration; `mt7603_unregister_device()` disables tasklets, unregisters, restarts MCU download mode, cleans DMA, and frees mt76.

## Control Flow
Probe code from PCI/SoC frontends creates the device and calls `mt7603_register_device()`. That function clones and overrides bus ops for remapping, initializes locks/work/tasklets/defaults, runs hardware init, fills mac80211 capability fields, installs optional LED callbacks and regulatory notifier, calls `mt76_register_device()`, initializes debugfs, and computes txpower. Unregister disables pre-TBTT work before common unregister and hardware cleanup.

## State And Persistence
Runtime state initialized here includes `bus_ops`, `ps_lock`, delayed `mac_work`, pre-TBTT tasklet, slot time, sensitivity defaults, dynamic sensitivity, `rxfilter`, `MT76_STATE_INITIALIZED`, global reserved WCID, `dev->tx_power_limit`, `mphy.txpower_cur`, LED callbacks, and wiphy capabilities. Hardware register state is extensively programmed but not persistent across reset.

## Dependencies And Integration Points
Depends on EEPROM, DMA, MCU, MAC, beacon, debugfs, mt76 common registration, mac80211, LED classdev, regulatory notifications, and chip-specific register definitions. It is the main integration point between bus probe units and the common mt76 stack.

## Risks
Initialization order is strict: EEPROM informs antenna/power, DMA must exist for firmware commands, firmware must run before MCU channel/power commands, and WTBL/PSE setup must precede traffic. Bus op wrapping must preserve original ops in `dev->bus_ops`; recursion or missing remap breaks high-register access. Error paths after partial hardware init rely on caller cleanup. Txpower parsing handles signed EEPROM encodings that are easy to misinterpret.

## Test Signals
Probe/remove repeatedly, including failure injection at EEPROM, DMA, firmware, and register stages. Verify firmware loads, mac80211 registration, LED behavior, debugfs creation, regulatory notifier updates, txpower/channel max values, WTBL reserved entry, and traffic after reset.
