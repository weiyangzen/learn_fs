# subset-b-004872 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt61pci.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt61pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt73usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt73usb.c

## Purpose

`rt73usb.c` implements the Ralink RT2571W/RT2671 USB wireless driver on top of rt2x00usb and mac80211. It owns BBP/RF indirect register access, firmware validation/loading, EEPROM normalization, RF/channel setup, hardware crypto programming, LED/rfkill support, link tuning, TX/RX descriptor translation, queue sizing, mac80211 callbacks, and the USB device ID table.

## Important APIs, Types, and Functions

Driver entry is `module_usb_driver(rt73usb_driver)`, with `rt73usb_probe()` delegating allocation/binding to `rt2x00usb_probe()`. `rt73usb_rt2x00_ops` is the main integration table: it supplies firmware hooks, device-state transitions, queue operations, descriptor writers, RX completion parsing, crypto configuration, link tuning, and config handlers. `rt73usb_mac80211_ops` exposes mac80211 callbacks, mostly via rt2x00 generic helpers plus local `conf_tx()` and `get_tsf()`. Critical helpers include `rt73usb_bbp_read/write()`, `rt73usb_rf_write()`, `rt73usb_config_shared_key()`, `rt73usb_config_pairwise_key()`, `rt73usb_config_channel()`, `rt73usb_write_tx_desc()`, `rt73usb_fill_rxdone()`, `rt73usb_validate_eeprom()`, `rt73usb_init_eeprom()`, and `rt73usb_probe_hw_mode()`.

## Control Flow

Probe flows through rt2x00usb into `probe_hw`: EEPROM is read and repaired, chip/RF IDs are validated, GPIO7 is configured for rfkill polling, channel/rate specs are built from RF-specific tables, and firmware/hardware-crypto/link-tuning capabilities are advertised. Startup later loads `rt73.bin` after CRC/length checks, initializes MAC/BBP registers, wakes the device through `MAC_CSR12`, clears security/beacon state, and applies EEPROM BBP overrides. Configuration callbacks update filters, MAC/BSSID, ERP timing, antenna/LNA, channel, TX power, retry limits, and power-save autowake. TX pushes a six-word descriptor into skb data, writes optional IV/EIV words, and relies on rt2x00usb to submit URBs. RX copies the descriptor out before skb pointer movement, reports CRC/crypto status, RSSI, rate signal type, BSS match, and strips descriptor bytes.

## State and Persistence Behavior

Persistent state is the EEPROM image: MAC, antenna defaults, RF type, hardware radio flag, LED polarity/mode, frequency offset, RSSI offsets, BBP overrides, and per-channel TX power. Volatile state includes CSR/BBP/RF registers, hardware key tables, beacon SRAM, `led_mcu_reg`, `lna_gain`, `freq_offset`, rf capability bits, queue descriptors, TSF registers, and link-quality tuner state. The `nohwcrypt` module parameter disables hardware crypto even when supported.

## Dependencies and Integration Points

The file depends on `rt2x00.h`, `rt2x00usb.h`, `rt73usb.h`, Linux USB, firmware, LED, rfkill, CRC ITU-T, and mac80211. It integrates with rt2x00lib for generic mac80211 operations, queue management, EEPROM storage, debugfs dumps, PLCP/rate handling, and crypto framing conventions. Hardware-facing integration is through USB vendor requests and register/multiwrite helpers.

## Risks and Edge Cases

Indirect BBP/RF access relies on busy-bit polling and `csr_mutex`; timeout paths can silently leave old values in place. Key-slot allocation uses bitmaps and `ffz()` with BSS/key index arithmetic, so invalid key indices or full tables can break encryption. The device requires exactly 2048-byte firmware with trailing CRC; bad firmware blocks startup. Beacon writes temporarily disable generation and free the skb, so error paths must keep `entry->skb` ownership clear. RSSI/LNA math depends on RF type, external LNA flags, and sane EEPROM offsets. USB packet length padding deliberately avoids exact max-packet multiples.

## Test Signals

Test with RT73 devices using each RF table, firmware CRC failure/success, hardware crypto enable/disable, shared/pairwise key exhaustion, rfkill GPIO transitions, LED radio/assoc/quality operations, 2.4/5 GHz channel changes, power-save sleep/wakeup, beacon generation, WMM `conf_tx`, RX crypto errors, descriptor length trimming, and USB suspend/resume/reset-resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt73usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt73usb.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt73usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/Kconfig

## Purpose

This Kconfig file defines the Realtek wireless vendor menu gate `WLAN_VENDOR_REALTEK`. When enabled, it exposes the Realtek subdriver families under `drivers/net/wireless/realtek/`.

## Important APIs, Types, and Functions

The only symbol defined here is `WLAN_VENDOR_REALTEK`, a default-y boolean menu selector. It sources `rtl818x`, `rtlwifi`, `rtl8xxxu`, `rtw88`, and `rtw89` Kconfig files.

## Control Flow

Kconfig processing enters the nested `if WLAN_VENDOR_REALTEK` block only when the vendor menu is enabled. Disabling it hides Realtek-specific questions but does not directly force lower-level symbols off if selected elsewhere.

## State and Persistence Behavior

Persistent state is the user's kernel `.config` choice for `WLAN_VENDOR_REALTEK` and any Realtek child symbols selected below it.

## Dependencies and Integration Points

This file integrates with the Linux wireless Kconfig vendor hierarchy and delegates all actual driver dependencies to child Kconfig files.

## Risks and Edge Cases

Because the vendor symbol is only a visibility gate, build assumptions should not treat it as a hardware-driver dependency. New Realtek families must be sourced here or they will not appear in menuconfig.

## Test Signals

Run `make menuconfig`/`olddefconfig` with the vendor option toggled and confirm all Realtek child menus appear/disappear while direct symbol dependencies remain controlled by their own Kconfig entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/Makefile

## Purpose

This Makefile routes enabled Realtek wireless configuration symbols to their subdirectories.

## Important APIs, Types, and Functions

It uses `obj-$(CONFIG_...) += dir/` entries for `RTL8180`, `RTL8187`, `RTLWIFI`, `RTL8XXXU`, `RTW88`, and `RTW89`.

## Control Flow

Kbuild descends into a subdirectory only when the matching config symbol is `y` or `m`. Both `CONFIG_RTL8180` and `CONFIG_RTL8187` point to `rtl818x/`, where the next Makefile selects the exact PCI or USB implementation.

## State and Persistence Behavior

Build output is entirely determined by `.config`; this file stores no runtime state.

## Dependencies and Integration Points

The Makefile integrates Realtek drivers with kernel kbuild and expects child directories to contain Makefiles keyed to the same config symbols.

## Risks and Edge Cases

Multiple symbols can cause the same directory to be visited. Child Makefiles must remain idempotent and symbol-specific to avoid missing or duplicate objects.

## Test Signals

Build with each Realtek symbol as built-in/module and verify the expected directory is visited and module names are generated once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Kconfig

## Purpose

`rtl818x/Kconfig` declares the legacy Realtek 818x mac80211 drivers: PCI/CardBus `RTL8180` for RTL8180/8185/8187SE and USB `RTL8187` for RTL8187/8187B, plus optional LED support for RTL8187.

## Important APIs, Types, and Functions

Symbols are `RTL8180`, `RTL8187`, and `RTL8187_LEDS`. `RTL8180` depends on `MAC80211 && PCI` and selects `EEPROM_93CX6`; `RTL8187` depends on `MAC80211 && USB` and also selects `EEPROM_93CX6`; `RTL8187_LEDS` is a bool enabled when LED class and mac80211 LED support are compatible.

## Control Flow

Selecting either driver exposes build rules under `rtl818x/`. Help text documents representative hardware and warns that Linksys WUSB54GC variants map to different drivers depending on revision.

## State and Persistence Behavior

Persistent state is the kernel config selection. Runtime driver behavior is in the selected child modules, not this file.

## Dependencies and Integration Points

The file links the rtl818x family to mac80211, PCI/USB buses, and the 93cx6 EEPROM helper. LED support is conditional on `MAC80211_LEDS` and `LEDS_CLASS` linkage mode.

## Risks and Edge Cases

The broad device descriptions can invite selecting the wrong driver for similarly branded hardware. `RTL8187_LEDS` has a linkage constraint so built-in/module combinations should be checked when changing dependencies.

## Test Signals

Use config combinations for built-in and modular `RTL8180`, `RTL8187`, `MAC80211_LEDS`, and `LEDS_CLASS`; confirm `EEPROM_93CX6` is selected and no unmet dependency warnings appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Makefile

## Purpose

This Makefile dispatches enabled rtl818x family symbols to PCI and USB subdrivers.

## Important APIs, Types, and Functions

`obj-$(CONFIG_RTL8180) += rtl8180/` and `obj-$(CONFIG_RTL8187) += rtl8187/` are the only build directives.

## Control Flow

Kbuild descends into `rtl8180/` for PCI/CardBus support and `rtl8187/` for USB support based on config state.

## State and Persistence Behavior

No runtime state is present; it is a pure kbuild routing file.

## Dependencies and Integration Points

It relies on parent Realtek Makefile selection and child subdirectory Makefiles to build concrete modules.

## Risks and Edge Cases

If both symbols are enabled, both subdirectories build. Any shared headers in `rtl818x/` must remain compatible with both child drivers.

## Test Signals

Build `CONFIG_RTL8180=m`, `CONFIG_RTL8187=m`, and both together to confirm expected modules and no duplicate object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/Makefile

## Purpose

This Makefile builds the RTL8180/8185/8187SE PCI module object composition.

## Important APIs, Types, and Functions

`rtl818x_pci-objs` links `dev.o`, RF front ends (`rtl8225.o`, `sa2400.o`, `max2820.o`, `grf5101.o`, `rtl8225se.o`), and `obj-$(CONFIG_RTL8180) += rtl818x_pci.o`. `ccflags-y += -I $(src)/..` exposes shared rtl818x headers.

## Control Flow

When `CONFIG_RTL8180` is enabled, kbuild compiles all listed objects into the `rtl818x_pci` module/built-in object. RF implementations are linked unconditionally because `dev.c` chooses the correct `rtl818x_rf_ops` at probe time.

## State and Persistence Behavior

There is no runtime state. Build state is derived from config and object timestamps.

## Dependencies and Integration Points

The module integrates the PCI driver core with all supported RF front-end implementations and shared register definitions one directory up.

## Risks and Edge Cases

Removing an RF object can break devices whose EEPROM RF type selects that frontend even if other devices still build. The include path must remain aligned with shared `rtl818x.h` placement.

## Test Signals

Build `rtl818x_pci` as module and built-in, verify all RF object symbols resolve, and probe cards for RF types 3, 4, 5, and 9.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/dev.c

## Purpose

`dev.c` is the RTL8180/RTL8185/RTL8187SE PCI/CardBus mac80211 driver core. It handles PCI probe/remove, MMIO/PIO mapping, EEPROM parsing, RF frontend selection, DMA ring allocation, interrupt handling, TX/RX descriptor processing, hardware reset/init/stop, mac80211 interface/config callbacks, software beaconing, and filter/basic-rate/ERP configuration.

## Important APIs, Types, and Functions

The module is registered through `module_pci_driver(rtl8180_driver)`. `rtl8180_ops` exposes mac80211 callbacks. `rtl8180_probe()` sets up PCI resources, `ieee80211_hw`, chip-family detection, bands/rates, EEPROM data, RF ops, and registration. `rtl8180_start()` allocates rings, initializes hardware, requests IRQ, enables interrupts, and turns on RX/TX. `rtl8180_stop()` disables interrupts/RX/TX, stops RF, powers down analog state, frees IRQ and rings. Data path functions are `rtl8180_tx()`, `rtl8180_handle_tx()`, and `rtl8180_handle_rx()`. Hardware helpers include `rtl8180_write_phy()`, `rtl8180_set_anaparam*()`, `rtl8180_init_hw()`, `rtl8180_conf_basic_rates()`, `rtl8180_conf_erp()`, and `rtl8180_eeprom_read()`.

## Control Flow

Probe enables PCI, requests BARs, requires 32-bit DMA, allocates mac80211 hardware, maps MMIO or PIO, detects chip family from `TX_CONF`, configures queue count and band capabilities, reads EEPROM, selects an RF ops table by RF type, validates/generates the MAC address, then registers with mac80211. Start allocates a 32-entry RX ring and 16-entry TX rings, writes descriptor base addresses, resets and configures MAC registers, performs RF init, sets basic rates/antenna config, installs an IRQ handler, and enables RX/TX. TX maps skb data, fills descriptor fields, assigns sequence numbers when requested, writes flags last with barriers, queues the skb, and kicks the mapped hardware queue. Interrupts dispatch completed TX rings and RX descriptors. RX swaps in a fresh mapped skb before delivering the old skb to mac80211 with rate, signal, TSF, FCS, and preamble metadata.

## State and Persistence Behavior

Persistent device state comes from 93cx6 EEPROM: RF type, carrier-sense threshold, MAC address, channel TX powers, analog parameters, RF parameters, RTL8187SE antenna diversity, crystal, and thermal data. Runtime state is in `struct rtl8180_priv`: MMIO map, RF ops, active vif, spinlock, RX/TX rings and DMA addresses, channel/rate tables, queue parameters, chip family, RX filter mask, slot/ACK timing, analog/RF calibration fields, and sequence number. `struct rtl8180_vif` stores per-interface beacon work and beacon-enable state.

## Dependencies and Integration Points

The driver depends on PCI, DMA mapping, interrupts, `eeprom_93cx6`, mac80211, shared `rtl818x.h` CSR definitions, and RF implementations (`rtl8225`, `rtl8225se`, `sa2400`, `max2820`, `grf5101`). It integrates with mac80211 queue flow control, rx/tx status APIs, BSS change notifications, multicast/filter callbacks, channel config, and TSF reads.

## Risks and Edge Cases

DMA descriptor ownership uses memory barriers and must keep flag writes last; reordering can let hardware read partial descriptors. RX error paths can leak or reuse mappings incorrectly if ring allocation partially fails. RTL8187SE differs in descriptor size, interrupt status width, queue mapping, and MMIO-only support. Software beaconing uses delayed work and the normal data queue rather than a finalized beacon queue, so queue stoppage and timing drift are expected risks. Filter updates toggle bits based on `changed_flags`, so callers must pass correct deltas. EEPROM-derived RF selection rejects unsupported RFs and invalid chip families.

## Test Signals

Validate PCI probe/remove for RTL8180, RTL8185, and RTL8187SE IDs; MMIO fallback behavior; invalid EEPROM MAC fallback; RF type selection; start/stop ring allocation and cleanup; TX queue stop/wake under load; RX descriptor wraparound; interrupt paths for 16-bit and 32-bit status; station and ad-hoc modes; BSSID/basic-rate/ERP changes; multicast/promiscuous/FCS/control filters; software beaconing; and suspend/resume stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/grf5101.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/grf5101.c

## Purpose

`grf5101.c` implements the `rtl818x_rf_ops` frontend for GCT GRF5101 radios on RTL8180-class hardware.

## Important APIs, Types, and Functions

It exports `grf5101_rf_ops` with `.init`, `.stop`, `.set_chan`, and `.calc_rssi`. Internal helpers are `write_grf5101()` for encoded bit-banged RF writes, `grf5101_write_phy_antenna()` for baseband antenna selection, and `grf5101_rf_calc_rssi()` for RTL8180 signal conversion.

## Control Flow

RF init restores analog parameters, sends a fixed GRF5101 register initialization sequence, enables the RF path, programs baseband registers, applies antenna diversity from `CONFIG2`, and sets carrier-sense threshold. Channel changes write TX power, latch frequency using channel index, and update channel-14/default antenna baseband bits. Stop powers down analog/RF state and writes shutdown values.

## State and Persistence Behavior

The code consumes `priv->anaparam`, `priv->rfparam`, `priv->csthreshold`, and per-channel `hw_value` loaded from EEPROM by `dev.c`. It writes volatile RF registers and baseband PHY registers only.

## Dependencies and Integration Points

It depends on `rtl8180_write_phy()`, `rtl8180_set_anaparam()`, MMIO helpers, `struct rtl8180_priv`, and mac80211 channel frequency conversion. `dev.c` selects this ops table for EEPROM RF type 5.

## Risks and Edge Cases

`write_grf5101()` uses a custom nibble-encoding table and magic host-bang control word; mistakes corrupt RF programming. RSSI conversion is approximate and saturates above AGC 60. Channel 14 antenna attenuation and `RF_PARAM_ANTBDEFAULT` need hardware validation.

## Test Signals

Probe a GRF5101 card, verify RF type 5 selection, associate on channels 1/6/11/14, compare RSSI with known signal levels, test antenna-diversity EEPROM settings, and confirm stop/start cycles leave RF powered correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/grf5101.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/grf5101.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/grf5101.h

## Purpose

`grf5101.h` declares the GRF5101 RF frontend contract for the RTL8180 driver.

## Important APIs, Types, and Functions

It defines `GRF5101_ANTENNA` and declares `extern const struct rtl818x_rf_ops grf5101_rf_ops`.

## Control Flow

`dev.c` references `grf5101_rf_ops` after EEPROM RF detection; `grf5101.c` uses `GRF5101_ANTENNA` as the base value for PHY antenna programming.

## State and Persistence Behavior

The header has no state. Its constant influences volatile PHY writes performed by the implementation.

## Dependencies and Integration Points

It depends on the shared declaration of `struct rtl818x_rf_ops` via included users and is included by `dev.c`/`grf5101.c`.

## Risks and Edge Cases

Changing the antenna constant affects all GRF5101 channel programming and must be checked with channel 14 and antenna-B EEPROM settings.

## Test Signals

Build the `rtl818x_pci` module and verify RF type 5 links to `grf5101_rf_ops`; runtime tests should confirm antenna selection and RX sensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/grf5101.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/max2820.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/max2820.c

## Purpose

`max2820.c` implements the Maxim MAX2820 RF frontend for RTL8180 hardware.

## Important APIs, Types, and Functions

It exports `max2820_rf_ops` with `.init`, `.stop`, `.set_chan`, and `.calc_rssi`. Internal helpers include the `max2820_chan[]` synthesizer table, `write_max2820()` for RF register writes through `RFPinsOutput`, `max2820_write_phy_antenna()`, and `max2820_rf_calc_rssi()`.

## Control Flow

Initialization writes MAX2820 test/enable/synth/RX/PA registers, sets channel 1, configures baseband registers, applies antenna diversity, sets signal thresholds, and calls channel setup again. Channel changes convert mac80211 frequency to channel, read EEPROM-backed TX power, drive PA bias through BB register 3, update antenna flags, and program the synthesizer. Stop lowers BB TX gain and disables the RF enable register.

## State and Persistence Behavior

The implementation uses EEPROM-derived `priv->channels[].hw_value` and `priv->rfparam` from `dev.c`. Runtime state is only hardware RF/BB register programming.

## Dependencies and Integration Points

It depends on `rtl8180_write_phy()`, MMIO write helpers, `struct rtl8180_priv`, and mac80211 frequency conversion. `dev.c` selects `max2820_rf_ops` for EEPROM RF type 4.

## Risks and Edge Cases

The `conf == NULL` path defaults channel setup to channel 1 during init. RSSI conversion depends on odd/even AGC encoding and approximate scaling. The PA bias is driven through BB rather than the RF chip, so TX power changes need over-the-air validation.

## Test Signals

Probe RF type 4 hardware, verify channel changes across 1-14, compare TX power behavior with EEPROM values, check RSSI monotonicity, and confirm stop/init cycles re-enable receive and transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/max2820.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/max2820.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/max2820.h

## Purpose

`max2820.h` declares the MAX2820 RF frontend contract for the RTL8180 PCI driver.

## Important APIs, Types, and Functions

It defines `MAXIM_ANTENNA` and declares `extern const struct rtl818x_rf_ops max2820_rf_ops`.

## Control Flow

`dev.c` links to `max2820_rf_ops` when EEPROM RF type 4 is detected; `max2820.c` uses `MAXIM_ANTENNA` during PHY antenna writes.

## State and Persistence Behavior

The file has no state. Its constant contributes to volatile baseband antenna configuration.

## Dependencies and Integration Points

It relies on `struct rtl818x_rf_ops` being visible to including C files and is part of the `rtl818x_pci` object list.

## Risks and Edge Cases

The antenna constant is hardware-specific; incorrect changes can silently degrade RX/TX path selection.

## Test Signals

Compile/link `rtl818x_pci` and verify RF type 4 devices initialize with `max2820_rf_ops`; runtime checks should cover antenna defaults and channel 14 attenuation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/max2820.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8180.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8180.h

## Purpose

`rtl8180.h` defines the private ABI for the RTL8180/8185/8187SE PCI driver: descriptor layouts, queue constants, RF/analog parameter flags, private driver state, per-vif state, exported hardware helpers, and MMIO access wrappers.

## Important APIs, Types, and Functions

Important types are `struct rtl8180_tx_desc`, `struct rtl818x_rx_cmd_desc`, `struct rtl8180_rx_desc`, `struct rtl8187se_rx_desc`, `struct rtl8180_tx_ring`, `struct rtl8180_vif`, and `struct rtl8180_priv`. Exported functions are `rtl8180_write_phy()`, `rtl8180_set_anaparam()`, and `rtl8180_set_anaparam2()`. Inline accessors wrap `ioread*`/`iowrite*` for future PIO/MMIO abstraction.

## Control Flow

`dev.c` allocates and mutates `rtl8180_priv` over probe/start/interrupt/config/stop/remove. TX/RX rings use the descriptor layouts here, with RTL8187SE selecting a larger RX descriptor. RF frontends call exported PHY/analog helpers and read EEPROM-derived fields from `rtl8180_priv`.

## State and Persistence Behavior

The private struct stores runtime MMIO mapping, RF ops, active vif, spinlock, RX/TX DMA rings, skb arrays, channel/rate/band copies, queue parameters, PCI device, RX filter mask, timing state, chip family, EEPROM-derived analog/RF/calibration/antenna data, MAC address, and sequence number. Persistent values originate from EEPROM but are cached here after probe.

## Dependencies and Integration Points

The header includes shared `rtl818x.h`, mac80211 types via including C files, Linux DMA/skb types, and RF ops consumers. It is the central integration point among `dev.c`, `rtl8225.c`, `max2820.c`, `grf5101.c`, `sa2400.c`, and `rtl8225se.c`.

## Risks and Edge Cases

Descriptor packing and endian annotations must match hardware exactly. The skb control buffer stores DMA addresses in `rx_buf`, so users must avoid conflicting `skb->cb` usage before RX completion. `RTL818X_NR_TX_QUEUES` is sized to the maximum family and code must respect `dev->queues + 1` for beacon rings.

## Test Signals

Build with sparse/endian checks, exercise RTL8180/8185/8187SE RX descriptor paths, TX descriptor DMA wraparound, RF frontend calls to exported helpers, and queue allocation/free for both two-queue and five-queue configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8180.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225.c

## Purpose

`rtl8225.c` implements Realtek RTL8225 and RTL8225Z2 RF frontend support for RTL8180/8185 PCI devices. It provides RF register bit-banging, RF detection, long initialization tables, transmit-power programming, channel changes, and power-down handling.

## Important APIs, Types, and Functions

The exported selector is `rtl8180_detect_rf()`, which returns either `rtl8225_ops` or `rtl8225z2_ops`. Internal operations include `rtl8225_write()`, `rtl8225_read()`, `rtl8225_rf_set_tx_power()`, `rtl8225_rf_init()`, `rtl8225z2_rf_set_tx_power()`, `rtl8225z2_rf_init()`, `rtl8225_rf_stop()`, and `rtl8225_rf_set_channel()`. Large static tables encode RX gain, AGC, OFDM/CCK gains, thresholds, CCK power tables, and channel synthesizer values.

## Control Flow

Detection primes RF pins, writes RF register 0, reads registers 8 and 9, and chooses Z2 when they match expected values. Init powers analog state, configures RF pins/timing, writes RF register sequences, fills RX gain and AGC tables, writes OFDM/CCK PHY tables, sets initial TX power and antenna defaults, and leaves RF pins enabled. Channel changes select old or Z2 TX power routine based on the init function, then write channel register 7. Stop writes a low-power RF value and disables analog parameters.

## State and Persistence Behavior

The code uses `priv->channels[channel - 1].hw_value` for CCK/OFDM TX power and analog constants from `rtl8225.h`. It writes only volatile RF, PHY, and analog registers; persistent calibration remains in EEPROM parsed by `dev.c`.

## Dependencies and Integration Points

It depends on `rtl8180.h`, `rtl8225.h`, PCI delay helpers, mac80211 channel conversion, and exported analog/PHY helpers. `dev.c` invokes detection for EEPROM RF type 9 on non-RTL8187SE chips.

## Risks and Edge Cases

Initialization contains many magic vendor-derived register writes and sleeps, so ordering and delays are fragile. TX power tables special-case channel 14 and specific CCK power values. RF read/write bit-banging temporarily changes RF pin select/enable registers and must restore them correctly. Detection fallback treats non-Z2-like reads as older RTL8225, which can hide read failures.

## Test Signals

Probe RF type 9 RTL8180/8185 hardware, verify detection result, scan/associate on channels 1-14, compare CCK/OFDM TX power, validate stop/start power cycling, and watch for RF pin or calibration failures after repeated channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225.h

## Purpose

`rtl8225.h` declares RTL8225 analog constants, RF detection, and PHY write wrappers for the RTL8180 driver.

## Important APIs, Types, and Functions

It defines analog on/off constants (`RTL8225_ANAPARAM_*`) and declares `rtl8180_detect_rf()`. Inline helpers `rtl8225_write_phy_ofdm()` and `rtl8225_write_phy_cck()` call `rtl8180_write_phy()`, with CCK writes setting bit `0x10000`.

## Control Flow

`dev.c` calls `rtl8180_detect_rf()` for RF type 9. `rtl8225.c` and RTL8187SE code use the inline PHY helpers to route OFDM/CCK table writes through the shared baseband write primitive.

## State and Persistence Behavior

No state is stored in the header. Constants determine volatile analog power programming during init/stop.

## Dependencies and Integration Points

The header depends on `struct ieee80211_hw`, `struct rtl818x_rf_ops`, and `rtl8180_write_phy()` declarations from including contexts.

## Risks and Edge Cases

The CCK helper's `0x10000` bit is an implicit bank/control selector; changing it would redirect PHY writes. Analog constants affect RF power sequencing and must remain paired with `rtl8225_rf_stop()`/init flows.

## Test Signals

Compile/link users of `rtl8225_write_phy_*`, probe RF type 9 cards, verify RTL8225/RTL8225Z2 detection, and confirm analog power-down/up across interface stop/start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225.h -->
