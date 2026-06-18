# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500pci.h

## Purpose

`rt2500pci.h` is the hardware contract for the PCI/CardBus RT2500 family driver, specifically RT2560 MAC/BBP devices paired with RF2522, RF2523, RF2524, RF2525, RF2525E, or RF5222 radios. It contains no executable functions; it defines register offsets, bitfields, EEPROM layout, DMA descriptor formats, RF/BBP fields, and transmit-power conversion macros used by the matching `rt2500pci` implementation and common `rt2x00` helpers.

The file maps the RT2560 device into several persistent hardware spaces: 32-bit CSR registers from `CSR_REG_BASE` through `CSR_REG_SIZE`, 16-bit EEPROM words, 8-bit BBP registers, and cached 32-bit RF words. Those definitions let the C driver perform typed field extraction through the common `FIELD8`, `FIELD16`, and `FIELD32` macros instead of hard-coded masks.

## Important APIs, types, and data

The public interface is a set of constants:

- RF identifiers `RF2522`, `RF2523`, `RF2524`, `RF2525`, `RF2525E`, and `RF5222`, plus RT2560 revision constants B, C, and D.
- Register layout constants: `CSR_REG_BASE`, `CSR_REG_SIZE`, `EEPROM_SIZE`, `BBP_SIZE`, `RF_SIZE`, and `NUM_TX_QUEUES`.
- MAC/system CSRs: `CSR0` for revision, `CSR1` for reset and host-ready, `CSR3` through `CSR6` for station MAC/BSSID, `CSR7`/`CSR8` for interrupt source/mask, timing CSRs, power CSRs, and TSF/beacon registers.
- TX/RX DMA registers: `TXCSR0` through ring-base registers, `RXCSR0` through `RXCSR3`, queue pointer registers, and PCI-specific `PCICSR`.
- BBP/RF indirect access registers: `BBPCSR`, `RFCSR`, and `BBPCSR1`, plus BBP antenna/IQ fields and RF transmit-power fields.
- EEPROM words for MAC address, antenna defaults, NIC options, geography, BBP override table, transmit-power table, and RSSI calibration offset.
- 11-word TX and RX descriptor layouts, including owner/valid/result bits, retry count, PLCP fields, IV/EIV/key slots, RSSI/signal fields, and drop/error flags.
- Power conversion macros `TXPOWER_FROM_DEV()` and `TXPOWER_TO_DEV()` clamp EEPROM/mac80211 power values into the hardware range 0 through 31, defaulting invalid device values to 24.

The file depends on common rt2x00 bitfield types and helpers from surrounding headers. It assumes `__le32`, `u8`, and `clamp_t()` are available through the driver include chain.

## Control flow

There is no direct control flow in the header, but it shapes the runtime control flow in `rt2500pci.c`:

1. Probe code reads `CSR0_REVISION`, validates EEPROM words such as `EEPROM_ANTENNA`, selects an RF table by `EEPROM_ANTENNA_RF_TYPE`, and stores defaults in `struct rt2x00_dev`.
2. Initialization code toggles `CSR1_SOFT_RESET`, `CSR1_BBP_RESET`, and `CSR1_HOST_READY`, sets ring base registers and descriptor counts, initializes timing registers, configures `PCICSR`, and loads BBP override entries from EEPROM.
3. Channel and antenna code programs `RFCSR`/`BBPCSR` using the RF and BBP fields in this file, including RF3 transmit power and BBP R2/R14 antenna/IQ-flip fields.
4. RX filter, beacon, power-save, and interrupt paths manipulate `RXCSR0`, `CSR14`, `CSR20`, `PWRCSR1`, `CSR7`, and `CSR8`.
5. TX/RX completion code reads and writes the descriptor fields defined here to pass status, retry counts, crypto state, signal, RSSI, and frame sizes between the hardware rings and rt2x00 queue layer.

## State and persistence behavior

Most definitions correspond to stateful hardware registers. MAC and BSSID CSRs persist until reconfigured by interface changes. Timing fields in `CSR11` through `CSR22` persist across normal operation and control slot timing, beacon intervals, TSF operation, ATIM/CFP windows, and automatic wake. `PWRCSR1` persists desired power state until the hardware reaches a new BBP/RF current state. `CSR7` is write-one-to-clear interrupt state, while `CSR8` is persistent interrupt masking.

EEPROM definitions describe nonvolatile board data copied into the driver at probe: MAC address, antenna defaults, RF type, LED mode, hardware radio switch presence, per-channel transmit power, BBP override entries, and RSSI offset. The driver may synthesize defaults for invalid EEPROM words in memory; those defaults affect later initialization and reporting.

Descriptor definitions describe DMA-visible shared memory. Ownership, valid bits, retry/result status, buffer addresses, key/IV material, RSSI, and error flags are transient but must remain layout-stable across the queue implementation and the hardware DMA engine.

## Dependencies and integration points

The header integrates with:

- `rt2500pci.c`, which consumes almost every register, EEPROM, descriptor, and RF/BBP field in this file.
- Common rt2x00 support for bitfield manipulation, EEPROM access, RF cache access, DMA queue setup, mac80211 configuration, LED handling, rfkill polling, and crypto mapping.
- Linux PCI DMA/ring handling. Descriptor fields include physical buffer addresses and owner bits, so endian and ring-size definitions must match hardware exactly.
- mac80211 abstractions indirectly through power, antenna, RX filter, key, and queue configuration fields.

RF5222 introduces dual-band behavior while the other listed RF chips are 2.4 GHz parts, so channel table selection in the C driver depends directly on these RF constants.

## Risks

- Bitfield mistakes are high impact. A wrong mask or offset can reset the wrong engine, corrupt DMA descriptors, acknowledge the wrong interrupt, or program an invalid RF/BBP value.
- The descriptor layout differs from USB RT2500 and later RT2800 hardware. Reusing PCI descriptor constants in another driver would corrupt frame metadata and possibly DMA addresses.
- EEPROM defaults can hide bad board data. Incorrect `EEPROM_ANTENNA_RF_TYPE`, RSSI offset, or transmit-power fallback changes regulatory behavior, signal reporting, and channel support.
- Power-state and reset fields require strict sequencing in the C driver. Definitions such as `CSR1_HOST_READY` and `PWRCSR1_SET_STATE` look simple but are tied to polling loops and hardware self-clearing behavior.
- Security descriptor fields expose key and IV slots in DMA descriptors; incorrect ownership/cipher fields can cause plaintext transmission, failed decryption, or key leakage into the wrong descriptor.
- Several names preserve legacy spelling such as `TRESHOLD` and `LENTH`; mechanical cleanup would risk breaking driver references.

## Test signals

Useful validation is hardware-centered:

- Probe on RT2560 devices should identify `CSR0_REVISION`, RF type, EEPROM MAC, antenna defaults, and RSSI offset correctly.
- Bring-up tests should verify reset/host-ready sequencing, ring base programming, interrupt enable/clear behavior, and BBP/RF indirect access.
- TX/RX tests should check descriptor ownership transitions, retry/result fields, RSSI/signal extraction, CRC/PLCP error flags, and encrypted frame fields.
- Channel tests should cover RF252x 2.4 GHz paths and RF5222 2.4/5 GHz paths, checking RF3 power clamping and antenna/IQ flip fields.
- Power-save/rfkill tests should exercise `PWRCSR1`, `CSR20`, and GPIO/radio switch fields.
- Static build coverage should include all `rt2500pci.c` references to catch renamed or accidentally changed bitfield constants.
