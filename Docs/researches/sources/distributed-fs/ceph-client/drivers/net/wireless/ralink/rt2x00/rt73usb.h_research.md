# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt73usb.h

## Purpose

`rt73usb.h` defines the RT73 USB hardware map consumed by `rt73usb.c`: RF IDs, firmware name/base address, register ranges, security SRAM layout, beacon SRAM layout, MAC/TXRX/PHY/security/statistics/QoS/WMM registers, BBP/RF/EEPROM fields, and USB-format TX/RX descriptor fields.

## Important APIs, Types, and Functions

The header exports packed `hw_key_entry` and `hw_pairwise_ta_entry` layouts, key-table address macros, register field definitions, descriptor sizes (`TXD_DESC_SIZE`, `TXINFO_SIZE`, `RXD_DESC_SIZE`), and TX power conversion macros. It has no callable functions, but its field definitions are the ABI between rt2x00 software descriptors and RT73 firmware/MAC hardware.

## Control Flow

The companion driver uses these fields to serialize BBP access through `PHY_CSR3`, RF access through `PHY_CSR4`, configure receive/drop behavior through `TXRX_CSR0`, drive beacon timing through `TXRX_CSR9`, update WMM parameters through `AIFSN_CSR`/`CWMIN_CSR`/`CWMAX_CSR`/`AC_TXOP_CSR*`, and parse RX/TX descriptors. Firmware flow is anchored by `FIRMWARE_RT2571` and `FIRMWARE_IMAGE_BASE`.

## State and Persistence Behavior

EEPROM definitions describe persistent MAC address, antenna, NIC/LNA, geography, BBP overrides, frequency, LED, TX power, and RSSI offset state. Volatile state lives in hardware key tables, beacon SRAM, counters, TSF registers, and descriptors. Descriptor flags track valid/owner state, crypto IV/EIV/ICV side data, RX size, rate signal, and TX retry/IFS/key metadata.

## Dependencies and Integration Points

The header assumes rt2x00 field macros and Linux endian integer types. It integrates with mac80211 rate/crypto semantics through descriptor bits consumed by `rt73usb_write_tx_desc()` and `rt73usb_fill_rxdone()`, and with debugfs through the declared register/EEPROM/BBP/RF address ranges.

## Risks and Edge Cases

Several hardware comments are guessed or inherited from vendor behavior, especially antenna and RX ICV semantics. Descriptor sizes differ from rt61 PCI, so sharing logic without respecting USB descriptor width would corrupt frames. EEPROM field validation is necessary because invalid RF type, offsets, or power bytes can create unsupported channel tables or bad RSSI/TX power reports.

## Test Signals

Exercise debugfs register access windows, BBP/RF busy polling, descriptor decode on encrypted and unencrypted frames, per-BSS shared key slot mapping, pairwise key valid bitmaps, beacon offsets 0-3, LED polarity settings, rfkill GPIO7, and EEPROM fallback handling for `0xffff` words.
