# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800soc.c

## Purpose
Implements the platform/SoC RT2800 WiSoC driver. It reuses the MMIO RT2800 path for embedded Ralink wireless MACs, allocates platform-backed rt2x00 device state, reads EEPROM from nvmem or a fixed SoC flash window, and registers an OF-matched platform driver.

## Important APIs, Types, And Functions
Important helpers include `rt2800soc_hwcrypt_disabled()`, `rt2800soc_disable_radio()`, `rt2800soc_set_device_state()`, `rt2800soc_read_eeprom()`, stub firmware callbacks that warn if called, optional PM suspend/resume, the shared mac80211 ops table, RT2800/MMIO operation tables, `rt2x00soc_probe()`, `rt2800soc_probe()`, `rt2800soc_remove()`, `rt2880_wmac_match`, and `rt2800soc_driver`.

## Control Flow
Platform probe ioremaps the first memory resource, obtains IRQ and optional clock, allocates devm EEPROM/RF buffers, allocates `ieee80211_hw`, fills `rt2x00_dev` fields, sets chip interface to SOC, then calls `rt2x00lib_probe_dev()`. Radio-on uses `rt2800mmio_enable_radio()`. Radio-off disables shared RT2800 radio state, clears `PWR_PIN_CFG`, and for RT3883 preserves `TX_PIN_CFG_RFTR_EN`. Sleep/awake states are treated as unsupported no-ops. Remove calls `rt2x00lib_remove_dev()` and frees the hw object.

## State And Persistence
Platform-managed EEPROM and RF caches live for the device lifetime. EEPROM is loaded either from nvmem or from physical address `0x1F040000`, ioremapped for `EEPROM_SIZE`. The SoC does not persist firmware state through this file; firmware callbacks are stubs because these devices are expected to run without the PCI/USB firmware path.

## Dependencies And Integration Points
Depends on OF platform matching (`ralink,rt2880-wifi`), platform resources, optional clock framework, MMIO register helpers, RT2800 shared library, rt2x00 core probe/remove/suspend/resume, and mac80211 callbacks from common rt2x00 code.

## Risks
The fixed EEPROM mapping is SoC-layout-specific and risky outside expected platforms; nvmem should be preferred when available. Firmware callbacks warn if invoked, so capability flags must not require firmware for SoC devices. Power management only uninitializes/restores common state and treats hardware sleep as unsupported. Probe uses devm buffers but manually frees `ieee80211_hw`; error paths must keep ownership clear.

## Test Signals
Device tree probe with `ralink,rt2880-wifi`, IRQ delivery, nvmem EEPROM override, fallback EEPROM mapping, radio on/off, suspend/resume, AP/STA operation, RT3883 TX pin behavior, and no unexpected firmware callback warnings.
