# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800lib.h

## Purpose
Defines the transport-neutral RT2800 library interface used by PCI/MMIO, SoC, and USB variants. It describes RT2800-specific private state, the `rt2800_ops` hardware access vtable, wrapper helpers that dispatch through `rt2x00dev->ops->drv`, and the public RT2800 library entry points consumed by bus drivers.

## Important APIs, Types, And Functions
`struct rt2800_drv_data` stores RT2800 calibration snapshots, TX mixer gain, max PSDU, beacon TBTT skew counter, AMPDU counters, and WCID-to-station mappings. `struct rt2800_ops` is the low-level bus contract: CSR read/write, multi-read/write, busy-register polling, EEPROM read, hardware crypto policy, firmware write, register initialization, TXWI lookup, and DMA-done index lookup. Inline wrappers such as `rt2800_register_read()`, `rt2800_read_eeprom()`, `rt2800_drv_write_firmware()`, and `rt2800_drv_get_dma_done()` hide the actual PCI/MMIO/USB/SOC implementation. Declared shared operations include firmware validation/load, TXWI/RXWI processing, tx status handling, beacon programming, watchdog, rfkill, key programming, STA WCID management, AMPDU, TSF, survey, and debugfs metadata.

## Control Flow
Bus drivers install a `struct rt2800_ops` in their `struct rt2x00_ops.drv`; shared RT2800 code calls these wrappers whenever it needs a register, firmware, EEPROM, or descriptor operation. Probe flows call shared `rt2800_probe_hw()` through bus `probe_hw`, which in turn relies on this vtable to populate capabilities and EEPROM-derived state. Runtime TX/RX and txdone paths use `rt2800_drv_get_txwi()` and `rt2800_drv_get_dma_done()` to interpret bus-specific descriptor layouts without duplicating the RT2800 MAC/PHY logic.

## State And Persistence
The header defines the RT2800 per-device persistence carried in `rt2x00dev->drv_data`. WCID state is bounded by `WCID_START`, `WCID_END`, and `STA_IDS_SIZE`, reflecting hardware table limits and beacon-buffer overlap. Calibration fields survive while the driver object exists and are reset only on device teardown or reprobe; hardware register state is rehydrated through callbacks after firmware/radio initialization.

## Dependencies And Integration Points
Depends on rt2x00 core objects (`rt2x00_dev`, queue entries, crypto descriptors), RT2800 register definitions from `rt2800.h`, mac80211 station/key structures, and debugfs support. It is the integration point between `rt2800lib.c` style shared logic and the bus-specific files in this work item.

## Risks
The vtable is type-erased through `const void *drv`, so a wrong bus ops table causes silent wrong register or descriptor behavior. WCID limits must stay aligned with hardware key/beacon table layout. Inline wrappers do no NULL checks; probe must fully initialize `ops->drv` before any shared RT2800 call. Bus implementations must agree on TXWI/RXWI sizes and descriptor offsets or RX/TX corruption follows.

## Test Signals
Probe RT2800 PCI, USB, and SoC devices and verify EEPROM parsing, firmware upload, radio enable, TX/RX, AP beaconing, hardware crypto, AMPDU, and tx status completion. KASAN and lockdep are useful around WCID allocation/removal, and debugfs register access should match the installed bus transport.
