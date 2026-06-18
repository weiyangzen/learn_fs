# Research Report: subset-b-004777

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.c

## Purpose
`smd.c` is the Qualcomm WCN36xx firmware control-plane transport implementation. It builds HAL request messages in `wcn->hal_buf`, sends them over the rpmsg/SMD endpoint, waits for matching firmware responses, and translates mac80211/cfg80211 operations into firmware commands for startup, NV download, scanning, station/BSS setup, keys, power management, BA aggregation, WoWLAN offloads, beacon filtering, and firmware indications.

## Important APIs, Types, and Functions
- `wcn36xx_smd_send_and_wait()` is the central synchronous RPC primitive. It initializes `hal_rsp_compl`, sends `wcn->hal_buf` through `rpmsg_send()`, waits up to `HAL_MSG_TIMEOUT`, and leaves the response copied back into `wcn->hal_buf`.
- `INIT_HAL_MSG*`, `PREPARE_HAL_BUF`, and `PREPARE_HAL_PTT_MSG_BUF` standardize HAL header setup and padding into the shared buffer.
- Startup/configuration APIs include `wcn36xx_smd_load_nv()`, `wcn36xx_smd_start()`, `wcn36xx_smd_stop()`, `wcn36xx_smd_feature_caps_exchange()`, and `wcn36xx_smd_update_cfg()`.
- Connection APIs include `wcn36xx_smd_add_sta_self()`, `wcn36xx_smd_join()`, `wcn36xx_smd_set_link_st()`, `wcn36xx_smd_config_sta()`, `wcn36xx_smd_config_bss()`, and delete variants.
- Runtime APIs cover software/hardware scan, channel list updates, channel switch, beacon/probe-response templates, unicast/group key programming, BMPS/IMPS power states, keepalive, ARP/IPv6 NS/GTK offloads, multicast filter setup, and beacon filter programming.
- `wcn36xx_smd_rsp_process()` is the rpmsg callback. Synchronous responses are copied to `hal_buf` and complete the waiter; asynchronous indications are copied into `struct wcn36xx_hal_ind_msg` and queued to `wcn36xx_ind_smd_work()`.

## Control Flow
Most exported operations lock `wcn->hal_mutex`, initialize a stack or allocated HAL message, fill firmware-specific fields from mac80211 state, copy into `hal_buf`, call `wcn36xx_smd_send_and_wait()`, and validate the firmware response with either `wcn36xx_smd_rsp_status_check()` or a command-specific parser. Firmware version and RF ID decide whether v0 or v1 STA/BSS structures are used, with WCN3680 enabling VHT and extra config values.

The response path is split. Expected command responses arrive through `wcn36xx_smd_rsp_process()`, overwrite the same shared buffer, set `hal_rsp_len`, and complete the blocked sender. Indications such as TX completion, scan offload events, missed beacon, station context deletion, and register info are copied under `hal_ind_lock` to a list and processed later on `hal_ind_wq`, where they call mac80211 notifications such as `ieee80211_scan_completed()`, `ieee80211_beacon_loss()`, `ieee80211_connection_loss()`, and DXE TX ACK handling.

## State and Persistence Behavior
The file mutates long-lived driver state: firmware version strings and API numbers, `fw_feat_caps`, scan flags and scan request pointer, VIF BSS/self station indices, STA firmware indices and DPU descriptors, GTK replay counter, SMD indication queue, and firmware-backed power/offload state. The NV image is requested from firmware storage through `request_firmware()` and fragmented in 3072-byte chunks; it persists in `wcn->nv` until released by wider driver teardown.

## Dependencies and Integration Points
This file depends on Linux rpmsg, firmware loading, mac80211/cfg80211 structures, Qualcomm HAL definitions in `hal.h`, firmware capability helpers in `firmware.h`, and DXE TX ACK callbacks. It is used by the WCN36xx mac80211 operations layer for control operations and by `testmode.c` for production test passthrough.

## Risks and Test Signals
Key risks are HAL ABI drift, buffer length mistakes in variable-length messages, firmware-version-specific structure sizing, race mistakes around the shared `hal_buf`, and stale firmware state if response parsing fails after the firmware partially applied a command. Test signals include successful firmware start/version logging, NV download completion, scan completion/abort behavior, association and AP bring-up, key install/remove, suspend/resume offloads, beacon-loss handling, and lack of HAL timeout or "response failed" logs under traffic and scan stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.h

## Purpose
`smd.h` is the public control-plane interface for the WCN36xx SMD/rpmsg HAL layer. It defines transport constants, common response/indication wrappers, firmware result values, and the exported functions used by the rest of the driver to command firmware.

## Important APIs, Types, and Functions
- `WCN36XX_NV_FRAGMENT_SIZE`, `WCN36XX_HAL_BUF_SIZE`, and `HAL_MSG_TIMEOUT` constrain NV transfer, shared HAL buffer size, and synchronous command wait time.
- `enum wcn36xx_fw_msg_result` documents success and known failure result codes returned in firmware responses.
- `struct wcn36xx_fw_msg_status_rsp` is the generic status body used by many HAL responses.
- `struct wcn36xx_hal_ind_msg` is the queued asynchronous indication container, using a flexible counted payload.
- Function prototypes expose the full SMD control surface: open/close, firmware start/stop/NV load, scan, STA/BSS lifecycle, keys, power, statistics, BA aggregation, offloads, host suspend/resume, beacon filter, multicast, testmode PTT, and rpmsg response dispatch.

## Control Flow
The header defines no executable control flow, but it establishes the driver layering: mac80211-facing code calls these exported functions, `smd.c` serializes them to firmware, and rpmsg calls `wcn36xx_smd_rsp_process()` for both command responses and asynchronous firmware events.

## State and Persistence Behavior
The API operates on `struct wcn36xx` plus per-VIF/per-STA mac80211 objects. Calls persist firmware-assigned BSS/STA indices, power/offload settings, firmware capabilities, and scan state in the private objects declared in `wcn36xx.h`.

## Dependencies and Integration Points
The header includes `wcn36xx.h` and references `rpmsg_device`, `ieee80211_vif`, `ieee80211_sta`, `cfg80211_scan_request`, `station_info`, and multiple HAL-specific structures. It is included by core driver files and testmode code.

## Risks and Test Signals
Because this is the driver ABI boundary, prototype or constant drift can break many call sites. Tests should build all WCN36xx configurations, exercise each mac80211 operation family, and verify that disabled optional paths, especially IPv6 and testmode, still compile cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.c

## Purpose
`testmode.c` implements the nl80211 testmode entry point for WCN36xx factory/production-test messages. It accepts a vendor test command, validates netlink attributes, handles a local build-release query, and forwards other PTT messages to firmware through the SMD HAL.

## Important APIs, Types, and Functions
- `wcn36xx_tm_policy` accepts `WCN36XX_TM_ATTR_CMD` as `NLA_U16` and `WCN36XX_TM_ATTR_DATA` as bounded binary data up to `WCN36XX_TM_DATA_MAX_LEN`.
- `struct build_release_number` is the packed response body for `MSG_GET_BUILD_RELEASE_NUMBER`.
- `wcn36xx_tm_cmd()` parses the netlink payload, requires command `WCN36XX_TM_CMD_PTT`, and dispatches to `wcn36xx_tm_cmd_ptt()`.
- `wcn36xx_tm_cmd_ptt()` interprets the incoming `struct ftm_rsp_msg`, either fills local firmware version fields or calls `wcn36xx_smd_process_ptt_msg()`, then replies with `cfg80211_testmode_reply()`.

## Control Flow
Netlink testmode data enters `wcn36xx_tm_cmd()`, is parsed by `nla_parse_deprecated()`, and must contain a command attribute. Unsupported commands return `-EOPNOTSUPP`. PTT data is inspected as an FTM message. The build-release message is answered directly from `wcn->fw_major/minor/version/revision`; all other payloads are sent to firmware, and if firmware returns no response the code echoes the request with the response status.

## State and Persistence Behavior
This file does not own persistent state. It reads firmware version fields from `struct wcn36xx`, temporarily allocates firmware response buffers, and relies on SMD to perform any firmware-side state change represented by PTT messages.

## Dependencies and Integration Points
It integrates nl80211 testmode (`cfg80211_testmode_alloc_reply_skb()`, `cfg80211_testmode_reply()`), netlink attribute parsing, `testmode.h`/`testmode_i.h` protocol definitions, and the SMD PTT function. It is compiled only when `CONFIG_NL80211_TESTMODE` enables the external entry point.

## Risks and Test Signals
Risks include trusting the binary test payload layout, response length mismatches, and using `msg_body_length` for both request forwarding and reply allocation. Test signals are correct rejection of missing/oversized attributes, successful build-release responses, PTT round trips with firmware, no leaks when firmware allocates a distinct response, and clean behavior when firmware returns no response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.h

## Purpose
`testmode.h` defines the public WCN36xx nl80211 testmode payload structures and provides the `wcn36xx_tm_cmd()` declaration or stub depending on `CONFIG_NL80211_TESTMODE`.

## Important APIs, Types, and Functions
- `struct ftm_rsp_msg` is the packed firmware test message wrapper containing message ID, body length, response status, and flexible response bytes.
- `struct ftm_payload` wraps an FTM command type with an embedded `ftm_rsp_msg`.
- `MSG_GET_BUILD_RELEASE_NUMBER` identifies the locally handled version query.
- `wcn36xx_tm_cmd()` is exported when testmode is enabled; otherwise an inline stub returns success so callers can compile without conditional code.

## Control Flow
The header has no active control flow. Its conditional compilation path determines whether cfg80211 testmode calls are wired to `testmode.c` or become a no-op.

## State and Persistence Behavior
The structures describe transient netlink/firmware payloads. They do not own persistent state, but their packed layout is part of the userspace-driver-firmware test ABI.

## Dependencies and Integration Points
The header includes `wcn36xx.h` for mac80211 types and driver context. It is consumed by the WCN36xx mac80211 operations and by `testmode.c`.

## Risks and Test Signals
The main risk is ABI mismatch in packed binary layouts or the disabled-testmode stub hiding unsupported userspace expectations. Test signals are allmodconfig build coverage, nl80211 testmode attribute interoperability, and correct version query layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode_i.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode_i.h

## Purpose
`testmode_i.h` holds the internal nl80211 testmode attribute IDs and command number used by WCN36xx production-test handling.

## Important APIs, Types, and Functions
- `WCN36XX_TM_DATA_MAX_LEN` caps binary test payloads at 5000 bytes.
- `enum wcn36xx_tm_attr` defines command and data attributes with the standard max marker.
- `WCN36XX_TM_CMD_PTT` is the accepted testmode command selector.

## Control Flow
There is no runtime control flow. `testmode.c` uses these constants to build the netlink policy and to reject unsupported commands.

## State and Persistence Behavior
The file defines ABI constants only. The values persist as part of the userspace-visible testmode protocol.

## Dependencies and Integration Points
It is included by `testmode.c` and indirectly tied to nl80211 netlink parsing. It intentionally stays small and private to avoid exposing internal attribute names beyond the driver implementation.

## Risks and Test Signals
Changing numeric values would break userspace tooling. Test signals are netlink policy validation, command rejection for unknown IDs, and fuzzing of oversized binary payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/testmode_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.c

## Purpose
`txrx.c` translates between WCN36xx firmware/DXE frame descriptors and mac80211 skbs. On RX it validates firmware buffer descriptors, reconstructs frame data, fills `ieee80211_rx_status`, updates survey data, handles chained A-MSDU fragments, and submits frames to mac80211. On TX it builds firmware TX descriptors, selects station/VIF indices, requests optional TX status, and hands frames to DXE.

## Important APIs, Types, and Functions
- `wcn36xx_rx_skb()` is the RX entry point. It endian-converts `struct wcn36xx_rx_bd`, checks descriptor offsets and lengths, extracts frame metadata, fills rate/signal/band/frequency fields, reassembles chained A-MSDUs, and calls `ieee80211_rx_irqsafe()`.
- `wcn36xx_start_tx()` is the TX entry point. It determines data vs management/control, broadcast vs unicast, ACK-status needs, fills `struct wcn36xx_tx_bd`, endian-converts it, and calls `wcn36xx_dxe_tx_frame()`.
- `wcn36xx_set_tx_data()` and `wcn36xx_set_tx_mgmt()` populate descriptor fields for data and management/control frames.
- `wcn36xx_tx_start_ampdu()` starts BA sessions after enough non-aggregated QoS frames.
- `wcn36xx_process_tx_rate()` converts firmware stats rate flags into mac80211 `rate_info`.
- `wcn36xx_rate_table` maps firmware RX rate IDs to mac80211 bitrate/MCS/encoding/bandwidth fields.

## Control Flow
RX starts with descriptor sanity checks before mutating skb length and data pointers. Scan-learn frames derive channel information from the descriptor; normal frames use current hardware channel state. Rate IDs are table-mapped when valid and defaulted otherwise. Chained A-MSDU fragments are queued in `wcn->amsdu` until the last segment, then copied into the first skb. Any malformed descriptor drops the skb and purges the chain.

TX starts by logging and initializing a zeroed descriptor. If mac80211 requested TX status, the driver stops queues because firmware supports one outstanding ACK indication, then sets `tx_comp`. Data frames get STA/DPU indices from `sta_priv` when available or from the owning VIF for non-unicast frames; management frames use self station indices. The descriptor is byte-swapped with `buff_to_be()`, stamped, and sent to DXE.

## State and Persistence Behavior
The file updates per-channel survey RSSI/SNR under `survey_lock`, adds SNR samples to kernel randomness, maintains the temporary A-MSDU skb queue, mutates per-STA AMPDU state under `ampdu_lock`, and temporarily stops/wakes mac80211 queues around firmware TX ACK indications.

## Dependencies and Integration Points
It depends on `txrx.h` descriptor definitions, `wcn36xx.h` private state, DXE transmit entry points, mac80211 RX/TX status APIs, Linux skb helpers, and channel/rate definitions. It cooperates with `smd.c` for BA session negotiation and statistics conversion.

## Risks and Test Signals
Risks include descriptor offset trust, endian conversion mistakes, A-MSDU chain leaks, NULL VIF lookup for management/non-unicast paths, queue stalls when TX ACK indication is lost, and inaccurate rate mappings for newer firmware. Test signals include RX malformed-descriptor drops without crashes, beacon/probe timestamps, scan result channels, sustained encrypted/unencrypted TX, AMPDU startup, TX-status queue recovery, and no skb leaks under chained A-MSDU traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.h

## Purpose
`txrx.h` defines WCN36xx firmware RX/TX buffer descriptor layouts, TX queue/rate constants, sequence-number fill policy, and the exported TX/RX helpers used by the DXE and mac80211 glue.

## Important APIs, Types, and Functions
- `struct wcn36xx_pdu` describes common MPDU layout fields embedded in RX and TX descriptors.
- `struct wcn36xx_rx_bd` mirrors the firmware RX descriptor, including status bits, PDU offsets, PHY stats, reorder metadata, channel/band, and A-MSDU flags.
- `struct wcn36xx_tx_bd` mirrors the firmware TX descriptor, including queue, rate, ACK policy, station index, DPU descriptor, and timing fields.
- `enum wcn36xx_txbd_ssn_type` controls whether sequence numbers are filled by host or DPU.
- `wcn36xx_rx_skb()`, `wcn36xx_start_tx()`, and `wcn36xx_process_tx_rate()` are the public functions implemented in `txrx.c`.

## Control Flow
The header does not implement control flow, but its bitfield ordering and descriptor sizes directly drive the TX/RX processing path. `txrx.c` writes these structures, converts them to firmware byte order, and validates their offset fields on receive.

## State and Persistence Behavior
Descriptor instances are transient per-frame objects. Constants such as `WCN36XX_TX_B_WQ_ID`, `WCN36XX_TX_U_WQ_ID`, and `WCN36XX_TID` encode persistent firmware queue contract assumptions.

## Dependencies and Integration Points
It includes Linux Ethernet helpers and `wcn36xx.h`; it references mac80211 skbs and HAL stats types. DXE code consumes the TX descriptor built from these definitions, while RX code receives firmware-populated instances.

## Risks and Test Signals
The risk is high for ABI drift: C bitfield layout must match firmware expectations and is sensitive to compiler/endianness assumptions mitigated by explicit word swapping in callers. Test signals include successful RX/TX across data, management, broadcast, QoS, and encrypted paths plus descriptor dumps that match firmware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/wcn36xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/wcn36xx.h

## Purpose
`wcn36xx.h` is the central private header for the WCN36xx mac80211 driver. It defines debug masks/macros, RF identifiers, channel helper macros, byte-order conversion helper, and the main per-driver, per-VIF, and per-STA private structures shared by SMD, DXE, TX/RX, PMC, debugfs, and mac80211 glue.

## Important APIs, Types, and Functions
- Debug macros (`wcn36xx_err`, `wcn36xx_warn`, `wcn36xx_info`, `wcn36xx_dbg`, `wcn36xx_dbg_dump`) gate logging by `wcn36xx_dbg_mask`.
- `enum wcn36xx_ampdu_state` tracks per-TID aggregation lifecycle.
- Channel macros derive hardware channel, band, frequency, listen interval, flags, and power from `wcn->hw->conf`.
- `buff_to_be()` converts an array of 32-bit words in place to big-endian representation used by firmware descriptors.
- `struct wcn36xx_vif` stores BSS type, encryption, firmware BSS/self station indices, power state, IPv6/GTK WoWLAN data, and per-VIF STA list.
- `struct wcn36xx_sta` stores association ID, TID, firmware STA/DPU indices, encryption state, rates, and AMPDU state.
- `struct wcn36xx` stores mac80211 device pointers, firmware/NV data, rpmsg endpoint, SMEM state bits, HAL synchronization, scan state, DXE channels, memory pools, TX ACK state, A-MSDU queue, RF ID, survey data, and optional debugfs state.
- Inline container helpers map between mac80211 objects and private structures.

## Control Flow
The header provides helpers rather than active workflows. Its structures are the shared state that `smd.c` mutates during firmware control operations, `txrx.c` consumes during frame processing, and higher mac80211 callbacks use to bind Linux wireless objects to firmware indices.

## State and Persistence Behavior
Most driver persistence is declared here: firmware version/capability state, NV firmware pointer, rpmsg/SMEM transport handles, locks/completions/workqueues, scan status, DXE rings and pools, TX ACK timer/skb, A-MSDU queue, RF module identity, and channel survey cache. VIF and STA structures persist for the lifetime of their mac80211 objects.

## Dependencies and Integration Points
It pulls in mac80211, Linux completion/spinlock/IPv6 definitions, and local headers `hal.h`, `smd.h`, `txrx.h`, `dxe.h`, `pmc.h`, and `debug.h`. This creates the central include hub for the WCN36xx driver.

## Risks and Test Signals
Risks include circular include fragility, shared-state locking errors, stale firmware indices after failed teardown, and helper misuse when mac80211 object lifetimes change. Test signals are build coverage across IPv6/debugfs options, interface add/remove, suspend/resume, scan cancellation, aggregation, and debug logging without use-after-free reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/wcn36xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Kconfig

## Purpose
`Kconfig` declares build-time configuration for the Wilocity/Qualcomm Atheros `wil6210` 60 GHz IEEE 802.11ad wireless driver and its debug/tracing options.

## Important APIs, Types, and Functions
- `CONFIG_WIL6210` is a tristate driver option depending on `CFG80211` and `PCI`, selecting `WANT_DEV_COREDUMP` and `CRC32`.
- `CONFIG_WIL6210_ISR_COR` selects clear-on-read interrupt status handling, defaulting to enabled for production.
- `CONFIG_WIL6210_TRACING` enables kernel tracepoints when `EVENT_TRACING` is available.
- `CONFIG_WIL6210_DEBUGFS` enables debugfs support when `DEBUG_FS` is available.

## Control Flow
There is no runtime control flow. The selected options control which objects the Makefile builds and which conditional code paths are compiled.

## State and Persistence Behavior
Configuration persists in the kernel build configuration. Runtime impact includes whether interrupt registers use COR semantics and whether tracing/debugfs interfaces exist.

## Dependencies and Integration Points
The file integrates the driver into the kernel wireless Kconfig tree. It constrains the driver to PCI/cfg80211 systems and drives conditional objects in `Makefile`.

## Risks and Test Signals
Risks include selecting debug defaults that expose unsupported interfaces or disabling trace/debug objects required during field diagnosis. Test signals are build coverage for built-in/module/disabled states and all combinations of tracing/debugfs/ISR mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Makefile

## Purpose
`Makefile` defines the `wil6210` kernel module composition and conditional object inclusion for debugfs and tracing support.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_WIL6210) += wil6210.o` ties module build to the Kconfig symbol.
- `wil6210-y` lists core objects: main, netdev, cfg80211, PCI bus, WMI, interrupt, TX/RX, eDMA TX/RX, debug, reorder, firmware, PM, PMC, platform, ethtool, crash dump, and P2P support.
- `wil6210-$(CONFIG_WIL6210_DEBUGFS)` and `wil6210-$(CONFIG_WIL6210_TRACING)` conditionally add `debugfs.o` and `trace.o`.
- `CFLAGS_trace.o := -I$(src)` lets the tracing framework locate `trace.h`.

## Control Flow
No runtime control flow exists. Build selection determines which translation units and optional feature code are linked into the module.

## State and Persistence Behavior
The file affects build artifacts only. It does not define runtime state.

## Dependencies and Integration Points
It depends on Kbuild conventions and symbols from `Kconfig`. The object order reflects driver subsystem boundaries: cfg80211 registration, WMI firmware control, bus/interrupt plumbing, TX/RX datapath, PM, and diagnostics.

## Risks and Test Signals
Risks include missing an object when adding cross-file APIs or breaking trace include paths. Test signals are clean incremental and full kernel builds with tracing/debugfs enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/boot_loader.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/boot_loader.h

## Purpose
`boot_loader.h` documents the memory-mapped boot-loader dedicated register layouts for the Qualcomm "Sparrow" 60 GHz solution used by `wil6210`.

## Important APIs, Types, and Functions
- `struct bl_dedicated_registers_v1` is the newer packed layout with readiness, structure version, RF/baseband IDs, MAC address, boot-loader version, assert diagnostics, shutdown handshake, reserved words, and magic number.
- `struct bl_dedicated_registers_v0` is the older packed layout with readiness, version, RF/baseband IDs, and MAC address.
- `BL_READY` marks boot-loader readiness.
- `BL_SHUTDOWN_HS_GRTD`, `BL_SHUTDOWN_HS_RTD`, and `BL_SHUTDOWN_HS_PROT_VER()` define shutdown handshake bits and protocol version extraction.

## Control Flow
The header has no active control flow. Runtime firmware/bus code reads these packed structures from fixed device memory/register offsets and interprets readiness, identity, version, assert, and shutdown fields.

## State and Persistence Behavior
The structures expose device boot-loader state. The driver reads them to discover MAC/RF/baseband/version data and participates in shutdown handshaking through the mapped register area.

## Dependencies and Integration Points
It relies on Linux endian types and `BIT()`/`WIL_GET_BITS()` macros from the broader driver include context. Firmware loading, crash/reset, and PCI bus code use these definitions.

## Risks and Test Signals
Risks include layout drift against hardware, incorrect endian conversion, and misinterpreting version-specific fields. Test signals are boot readiness polling, correct MAC/version logging, RF status handling, crash/assert diagnostics, and clean shutdown handshake across supported hardware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/boot_loader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/cfg80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/cfg80211.c

## Purpose
`cfg80211.c` is the cfg80211/nl80211 integration layer for the `wil6210` 60 GHz PCI wireless driver. It advertises wiphy capabilities, maps Linux wireless operations to WMI firmware commands, manages virtual interfaces and P2P device state, performs scan/connect/AP/key management, handles scheduled scan and power management, exposes QCA vendor RF-sector commands, and initializes/deinitializes the wiphy.

## Important APIs, Types, and Functions
- Capability setup lives in `wil_wiphy_init()`, `update_supported_bands()`, `wil_cfg80211_iface_combinations_from_fw()`, and static definitions for 60 GHz channels, management frame subtypes, cipher suites, WoWLAN, and vendor commands.
- Interface lifecycle is implemented by `wil_cfg80211_add_iface()`, `wil_cfg80211_del_iface()`, `wil_cfg80211_change_iface()`, `wil_vif_prepare_stop()`, and P2P start/stop helpers.
- Station reporting uses `wil_cid_fill_sinfo()`, `wil_cfg80211_get_station()`, `wil_cfg80211_dump_station()`, and `wil_find_cid_by_idx()`.
- Client operations include `wil_cfg80211_scan()`, `wil_cfg80211_abort_scan()`, `wil_cfg80211_connect()`, `wil_ft_connect()`, `wil_cfg80211_disconnect()`, and `wil_cfg80211_update_ft_ies()`.
- AP operations include `_wil_cfg80211_start_ap()`, `wil_cfg80211_start_ap()`, `wil_cfg80211_change_beacon()`, `wil_cfg80211_stop_ap()`, station add/delete/change handlers, AP recovery, probe-client worker support, and BSS parameter changes.
- Security/key code includes `wil_detect_key_usage()`, `wil_find_sta_by_key_usage()`, `wil_cfg80211_add_key()`, `wil_cfg80211_del_key()`, and RX PN cache helpers.
- Vendor commands are handled by `wil_rf_sector_get_cfg()`, `wil_rf_sector_set_cfg()`, `wil_rf_sector_get_selected()`, and `wil_rf_sector_set_selected()`.
- `wil_cfg80211_ops` binds all handlers into cfg80211; `wil_cfg80211_init()` and `wil_cfg80211_deinit()` allocate/free the wiphy.

## Control Flow
At initialization, `wiphy_new()` allocates `struct wil6210_priv` as wiphy private data, `wil_wiphy_init()` fills cfg80211 capabilities, and later firmware records may update interface combinations and supported channels. cfg80211 callbacks then translate userspace requests into WMI commands.

Scan validates interface type, serializes under `wil->mutex`, prevents concurrent scan/discovery, configures SSID and probe-request IEs, starts a scan timer, optionally assigns `radio_wdev`, and sends `WMI_START_SCAN_CMDID`; abort paths stop P2P radio operations or call `wil_abort_scan()`. Connect validates state, BSS, privacy, RSN/WSC/FT constraints, clears old keys for secure associations, fills `wmi_connect_cmd`, requests bus bandwidth, starts a connect timer, and stores the BSS. Disconnect performs a synchronous WMI disconnect call.

AP start resets firmware when needed, configures SSID and IEs, records recovery state in the VIF, raises carrier, requests bus bandwidth, starts PCP via WMI, and initializes broadcast resources. AP recovery replays stored SSID/IE/GTK data after firmware recovery. Key install chooses WMI key usage based on interface type and pairwise/group context, handles FT rekey state, sends the key to firmware, and updates local RX PN or GTK recovery caches.

Vendor RF-sector commands parse nested netlink attributes, validate sector/module/MAC input, issue WMI get/set calls, translate firmware status codes to errno, and return nested cfg80211 vendor replies with TSF and sector data.

## State and Persistence Behavior
The file mutates `wil6210_priv` and per-VIF state extensively: supported channel count, EDMG capability, interface combinations, max VIFs, P2P/radio wdev pointers, monitor channel, scan request pointers/timers, connection flags and BSS pointer, privacy/PBSS/channel/SSID/IE recovery data, GTK cache, AP isolate, multicast-to-unicast flag, CQM RSSI threshold, firmware recovery state, bus bandwidth request level, and per-station RX crypto PN caches.

## Dependencies and Integration Points
It integrates Linux cfg80211, nl80211 vendor commands, netdevice carrier state, kernel module parameters, WMI command helpers, firmware capability records, P2P helpers, bus bandwidth management, TX/RX station stats, and kernel PM/WoWLAN hooks. It is central to userspace interaction through `iw`, wpa_supplicant/hostapd, P2P management, and vendor RF tooling.

## Risks and Test Signals
Risks include cfg80211 API drift, lock ordering across `wil->mutex` and `vif_mutex`, stale scan/connect timers, mismatched VIF concurrency rules from firmware, AP recovery restoring incomplete IE/key state, FT-roam state transitions, vendor nested-attribute validation bugs, and incorrect key usage for group keys in AP/client modes. Test signals include wiphy registration, scan/abort/P2P social scan, connect/disconnect with open/GCMP/WSC/FT, AP start/change/stop/recovery, VIF add/change/delete, scheduled scan, suspend/resume, CQM updates, RF-sector vendor command round trips, and lockdep under concurrent cfg80211 operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/cfg80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debug.c

## Purpose
`debug.c` centralizes `wil6210` logging wrappers so driver messages are emitted both to the netdevice log and to tracing when enabled.

## Important APIs, Types, and Functions
- `__wil_err()` emits error messages through `netdev_err()` and `trace_wil6210_log_err()`.
- `__wil_err_ratelimited()` wraps the same error path with `net_ratelimit()`.
- `wil_dbg_ratelimited()` rate-limits debug messages through `netdev_dbg()` and `trace_wil6210_log_dbg()`.
- `__wil_info()` emits info messages through `netdev_info()` and trace info.
- `wil_dbg_trace()` emits debug tracepoints without printing to netdev.
- All helpers use `struct va_format` to share a variadic format with both sinks.

## Control Flow
Each function builds a `va_list`, assigns it to `va_format`, emits to the appropriate netdev and/or trace sink, and then calls `va_end()`. The rate-limited variants return early if `net_ratelimit()` denies the message.

## State and Persistence Behavior
There is no persistent state. The functions read `wil->main_ndev` for logging context and emit transient kernel log/trace records.

## Dependencies and Integration Points
It depends on `wil6210.h` logging declarations/macros and `trace.h` tracepoint definitions. Other driver files use these wrappers instead of directly calling netdev logging.

## Risks and Test Signals
Risks include using a NULL or freed `main_ndev`, trace format lifetime mistakes, and suppressed diagnostics from global rate limiting during failure storms. Test signals are compile coverage with tracing enabled/disabled, visible netdev messages, tracepoint capture, and no warnings from variadic formatting paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debug.c -->
