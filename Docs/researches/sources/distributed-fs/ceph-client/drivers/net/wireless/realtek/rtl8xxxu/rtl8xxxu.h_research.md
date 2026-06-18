# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/rtl8xxxu.h

## Purpose
`rtl8xxxu.h` is the central private interface for the Realtek `rtl8xxxu` USB driver. It defines debug classes, USB control constants, TX page geometry, EFUSE layouts, RX/TX descriptor layouts, firmware/H2C/C2H message formats, rate and Bluetooth coexistence metadata, per-device private state, per-station/vif state, the chip operation table, and the cross-file helper prototypes used by the driver implementation.

## Important APIs, Types, And Functions
Key hardware data structures include `struct rtl8xxxu_rxdesc16`, `struct rtl8xxxu_rxdesc24`, `struct rtl8xxxu_txdesc32`, and `struct rtl8xxxu_txdesc40`, which model descriptor formats with endian-dependent bit fields. Rate constants `DESC_RATE_*`, `TXDESC_*`, and `enum ratr_table_mode_new` connect mac80211 rate decisions to firmware/HW descriptor fields. PHY-stat structures include `struct rtl8723au_phy_stats` and the Jaguar2 type 0/1/2 stat layouts.

Persistent identity/calibration data is represented by `struct rtl8xxxu_firmware_header`, `struct rtl8xxxu_power_base`, and chip-specific EFUSE structs for 8723AU/BU, 8192CU/EU/FU, 8188EU/FU, and 8710BU. H2C/C2H integration is described by `enum h2c_cmd_8723a`, `enum h2c_cmd_8723b`, `struct h2c_cmd`, `enum c2h_evt_8723b`, BT MP opcodes, and `struct rtl8723bu_c2h`.

The main runtime container is `struct rtl8xxxu_priv`, which stores USB device handles, URB anchors/lists, endpoint mappings, firmware and EFUSE data, calibration backups, chip capabilities, locks, queues, delayed work, Bluetooth coexistence state, rate-adaptation state, CFO tracking, LEDs, MAC-ID and CAM bitmaps, and mac80211 vif pointers. `struct rtl8xxxu_fileops` is the chip-specific dispatch table for identify, EFUSE parse, firmware load, power on/off, LLT, BB/RF init, calibration, channel setup, RX descriptor parsing, aggregation, statistics, RF control, USB quirks, TX power, rate masks, connect/RSSI reporting, TX descriptor fill, crystal cap, RSSI conversion, and chip capability constants.

Public prototypes cover register and RF access, masked writes, register backup/restore, PHY/RF init, firmware load/reset, endpoint config, EFUSE read, LLT setup, power-state transitions, calibration, channel setup, rate-mask reporting, aggregation, RX descriptor/stat parsing, TX descriptor fill, BT coexistence helper commands, crystal calibration, RA reports, and chip `fileops` objects.

## Control Flow
The header does not implement control flow, but it defines the objects that make probe and runtime dispatch possible. Probe allocates `rtl8xxxu_priv`, identifies a chip, selects one `rtl8xxxu_fileops`, reads/parses EFUSE into the union, loads firmware, configures endpoints, initializes BB/RF/MAC state, and registers mac80211. TX paths build a `rtl8xxxu_txdesc32` or 40-byte variant using the selected `fill_txdesc` callback and queue mapping constants. RX paths parse 16- or 24-byte descriptors, optionally parse PHY stats, then deliver frames to mac80211. Firmware command paths serialize `struct h2c_cmd` through mailbox helpers and parse C2H reports into BT, TX report, and rate-adaptation state.

## State And Persistence
`struct rtl8xxxu_priv` is the persistent driver state for a USB device lifetime. Hardware state is mirrored in capability flags, endpoint arrays, `regrcr`, RF path counts, power-index arrays, backup register arrays, firmware pointers, queue anchors, work items, and bitmaps for MAC IDs and security CAM slots. `rtl8xxxu_sta_info` persists per-station MAC-ID/RSSI state in mac80211 private storage, while `rtl8xxxu_vif` stores the port number and hardware key index. EFUSE data is retained in memory after parsing, but hardware registers and firmware state must be rebuilt after reset, disconnect, or full power cycling.

## Dependencies And Integration Points
The header depends on Linux USB, mac80211, LED, bitmap, average/EWMA, sk_buff, endian, and kernel locking/workqueue APIs. It integrates with `regs.h`, chip implementation files, firmware blobs, mac80211 callbacks, cfg80211 bands/rates, USB URB submission, security CAM management, Bluetooth coexistence, LED classdev registration, and rate control. `rtl8xxxu_fileops` is the key integration seam between common USB/mac80211 logic and per-chip hardware procedures.

## Risks
Descriptor bit fields and EFUSE packed structs are ABI-sensitive; endian mistakes, padding changes, or field width changes can corrupt RX status, TX control, power tables, or MAC addresses. `rtl8xxxu_fileops` mixes required callbacks and capability data, so a new chip definition with a missing or mismatched callback can fail late in probe or runtime. The large `rtl8xxxu_priv` state has several concurrency domains: URB locks, H2C mutex, station mutex, indirect-register mutex, workqueues, anchors, and bitmaps must stay coordinated. H2C/C2H formats differ between generations, making command length and command-id mistakes high-risk.

## Test Signals
Signals include descriptor parsing for both old and new chips, successful EFUSE parse with valid MAC/power/channel data, firmware load and H2C mailbox operation, TX/RX under aggregation, rate adaptation reports, security CAM allocation exhaustion behavior, LED and rfkill behavior, Bluetooth coexistence notifications, suspend/disconnect cleanup of URB anchors, and chip-specific probe coverage for each exported `rtl8xxxu_fileops`. Sparse/smatch and compiler warnings around packed bit fields are useful early warnings.
