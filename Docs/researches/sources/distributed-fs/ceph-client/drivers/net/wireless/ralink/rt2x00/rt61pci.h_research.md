# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt61pci.h

## Purpose

`rt61pci.h` is the hardware contract for the Ralink rt61 PCI rt2x00 driver family. It names supported PCI/RF IDs, firmware images, register windows, shared on-chip memory regions, EEPROM layout, BBP/RF fields, host DMA registers, interrupt bits, MCU mailbox commands, and TX/RX descriptor formats used by the companion PCI implementation.

## Important APIs, Types, and Functions

The file exports constants and packed hardware records rather than functions. Important structures are `struct hw_key_entry`, `struct hw_pairwise_ta_entry`, and the descriptor field macros for 16-word TX/RX DMA descriptors. Key macros map security table slots (`SHARED_KEY_ENTRY`, `PAIRWISE_KEY_ENTRY`, `PAIRWISE_TA_ENTRY`), beacon memory (`HW_BEACON_OFFSET`), and EEPROM-derived power conversion (`TXPOWER_FROM_DEV`, `TXPOWER_TO_DEV`).

## Control Flow

Runtime control flow is encoded through register semantics: host code resets MAC/BBP via `MAC_CSR1`, drives firmware and MCU commands through mailbox/firmware registers, configures DMA rings through base/ring/kick registers, clears interrupts by writing `INT_SOURCE_CSR`, and gates RX/TX behavior through `TXRX_CSR*`, `SEC_CSR*`, and descriptor owner/valid bits.

## State and Persistence Behavior

Persistent calibration and identity state lives in EEPROM fields for MAC address, RF type, antenna defaults, LNA flags, geography, BBP overrides, frequency offset, LED polarity/mode, RSSI offsets, and per-band TX power. Volatile state is represented in CSR registers, security key SRAM, beacon SRAM, firmware memory, DMA ring descriptors, and counters that may clear on read.

## Dependencies and Integration Points

The header depends on rt2x00 field helpers such as `FIELD32`, `FIELD16`, and `FIELD8`, Linux endian types, and shared rt2x00 concepts for RF chips, queues, ciphers, and EEPROM parsing. It integrates the rt61 PCI driver with mac80211 queue setup, firmware loading, hardware crypto, rt2x00 debugfs register access, and PCI DMA.

## Risks and Edge Cases

Descriptor size and owner-bit ordering are correctness-critical because hardware consumes DMA entries asynchronously. EEPROM defaults must tolerate `0xffff`/invalid values without selecting unsupported RF parts. Bitfield comments include several guessed semantics, so register changes should be validated on hardware. Security-table indexing spans shared and pairwise tables with narrow bitmap fields, making off-by-one errors high impact.

## Test Signals

Useful signals include rt61 PCI probe on each chipset ID, firmware upload for `rt2561.bin`, `rt2561s.bin`, and `rt2661.bin`, EEPROM fallback behavior, hardware crypto key install/remove, beacon SRAM writes, RX/TX DMA ring wraparound, interrupt clear/mask behavior, suspend/resume power transitions, and TX power clamping across 2.4/5 GHz channel tables.
