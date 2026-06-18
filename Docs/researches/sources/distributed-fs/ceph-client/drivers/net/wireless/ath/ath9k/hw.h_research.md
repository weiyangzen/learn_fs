# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.h

## Purpose

`hw.h` is the central hardware contract for ath9k. It defines supported Atheros device IDs, register access macros, timing constants, capability flags, channel/calibration/beacon/power/timer/radar data structures, operation tables, the full `struct ath_hw` state container, bus callbacks, inline accessors, and exported hardware-core function prototypes.

## Important APIs, Types, and Functions

The top-level constants enumerate PCI/PCIe/SoC/USB-capable AR9xxx device IDs and hardware limits such as `ATH9K_NUM_CHANNELS`, `ATH9K_NUM_QUEUES`, `AR_KEYTABLE_SIZE`, TX power limits, wait timeouts, and WoW pattern limits.

Register macros `REG_WRITE`, `REG_READ`, `REG_READ_MULTI`, `REG_RMW`, buffered write/RMW helpers, `SM`, `MS`, field helpers, and INI array helpers abstract bus-specific register operations through `ah->reg_ops`. This is what lets HTC USB supply WMI-backed register operations while PCI code can use MMIO-style operations.

Major types include `enum ath9k_hw_caps`, `struct ath9k_hw_capabilities`, `enum ath9k_int`, `struct ath9k_hw_cal_data`, `struct ath9k_channel`, channel flag macros, `enum ath9k_power_mode`, `struct ath9k_beacon_state`, `struct chan_centers`, `struct ath9k_hw_version`, generic timer structs, `struct ath_hw_antcomb_conf`, `struct ath_hw_radar_conf`, `struct ath_hw_private_ops`, `struct ath_hw_ops`, `struct ath_spec_scan`, `struct ath_nf_limits`, `struct ath_bus_ops`, and `struct ath_hw`.

`struct ath_hw` is the persistent state hub. It contains register ops, device/mac80211/common pointers, revision, config, capabilities, channel table, EEPROM storage and ops, software crypto flags, bus/revision flags, RF kill, reset/power state, calibration data and measurements, opmode, TX queues and interrupts, private/public ops tables, INI arrays, generic timers, TX status ring, watchdog state, PAPRD state, WA registers, MCI/BT fields, EEPROM blobs, dynamic ACK, TPC, MSI, and more.

The prototypes export initialization, reset, GPIO, general operation, power, generic timers, PHY utilities, family-specific attach helpers, ANI, timeout setters, BT coexistence wrappers, WoW wrappers, and hardware-name reporting.

## Control Flow

The header establishes how code should move through the hardware layer. Bus code allocates `struct ath_hw`, fills `reg_ops`, `bus_ops`, device IDs, and platform hooks, then calls `ath9k_hw_init()`. Family attach code populates `private_ops` and `ops`, and runtime code calls prototypes or `hw-ops.h` wrappers to reset, configure channels, start RX/TX, handle calibration, and enter power states.

## State and Persistence Behavior

State is explicitly centralized in `struct ath_hw` and `struct ath_common`. The file distinguishes board-derived persistent state, runtime state, reset-preserved state, and optional feature state. Register access itself is stateful through optional buffering callbacks. Channel/calibration state is preserved per `struct ath9k_hw_cal_data` when channel-compatible. Capability bits gate runtime features and must be filled before mac80211 capability publication.

## Dependencies and Integration Points

The header includes Linux networking, delay, I/O, and firmware headers plus ath9k local `mac.h`, `ani.h`, `eeprom.h`, `calib.h`, `reg.h`, `reg_mci.h`, `phy.h`, `btcoex.h`, `dynack.h`, and common regulatory definitions. It is consumed by shared hardware code, HTC code, PCI/platform drivers, family-specific PHY/MAC/calibration files, common ath helpers, debugfs, BT coexistence, WoW, and spectral scan code.

## Risks

This header is a broad ABI inside the driver. Changing `struct ath_hw`, ops tables, or macros affects many files and chip families. Register macros evaluate through function pointers, so callers must not assume MMIO timing or sleepability; HTC paths can use WMI. Bitmask constants and structure sizes must match hardware and firmware expectations. Conditional compilation can hide missing operations in some configs. Adding fields to `struct ath_hw` without initialization in every bus path can leave reset or power logic reading garbage.

## Test Signals

Build all ath9k configurations, including HTC, PCI, BT coexistence, WoW, RFKILL, and debugfs. Probe multiple chip families, verify capabilities published by mac80211, run register read/write buffer paths, reset/channel/power operations, GPIO/rfkill, generic timers, calibration/ANI, spectral scan, and WoW where enabled. Static analysis should check ops-table mandatory callbacks and structure initialization paths.
