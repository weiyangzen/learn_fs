# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.c

## Purpose
This PCI driver exposes the Cavium/ThunderX PTP 1588 coprocessor as a Linux PTP hardware clock and provides exported reference-counted accessors for other Cavium network drivers that need to convert hardware timestamps.

## Important APIs, Types, And Functions
Public exports are `cavium_ptp_get()` and `cavium_ptp_put()`. PTP clock methods are `cavium_ptp_adjfine()`, `cavium_ptp_adjtime()`, `cavium_ptp_gettime()`, `cavium_ptp_settime()`, and `cavium_ptp_enable()`. Hardware-cycle integration uses `cavium_ptp_cc_read()`, `struct cyclecounter`, and `struct timecounter`. Probe/remove are `cavium_ptp_probe()` and `cavium_ptp_remove()`.

## Control Flow
Probe allocates `struct cavium_ptp`, enables the PCI device with managed PCI helpers, maps BAR0, initializes locking, cyclecounter, and timecounter, derives the coprocessor clock rate by probing the Cavium reset device and reading `RST_BOOT`, enables the PTP clock register, writes the compensation value, registers the PTP clock, and stores the clock pointer as PCI driver data. On failure, it stores an `ERR_PTR(err)` in driver data and returns success so consumers can distinguish failed initialization from an unprobed device. `cavium_ptp_get()` finds the PTP PCI function, returns `-ENODEV` if absent, returns `-EPROBE_DEFER` if driver data is not ready, and drops the PCI reference on errors. Remove unregisters the clock and clears the hardware enable bit.

## State And Persistence
State lives in `struct cavium_ptp`: PCI device reference, spinlock, MMIO base, clock rate, timecounter/cyclecounter, and registered PTP clock. Frequency adjustment is stored in the hardware compensation register; time adjustment is stored in the software timecounter. No data is persisted across driver unload or reboot.

## Dependencies And Integration Points
The file integrates with PCI, PTP clock framework, timecounter/cyclecounter helpers, MMIO `readq/writeq`, and Cavium reset-device registers. It exports symbols for other Cavium network drivers and matches specific Cavium subsystem IDs.

## Risks
The probe intentionally returns success on internal failures after storing an error pointer; code touching `pci_get_drvdata()` must use `IS_ERR_OR_NULL`. Clock-rate discovery probes a separate reset PCI device and falls back to `CLOCK_BASE_RATE * 16` if unavailable, which can skew timestamps. `cavium_ptp_adjfine()` performs fixed-point math and relies on spinlock serialization for register writes. `cavium_ptp_enable()` rejects ancillary features, so PPS/ext timestamp requests are unsupported.

## Test Signals
Load/unload the driver on supported PCI IDs; verify `/dev/ptp*` registration, `phc_ctl` get/set/adj operations, frequency adjustment behavior, consumers receiving `-EPROBE_DEFER` before readiness, and timestamp conversion stability under concurrent reads and adjustments.
