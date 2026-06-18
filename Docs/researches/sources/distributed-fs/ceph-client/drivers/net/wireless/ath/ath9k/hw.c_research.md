# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.c

## Purpose

`hw.c` is the shared ath9k hardware core for AR5008/AR9001/AR9002/AR9003-family devices, including HTC USB users. It detects hardware revisions, attaches family ops, initializes EEPROM/regulatory/capability state, performs reset and channel change, manages power modes, programs timing, beacon, DMA, interrupt, GPIO, RX filter, TX power, TSF, generic timer, and hardware-name behavior.

## Important APIs, Types, and Functions

Initialization is driven by `ath9k_hw_init()`, which validates device ID, calls `__ath9k_hw_init()`, and initializes dynamic ACK. `__ath9k_hw_init()` reads revisions, validates supported MAC versions, sets reset/WA defaults, attaches family ops, wakes the chip, initializes PHY/calibration settings, disables PCIe on non-PCIe devices, initializes EEPROM and ANI, fills capabilities, reads MAC address, initializes hang checks, and marks `ATH_HW_INITIALIZED`.

Reset and channel change are handled by `ath9k_hw_reset()`, `ath9k_hw_do_fastcc()`, `ath9k_hw_channel_change()`, `ath9k_hw_chip_reset()`, `ath9k_hw_set_reset_reg()`, `ath9k_hw_set_reset()`, and `ath9k_hw_set_reset_power_on()`. The reset path preserves/restores TSF, LED state, antenna defaults, opmode, calibration data, noise floor history, queue state, interrupt masks, global timing, DMA, baseband, chainmask, descriptors, BT/MCI state, GPIO overrides, DFS radar params, and noise-floor calibration.

Power management is exposed as `ath9k_hw_setpower()` with modes `ATH9K_PM_AWAKE`, `ATH9K_PM_FULL_SLEEP`, and `ATH9K_PM_NETWORK_SLEEP`. Helpers program force-wake, RTC reset/status, STA power-save bits, autosleep/MCI behavior, and AR_WA workarounds.

General exported hardware APIs include `ath9k_hw_wait()`, `ath9k_hw_synth_delay()`, INI array read/write helpers, `ath9k_hw_computetxtime()`, `ath9k_hw_get_channel_centers()`, `ath9k_hw_init_global_settings()`, RX filter get/set, PHY/hardware disable, TX power application/limits, opmode, multicast filters, association ID writes, TSF get/set/reset, 20/40 MAC mode, beacon timers, station beacon timers, NAV/alive checks, GPIO request/get/set/free, antenna selection, generic timer alloc/start/stop/free/ISR, and `ath9k_hw_name()`.

## Control Flow

Initialization first establishes what chip is present and which operation table should be used. After reset and wake, EEPROM initialization populates board-specific data, capability fill reads regulatory, band, chainmask, GPIO, crypto, HT, autosleep, EDMA, LDPC, SGI, antenna diversity, MCI/RTT/PAPRD/WoW support, and descriptor lengths.

`ath9k_hw_reset()` is the central operational flow. It wakes hardware, saves current NF if possible, installs/reset calibration data for the requested channel, tries fast channel change if requested, handles MCI reset choreography, saves state that a reset would clobber, marks PHY inactive, applies AR9271 first-reset sequencing, resets the chip and PLL, restores TSF with elapsed-time compensation, processes INI/register tables, configures RF mode/frequency, applies EEPROM board values and TX power, restores opmode and queues, initializes interrupts/QoS/timing/DMA/baseband/descriptors, runs initial calibration, restarts generic timers, re-enables BT/MCI/PAPRD/noise-floor/radar/GPIO behaviors, and returns status.

Fast channel change is intentionally conservative. It rejects fullsleep, missing current channel, same channel, half/quarter rates, incompatible band/mode flags, dead hardware, pending TX queues, and missing calibration on AR9462. If allowed, it uses RF bus locking, family fast channel ops, board-value refresh when needed, baseband init, and NF calibration without a full chip reset.

## State and Persistence Behavior

`hw.c` mutates most fields in `struct ath_hw`: revision and capability data, EEPROM ops/data, current channel, power mode, chip sleep state, calibration pointers and flags, noise floor, opmode, interrupt masks, queue configs, timing values, chainmasks, GPIO masks/values, WA registers, generic timers, BT/MCI state, descriptor lengths, radar config, TSF, and hardware workarounds. Some state is persistent across resets and deliberately restored, such as TSF, LED config, default antenna, `WARegVal`, opmode, BSSID mask, global TX timeout, GPIO overrides, and calibration history when channel-compatible.

## Dependencies and Integration Points

The file depends on register definitions, PHY/MAC helpers, EEPROM ops, ANI/calibration, BT coexistence/MCI, dynamic ACK, regulatory helpers, Linux GPIO, firmware and device APIs, and family-specific AR9002/AR9003 attach code. It is used by PCI, platform, and USB/HTC drivers through `struct ath_ops` register callbacks, so register access may be direct MMIO or firmware-mediated WMI depending on bus.

## Risks

Reset sequencing is highly chip-specific; small ordering changes can break certain revisions. Register reads during sleep are avoided through cached values such as `WARegVal`, and violating that assumption can hang hardware. Fast channel change must not proceed with pending TX or incompatible calibration. Capability fill depends on EEPROM correctness and device revision macros. Power transitions interact with MCI/BT and autosleep; wrong force-wake handling can leave the chip inaccessible. GPIO paths split between WMAC and SoC GPIO domains. Generic timer callbacks run from interrupt context and must tolerate missing timer slots. USB/HTC users depend on all register ops being safe over WMI latency.

## Test Signals

Test probe/reset on representative AR5416, AR9280/9285/9287/9271, AR9300, AR9330/9340, AR9462/9565, and SoC variants; channel changes with and without fastcc; half/quarter/HT40 timing; sleep/wake/network sleep loops; TX/RX after reset; EEPROM/regulatory band disable cases; rfkill GPIO; TSF continuity across reset; beacon timers in AP/STA; generic timer interrupts; DFS/radar-enabled channels; BT/MCI coexistence; hot-unplug paths that set `AH_UNPLUGGED`; and WMI-backed HTC register operations.
