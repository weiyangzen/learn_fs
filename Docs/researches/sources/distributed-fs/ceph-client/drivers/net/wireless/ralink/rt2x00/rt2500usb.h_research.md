# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500usb.h

## Purpose

`rt2500usb.h` is the RT2570 USB hardware definition header consumed by `rt2500usb.c`. It defines the RT2500 USB register map, EEPROM format, RF/BBP field masks, security key layout, USB descriptor layout, chip/RF identifiers, RSSI defaults, and transmit-power conversion macros.

The header is intentionally parallel to `rt2500pci.h` but reflects the RT2570 USB hardware differences: 16-bit CSR access at base `0x0400`, smaller EEPROM size, four-word RX descriptors, five-word TX descriptors, different MAC/TXRX/PHY/STA CSR naming, and USB-specific indirect BBP/RF access registers.

## Important APIs, types, and data

Important constants include:

- RF identifiers `RF2522`, `RF2523`, `RF2524`, `RF2525`, `RF2525E`, and `RF5222`; note that RT2500 USB defines `RF2525E` as `0x0005`, unlike the PCI header.
- RT2570 revision identifiers B, C, and D.
- Register-space constants: `CSR_REG_BASE = 0x0400`, `CSR_REG_SIZE = 0x0100`, `EEPROM_SIZE = 0x006e`, `BBP_SIZE = 0x0060`, and `RF_SIZE = 0x0010`.
- `MAC_CSR*` system registers for revision, reset/host-ready, station MAC, BSSID, max frame length, power state, autowake, GPIO, and LEDs.
- `TXRX_CSR*` registers for crypto algorithm/key selection, TX timing, RX filtering, BBP ID auto-write fields, auto responder/basic rates, beacon/TSF synchronization, and beacon preload.
- `SEC_CSR0` through `SEC_CSR31`, with `KEY_ENTRY(idx)` mapping four shared hardware keys to contiguous 16-byte regions.
- `PHY_CSR*` registers for RF switching, BBP indirect access, RF indirect access, low RF latch behavior, CCK/OFDM pre-TX antenna/IQ fields, and dummy revision-sensitive PHY configuration.
- `STA_CSR*` statistics registers for FCS and false CCA counts.
- BBP fields for TX/RX antenna selection and IQ flip, RF fields for tuner and transmit power, and EEPROM words for MAC address, antenna/NIC/geography, BBP overrides, per-channel TX power, BBP tuning, and RSSI offset.
- TX/RX descriptor fields for retry, ACK, OFDM, sequence, IFS, cipher/key id, byte count, PLCP, IV/EIV, RSSI, signal, CRC/physical/cipher errors, and BSS classification.
- `TXPOWER_FROM_DEV()` and `TXPOWER_TO_DEV()` for clamping device and mac80211 TX power in the 0 through 31 range.

The file has no functions or structs of its own. It relies on common rt2x00 `FIELD*` macros and Linux integer/endian types.

## Control flow

The header drives several `rt2500usb.c` paths:

1. Register access helpers read and write 16-bit CSR offsets defined here with USB vendor requests.
2. BBP and RF helper routines poll `PHY_CSR8_BUSY` and `PHY_CSR10_RF_BUSY`, fill `PHY_CSR7`, `PHY_CSR9`, and `PHY_CSR10`, and use `BBP_R2`, `BBP_R14`, and `RF3_TXPOWER` fields for antenna and TX power configuration.
3. Initialization writes `MAC_CSR1`, `TXRX_CSR5` through `TXRX_CSR8`, `TXRX_CSR19`, `MAC_CSR8`, `TXRX_CSR0`, `MAC_CSR18`, `PHY_CSR4`, and `TXRX_CSR1` using these field definitions.
4. Runtime configuration writes `TXRX_CSR0` for key state, `TXRX_CSR2` for filters, `TXRX_CSR18`/`TXRX_CSR19`/`TXRX_CSR20` for synchronization, `MAC_CSR10` through `MAC_CSR12` for timing, `MAC_CSR17`/`MAC_CSR18` for power save, and `MAC_CSR19` for rfkill GPIO.
5. TX/RX queue code uses `TXD_DESC_SIZE`, `RXD_DESC_SIZE`, and all descriptor fields to format frames and parse completions.
6. EEPROM probe code uses the EEPROM constants to validate board data, choose RF tables, set antenna defaults, register LEDs, set hardware-button capability, and derive tuning/RSSI values.

## State and persistence behavior

The constants describe persistent hardware state rather than local software state. `MAC_CSR1` reset and host-ready bits control device lifecycle. MAC/BSSID fields persist until interface changes. `MAC_CSR17` persists desired power state and reports current BBP/RF state. `MAC_CSR18` persists autowake timing. LED fields in `MAC_CSR20`/`MAC_CSR21` persist visible device behavior.

`TXRX_CSR0` and `SEC_CSR*` hold hardware crypto state. Because the hardware exposes only four shared key slots and an algorithm selector common to active keys, the C driver must serialize key installation and fall back to software crypto for unsupported combinations.

EEPROM words describe nonvolatile per-board state. The driver reads them once at probe and may replace invalid in-memory words with defaults. Tuning words such as `EEPROM_BBPTUNE_R24`, `R25`, `R61`, `VGC`, and `R17` are later used to restore BBP tuner state.

Descriptor fields are transient USB transfer metadata. The RT2570 format stores the RX descriptor at the end of the USB buffer, unlike many PCI ring layouts; code consuming `RXD_*` must preserve that placement assumption.

## Dependencies and integration points

`rt2500usb.h` integrates directly with `rt2500usb.c` and indirectly with rt2x00 core queue, EEPROM, RF cache, crypto, and mac80211 layers. It also informs optional debugfs register windows through `CSR_REG_BASE`, `CSR_REG_SIZE`, `EEPROM_SIZE`, `BBP_SIZE`, and `RF_SIZE`.

The header is source-compatible with the common `struct rf_channel` channel-table format used by rt2x00 drivers. RF constants select local RF tables in `rt2500usb.c`. Descriptor constants must align with `rt2x00usb` queue allocation and SKB descriptor handling.

## Risks

- The USB register map is 16-bit and not interchangeable with the PCI RT2500 32-bit map. Copying CSR or descriptor fields between headers would break register programming.
- `RF2525E` has a different numeric value than in `rt2500pci.h`; cross-driver comparisons must never assume the PCI and USB RF IDs are identical.
- `KEY_ENTRY(idx)` assumes a fixed 16-byte stride and four shared keys. Incorrect key index arithmetic can overwrite another key or unrelated CSR space.
- `PHY_CSR2` is documented as unclear/dummy; revision-specific writes in the C driver should be treated cautiously because the field semantics are not well established.
- Descriptor size and field definitions directly affect SKB headroom and USB buffer parsing. A wrong descriptor size can misalign frame data, lose IV/EIV data, or read beyond actual transfer length.
- EEPROM tuning and RSSI fields are board-specific. Invalid fallback values can degrade receive sensitivity, RSSI reporting, or transmit power accuracy.
- Power macros use `clamp_t(u8, ...)`; signed or out-of-range caller values must be checked at higher layers if negative power levels are possible.

## Test signals

- Compile tests should include `rt2500usb.c` with debugfs and LED options to verify all optional references.
- Probe tests should confirm register base/size values expose correct debugfs windows and EEPROM size matches USB EEPROM reads.
- Hardware initialization tests should verify `MAC_CSR1`, `PHY_CSR*`, and `TXRX_CSR*` field programming by register trace.
- Crypto tests should verify `SEC_CSR*`, `KEY_ENTRY()`, `TXRX_CSR0_ALGORITHM`, `IV_OFFSET`, and `KEY_ID` fields for each supported cipher path.
- TX/RX tests should validate five-word TX descriptor formatting and four-word RX descriptor parsing, including signal/RSSI, CRC/physical errors, cipher errors, and IV/EIV extraction.
- Power-save tests should validate `MAC_CSR17` state fields and `MAC_CSR18_AUTO_WAKE`.
- RF table/channel tests should cover each RF type constant, especially RF2525E and RF5222.
