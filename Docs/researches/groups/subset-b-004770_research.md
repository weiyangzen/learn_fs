# Research: subset-b-004770

Grouped source research for the ath9k EEPROM, GPIO, USB HIF, and HTC support subset. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.h

Purpose: Declares the optional dynamic ACK timeout data structures and entry points used by ath9k when `CONFIG_ATH9K_DYNACK` is enabled. The feature samples transmit and ACK timestamps to adapt ACK timeout values for long-distance links.

Important APIs and types: `ATH_DYN_BUF` fixes the TX and ACK timestamp ring depth at 64 entries. `struct ath_dyn_rxbuf` stores ACK receive timestamps; `struct ath_dyn_txbuf` stores TX timestamp/duration records plus destination/source address pairs; `struct ath_dynack` is the per-hardware state block containing enable state, current timeout, node list, spinlock, and both rings. Public hooks are `ath_dynack_init()`, `ath_dynack_reset()`, node init/deinit, `ath_dynack_sample_ack_ts()`, and `ath_dynack_sample_tx_ts()`. When the config option is disabled, most hooks compile to no-op inline stubs.

Control flow: TX completion and ACK receive paths call the sampling hooks, while node lifecycle calls maintain the dynamic ACK peer list. The implementation is elsewhere, but this header makes the call sites compile regardless of feature configuration.

State and persistence: State is runtime-only under `struct ath_hw`. Ring heads/tails and timestamp buffers are protected by `qlock`; peer state is tracked through a linked list of `ath_node` entries. There is no durable persistence.

Dependencies and integration points: Depends on ath9k hardware/node types, socket buffers, TX status, mac80211 station pointers, list heads, and spinlocks. It integrates with TX status handling, RX ACK observation, and hardware ACK timeout programming.

Risks: Ring depth and timestamp wrap handling are central to correctness. Compile-time stubs mean callers must not rely on side effects when dynamic ACK is disabled. Lock ordering around timestamp queues and node teardown must avoid use-after-free during station removal.

Test signals: Build with and without `CONFIG_ATH9K_DYNACK`, associate/disassociate stations while traffic is active, run long-distance traffic that triggers timeout adaptation, and verify no timestamp queue races under concurrent TX/RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.c

Purpose: Provides shared EEPROM/NVRAM helpers for ath9k calibration data loading, byte swapping, checksum/version validation, interpolation, target-power lookup, regulatory edge limiting, PDADC table generation, and EEPROM ops selection.

Important APIs and functions: `ath9k_hw_nvram_read()` abstracts reads from nvmem, firmware blob, or bus EEPROM. `ath9k_hw_nvram_swap_data()`, `ath9k_hw_nvram_validate_checksum()`, and `ath9k_hw_nvram_check_version()` validate persistent calibration contents. `ath9k_hw_get_legacy_target_powers()`, `ath9k_hw_get_target_powers()`, `ath9k_hw_get_max_edge_power()`, `ath9k_hw_get_scaled_power()`, and `ath9k_hw_get_gain_boundaries_pdadcs()` are consumed by all layout-specific EEPROM implementations. `ath9k_hw_eeprom_init()` selects `eep_ar9300_ops`, `eep_ar9287_ops`, `eep_4k_ops`, or `eep_def_ops`.

Control flow: Probe code calls `ath9k_hw_eeprom_init()`, which chooses an ops table by silicon revision, fills `ah->eeprom`, then delegates validation. Later channel setup calls shared interpolation helpers to convert calibration piers and target power records into per-channel values and PDADC curves. NVRAM read errors are logged through ath common debug/error paths.

State and persistence: The persistent input is EEPROM, flash/nvmem, or firmware-provided calibration data. Runtime state is stored in `ah->eeprom`, `ah->eep_ops`, regulatory max power, and `ah->initPDADC` for open-loop paths. The code modifies only in-memory swapped copies, not the backing NVRAM.

Dependencies and integration points: Depends on `hw.h`, bus ops, firmware/nvmem blobs, endian helpers, channel-center helpers, silicon revision macros, regulatory state, and layout structs from `eeprom.h`. It is a central dependency for `eeprom_def.c`, `eeprom_4k.c`, `eeprom_9287.c`, and AR9300 EEPROM code.

Risks: EEPROM endianness detection and `AH_NO_EEP_SWAP` handling can corrupt all following calibration if wrong. `ath9k_hw_get_gain_boundaries_pdadcs()` uses static temporary VPD tables, so callers rely on serialized hardware configuration. Boundary and interpolation math is sensitive to unused pier markers, chain counts, and half-dB units.

Test signals: Exercise nvmem, firmware-blob, USB register, and bus EEPROM reads; invalid magic and checksum failures; big-endian EEPROM data; 2 GHz and 5 GHz HT20/HT40 target interpolation; regulatory edge limits; and PDADC output for AR9285/AR9271, AR9287, and default layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.h

Purpose: Defines the ath9k EEPROM ABI: magic values, regulatory/control constants, per-layout packed calibration structures, common helper prototypes, and the `struct eeprom_ops` dispatch table used by hardware setup code.

Important APIs and types: Key persistent structures include `base_eep_header`, `modal_eep_header`, `ar5416_eeprom_def`, `ar5416_eeprom_4k`, and `ar9287_eeprom`. Calibration helpers include `cal_data_per_freq`, `cal_target_power_leg`, `cal_target_power_ht`, and CTL edge tables. `enum eeprom_param` provides a common query surface for MAC address words, regulatory domains, masks, gain types, open-loop control, temperature slopes, power table offsets, and antenna gain. `struct eeprom_ops` defines layout callbacks for fill, check, dump, board programming, optional ADDAC programming, TX power programming, spur lookup, and EEPROM misc access.

Control flow: Silicon-specific code fills the union inside `struct ath_hw`, validates it, and exposes values through `get_eeprom()`. Hardware reset/channel changes call `set_board_values()`, `set_addac()`, and `set_txpower()` through the ops table. Static inline `ath9k_hw_fbin2freq()` and `ar5416_get_ntxchains()` are used by shared calibration math.

State and persistence: The packed structs mirror persistent EEPROM/flash/firmware contents and must stay byte-layout compatible with device calibration images. Runtime callbacks interpret that data but do not persist changes back to NVRAM.

Dependencies and integration points: Includes shared ath definitions, cfg80211 regulatory types, and AR9003 EEPROM definitions. It is included by hardware setup, debugfs EEPROM dump code, USB HTC EEPROM helpers, and all EEPROM implementation files.

Risks: Layout drift, endian annotation mistakes, or bitfield-order changes would break calibration parsing. The duplicate `extern const struct eeprom_ops eep_ar9287_ops;` declaration is harmless for C but signals header hygiene risk. Many constants are hardware ABI values, so off-by-one array counts can become register programming errors.

Test signals: Compile all supported endian/config combinations, validate struct sizes against expected EEPROM lengths, dump base/modal EEPROM through debugfs, boot devices for each ops table, and verify regulatory domain, MAC address, chain masks, spur channels, and TX power limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_4k.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_4k.c

Purpose: Implements EEPROM operations for 4K single-chain 2 GHz AR9285/AR9271-style devices, including EEPROM loading, validation, debug dumping, board register programming, PDADC table setup, and per-rate TX power programming.

Important APIs and functions: The exported ops table is `eep_4k_ops`. Internal callbacks include `ath9k_hw_4k_fill_eeprom()`, `ath9k_hw_4k_check_eeprom()`, `ath9k_hw_4k_get_eeprom()`, `ath9k_hw_4k_set_board_values()`, `ath9k_hw_4k_set_txpower()`, and `ath9k_hw_4k_get_spur_channel()`. Important helpers are `ath9k_hw_set_4k_power_cal_table()`, `ath9k_hw_set_4k_power_per_rate_table()`, and `ath9k_hw_4k_set_gain()`.

Control flow: Fill reads the 4K layout from offset 64, using USB register reads on USB devices. Check swaps fields if needed, validates checksum and major/minor version, and converts endian-sensitive modal fields. Board programming writes antenna switch, IQ correction, gain, antenna diversity, RF timing, CCA, PA timing, output/driver bias, and optional baseband desired-scale registers. TX power programming builds target power arrays, applies CTL/regulatory limits, programs PDADC tables, updates `regulatory->max_power_level`, and writes OFDM/CCK/HT rate power registers unless in test mode.

State and persistence: Persistent data lives in `ah->eeprom.map4k`. Runtime state includes PHY registers, `regulatory->max_power_level`, LED/antenna diversity related PHY state, and optional TPC register state. EEPROM content is only read and endian-normalized in memory.

Dependencies and integration points: Depends on common EEPROM helpers, AR9002 PHY register macros, silicon revision checks for AR9271 and AR9285 behavior, USB bus detection, mac80211 channel flags, and regulatory CTL values. Selected by `ath9k_hw_eeprom_init()` for AR9285/AR9271.

Risks: This layout supports only one chain, but the code still writes mirrored gain fields in places; chain mask assumptions need care. Version-dependent modal bitfields affect output bias and antenna diversity. PDADC arrays are static and register writes are buffered, so reset/channel configuration must be serialized.

Test signals: Probe AR9285 and AR9271 USB/non-USB devices, validate checksum and endian swap paths, test antenna diversity and diversity-combining, compare 2 GHz CCK/OFDM/HT20/HT40 power tables, verify TPC enable/disable paths, and confirm spur and MAC/regdomain debugfs dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_4k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_9287.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_9287.c

Purpose: Implements EEPROM operations for AR9287 two-chain 2 GHz devices, with support for normal closed-loop PDADC programming and open-loop power control calibration.

Important APIs and functions: The exported ops table is `eep_ar9287_ops`. Major callbacks are `ath9k_hw_ar9287_fill_eeprom()`, `ath9k_hw_ar9287_check_eeprom()`, `ath9k_hw_ar9287_get_eeprom()`, `ath9k_hw_ar9287_set_board_values()`, and `ath9k_hw_ar9287_set_txpower()`. Helper functions include `ar9287_eeprom_get_tx_gain_index()`, `ar9287_eeprom_olpc_set_pdadcs()`, `ath9k_hw_set_ar9287_power_cal_table()`, and `ath9k_hw_set_ar9287_power_per_rate_table()`.

Control flow: Fill reads from `AR9287_EEP_START_LOC` for regular devices or `AR9287_HTC_EEP_START_LOC` for USB. Check handles byte swapping, checksum, modal field conversion, and version validation. `get_eeprom()` exposes revision-gated temperature slope and open-loop fields. Calibration setup either computes PDADC gain boundaries from calibration piers or programs open-loop reference power registers per chain. TX power setup clamps target powers by CTL edge and scaled chain power, writes OFDM/CCK/HT rate registers, applies HT40 PDADC increment only for closed-loop mode, and enables/disables TPC.

State and persistence: Persistent calibration is `ah->eeprom.map9287`. Runtime state includes `ah->initPDADC` for open-loop mode, PHY analog/BB registers, PDADC tables, and regulatory max power. No EEPROM writes occur.

Dependencies and integration points: Depends on common EEPROM math, AR9002 PHY fields, USB HTC EEPROM loading, AR9287 revision macros, regulatory CTL tables, and `ath9k_hw_update_regulatory_maxpower()`. It is selected by `ath9k_hw_eeprom_init()` for AR9287 silicon.

Risks: Open-loop and closed-loop paths share data unions but interpret calibration rows differently. Power table offset adjustment shifts PDADC arrays and can underflow if EEPROM values are inconsistent. Chain-specific direct register addresses in OLPC code are less self-documenting than macro-based writes.

Test signals: Validate regular and HTC USB EEPROM offsets, minor version 1/2/3 feature gates, two-chain mask combinations, open-loop power control enabled and disabled, HT20/HT40 rate power programming, temperature slope queries, and board RF bias programming for both chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_9287.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_def.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_def.c

Purpose: Implements the default AR5416/AR9280-family EEPROM operations for dual-band devices with up to three chains, including 2 GHz and 5 GHz modal headers, ADDAC adjustment, PDADC calibration, regulatory TX power limiting, and board register setup.

Important APIs and functions: The exported ops table is `eep_def_ops`. Main callbacks are `ath9k_hw_def_fill_eeprom()`, `ath9k_hw_def_check_eeprom()`, `ath9k_hw_def_get_eeprom()`, `ath9k_hw_def_set_board_values()`, `ath9k_hw_def_set_addac()`, and `ath9k_hw_def_set_txpower()`. Calibration helpers include `ath9k_get_txgain_index()`, `ath9k_olc_get_pdadcs()`, `ath9k_hw_set_def_power_cal_table()`, `ath9k_hw_set_def_power_per_rate_table()`, `ath9k_change_gain_boundary_setting()`, and `ath9k_adjust_pdadc_values()`.

Control flow: Fill reads the default EEPROM image from offset `0x100`, with USB support through register multi-read. Check performs byte-swap conversion, checksum and version validation, AR9280 top2 fixup detection, and a USB AR9280 xpa bias workaround. Board setup chooses 2 GHz or 5 GHz modal data, writes antenna switch/IQ/gain/RF timing/CCA/analog bias registers, handles special chainmask offset mapping, and applies revision-gated DAC and CCK scale fields. TX power setup interpolates target powers for 2 GHz or 5 GHz, clamps by regulatory CTLs and chain scaling, writes PDADC tables, records max power, and programs rate power/TPC registers.

State and persistence: Persistent data is held in `ah->eeprom.def`. Runtime mutations include `ah->need_an_top2_fixup`, `ah->initPDADC`, regulatory max power, ADDAC ini table entries, PHY registers, and TPC state. Backing EEPROM is not modified.

Dependencies and integration points: Depends on common EEPROM helpers, AR9002 PHY registers, AR5416/AR9280 silicon revision macros, regulatory CTL definitions, chain masks, and common debugfs EEPROM dump helpers. It is the fallback ops table for pre-AR9300 devices not handled by 4K or AR9287 layouts.

Risks: This is the broadest layout and contains many revision gates; regressions can be band-, chain-, or silicon-specific. Open-loop control for AR9280 2.0 changes PDADC generation and CCK deltas. Chainmask `5` remapping changes register offsets. EEPROM minor-version gates protect fields that may be uninitialized on older boards.

Test signals: Boot AR5416/AR9160/AR9280 variants, test both 2 GHz and 5 GHz HT20/HT40 channels, chain masks 1/3/5/7, open-loop and closed-loop TX power, ADDAC xpa bias interpolation, endian swap/checksum failures, AR9280 USB workaround, and debugfs base/modal dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_def.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/gpio.c

Purpose: Provides non-HTC ath9k GPIO-adjacent support: LED registration/control, hardware rfkill polling, and optional Bluetooth coexistence timer management for PCI/AHB devices.

Important APIs and functions: LED entry points are `ath_init_leds()` and `ath_deinit_leds()`, backed by `ath_fill_led_pin()` and `ath_led_brightness()`. Rfkill functions are `ath9k_rfkill_poll_state()` and `ath_start_rfkill_poll()`. BT coexistence exports include `ath9k_init_btcoex()`, `ath9k_start_btcoex()`, `ath9k_stop_btcoex()`, `ath9k_btcoex_timer_resume()`, `ath9k_btcoex_timer_pause()`, `ath9k_btcoex_aggr_limit()`, interrupt handling, cleanup, and debug dump helpers.

Control flow: LED init selects a default GPIO by silicon revision, requests it as output, sets active-low/off state, and registers a mac80211 LED class device. Rfkill polling wakes the hardware, reads the configured GPIO polarity, restores power state, and reports to wiphy. BT coexistence initialization selects 2-wire, 3-wire, or MCI hardware setup; period and no-stomp timers alternate Bluetooth and WLAN priority, detect BT priority traffic, update MCI RSSI/profile handling, and program coexistence weights.

State and persistence: Runtime state lives in `ath_softc`, `ath_hw`, and `sc->btcoex`: LED registration/name, GPIO ownership, rfkill GPIO/polarity, timer state, op flags, priority counters, MCI profile counters, and wait times. There is no durable persistence.

Dependencies and integration points: Depends on `ath9k.h`, mac80211 LED and rfkill APIs, kernel timers/jiffies, ath9k power-save wake/restore, ath9k hardware GPIO and BTCOEX helpers, MCI profile code, TX queue mapping, and debug dump macros.

Risks: Timer callbacks access hardware and must coordinate with power state and teardown via synchronous timer deletion. BT priority counters are time-window based and can misclassify scan traffic. LED GPIO defaults vary by chip revision. Rfkill reads require power-save transitions around GPIO access.

Test signals: LED registration/unregistration across module load/unload, LED active-high override, rfkill polarity changes, BTCOEX 2-wire/3-wire/MCI init/start/stop, timer pause/resume during suspend/reset, MCI interrupts, aggregation limit changes under BT priority, and debug dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.c

Purpose: Implements the ath9k_htc USB Host Interface transport: USB device matching, firmware request/download, URB allocation, aggregated TX/RX stream handling, register pipe messaging, suspend/resume, disconnect, and module USB driver registration.

Important APIs and functions: Public module hooks are `ath9k_hif_usb_init()`, `ath9k_hif_usb_exit()`, and `ath9k_hif_usb_dealloc_urbs()`. The `hif_usb` transport callbacks expose `start`, `stop`, `sta_drain`, and `send` to HTC. Key internal paths are `hif_usb_send_tx()`, `__hif_usb_tx()`, TX/mgmt/regout callbacks, `ath9k_hif_usb_rx_stream()`, RX and reg-in callbacks, firmware request/download callbacks, `ath9k_hif_usb_probe()`, disconnect, suspend, and resume.

Control flow: Probe validates endpoint numbers, handles storage-mode eject devices, allocates `hif_device_usb`, and starts async firmware lookup with fallback from development/latest firmware to older 1.3 names. Firmware callback allocates the HTC target, downloads firmware over control messages, allocates URBs, and initializes HTC hardware. TX data SKBs are queued and aggregated into USB stream frames with length/tag headers; management/beacon frames use separate anchored URBs. RX bulk URBs are continuously resubmitted, stream frames are parsed by tag/length/padding, split packets are completed with `remain_skb`, and packets are delivered to HTC. Disconnect waits for firmware completion, deinitializes HTC, optionally reboots the device, and frees state.

State and persistence: Runtime state includes USB anchors, TX free/pending lists, queued SKB counts, flags `HIF_USB_START/READY` and `HIF_USB_TX_STOP/FLUSH`, RX split-packet bookkeeping, firmware name/version index, and HTC handle. Firmware is loaded into device RAM and reloaded after resume; no host-side persistent state is written.

Dependencies and integration points: Depends on Linux USB core, firmware loader, skbuffs, HTC host APIs, WMI callbacks through HTC, debug stat macros, and device IDs for AR9271/AR7010/AR9287 USB devices. It bridges mac80211/HTC traffic to USB endpoints 1-4.

Risks: URB lifetime and anchor cleanup must be exact across stop, disconnect, error callbacks, and suspend. RX stream parsing drops the whole transfer on invalid tags/lengths and has split-packet state protected by `rx_lock`. Firmware fallback is asynchronous, so disconnect waits on `fw_done`. `BUG_ON(!nskb)` assumes queue counts and SKB queue never diverge.

Test signals: Probe supported IDs, storage eject transition, missing firmware fallback sequence, firmware download failure unwind, TX aggregation and management TX completion, RX multi-packet and split-packet transfers, invalid stream tag/length drops, station drain, suspend/resume firmware reload, hot unplug, and soft unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.h

Purpose: Defines the ath9k_htc USB transport constants, firmware names/version bounds, endpoint IDs, URB pool sizing, stream tags, and USB HIF state structures used by `hif_usb.c` and HTC code.

Important APIs and types: Firmware macros define current module firmware paths and legacy filenames. Endpoint constants map WLAN TX/RX and register IN/OUT pipes. `struct tx_buf`, `rx_buf`, `cmd_buf`, `hif_usb_tx`, and `hif_device_usb` describe TX aggregation buffers, RX buffers, command contexts, transport queues/locks, USB anchors, firmware state, RX split-frame bookkeeping, and HTC linkage. Public prototypes are `ath9k_hif_usb_init()`, `ath9k_hif_usb_exit()`, and `ath9k_hif_usb_dealloc_urbs()`.

Control flow: The header has no executable flow, but its constants determine how `hif_usb.c` frames USB stream packets, sizes URB pools, requests firmware, and routes HTC control/data pipes.

State and persistence: Structures hold runtime-only USB device state. Firmware name and blob pointers are transient; the firmware image itself is requested from the system firmware store and downloaded to device RAM.

Dependencies and integration points: Depends on Linux USB, SKB, URB, anchor, completion, and list types through includers. It integrates with HTC target allocation and transport registration.

Risks: Pool-size constants directly bound memory use, queue pressure, and stream parsing assumptions. Endpoint IDs must match device descriptors checked at probe. Firmware version bounds control fallback behavior and supported device boot.

Test signals: Compile USB builds, validate endpoint matching, run with current and legacy firmware names, stress MAX_TX_URB_NUM/MAX_TX_BUF_NUM aggregation, and test RX transfers near `MAX_RX_BUF_SIZE` and `MAX_PKT_NUM_IN_TRANSFER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc.h

Purpose: Central private header for the ath9k_htc USB driver, defining target command payloads, driver state, queue/rate/beacon/BTCOEX/LED/debug structures, feature constants, and cross-file function prototypes.

Important APIs and types: Target-facing wire structs include `tx_frame_hdr`, `tx_mgmt_hdr`, `tx_beacon_header`, target VIF/STA/aggr/rate/rate-mask structs, and target stats structs. Runtime state includes `ath9k_htc_vif`, `ath9k_htc_sta`, `ath9k_htc_rx`, `ath9k_htc_tx`, `ath9k_htc_tx_ctl`, `htc_beacon`, `ath_btcoex`, and the main `ath9k_htc_priv`. `HTC_SKB_CB()` maps mac80211 SKB driver data to HTC TX metadata. The header declares beacon, RX, TX, ANI, power-save, rfkill, LED, probe/disconnect, PM, and debug functions.

Control flow: Most ath9k_htc source files include this header to share the same private state layout. TX paths fill `ath9k_htc_tx_ctl` before `htc_send()`, RX/USB paths update debug counters through macros, beacon paths use `htc_beacon`, and mac80211 callbacks operate on `ath9k_htc_priv`.

State and persistence: State is runtime-only and spans HTC endpoint IDs, firmware version, VIF/STA slots, TX/RX queues, beacon slots, calibration data, power-save counters, work/tasklets, LED state, BTCOEX work, debugfs counters, and channel-switch state. Target command structures are transient host/firmware ABI payloads.

Dependencies and integration points: Includes Linux module/USB/firmware/SKB/netdevice/LED/mac80211 APIs plus ath9k common, HTC host, USB HIF, and WMI headers. It is the integration point between mac80211, the HTC firmware protocol, USB transport, hardware ops, and debugfs/ethtool.

Risks: This high-fanout header makes structure layout and lock ownership changes broad in impact. `HTC_SKB_CB()` relies on mac80211 driver-data size. VIF/STA limits are firmware constraints. Conditional debug/LED/BTCOEX stubs must preserve call-site behavior across configs.

Test signals: Build with combinations of HTC debugfs, LEDs, BTCOEX, and PM; run mac80211 VIF/STA lifecycle, TX/RX queueing, beaconing, power-save transitions, firmware capability update, debug stats, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_beacon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_beacon.c

Purpose: Implements ath9k_htc beacon queue configuration, beacon timer setup for STA/AP/IBSS/mesh modes, SWBA event handling, multi-VIF beacon slot assignment, buffered broadcast/multicast delivery, and channel switch completion checks.

Important APIs and functions: Public functions are `ath9k_htc_beaconq_config()`, `ath9k_htc_beaconep()`, `ath9k_htc_swba()`, `ath9k_htc_assign_bslot()`, `ath9k_htc_remove_bslot()`, `ath9k_htc_set_tsfadjust()`, `ath9k_htc_beacon_config()`, `ath9k_htc_beacon_reconfig()`, and `ath9k_htc_csa_is_finished()`. Internal helpers configure STA/AP/adhoc timers, choose beacon slots from TSF, send buffered CAB frames, and build/transmit beacon SKBs.

Control flow: Beacon configuration validates mode constraints, fills `cur_beacon_conf`, disables firmware interrupts through WMI, programs hardware beacon timers/queues, and re-enables interrupts. On SWBA events, the code handles beacon-pending stuck detection, chooses a slot from TSF modulo interval, sends buffered BC/MC frames from mac80211, then sends the current beacon with HTC beacon metadata prepended. Beacon slot assignment stores VIF pointers under `beacon_lock`; TSF adjustment offsets nonzero slots.

State and persistence: Runtime state includes `priv->cur_beacon_conf`, `priv->beacon.bslot[]`, beacon miss count, per-VIF beacon sequence and TSF adjust, queued TX count, and `priv->csa_vif`. No durable persistence exists.

Dependencies and integration points: Depends on mac80211 beacon APIs, WMI interrupt commands, ath9k common beacon config helpers, HTC TX slot handling, hardware TX queue programming, task/work reset path, and CSA helpers.

Risks: Beacon slot selection assumes a common beacon interval for multi-AP mode. `ath9k_htc_assign_bslot()` assumes a free slot exists. CAB frame padding manipulates SKB headroom and must preserve headers. Repeated beacon-pending events trigger fatal reset after `BSTUCK_THRESHOLD`.

Test signals: STA beacon timer setup, AP/mesh and IBSS beaconing, two beaconing VIFs with TSF adjustment, beacon interval change rejection for multi-AP, CAB delivery and TX slot exhaustion, SWBA stuck reset, CSA countdown finish, and scanning suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_beacon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_debug.c

Purpose: Provides ath9k_htc debugfs files and ethtool statistics for target interrupt/TX/RX stats, host TX/RX SKB counters, TX slot/queue state, debug mask control, spectral debug setup, and EEPROM debug exposure.

Important APIs and functions: Debugfs read handlers include `read_file_tgt_int_stats()`, `read_file_tgt_tx_stats()`, `read_file_tgt_rx_stats()`, `read_file_xmit()`, `read_file_skb_rx()`, `read_file_slot()`, `read_file_queue()`, and `read_file_debug()`, with `write_file_debug()` updating the common debug mask. Exported functions are `ath9k_htc_err_stat_rx()`, `ath9k_htc_get_et_strings()`, `ath9k_htc_get_et_sset_count()`, `ath9k_htc_get_et_stats()`, `ath9k_htc_init_debug()`, and `ath9k_htc_deinit_debug()`.

Control flow: Init creates a driver debugfs directory under the wiphy, initializes spectral debug, creates stats/control files, and registers common RX PHY error and EEPROM dump nodes. Target stats readers wake the device from HTC power save, send WMI stat commands, restore power state, and format big-endian firmware counters. Host stats readers sample local counters and queues, with TX slot reading protected by `tx_lock`. Ethtool callbacks copy static stat names and fill values from debug counters.

State and persistence: Debug counters live in `priv->debug`; debugfs dentries are runtime filesystem state; `common->debug_mask` persists only for the loaded driver instance. There is no durable persistence.

Dependencies and integration points: Depends on debugfs, ethtool stats ABI, WMI commands, HTC power-save helpers, common ath9k debug/stat helpers, spectral debug support, EEPROM dump helpers, and TX/RX stat macros used by USB/TX/RX code.

Risks: WMI target stats reads depend on firmware response behavior while power state is temporarily forced awake. Some queue readers sample lockless SKB queue lengths. Debugfs creation return values are not treated as fatal. Stat ordering must stay aligned between string names and `ath9k_htc_get_et_stats()`.

Test signals: Mount/read each debugfs node, write debug mask, collect ethtool stats and verify string/value count, query target stats during active traffic and power save, inspect TX slot bitmap under load, and deinit debugfs on disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_gpio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_gpio.c

Purpose: Implements HTC-specific GPIO-adjacent support: 3-wire Bluetooth coexistence work scheduling, HTC LED registration/control, and hardware rfkill polling for USB ath9k_htc devices.

Important APIs and functions: BTCOEX entry points are `ath9k_htc_init_btcoex()`, `ath9k_htc_start_btcoex()`, and `ath9k_htc_stop_btcoex()`, backed by `ath_detect_bt_priority()`, `ath_btcoex_period_work()`, and `ath_btcoex_duty_cycle_work()`. LED entry points are `ath9k_init_leds()`, `ath9k_configure_leds()`, `ath9k_deinit_leds()`, and `ath9k_led_work()`. Rfkill functions are `ath9k_htc_rfkill_poll_state()` and `ath9k_start_rfkill_poll()`.

Control flow: BTCOEX init checks global enablement and the USB product string prefix `wb193`, configures fixed GPIOs for BT active/priority/WLAN active, initializes 3-wire hardware, and schedules delayed work. Period work detects BT priority/scan windows, updates target coex capability over HTC, sets stomp mode, enables hardware coex, and schedules a duty-cycle work item. LED init selects a chip-specific GPIO pin, requests it as output, registers a LED class device, and routes brightness changes through mac80211 work to avoid direct GPIO writes in the brightness callback. Rfkill polling wakes HTC power state, reads GPIO polarity, restores power, and updates wiphy state.

State and persistence: Runtime state includes `priv->btcoex` counters/timing, `priv->op_flags`, delayed work items, LED brightness/name/registration, `ah->led_pin`, and rfkill GPIO/polarity. No durable persistence exists.

Dependencies and integration points: Depends on HTC power-save helpers, `ath9k_htc_update_cap_target()`, ath9k hardware BTCOEX/GPIO functions, mac80211 delayed work and LED APIs, wiphy rfkill polling, product strings from USB probe, and common BT threshold constants.

Risks: BTCOEX support is limited to recognized product strings and 3-wire mode. Work cancellation must be synchronous before disabling hardware. LED brightness is intentionally lightly synchronized and delayed through work. Rfkill GPIO reads require correct power-save wake/restore around USB-backed hardware access.

Test signals: HTC device with and without `wb193` product string, BT scan/priority GPIO pulses, start/stop BTCOEX around interface up/down, LED registration and brightness changes for AR9287/AR9271/AR7010, rfkill polling with both polarities, suspend/disconnect while delayed work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_gpio.c -->
