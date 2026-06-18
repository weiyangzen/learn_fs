# subset-b-004793 Research

Grouped source-tree-aligned research for Broadcom b43legacy PHY/radio/PIO/TX support and brcm80211/brcmfmac SDIO, BCDC, BT coexistence, ACPI, and BCA vendor glue.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.c

## Purpose
Implements b43legacy baseband PHY initialization, calibration, antenna diversity, local-oscillator measurement, and closed-loop transmit-power control for legacy Broadcom B/G PHYs. It programs many revision-specific PHY, radio, shared-memory, and ILT values, with code paths split by PHY type, PHY revision, analog revision, radio version/revision, board flags, and SPROM power calibration fields.

## Important APIs, Types, and Functions
Public entry points include `b43legacy_phy_lock()`, `b43legacy_phy_unlock()`, `b43legacy_phy_read()`, `b43legacy_phy_write()`, `b43legacy_phy_calibrate()`, `b43legacy_phy_init_tssi2dbm_table()`, `b43legacy_phy_init()`, `b43legacy_phy_set_antenna_diversity()`, `b43legacy_phy_lo_b_measure()`, `b43legacy_phy_lo_g_measure()`, `b43legacy_phy_lo_adjust()`, `b43legacy_phy_lo_mark_all_unused()`, `b43legacy_phy_xmitpower()`, `b43legacy_phy_set_baseband_attenuation()`, and `b43legacy_power_saving_ctl_bits()`. Internal helpers cover B-PHY init revisions 2/4/5/6, G-PHY setup and AGC tables, loopback gain calculation, TSSI-to-dBm table generation, LO pair search, and power-control initialization.

## Control Flow, State, and Persistence
Initialization dispatches on `dev->phy.type` and `dev->phy.rev`, then runs large register scripts and radio setup. Calibration for G rev 1 temporarily resets the wireless core. LO measurement saves register stacks, forces known channel/gain states, searches low/high LO pairs, writes selected pairs into `phy->_lo_pairs`, and restores hardware state. Transmit-power recalculation reads recent TSSI samples from shared memory, converts them through `phy->tssi2dbm`, clamps to SPROM/regulatory limits, updates `phy->bbatt`, `phy->rfatt`, and `phy->txctl1`, then applies radio/PHY attenuation under PHY and radio locks. Persistent driver state is in `struct b43legacy_phy`: calibration flags, channel, attenuation, power table pointer, LO pairs, NRSSI values, saved power-control register, antenna diversity, and debug/manual-power flags. Dynamically generated TSSI tables allocate memory and set `dyn_tssi_tbl`.

## Dependencies and Integration Points
Depends on b43legacy MMIO, SHM, ILT, radio, MAC suspend/resume, core reset, SPROM board data, mac80211 mode information, and debug helpers. `radio.c` calls PHY helpers for attenuation and LO adjustment; `xmit.c` uses PHY RSSI state indirectly through RX reporting; rfkill and sysfs paths can trigger radio and interference changes that rely on this file.

## Risks and Test Signals
Risk is high because this is timing-sensitive undocumented hardware programming. Register-save omissions, wrong revision checks, or bad SPROM interpretation can leave radio gain, LO, antenna diversity, or power control miscalibrated. Test signals include successful association on B/G devices, stable RSSI, channel changes, no excessive retries, correct regulatory TX power, suspend/resume with power control intact, sysfs interference changes, and no warnings from LO pair range checks or invalid max-power handling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.h

## Purpose
Defines the public PHY interface and register/table constants for b43legacy. It centralizes antenna and interference mode enums, routed PHY register address macros, OFDM/G-PHY table selectors, version masks, and prototypes for PHY initialization, calibration, LO, power, and antenna operations.

## Important APIs, Types, and Functions
Key enums are `B43legacy_ANTENNA*` and `B43legacy_INTERFMODE_*`. Register helpers include `B43legacy_PHY_BASE()`, `B43legacy_PHY_OFDM()`, `B43legacy_PHY_EXTG()`, and `B43legacy_OFDMTAB()`. Prototypes expose `b43legacy_phy_lock()`, `b43legacy_phy_read()`, `b43legacy_phy_init_tssi2dbm_table()`, `b43legacy_phy_init()`, `b43legacy_set_rx_antenna()`, `b43legacy_phy_set_antenna_diversity()`, `b43legacy_phy_calibrate()`, `b43legacy_phy_connect()`, `b43legacy_phy_lo_*()`, `b43legacy_phy_xmitpower()`, `b43legacy_phy_set_baseband_attenuation()`, and `b43legacy_power_saving_ctl_bits()`.

## Control Flow, State, and Persistence
The header has no executable state. It defines the symbolic contract used by `phy.c`, `radio.c`, `sysfs.c`, and MAC/radio paths to address routed PHY registers and to mutate `struct b43legacy_phy` state owned elsewhere.

## Dependencies and Integration Points
Includes Linux integer types and forward declares `struct b43legacy_wldev`. It is used anywhere b43legacy needs PHY register definitions, OFDM tables, antenna diversity settings, or transmit-power recalculation hooks.

## Risks and Test Signals
Incorrect register constants or enum values break hardware programming globally. Build coverage should catch missing prototypes; runtime test signals are PHY init success, stable RX/TX, antenna selection, interference sysfs behavior, and no mismatched routed register accesses.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.c

## Purpose
Implements the optional programmed-I/O data path for b43legacy cards when DMA is not used. It manages four PIO queues, formats TX headers, writes frames into device PIO FIFOs, handles TX completion cookies, receives PIO frames and hardware TX-status reports, and freezes/thaws queues during TX suspension.

## Important APIs, Types, and Functions
Public functions are `b43legacy_pio_init()`, `b43legacy_pio_free()`, `b43legacy_pio_tx()`, `b43legacy_pio_handle_txstatus()`, `b43legacy_pio_rx()`, `b43legacy_pio_tx_suspend()`, `b43legacy_pio_tx_resume()`, `b43legacy_pio_freeze_txqueues()`, and `b43legacy_pio_thaw_txqueues()`. Internal helpers include `generate_cookie()`, `parse_cookie()`, `pio_tx_write_fragment()`, `pio_tx_packet()`, `tx_tasklet()`, queue setup/destruction, and `pio_rx_error()`.

## Control Flow, State, and Persistence
Initialization allocates one queue per PIO MMIO base, discovers each device FIFO size, applies a safety adjustment, and creates a fixed cache of `B43legacy_PIO_MAXTXPACKETS` packet descriptors. TX enqueues an skb on queue1, schedules a tasklet, checks device FIFO packet/byte capacity, generates a firmware TX header with a cookie, writes data words and odd trailing bytes, and moves descriptors from free to queued to running lists. TX status parses the cookie, decrements device FIFO accounting, maps retry counts back into `ieee80211_tx_info`, reports status to mac80211, and frees the descriptor. RX waits for the ready bit, reads a preamble/RX header, treats PIO4 as TX-status transport, allocates an skb for normal frames, reads payload words, and calls `b43legacy_rx()`. State is volatile queue state: list heads, `nr_txfree`, `tx_devq_used`, `tx_devq_packets`, frozen flags, workarounds, and tasklets.

## Dependencies and Integration Points
Depends on b43legacy MMIO accessors, `xmit.c` TX header/RX/TX-status conversion, mac80211 skb control blocks, IRQ lock serialization through `wl->irq_lock`, Linux tasklets and skbuff allocation. `xmit.c` selects PIO versus DMA for TX-status and suspend/resume.

## Risks and Test Signals
Risks include descriptor leaks, bad cookie decoding, FIFO byte accounting underflow, tasklet races with teardown, odd-length write bugs on old core revisions, and RX error recovery. Test with `pio=1`, high TX load, encrypted frames during resume, packet loss/retry reporting, RX FCS errors, teardown while traffic is queued, and queue freeze/thaw around suspend.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.h

## Purpose
Declares b43legacy PIO register offsets, control bits, queue limits, queue/packet data structures, inline MMIO helpers, and PIO API entry points. It also provides no-op inline stubs when `CONFIG_B43LEGACY_PIO` is disabled.

## Important APIs, Types, and Functions
Defines `struct b43legacy_pio_txpacket` and `struct b43legacy_pioqueue`, plus `pio_txpacket_getindex()`, `b43legacy_pio_read()`, and `b43legacy_pio_write()`. Constants include TX/RX control/data offsets, `B43legacy_PIO_TXCTL_*`, `B43legacy_PIO_RXCTL_*`, `B43legacy_PIO_MAXTXDEVQPACKETS`, `B43legacy_PIO_TXQADJUST`, and `B43legacy_PIO_MAXTXPACKETS`.

## Control Flow, State, and Persistence
The header itself does not execute. It describes runtime queue state that persists while a wireless device is active: MMIO base, device FIFO size/usage, free/queued/running lists, tasklet, and descriptor cache.

## Dependencies and Integration Points
Includes b43legacy core definitions, Linux interrupt/list/skbuff headers, and references `struct b43legacy_txstatus`. It is consumed by PIO implementation and higher-level TX paths that need conditional PIO support.

## Risks and Test Signals
Compile-time risks are mismatched stubs when PIO is disabled and structure drift from `pio.c`. Runtime risks follow from queue constants and register bit definitions. Test build permutations with and without `CONFIG_B43LEGACY_PIO`, plus PIO TX/RX traffic if enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.c

## Purpose
Implements b43legacy radio register access, channel programming, radio calibration, NRSSI calibration, adjacent-channel interference mitigation, TX antenna/power setup, and radio on/off sequencing. It is the companion to `phy.c` for RF-side behavior on legacy B/G devices.

## Important APIs, Types, and Functions
Important public functions include `b43legacy_radio_lock()`, `b43legacy_radio_unlock()`, `b43legacy_radio_read16()`, `b43legacy_radio_write16()`, `b43legacy_radio_aci_detect()`, `b43legacy_radio_aci_scan()`, `b43legacy_nrssi_*()`, `b43legacy_calc_nrssi_slope()`, `b43legacy_calc_nrssi_threshold()`, `b43legacy_radio_set_interference_mitigation()`, `b43legacy_radio_calibrationvalue()`, `b43legacy_radio_init2050()`, `b43legacy_radio_selectchannel()`, `b43legacy_radio_set_txantenna()`, `b43legacy_radio_set_txpower_a()`, `b43legacy_radio_set_txpower_bg()`, `b43legacy_default_*()`, `b43legacy_radio_turn_on()`, `b43legacy_radio_turn_off()`, and `b43legacy_radio_clear_tssi()`.

## Control Flow, State, and Persistence
Radio access maps logical offsets differently for 2050/2053 radios and B/G PHYs, then uses MMIO radio-control/data registers. Channel selection optionally runs the synthetic power-up workaround, writes frequency codes, updates Japan channel-14 flags, stores `phy->channel`, and waits for settling. Calibration paths save large PHY/radio/ILT stacks, force known gains, sample measurement registers, derive NRSSI slope/threshold and calibration values, then restore state. Interference mitigation uses explicit enable/disable scripts with stack save/restore and updates `phy->interfmode`, `aci_enable`, `aci_hw_rssi`, and `aci_wlan_automatic`. Radio power-off stores RF override context for later restore unless forced; power-on restores context and retunes the channel. TX power setters update attenuation fields and shared-memory radio attenuation, and may trigger LO adjustment.

## Dependencies and Integration Points
Depends on PHY accessors, ILT helpers, b43legacy MMIO/SHM, SPROM board flags/country code, sleep/delay APIs, and `struct b43legacy_phy` state. It is called from PHY initialization/power control, rfkill polling, sysfs interference control, channel change code, and transmit-power recalculation.

## Risks and Test Signals
High-risk areas are register stack balance, revision-specific radio offset mapping, channel-14 country handling, interference mitigation restore paths, and radio-off context preservation across rfkill/suspend. Test channel changes across 1-14, rfkill toggles, ACI mitigation sysfs modes, TX power changes, RSSI calibration, resume, and no stuck `RADIOLOCK` or corrupted attenuation/LO settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.h

## Purpose
Declares b43legacy radio defaults, TX antenna constants, radio interference mode constants, and public RF/NRSSI/channel/power APIs.

## Important APIs, Types, and Functions
Defines `B43legacy_RADIO_DEFAULT_CHANNEL_BG`, `B43legacy_RADIO_TXANTENNA_*`, and `B43legacy_RADIO_INTERFMODE_*`. Exposes radio locking, 16-bit radio access, radio 2050 init, on/off, channel selection, TX-power setters/defaults, TX antenna selection, TSSI clearing, ACI scan/detect, interference mitigation, NRSSI helpers, and `b43legacy_radio_calibrationvalue()`.

## Control Flow, State, and Persistence
The header has no state. Runtime state is in `struct b43legacy_phy`, including current channel, radio-on flag, attenuation values, NRSSI tables, interference mode, and radio-off context.

## Dependencies and Integration Points
Includes `b43legacy.h` and is used by `phy.c`, `radio.c`, `rfkill.c`, `sysfs.c`, and TX-power/channel paths.

## Risks and Test Signals
Incorrect constants or prototypes affect all RF programming. Test by building b43legacy and exercising channel change, rfkill, interference mitigation, NRSSI calibration, and TX power paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.c

## Purpose
Implements hardware radio-enable detection and mac80211 rfkill polling for b43legacy. It reads the card-specific hardware switch state, updates cfg80211/mac80211 rfkill state, and turns the radio on or off to match the switch.

## Important APIs, Types, and Functions
`b43legacy_is_hw_radio_enabled()` reads high or low hardware-enable registers depending on core revision and handles early resume/not-started cases. `b43legacy_rfkill_poll()` powers up the SSB device temporarily if needed, reads the switch, updates `dev->radio_hw_enable`, calls `wiphy_rfkill_set_hw_state()`, and invokes `b43legacy_radio_turn_on()` or `b43legacy_radio_turn_off()`.

## Control Flow, State, and Persistence
Polling runs under `wl->mutex`. If the device is not initialized, it uses `ssb_bus_powerup()` and `ssb_device_enable()` for a temporary register read, then disables/powers down again. Persistent state is `dev->radio_hw_enable` and `dev->phy.radio_on`; rfkill state is held in the wiphy.

## Dependencies and Integration Points
Depends on SSB bus power management, b43legacy status checks, MMIO hardware-enable registers, radio on/off routines, and cfg80211 rfkill state. It is called through mac80211 rfkill polling.

## Risks and Test Signals
Risks include reading unavailable registers during early resume, leaving SSB powered, wrong active-low semantics between revision families, or desynchronizing rfkill and actual radio power. Test hardware switch toggles before start, while associated, during suspend/resume, and on both pre-rev3 and newer cores.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.h

## Purpose
Declares the b43legacy rfkill polling and hardware-radio-state helpers.

## Important APIs, Types, and Functions
Forward declares `struct ieee80211_hw` and `struct b43legacy_wldev`, and exposes `b43legacy_rfkill_poll()` plus `b43legacy_is_hw_radio_enabled()`.

## Control Flow, State, and Persistence
No executable state. Runtime rfkill state is maintained by `rfkill.c`, wiphy rfkill, and `struct b43legacy_wldev`.

## Dependencies and Integration Points
Consumed by b43legacy main/mac80211 registration paths that provide the rfkill poll callback and by code that needs a hardware radio switch query.

## Risks and Test Signals
Risks are limited to prototype drift. Build coverage and rfkill polling tests validate this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.c

## Purpose
Provides legacy b43 sysfs attributes for privileged runtime tuning of interference mitigation and short preamble mode.

## Important APIs, Types, and Functions
Helpers `get_integer()` and `get_boolean()` parse sysfs input. Attribute handlers implement `interference` show/store and `shortpreamble` show/store. `b43legacy_sysfs_register()` creates `interference` and `shortpreamble`; `b43legacy_sysfs_unregister()` removes them.

## Control Flow, State, and Persistence
All show/store operations require `CAP_NET_ADMIN`. Interference writes parse modes 0-3, lock `wl->mutex` and `wl->irq_lock`, call `b43legacy_radio_set_interference_mitigation()`, and store the resulting mode in PHY state via radio code. Short-preamble writes parse common boolean strings and update `wldev->short_preamble` under the same locks. State lasts for the active device instance and is not persisted to disk.

## Dependencies and Integration Points
Depends on Linux device sysfs, capability checks, b43legacy device conversion helpers, radio interference mitigation, and PHY constants. It is registered after the device reaches `B43legacy_STAT_INITIALIZED`.

## Risks and Test Signals
Risks include accepting malformed input, changing radio registers while interrupts race, exposing knobs without permission, and failing cleanup if the second file creation fails. Test with root/non-root reads and writes, all interference modes, invalid values, module removal, and radio behavior after manual WLAN/non-WLAN mitigation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.h

## Purpose
Declares sysfs registration helpers for b43legacy wireless devices.

## Important APIs, Types, and Functions
Forward declares `struct b43legacy_wldev` and exposes `b43legacy_sysfs_register()` and `b43legacy_sysfs_unregister()`.

## Control Flow, State, and Persistence
No state in the header. Attribute lifetime is controlled by `sysfs.c` and the device lifecycle.

## Dependencies and Integration Points
Included by b43legacy setup/teardown code and by `sysfs.c`.

## Risks and Test Signals
Risks are prototype drift and lifecycle mismatch. Build and module load/unload with sysfs attribute presence/absence are sufficient signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.c

## Purpose
Implements b43legacy TX header generation, PLCP rate encoding, RX frame conversion to mac80211 status, hardware TX-status decoding, and generic TX suspend/resume dispatch between PIO and DMA.

## Important APIs, Types, and Functions
Public functions are `b43legacy_plcp_get_ratecode_cck()`, `b43legacy_plcp_get_ratecode_ofdm()`, `b43legacy_generate_plcp_hdr()`, `b43legacy_generate_txhdr()`, `b43legacy_rx()`, `b43legacy_handle_txstatus()`, `b43legacy_handle_hwtxstatus()`, `b43legacy_tx_suspend()`, `b43legacy_tx_resume()`, and `b43legacy_qos_init()`. Internal helpers extract bitrate indexes, calculate fallback rates, generate firmware v3 TX headers, and postprocess RSSI.

## Control Flow, State, and Persistence
TX header generation chooses the mac80211 primary and fallback rates, copies frame-control and receiver fields, calculates fallback duration, embeds encryption IV/key metadata only if the key is still enabled, builds data and RTS/CTS PLCP headers, sets MAC/PHY control bits, and stores a caller-provided cookie. It may return `-ENOKEY` to prevent plaintext leakage during resume races. RX strips PLCP and optional padding, validates minimum lengths, accounts FCS errors, removes IV/ICV for hardware-decrypted frames, computes signal/rate/antenna/timestamp/channel fields, stores `ieee80211_rx_status`, and reports the skb through `ieee80211_rx_irqsafe()`. TX status ignores intermediate/AMPDU status, updates IEEE counters, then dispatches to PIO or DMA status handling.

## Dependencies and Integration Points
Depends on mac80211 rate, duration, RTS/CTS, TX/RX status, and skb APIs; b43legacy security key indexing; DMA/PIO backends; PHY RSSI/radio metadata; TSF reading; debugfs TX-status logging.

## Risks and Test Signals
Risks include invalid rate-code BUG paths, wrong retry-count accounting, encryption key races, skb underruns, timestamp wrap assumptions, and mismatched channel frequency reporting. Test encrypted traffic across suspend/resume, RTS/CTS and CTS-to-self, fallback/retry statistics, monitor/beacon timestamps, FCS/decrypt error handling, and both DMA and PIO TX-status paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.h

## Purpose
Defines b43legacy firmware v3 TX/RX descriptor layouts, PLCP header structures, TX/RX status bitfields, QoS constants, and TX/RX helper prototypes.

## Important APIs, Types, and Functions
Key types are `struct b43legacy_plcp_hdr4`, `struct b43legacy_plcp_hdr6`, `struct b43legacy_txhdr_fw3`, `struct b43legacy_txstatus`, `struct b43legacy_hwtxstatus`, and `struct b43legacy_rxhdr_fw3`. The header defines `B43legacy_TX4_MAC_*`, `B43legacy_TX4_PHY_*`, `B43legacy_RX_PHYST*`, `B43legacy_RX_MAC_*`, `B43legacy_RX_CHAN_*`, TX suppression reasons, and inline key-index translators `b43legacy_kidx_to_fw()`/`b43legacy_kidx_to_raw()`.

## Control Flow, State, and Persistence
No executable control except key-index inline helpers. The structs describe packed firmware-facing state carried in device queues and RX/TX status rings; incorrect layout directly changes hardware protocol interpretation.

## Dependencies and Integration Points
Includes `main.h` and is consumed by `xmit.c`, PIO, DMA, and status handling. The key-index helpers depend on firmware revision and driver key-table layout.

## Risks and Test Signals
Packed layout and bitfield risks are high: size/alignment drift breaks firmware communication. Test compile with structure users, TX/RX traffic, encrypted traffic on old and newer firmware key-index APIs, and TX-status decoding.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Kconfig -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Kconfig

## Purpose
Defines top-level Kconfig symbols for the brcm80211 family: common utilities, brcmsmac SoftMAC, brcmfmac FullMAC inclusion, tracing, and debug support.

## Important APIs, Types, and Functions
Symbols are `BRCMUTIL`, `BRCMSMAC`, `BRCMSMAC_LEDS`, `BRCM_TRACING`, and `BRCMDBG`, plus a `source` directive for `brcmfmac/Kconfig`. `BRCMSMAC` selects `BCMA`, `BRCMUTIL`, `FW_LOADER`, and `CORDIC`; `BRCMDBG` selects `WANT_DEV_COREDUMP` for brcmfmac.

## Control Flow, State, and Persistence
Kconfig has no runtime state. It controls which objects compile and which debug/tracing code is reachable.

## Dependencies and Integration Points
Integrates with kernel `MAC80211`, `CFG80211` through child config, `BCMA`, tracing, debug, LED, firmware loader, and device coredump infrastructure.

## Risks and Test Signals
Dependency mistakes lead to impossible build combinations or missing helper libraries. Test `allyesconfig`, modular brcmsmac/brcmfmac builds, tracing/debug toggles, and LED dependency combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Makefile -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Makefile

## Purpose
Routes brcm80211 subdirectory builds and applies common debug compiler flags.

## Important APIs, Types, and Functions
Adds `-DDEBUG` when `CONFIG_BRCMDBG` is enabled and builds `brcmutil/`, `brcmfmac/`, and `brcmsmac/` according to `CONFIG_BRCMUTIL`, `CONFIG_BRCMFMAC`, and `CONFIG_BRCMSMAC`.

## Control Flow, State, and Persistence
No runtime behavior. It controls object inclusion at build time.

## Dependencies and Integration Points
Depends on Kbuild variable expansion and the Kconfig symbols defined in this directory and child directories.

## Risks and Test Signals
Risks are missing subdir objects or inconsistent debug flag propagation. Build all brcm80211 permutations as built-in and modules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Kconfig -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Kconfig

## Purpose
Defines brcmfmac FullMAC driver and bus/protocol feature options.

## Important APIs, Types, and Functions
Symbols are `BRCMFMAC`, protocol internals `BRCMFMAC_PROTO_BCDC` and `BRCMFMAC_PROTO_MSGBUF`, and bus options `BRCMFMAC_SDIO`, `BRCMFMAC_USB`, and `BRCMFMAC_PCIE`. SDIO and USB select BCDC; PCIe selects MSGBUF; all bus options select `FW_LOADER`.

## Control Flow, State, and Persistence
No runtime state. The selected bus options decide which transport code and protocol backend are compiled into `brcmfmac`.

## Dependencies and Integration Points
Depends on `CFG80211`, `MMC`, `USB`, `PCI`, and top-level `BRCMUTIL`. The bus selections align with object lists in the brcmfmac Makefile.

## Risks and Test Signals
Incorrect dependencies can build a transport without the needed subsystem or omit the matching protocol. Test modular and built-in combinations for SDIO, USB, PCIe, and multi-bus builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Makefile -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Makefile

## Purpose
Builds the brcmfmac FullMAC driver from core, protocol, bus, debug, firmware-vendor, OF, DMI, and ACPI objects.

## Important APIs, Types, and Functions
The base `brcmfmac-objs` list includes cfg80211, chip, firmware interface, event handling, P2P, protocol, common, core, firmware, fwvid, feature, BT coexistence, vendor, PNO, and XTLV objects. Conditional lists add BCDC/fwsignal, MSGBUF/rings/flowring, SDIO, USB, PCIe, debug, tracing, OF, DMI, and ACPI. When `BRCMFMAC=m`, vendor folders `wcc/`, `cyw/`, and `bca/` build as modules; otherwise their core objects are linked into brcmfmac.

## Control Flow, State, and Persistence
No runtime state. It determines which vendor ops are linked versus separated into plugin modules and which protocol/bus functions are available.

## Dependencies and Integration Points
Uses `ccflags-y` include paths for brcmfmac and shared include headers. Must match Kconfig protocol and bus selections and module namespace expectations from vendor modules.

## Risks and Test Signals
Risks include missing object dependencies, wrong built-in versus module vendor linking, and include path drift. Test SDIO/USB/PCIe builds, debug/tracing builds, ACPI/OF/DMI combinations, and modular vendor plugin loading.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/acpi.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/acpi.c

## Purpose
Extracts brcmfmac platform identity hints from ACPI, primarily for Apple/Asahi systems that expose module instance and antenna SKU metadata.

## Important APIs, Types, and Functions
`brcmf_acpi_probe()` looks up the ACPI companion, reads the `"module-instance"` string property, assigns `settings->board_type` as `"apple,<module-instance>"`, evaluates `RWCV`, and if it returns a buffer with at least two bytes, stores a two-character `settings->antenna_sku`.

## Control Flow, State, and Persistence
The function returns early without an ACPI companion or without `module-instance`. Allocations use `devm_kasprintf()` and `devm_kzalloc()`, so state persists for device lifetime. The ACPI buffer from `RWCV` is freed after parsing when present.

## Dependencies and Integration Points
Depends on ACPI property/evaluate APIs, brcmfmac `struct brcmf_mp_device`, and debug logging. It is included when `CONFIG_ACPI` selects `acpi.o` in the brcmfmac Makefile and feeds firmware/board file selection through `settings`.

## Risks and Test Signals
Risks include malformed ACPI objects, missing buffer cleanup on unusual paths, and board-type strings that do not match firmware naming. Test ACPI systems with and without `module-instance`, with valid/absent `RWCV`, and firmware board selection for Apple modules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/Makefile -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/Makefile

## Purpose
Builds the brcmfmac BCA firmware-vendor plugin module.

## Important APIs, Types, and Functions
Sets include paths for the plugin, parent brcmfmac directory, and shared include directory. Builds `brcmfmac-bca.o` from `core.o` and `module.o`.

## Control Flow, State, and Persistence
No runtime behavior. It controls module composition for the BCA vendor plugin.

## Dependencies and Integration Points
Used when brcmfmac is built modular and the parent Makefile descends into `bca/`. It must line up with module namespace imports in `module.c` and exported vendor ops from `core.c`.

## Risks and Test Signals
Risks are include path breakage or incomplete module object lists. Test modular brcmfmac builds and loading `brcmfmac-bca.ko`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/core.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/core.c

## Purpose
Provides BCA-specific firmware-vendor operations for brcmfmac Broadcom AP chipsets.

## Important APIs, Types, and Functions
`brcmf_bca_feat_attach()` clears `BRCMF_FEAT_SAE` because SAE support is not confirmed. `brcmf_bca_alloc_fweh_info()` allocates `struct brcmf_fweh_info` with `BRCMF_BCA_E_LAST` event handler slots and stores it in `drvr->fweh`. `brcmf_bca_ops` publishes these callbacks as `struct brcmf_fwvid_ops`.

## Control Flow, State, and Persistence
Feature attach mutates driver feature flags after interface setup. Event allocation creates driver-owned event-handler state sized for BCA firmware event codes and persists in `drvr->fweh` until normal driver cleanup.

## Dependencies and Integration Points
Depends on brcmfmac core, bus, fwvid, feature, and flexible allocation helpers. It is registered by `module.c` for `BRCMF_FWVENDOR_BCA` or linked directly in built-in configurations through the parent Makefile.

## Risks and Test Signals
Risks include disabling SAE unnecessarily, event-code table size mismatch with firmware, and allocation failure paths. Test BCA firmware probe, event delivery near high event codes, feature negotiation, and WPA3/SAE capability exposure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/module.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/module.c

## Purpose
Registers and unregisters the BCA brcmfmac firmware-vendor plugin as a kernel module.

## Important APIs, Types, and Functions
`brcmf_bca_init()` calls `brcmf_fwvid_register_vendor(BRCMF_FWVENDOR_BCA, THIS_MODULE, &brcmf_bca_ops)`. `brcmf_bca_exit()` calls `brcmf_fwvid_unregister_vendor()`. Module metadata declares description, dual BSD/GPL license, and imports the `BRCMFMAC` namespace.

## Control Flow, State, and Persistence
Registration state exists while the module is loaded. The fwvid registry maps BCA firmware vendor IDs to the ops defined in `core.c`.

## Dependencies and Integration Points
Depends on brcmfmac fwvid registry exports and the BCA ops declaration. It is used only for modular vendor-plugin builds.

## Risks and Test Signals
Risks are namespace/import mismatch, duplicate vendor registration, or unregistering while devices still rely on ops. Test module load/unload, autoload by matching firmware vendor, and removal with active/inactive devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/vops.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/vops.h

## Purpose
Declares the BCA vendor-ops object and a convenience macro for brcmfmac vendor integration.

## Important APIs, Types, and Functions
Exposes `extern const struct brcmf_fwvid_ops brcmf_bca_ops;` and defines `BCA_VOPS` as `(&brcmf_bca_ops)`.

## Control Flow, State, and Persistence
No control flow or state. The referenced object is defined in `core.c`.

## Dependencies and Integration Points
Included by BCA core/module files and by built-in vendor linking code that needs a vendor ops pointer.

## Risks and Test Signals
Risks are declaration drift or missing include guards. Build BCA plugin and built-in vendor configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/vops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.c

## Purpose
Implements the brcmfmac BCDC protocol backend used by SDIO and USB FullMAC transports. It formats dongle control commands, wraps data packets in BCDC headers, integrates firmware-signaling flow control, and installs protocol callbacks into `drvr->proto`.

## Important APIs, Types, and Functions
Defines `struct brcmf_proto_bcdc_dcmd`, `struct brcmf_proto_bcdc_header`, and private `struct brcmf_bcdc`. Public functions are `drvr_to_fws()`, `brcmf_proto_bcdc_txflowblock()`, `brcmf_proto_bcdc_txcomplete()`, `brcmf_proto_bcdc_attach()`, and `brcmf_proto_bcdc_detach()`. Callback helpers include query/set dcmd, control-message completion, header push/pull, queued data TX, direct data TX, interface add/delete/reset, RX reorder, init-done, and debugfs creation.

## Control Flow, State, and Persistence
Control requests increment a 16-bit request id, fill the BCDC dcmd header with command, length, set/query flag, and interface index, send via `brcmf_bus_txctl()`, then loop on `brcmf_bus_rxctl()` until the matching id arrives or retries fail. Data TX pushes a 4-byte BCDC header with protocol version, checksum hints, priority, interface index, and firmware-signal offset before bus TX. RX validates length, version, interface mapping, checksum flag, priority, and data offset, optionally lets firmware signaling consume headers, and returns the target `brcmf_if`. Attach allocates `struct brcmf_bcdc`, verifies the control message buffer layout, assigns protocol callbacks, grows `drvr->hdrlen`, and sets bus control max length. Detach tears down firmware signaling and frees state.

## Dependencies and Integration Points
Depends on brcmfmac bus control/data APIs, fwsignal, proto core, tracepoints, debug, cfg interface lookup, skbuff helpers, and firmware iovar/dcmd semantics. It is selected by SDIO/USB Kconfig.

## Risks and Test Signals
Risks include request-id mismatch, stale control responses, header offset underflow/overpull, missing interface lookup, flow-control deadlock, and checksum flag misuse. Test control get/set commands, multi-interface data RX/TX, firmware signaling on/off, bus flow block/unblock, TX completion paths, and malformed short/non-BCDC packets.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.h

## Purpose
Declares the BCDC protocol attach/detach and TX completion/flow-control entry points, with stubs when BCDC is not compiled.

## Important APIs, Types, and Functions
When `CONFIG_BRCMFMAC_PROTO_BCDC` is enabled, exposes `brcmf_proto_bcdc_attach()`, `brcmf_proto_bcdc_detach()`, `brcmf_proto_bcdc_txflowblock()`, `brcmf_proto_bcdc_txcomplete()`, and `drvr_to_fws()`. Disabled builds get no-op attach/detach stubs.

## Control Flow, State, and Persistence
No state in the header. Runtime BCDC protocol state lives in `struct brcmf_bcdc` allocated by `bcdc.c`.

## Dependencies and Integration Points
Used by brcmfmac protocol selection and bus code that calls BCDC TX completion/flow-control callbacks.

## Risks and Test Signals
Risks are missing prototypes in non-BCDC builds and conditional compilation mismatch. Test SDIO/USB BCDC builds and PCIE/MSGBUF-only builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcmsdh.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcmsdh.c

## Purpose
Implements brcmfmac's SDIO host/device interface. It registers the SDIO driver, probes/removes two-function devices, configures block sizes and interrupts, provides function/backplane reads and writes, transfers skbs with optional scatter-gather, supports firmware RAM access, and handles suspend/resume/WOWL/freezer behavior.

## Important APIs, Types, and Functions
Key public routines include `brcmf_sdiod_intr_register()`, `brcmf_sdiod_intr_unregister()`, `brcmf_sdiod_change_state()`, `brcmf_sdiod_readl()`, `brcmf_sdiod_writel()`, `brcmf_sdiod_recv_buf()`, `brcmf_sdiod_recv_pkt()`, `brcmf_sdiod_recv_chain()`, `brcmf_sdiod_send_buf()`, `brcmf_sdiod_send_pkt()`, `brcmf_sdiod_ramrw()`, `brcmf_sdiod_abort()`, `brcmf_sdiod_sgtable_alloc()`, freezer helpers, `brcmf_sdiod_probe()`, `brcmf_sdiod_remove()`, `brcmf_sdio_wowl_config()`, `brcmf_sdio_register()`, and `brcmf_sdio_exit()`. Static SDIO driver callbacks cover probe, remove, suspend, and resume.

## Control Flow, State, and Persistence
Probe ignores function 1 callbacks except to keep the card alive, consumes function 2, allocates `brcmf_bus` and `brcmf_sdio_dev`, records func1/func2, saves ACPI power flags, sets state DOWN, configures F1/F2 block sizes, enables F1, attaches the freezer, calls lower `brcmf_sdio_probe()`, and marks the host non-removable while forbidding runtime PM power-off. Interrupt registration chooses OOB GPIO IRQs or in-band SDIO IRQs, configures CCCR interrupt bits for OOB, and records request flags. Backplane 32-bit access caches the SB window in `sdiodev->sbwad`. Packet transfers use simple CMD53 for single packets or manual MMC scatter-gather requests with fallbacks for broken SG hosts. State includes SDIO functions, bus interface, current SDIOD state, cached backplane window, IRQ request/enabled flags, SG table/capabilities, freezer counters/completion, WOWL state, and saved ACPI power-manageable flags.

## Dependencies and Integration Points
Depends on Linux MMC/SDIO, PM runtime/sleep, ACPI, cfg80211 coredump hook, brcmfmac bus/core/sdio lower layer, chipcommon addressing, firmware vendor ids, skbuff and scatterlist helpers. The SDIO ID table maps Broadcom/Cypress device IDs to WCC/CYW firmware vendor IDs.

## Risks and Test Signals
Risks include host-claim imbalance, OOB IRQ wake misconfiguration, SG segmentation errors, backplane window cache corruption, ENOMEDIUM state transitions, freezer deadlock during suspend, ACPI power flag restoration, and reprobe after power-off resume. Test SDIO probe/remove, OOB and in-band IRQs, glommed RX/TX with and without SG, firmware RAM download/readback, WOWL suspend/resume, power-off suspend/resume reprobe, card removal, and runtime PM interactions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcmsdh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.c -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.c

## Purpose
Implements brcmfmac Bluetooth coexistence handling for DHCP/critical-protocol windows. When SCO/eSCO activity is detected, it temporarily changes firmware `btc_params` to favor Wi-Fi progress during DHCP, then restores saved coexistence parameters.

## Important APIs, Types, and Functions
Defines `enum brcmf_btcoex_state` and private `struct brcmf_btcoex_info`. Public APIs are `brcmf_btcoex_attach()`, `brcmf_btcoex_detach()`, and `brcmf_btcoex_set_mode()`. Internal helpers read/write `btc_params`, detect SCO activity, save/restore two groups of firmware registers, boost Wi-Fi, run a timer callback, and process the state machine in workqueue context.

## Control Flow, State, and Persistence
Attach allocates state, initializes a timer and work item, and stores it in `cfg->btcoex`. `brcmf_btcoex_set_mode(BRCMF_BTCOEX_DISABLED)` treats the critical protocol as starting: if idle and SCO is detected through repeated `btc_params` 27 reads, it saves part1 registers, writes DHCP-friendly values, records the vif/duration, and schedules work. The work handler moves from START to opportunity window, then to forced Wi-Fi boost after T1, then to idle after T2 or early DHCP completion. Boosting saves part2 registers 50/51/64/65/71 once, writes DHCP values, and restores them on idle. End mode marks DHCP done, cancels timers as needed, restores registers, calls `cfg80211_crit_proto_stopped()`, and clears `vif`. Detach shuts down timer/work and restores any saved firmware parameters.

## Dependencies and Integration Points
Depends on brcmfmac firmware iovar access, cfg80211 critical protocol notifications, P2P/cfg80211 structures, workqueues/timers, and firmware `btc_params` semantics. It is initialized from brcmfmac cfg80211 setup and invoked by critical-protocol mode changes.

## Risks and Test Signals
Risks include not restoring firmware coexistence registers, races between timer/work/end/detach, stale `vif` pointers, firmware read/write failures ignored by many paths, and over-boosting when SCO detection is wrong. Test DHCP with active Bluetooth SCO/eSCO, DHCP completion before T1/T2, timeout path, detach during active timer, repeated critical-protocol requests returning `-EBUSY`, and firmware parameter restoration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.h -->

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.h

## Purpose
Declares brcmfmac Bluetooth coexistence modes and attach/detach/control APIs.

## Important APIs, Types, and Functions
Defines `enum brcmf_btcoex_mode` with `BRCMF_BTCOEX_DISABLED` and `BRCMF_BTCOEX_ENABLED`. Exposes `brcmf_btcoex_attach()`, `brcmf_btcoex_detach()`, and `brcmf_btcoex_set_mode()`.

## Control Flow, State, and Persistence
No state in the header. Runtime state is `struct brcmf_btcoex_info` private to `btcoex.c` and referenced through cfg80211 private data.

## Dependencies and Integration Points
Used by brcmfmac cfg80211/P2P code to initialize coexistence and wrap critical protocol windows.

## Risks and Test Signals
Risks are enum semantic mismatch and prototype drift. Test build coverage and runtime DHCP critical-protocol calls with and without Bluetooth activity.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.h -->
