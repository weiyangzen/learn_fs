# subset-b-004867 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500pci.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500usb.c

## Purpose

`rt2500usb.c` is the device-specific Linux driver for Ralink RT2570 USB wireless adapters in the rt2x00 stack. It connects USB vendor requests and RT2570 register semantics to the generic rt2x00 queue, EEPROM, mac80211, LED, rfkill, crypto, link-quality, and device-state callbacks.

The driver handles register access, BBP/RF indirect programming, EEPROM validation, radio bring-up, RF channel tables, power management, beacon upload, descriptor formatting, RX completion parsing, and USB device binding for many vendor/product IDs. It supports legacy 802.11b/g and limited 5 GHz operation when the RF5222 radio is present.

## Important APIs, types, and functions

Register access is centralized in `rt2500usb_register_read()`, `rt2500usb_register_write()`, their `_lock` variants, and `rt2500usb_register_multiwrite()`. They issue rt2x00 USB vendor requests using little-endian 16-bit CSR values. `rt2500usb_regbusy_read()` polls busy bits and backs the `WAIT_FOR_BBP` and `WAIT_FOR_RF` macros.

Indirect PHY access is implemented by:

- `rt2500usb_bbp_write()` and `rt2500usb_bbp_read()`, which serialize through `rt2x00dev->csr_mutex`, poll `PHY_CSR8_BUSY`, and use `PHY_CSR7` for data/register/read-control fields.
- `rt2500usb_rf_write()`, which polls `PHY_CSR10_RF_BUSY`, writes low RF bits through `PHY_CSR9`, writes high RF bits and bit count through `PHY_CSR10`, then updates the rt2x00 RF cache.

Major configuration callbacks include `rt2500usb_config_key()`, `rt2500usb_config_filter()`, `rt2500usb_config_intf()`, `rt2500usb_config_erp()`, `rt2500usb_config_ant()`, `rt2500usb_config_channel()`, `rt2500usb_config_txpower()`, `rt2500usb_config_ps()`, and aggregate `rt2500usb_config()`.

Initialization and state callbacks include `rt2500usb_init_registers()`, `rt2500usb_wait_bbp_ready()`, `rt2500usb_init_bbp()`, `rt2500usb_enable_radio()`, `rt2500usb_disable_radio()`, `rt2500usb_set_state()`, and `rt2500usb_set_device_state()`.

Queue and frame handling includes `rt2500usb_start_queue()`, `rt2500usb_stop_queue()`, `rt2500usb_write_tx_desc()`, `rt2500usb_write_beacon()`, `rt2500usb_get_tx_data_len()`, `rt2500usb_fill_rxdone()`, and the beacon URB callback `rt2500usb_beacondone()`.

Probe-time functions include `rt2500usb_validate_eeprom()`, `rt2500usb_init_eeprom()`, `rt2500usb_probe_hw_mode()`, `rt2500usb_probe_hw()`, and USB module binding through `rt2500usb_probe()` and `rt2500usb_driver`.

The file exports integration tables: `rt2500usb_mac80211_ops`, `rt2500usb_rt2x00_ops`, `rt2500usb_ops`, and `rt2500usb_device_table`.

## Control flow

Probe begins when `module_usb_driver()` registers `rt2500usb_driver` and the USB core matches an ID from `rt2500usb_device_table`. `rt2500usb_probe()` calls `rt2x00usb_probe()` with `rt2500usb_ops`. The rt2x00 core later calls `rt2500usb_probe_hw()`.

Hardware probing first reads and normalizes EEPROM in `rt2500usb_validate_eeprom()`. Invalid words are replaced with defaults for antenna, NIC, RSSI offset, BBP tuning threshold, and BBP tuning values. `rt2500usb_init_eeprom()` reads RF type, revision, antenna defaults, LED mode, hardware radio-button capability, and RSSI offset. `rt2500usb_probe_hw_mode()` sets mac80211 feature bits, selects RF channel tables, allocates per-channel info, and imports 2.4 GHz transmit power values from EEPROM.

Radio enable flows through `rt2500usb_enable_radio()`. `rt2500usb_init_registers()` sends USB device-mode setup requests, disables RX, toggles `MAC_CSR1` soft/BBP reset bits, programs BBP-ID auto-write registers, disables beacon generation, transitions to `STATE_AWAKE`, sets host-ready, programs revision-specific `PHY_CSR2`, sets frame length, clears crypto key state, configures RF latch behavior, and enables hardware sequence numbers. `rt2500usb_init_bbp()` waits until BBP register 0 is readable, writes a fixed BBP initialization table, then applies EEPROM BBP overrides.

Runtime configuration is split by mac80211 change flags. Channel changes patch RF3 transmit power, optionally perform a half-band prewrite for RF2525E, then write RF1 through RF4. Power-only updates rewrite RF3. Power-save updates program `MAC_CSR18` autowake fields, then request sleep or awake state through the device-state callback. Interface and ERP updates program beacon timing, TSF sync, MAC/BSSID, preamble, basic rates, beacon interval, and slot/SIFS/EIFS timing. RX filter updates `TXRX_CSR2` drop bits based on monitor mode and filter flags.

TX flow builds the RT2570 five-word descriptor in the SKB headroom. The descriptor carries retry limit, fragmentation, ACK, timestamp, OFDM, sequence, IFS, byte count, cipher/key, IV offset, queue contention settings, and PLCP values. Beacon TX is special: the driver disables beacon generation, prepends a descriptor, fills a USB bulk URB for a one-byte guardian transfer, submits the guardian URB, and then the callback submits the real beacon URB before freeing the SKB. The driver toggles `TXRX_CSR19` several times to avoid initial beacon-generation failure.

RX flow receives the hardware RX descriptor at the end of the USB buffer. `rt2500usb_fill_rxdone()` copies it to stable SKB descriptor storage, parses CRC/PLCP/cipher status, extracts IV/EIV when present, computes RSSI by subtracting `rt2x00dev->rssi_offset`, maps signal as PLCP or bitrate, marks same-BSS frames, and trims the SKB to the reported MPDU length.

## State and persistence behavior

The module parameter `nohwcrypt` disables hardware crypto capability at probe. EEPROM contents are read into `rt2x00dev->eeprom`; the driver mutates invalid values in that in-memory copy and uses those synthesized values for later setup. `rt2x00dev->rssi_offset`, `rt2x00dev->default_ant`, capability flags, and per-channel `channels_info` persist for the device lifetime.

The RF cache is updated by `rt2500usb_rf_write()` after each successful RF write, making later power-only updates possible through `rt2x00_rf_read()`. BBP tuning state persists in BBP registers and is reset by `rt2500usb_reset_tuner()` from EEPROM tuning words.

Hardware crypto state persists in key registers `SEC_CSR*` and key-valid bits in `TXRX_CSR0`. The driver enforces a single cipher algorithm across active hardware keys and only supports WEP key index 0 for WEP, otherwise falling back to software crypto.

Power state is requested through `MAC_CSR17` desired/current fields and polled until BBP/RF current state matches. Beacon generator state persists in `TXRX_CSR19`; RX enable state persists in `TXRX_CSR2`.

## Dependencies and integration points

This file depends on Linux USB, mac80211, LED class, module infrastructure, and rt2x00 core headers. It uses `rt2x00usb_vendor_request_buff()`, `rt2x00usb_vendor_req_buff_lock()`, `rt2x00usb_initialize()`, `rt2x00usb_uninitialize()`, `rt2x00usb_kick_queue()`, `rt2x00usb_flush_queue()`, `rt2x00usb_watchdog()`, `rt2x00usb_disable_radio()`, suspend/resume/disconnect helpers, and EEPROM USB reads.

It integrates with mac80211 through `struct ieee80211_ops`, mostly delegating generic operations to `rt2x00mac_*` wrappers. It integrates with rt2x00lib through `struct rt2x00lib_ops`, where the device-specific callbacks are registered. Queue sizing is provided through `rt2500usb_queue_init()`, including RX, four AC queues, beacon queue, and required ATIM queue.

RF channel tables are local static data keyed by RF type. Hardware capability export depends on those tables, EEPROM TX power bytes, and the RF5222 dual-band case.

## Risks

- USB register access is mostly fire-and-forget. Basic read/write helpers ignore vendor request status, so failures can surface later as bad register values or busy-loop errors.
- BBP/RF indirect access relies on `csr_mutex` and bounded polling. Calling unlocked variants while already serialized is intentional; mixing variants incorrectly risks deadlock or register races.
- `rt2500usb_config_key()` has strict hardware limits: all active hardware keys must use the same cipher, WEP is restricted to key index 0, and pairwise/shared key index collisions can return `-ENOSPC`.
- EEPROM validation reads BBP register 17 before the full radio initialization path. If BBP access is not ready, the derived VGC lower bound can be wrong.
- `rt2500usb_probe_hw()` reads calibrated RSSI offset in `rt2500usb_init_eeprom()` but then sets `rt2x00dev->rssi_offset = DEFAULT_RSSI_OFFSET` at the end, overriding EEPROM calibration. This is intentional or legacy behavior but is a strong audit point for RSSI accuracy.
- Beacon upload depends on guardian URB ordering and repeated `TXRX_CSR19` toggles. URB submission failure is not checked in this path, so beacon loss may be silent.
- RX descriptor location is computed from `actual_length - desc_size`; malformed short USB transfers would underflow without prior core validation.
- Power-save autowake programs `beacon_int - 20`; unexpectedly low beacon intervals could underflow the field.
- RF tables are hand-coded constants. Incorrect RF type detection or channel index assumptions can program invalid synthesizer values.

## Test signals

- Build coverage for `CONFIG_RT2X00_LIB_LEDS`, `CONFIG_RT2X00_LIB_DEBUGFS`, and normal builds should cover optional callback tables.
- Probe tests on RT2570 devices should validate EEPROM defaults, RF detection, channel table selection, LED registration, hardware button capability, and queue setup.
- USB fault-injection or tracing should confirm vendor request failures, BBP/RF busy timeouts, and register read/write ordering are observable.
- Radio bring-up should reach `STATE_AWAKE`, set `MAC_CSR1_HOST_READY`, complete BBP initialization, and avoid "BBP register access failed" and "Indirect register access failed" logs.
- Channel tests should cover all supported RF chip table paths, including RF2525E half-band prewrite and RF5222 5 GHz channels.
- Crypto tests should verify hardware crypto success for supported single-cipher cases and software fallback for mixed cipher, WEP nonzero index, and full key mask cases.
- TX/RX tests should inspect descriptor fields, USB packet length padding rules, RSSI offset application, FCS/PLCP reporting, and encrypted RX IV/EIV propagation.
- Beacon/AP tests should verify guardian URB behavior, TSF/beacon enable toggling, DTIM/multicast behavior, and AP interface limit handling.
- Power-save and rfkill tests should exercise GPIO polling, autowake, sleep/awake transitions, and failure logging from `rt2500usb_set_device_state()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500usb.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800.h

## Purpose

`rt2800.h` is the shared hardware definition header for the rt2800 generation of rt2x00 drivers, covering RT2800 PCI/PCIe/USB devices and related SoC variants. It is a broad register and descriptor contract used by `rt2800lib.c`, `rt2800pci.c`, `rt2800usb.c`, and companion headers. It supports many RF chips, MAC revisions, EEPROM/efuse formats, MCU mailbox commands, WMM/HT registers, DMA engines, security tables, BBP/RFCSR fields, TX/RX wireless-info descriptors, and transmit-power conversion rules.

Unlike `rt2500usb.h` and `rt2500pci.h`, this header covers a much larger device family: legacy RF2820/RF2850 parts, RT30xx/33xx/35xx/53xx/55xx, RT3290, RT5350, MT7620-like RF7620, and three-chain devices such as RF3053/RF3853. It therefore contains many overlapping or revision-specific field definitions.

## Important APIs, types, and data

Major identifier groups include:

- RF identifiers from `RF2820` through `RF7620`.
- Revision constants such as `REV_RT2860C`, `REV_RT2872E`, `REV_RT3070F`, `REV_RT5390F`, `REV_RT5370G`, `REV_RT5390R`, and `REV_RT5592C`.
- Global layout constants: CSR base `0x1000`, EEPROM size `0x0200`, BBP size `0x00ff`, RFCSR size `0x0040`, and four TX queues.

The low register ranges define EEPROM/efuse and SoC control:

- `E2PROM_CSR`, RT3290 `EFUSE_CTRL_3290`/data registers, generic `EFUSE_CTRL`/data registers.
- `CMB_CTRL`, `OSC_CTRL`, `PLL_CTRL`, `WLAN_FUN_CTRL`, `AUX_CTRL`, `OPT_14_CSR`, coexistence registers, GPIO controls, LDO controls, and calibration/debug controls.

DMA and queue definitions include:

- `INT_SOURCE_CSR` and `INT_MASK_CSR` for interrupt source/mask bits.
- `WPDMA_GLO_CFG`, `WPDMA_RST_IDX`, `DELAY_INT_CFG`, TX/RX ring base/count/index registers, USB DMA fields, PBF registers, and queue page counters.
- WMM registers `WMM_AIFSN_CFG`, `WMM_CWMIN_CFG`, `WMM_CWMAX_CFG`, and `WMM_TXOP*`.

MAC/PHY registers include:

- MAC identity, reset, address, BSSID, frame length, BBP/RF indirect access, LED control, AMPDU limits, block-ack window forcing, timing/TSF/beacon registers, channel busy/idle counters, power/autowake, MIMO power save, EDCA, TX power per rate, TX pin/band/SW config, TXOP/RTS/retry/link/fallback/protection registers, RX filter and auto response fields, basic rate registers, security counters, survey/statistics counters, and TX status FIFO fields.

Memory-map helpers include:

- Security table base addresses and helpers: `MAC_WCID_ENTRY()`, `PAIRWISE_KEY_ENTRY()`, `MAC_IVEIV_ENTRY()`, `MAC_WCID_ATTR_ENTRY()`, `SHARED_KEY_ENTRY()`, and `SHARED_KEY_MODE_ENTRY()`.
- Packed structs `struct mac_wcid_entry`, `struct hw_key_entry`, and `struct mac_iveiv_entry`.
- Beacon memory base helpers `HW_BEACON_BASE()` and `BEACON_BASE_TO_OFFSET()`.

EEPROM definitions include `enum rt2800_eeprom_word` plus field masks for NIC chain counts, RF type, hardware radio, external PA/LNA/ALC, BT coexistence, antenna diversity, LED polarity/mode, frequency offset, RSSI offsets, LNA values, per-band transmit power, TSSI/temperature compensation boundaries, per-rate power offsets, BBP overrides, extended LNA/three-chain entries, and byte-addressed IQ calibration data.

Descriptor definitions include TXWI and RXWI sizes and fields for AMPDU, MCS, bandwidth, short GI, STBC, PHY mode, MPDU density, wireless client ID, packet ID mapping, IV/EIV, RX sequence/TID, RSSI chains, and SNR.

MCU definitions include mailbox registers, LED control fields, commands such as `MCU_SLEEP`, `MCU_WAKEUP`, `MCU_RADIO_OFF`, `MCU_LED`, `MCU_RADAR`, `MCU_FREQ_OFFSET`, `MCU_POWER_SAVE`, and mailbox tokens.

## Control flow

There is no executable control flow in this header, but it defines the state machine used by rt2800 code:

1. Probe code reads MAC revision through `MAC_CSR0` or `MAC_CSR0_3290`, detects EEPROM versus efuse using the EEPROM/efuse registers, validates `enum rt2800_eeprom_word` contents, extracts RF type and stream counts, and sets capabilities.
2. Firmware and MCU setup use PBF, mailbox, H2M, and MCU command constants for device boot, sleep/wake, LED, radar, frequency offset, and power-save control.
3. Radio initialization waits for CSR, WPDMA, BBP, RFCSR, PLL, oscillator, and MAC busy fields; then programs BBP/RFCSR/RF fields by RF type and revision.
4. Queue setup uses WPDMA ring registers for PCI-style devices, USB DMA registers for USB devices, WMM/EDCA registers for QoS, and TXWI/RXWI definitions for per-frame metadata.
5. TX completion reads `TX_STA_FIFO`, maps packet IDs back to rt2x00 queue entries, and extracts success, aggregation, ACK-required, WCID, MCS, bandwidth, SGI, and PHY mode.
6. RX handling reads RXWI fields for length, WCID, key index, BSSID, TID, sequence, MCS, bandwidth, SGI, STBC, PHY mode, RSSI0-2, and SNR.
7. Security configuration writes WCID, pairwise/shared key, IV/EIV, and attribute tables using the memory-map helpers.
8. Channel, antenna, calibration, and transmit-power code uses RFCSR, BBP, TX pin, TX band, frequency offset, per-rate power, TSSI, IQ calibration, and RF gain fields to program band-specific operation.

## State and persistence behavior

The header describes persistent hardware state across several domains:

- MAC state: reset, TX/RX enable, address/BSSID matching, frame limits, beacon/TSF timing, RX filtering, auto response, EDCA/WMM, retry/fallback, protection, AMPDU, and block-ack behavior.
- DMA state: ring bases, counters, current/done indexes, delay interrupts, WPDMA global enable/busy state, USB bulk aggregation state, and PBF page counters.
- Radio/PHY state: BBP, RF, RFCSR, TX power, TX pin, band, bandwidth, calibration, chain, LNA, PA, VCO, RSSI, TSSI, and oscillator/PLL controls.
- Security state: WCID table, pairwise/shared keys, IV/EIV state, key attributes, and shared key modes. Some key memory overlaps beacon memory for beacon slots 6 and 7, so enabling all MBSS beacons reduces usable pairwise key table space.
- EEPROM/efuse state: persistent board calibration values and capability flags imported at probe and interpreted throughout the device lifetime.
- MCU state: mailbox ownership/status slots and command tokens persist until firmware consumes and reports them.

Many register fields are clear-on-read or write-one-to-clear status/counter fields, especially interrupt and statistics registers. Others are self-clearing trigger bits such as efuse kick, EEPROM reload, oscillator calibration request, and reset/index bits.

## Dependencies and integration points

`rt2800.h` integrates with:

- `rt2800lib.c`, which implements shared rt2800 logic for EEPROM parsing, BBP/RF/RFCSR programming, channel/power calibration, crypto, TSF/survey, filters, antenna, link tuning, watchdog, and TX/RX wireless-info handling.
- `rt2800usb.c` and `rt2800pci.c`, which provide bus-specific firmware loading, DMA setup, queue operation, device state transitions, and probe glue.
- Common rt2x00 bitfield helpers, RF cache, EEPROM/efuse helpers, queue descriptors, mac80211 integration, and debugfs register windows.
- Linux endian/packed struct semantics for hardware memory tables and TXWI/RXWI descriptors.

The header contains several intentional aliases and overlapping addresses for different chip families. For example, some TX power, TX beamforming, RF gain, and HT fallback registers share numeric addresses depending on revision. Correct consumers must always gate by chipset/RF/revision before applying a field.

## Risks

- Revision and RF gating is the dominant risk. The same offset can mean different things on legacy PCI, USB, RT3290, RT3593, RT5592, MT7620, or three-chain devices.
- Bitfield overlaps are intentional in places. Applying a generic field to a chip-specific register variant can corrupt power, calibration, beamforming, or fallback state.
- EEPROM word enum values are logical indices, while IQ calibration constants are byte addresses. Mixing those addressing models will read or write the wrong calibration data.
- Security and beacon memory overlap for beacon slots 6 and 7. Code enabling many beacons must respect the reduced pairwise key table limit or key memory can be overwritten by beacon data.
- TX status FIFO is finite and read-to-pop. Failing to drain it after `TX_FIFO_STATUS` can lose status, while over-reading invalid entries can fabricate completions.
- TXWI packet ID is only four bits and encodes queue/entry information. Aggregation reports the first frame's packet ID, so completion code must handle ambiguous aggregate status carefully.
- Transmit power fields span EEPROM, BBP, RFCSR, RF, per-rate MAC registers, TSSI boundaries, external PA/LNA flags, EIRP limits, and per-chain corrections. Incorrect clamping or signed handling can create regulatory or connectivity problems.
- USB and PCI DMA controls coexist in the same header. Bus-specific drivers must not program the wrong DMA block.
- Several comments label registers as unknown, undocumented, or FIXME. Those areas should be treated as empirically derived hardware programming sequences.

## Test signals

- Compile coverage should include rt2800 PCI and USB variants, debugfs, hardware crypto, firmware loading, and optional chipset families.
- Probe validation should cover EEPROM and efuse devices, RT3290 special identity paths, RF type detection, stream count extraction, and LED/frequency/RSSI/LNA/TX power parsing.
- Register trace tests should verify reset, WPDMA/USB DMA, BBP/RF/RFCSR busy polling, MCU mailbox, and firmware boot sequences.
- TX/RX tests should validate TXWI/RXWI sizes for four-, five-, and six-word variants; packet ID mapping; TX status FIFO draining; aggregate status handling; RSSI/SNR chain values; and cipher/key index propagation.
- Security tests should exercise pairwise/shared key tables, WCID attributes, IV/EIV table updates, shared key modes, and reduced key table behavior when beacon slots 6/7 are used.
- Channel and calibration tests should cover 2.4 GHz, 5 GHz, HT20, HT40, RFCSR VCO calibration, frequency offset, external PA/LNA, TSSI compensation, and IQ calibration data.
- Power tests should compare EEPROM per-rate/per-channel settings with programmed `TX_PWR_CFG*`, RFCSR, BBP, EIRP limit, and measured conducted output.
- Watchdog tests should exercise `RT2800_WATCHDOG_HANG` and `RT2800_WATCHDOG_DMA_BUSY` conditions, DMA busy recovery, and MAC/BBP/RF busy detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800.h -->
