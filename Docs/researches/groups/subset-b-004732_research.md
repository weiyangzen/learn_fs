# subset-b-004732 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.h

## Purpose
`hal.h` is the central ath11k hardware-abstraction contract for SRNG rings, REO command/state objects, ring register offsets, and common descriptor helpers. It does not implement hardware access directly; instead it names the register layout and public HAL APIs used by data path, copy engine, WMI/HTT transport setup, and hardware-specific ops. Most constants are tied to Qualcomm Wi-Fi UMAC blocks: TCL, REO, WBM, CE, RXDMA, LMAC rings, shadow registers, MSI pointer registers, and DSCP/TID tables.

## Important APIs, types, and data
Key exported types are `struct hal_srng`, `struct hal_srng_params`, `struct hal_srng_config`, `struct ath11k_hal_reo_cmd`, `struct hal_reo_status`, and `struct ath11k_hal`. `struct hal_srng` persists per-ring runtime state: ring id, physical/virtual ring base, entry size, interrupt thresholds, MSI address/data, flags, spinlock, register bases, timestamps, direction, source head/reap/tail tracking, or destination tail/head tracking. `struct ath11k_hal` owns the full `srng_list`, the SRNG config table, remote/write ring pointer DMA regions, REO blocking resource state, shadow register addresses, and lock class keys.

The public API surface includes REO queue descriptor sizing/setup, REO command ring initialization, WBM idle list setup, link descriptor address setting, CE descriptor helpers, SRNG setup/init/deinit/access/read/write helper operations, SRNG shadow configuration, and debug dumping. Ring type and ring id enums define the mapping from driver concepts (`HAL_TCL_DATA`, `HAL_REO_DST`, `HAL_RXDMA_BUF`, `HAL_CE_SRC`, etc.) to hardware ring id ranges.

## Control flow and integration
This header is consumed by `hal.c` for generic SRNG implementation, by `hal_rx.c` and `hal_tx.c` for command descriptor setup and parser helpers, by DP RX/TX code for enqueue/reap paths, by CE code for copy engine rings, and by hardware setup code for REO routing/aging registers. Register macros frequently dereference `ab->hw_params.regs`, so the same code can target multiple ath11k chips with different register offsets.

## State and persistence
All persistent state described here is in memory or DMA memory owned by the driver and device. The most important mutable state is ring pointer state in `struct hal_srng`, shadow pointer memory in `ath11k_hal.rdp`/`wrp`, `avail_blk_resource`/`current_blk_index` for REO cache blocking resources, and the per-ring lock. There is no filesystem persistence.

## Dependencies
`hal.h` depends on `hal_desc.h` for packed hardware descriptor structures and `rx_desc.h` for RX descriptor definitions. It assumes Linux kernel helpers such as `BIT`, `GENMASK`, DMA address types, spinlocks, and `FIELD_PREP` users. It also depends on `struct ath11k_base` hardware parameter population before any register macro is evaluated.

## Risks
The header encodes hardware ABI. Incorrect ring sizes, register offsets, ring ids, bit masks, or enum values can cause DMA corruption, wedged rings, interrupt storms, or silent packet loss. Many macros are chip-parametric; incomplete `hw_params.regs` initialization will break later HAL calls. SRNG state must be protected consistently by the embedded lock and access begin/end protocol. BA window and PN constants must stay aligned with descriptor fields in `hal_desc.h`.

## Test signals
Useful validation comes from successful `ath11k_hal_srng_setup()`/init paths, stable boot without SRNG setup warnings, DP RX/TX traffic, REO command completion, MSI/interrupt delivery, monitor mode captures, suspend/resume, and debugfs/SRNG dump sanity. Compile coverage should catch prototype drift, but only hardware or emulation traffic can validate register-level correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_desc.h

## Purpose
`hal_desc.h` defines the packed hardware descriptor ABI used by ath11k HAL, DP, CE, TCL, REO, RXDMA, and WBM paths. It maps device-produced and host-produced ring entries to C structs and bit masks. The file is mostly declarative: TLV tags, buffer address layouts, RX/TX command descriptors, CE source/destination/status descriptors, WBM release descriptors, REO queue descriptors, REO commands, and REO status records.

## Important APIs, types, and data
The foundational type is `struct ath11k_buffer_addr`, which carries a 40-bit DMA address, return buffer manager, and software cookie. `enum hal_tlv_tag` enumerates hundreds of hardware TLV tags used by monitor status, RX/TX data, REO/TQM, CCE, and PHY/MAC status streams. `struct hal_tlv_hdr` defines the common TLV header.

RX-facing descriptors include `struct rx_mpdu_desc`, `struct rx_msdu_desc`, `struct hal_reo_dest_ring`, `struct hal_reo_entrance_ring`, `struct hal_sw_monitor_ring`, `struct hal_rx_msdu_link`, `struct hal_rx_reo_queue`, and `struct hal_rx_reo_queue_ext`. TX-facing descriptors include `struct hal_tcl_data_cmd`, `struct hal_tcl_gse_cmd`, and `struct hal_tcl_status_ring`. CE descriptors include `struct hal_ce_srng_src_desc`, `struct hal_ce_srng_dest_desc`, and `struct hal_ce_srng_dst_status_desc`. WBM completion/release data is represented by `struct hal_wbm_release_ring`, `struct hal_tx_rate_stats`, and related release/status enums.

REO command/status types include `struct hal_reo_get_queue_stats`, `struct hal_reo_flush_queue`, `struct hal_reo_flush_cache`, `struct hal_reo_update_rx_queue`, `struct hal_reo_unblock_cache`, and status records for queue stats, flush queue, flush cache, unblock cache, timeout list, and descriptor threshold notifications.

## Control flow and integration
The file has no executable control flow. Its descriptors are written by helpers in `hal_rx.c`, `hal_tx.c`, `hal.c`, CE code, and DP code, and read from hardware rings by DP RX/TX and monitor paths. `hal_rx.c` uses the REO command/status structures and RX monitor structures. `hal_tx.c` writes `hal_tcl_data_cmd`. CE code uses the CE descriptor layouts. TX completion parsing relies on the WBM release ring fields and the HTT overlay comment.

## State and persistence
The structs represent state in DMA rings or DMA descriptors shared with hardware. Ownership fields in `struct hal_desc_header`, return buffer manager fields, ring id/loop counts, queue PN/bitmap/stat counters, and WBM release details are persistent only while descriptors live in device/host memory. There is no disk persistence and no internal static state.

## Dependencies
This header includes `core.h` and relies on Linux kernel bitfield helpers and packed/aligned layout semantics. It must stay synchronized with firmware/hardware interface definitions and with `hal.h` enums such as return buffer managers and descriptor ownership constants. It is also tied to `rx_desc.h` and chip-specific ops that interpret variant RX MPDU layouts.

## Risks
The dominant risk is hardware ABI drift. A wrong mask, field width, struct order, packed attribute, enum value, or descriptor size can corrupt DMA interpretation. Several fields are overlays or chip-specific variants; parsing the wrong variant can report bogus peer ids, lengths, or status. Some definitions are only comments plus masks, so compile tests cannot prove semantic correctness. The apparent `HAL_RX_REO_QUEUE_INFO2_MSDU_COUNT` definition lacks `GENMASK`, which is a local risk if used as a bit mask.

## Test signals
Compile coverage validates structure references. Runtime signals include clean firmware boot, successful CE/HTC messaging, TCL enqueue and TX completion, RX buffer recycling, REO queue setup, REO status processing, monitor-mode radiotap data, and absence of DMA mapping, invalid RBM, descriptor type, or REO error warnings under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.c

## Purpose
`hal_rx.c` implements RX-side HAL helpers for REO command construction, REO status parsing, RX/WBM error descriptor parsing, RX buffer address extraction, REO queue descriptor setup, REO command ring initialization, and monitor-status TLV parsing into `hal_rx_mon_ppdu_info`. It is a bridge between packed descriptors from `hal_desc.h`/`hal_rx.h` and higher-level DP RX logic.

## Important APIs, types, and functions
Important exported functions include `ath11k_hal_reo_cmd_send()`, `ath11k_hal_rx_buf_addr_info_set()`, `ath11k_hal_rx_buf_addr_info_get()`, `ath11k_hal_rx_msdu_link_info_get()`, `ath11k_hal_desc_reo_parse_err()`, `ath11k_hal_wbm_desc_parse_err()`, `ath11k_hal_rx_reo_ent_paddr_get()`, `ath11k_hal_rx_msdu_link_desc_set()`, all `ath11k_hal_reo_*_status()` parsers, `ath11k_hal_reo_process_status()`, `ath11k_hal_reo_qdesc_size()`, `ath11k_hal_reo_qdesc_setup()`, `ath11k_hal_reo_init_cmd_ring()`, `ath11k_hal_rx_parse_mon_status()`, `ath11k_hal_rx_reo_ent_buf_paddr_get()`, and `ath11k_hal_rx_sw_mon_ring_buf_paddr_get()`.

Internal command builders create TLV entries for `HAL_REO_GET_QUEUE_STATS`, `HAL_REO_FLUSH_CACHE`, and `HAL_REO_UPDATE_RX_REO_QUEUE`. The monitor parser handles PPDU start/end, HT/VHT/HE SIG fields, RSSI, MPDU start peer id, RX duration/TSFT, dummy/status-done TLVs, and radiotap HE/HE-MU fields.

## Control flow
`ath11k_hal_reo_cmd_send()` locks the SRNG, begins access, obtains the next source entry, dispatches on REO command type, starts the DP REO command timer, ends access, and unlocks. Unsupported REO commands return `-EOPNOTSUPP`; unknown commands return `-EINVAL`; no ring space returns `-ENOBUFS`.

REO status parsing functions cast the TLV payload to the expected status struct and populate a generic `struct hal_reo_status`. Queue stats also emit debug fields. Flush-cache and unblock-cache parsing update `ab->hal.avail_blk_resource` using `current_blk_index`.

Monitor parsing iterates through TLV headers in an SKB until PPDU done, buffer done, or `DP_RX_BUFFER_SIZE` is reached. Each TLV is decoded by tag and aligned to `HAL_TLV_ALIGN`; `HAL_RX_PPDU_END` has a special skip length.

## State and persistence
State mutation is limited but important: REO cache blocking resource bookkeeping in `ab->hal`, SRNG head/tail updates through HAL access helpers, `ab->soc_stats.reo_error[]` and `invalid_rbm`, and output structures filled for DP callers. REO queue descriptors are initialized in DMA memory with owner/type/magic fields, BA window size, PN policy, AC, retry, SSN, and extension descriptors. There is no filesystem persistence.

## Dependencies and integration
This file depends on `debug.h`, `hal.h`, `hal_tx.h`, `hal_rx.h`, `hal_desc.h`, `hif.h`, hardware ops such as `mpdu_info_get_peerid()` and `tx_mesh_enable()`, DP timers, Linux SKB and endian helpers, and mac80211 radiotap constants. DP RX consumes the address extraction, REO status, REO queue, and monitor parser helpers. DP TX uses `ath11k_hal_reo_cmd_send()` for REO commands declared through `hal_tx.h`.

## Risks
REO command support is partial: flush queue, unblock cache, and flush timeout list sends are explicitly unsupported even though status parsers exist. The REO flush-cache resource bookkeeping is a single `current_blk_index`, so concurrent blocked flushes would be fragile if higher layers do not serialize correctly. Monitor TLV parsing assumes buffer size bounds and correct TLV lengths; malformed firmware data can truncate parsing or produce misleading radiotap fields. BA window coercion from 1 to 2 for QoS TIDs is subtle and must stay aligned with allocation size. Error parsers reject unexpected buffer types/RBMs and increment stats, which are good signals but can drop buffers if descriptor ABI changes.

## Test signals
Expected signals are successful REO command completions, valid DP RX reorder setup, no `Unsupported reo command` use from active paths, stable RX traffic, sane monitor mode radiotap fields for HT/VHT/HE traffic, valid peer ids, and no invalid RBM or unexpected REO push reason warnings. Hardware traffic tests are more meaningful than unit tests because most behavior depends on DMA descriptors from firmware/hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.h

## Purpose
`hal_rx.h` is the public RX HAL interface and monitor-status data contract for ath11k. It declares RX error/release info, monitor PPDU status structures, PHY SIG TLV layouts, RX MPDU layout variants, helper prototypes implemented in `hal_rx.c`, and magic patterns for REO queue descriptors.

## Important APIs, types, and data
`struct hal_rx_wbm_rel_info` carries parsed WBM error-release details: cookie, release source, push reason, error code, and first/last MSDU flags. `enum hal_rx_mon_status` describes monitor parse progress. `struct hal_rx_user_status`, `struct hal_sw_mon_ring_entries`, and `struct hal_rx_mon_ppdu_info` are the main outputs used by monitor receive code to build rate/RSSI/radiotap information.

The header defines packed TLV payload structures for PPDU start, PPDU end user stats, HT SIG, L-SIG A/B, VHT SIG A, HE SIG A SU/MU, HE SIG B MU/OFDMA, legacy RSSI, per-chip RX MPDU info layouts, PPDU duration, and RXPCU classification overview. It also declares the REO status parsers, buffer-address helpers, REO entrance/monitor ring address extractors, REO queue helpers from `hal.h`, and monitor parser.

## Control flow and integration
Control flow lives in `hal_rx.c`, but this header defines the data shape for callers in `dp_rx.c`, `dbring.c`, and monitor-mode code. The DP layer calls buffer address setters when replenishing RX rings and getters when consuming status/ring descriptors. REO status handlers are selected in DP RX status processing according to TLV tags. Monitor code feeds status SKBs to `ath11k_hal_rx_parse_mon_status()` and consumes `hal_rx_mon_ppdu_info`.

## State and persistence
The header itself owns no state. Its structures are transient per-packet/per-PPDU outputs or views over DMA descriptor data. Persistent effects happen in caller-owned objects, such as SKBs, RX ring descriptors, DP RX peer/TID state, and REO queue DMA memory initialized through the declared APIs.

## Dependencies
The header depends on definitions from `hal.h`/`hal_desc.h`, Linux endian types, mac80211 radiotap constants used by the implementation, and chip-specific hardware ops that choose the right MPDU info variant. The `HAL_RX_MAX_NSS`, MCS, GI, bandwidth, preamble, and reception type constants are shared assumptions with DP monitor and mac80211 reporting code.

## Risks
The biggest risk is mismatched TLV layout across chips or firmware revisions. The header contains multiple chip-specific MPDU info layouts, so the correct hardware op must select peer id extraction. `struct hal_rx_mon_ppdu_info` is broad and easy to partially populate; consumers must check validity flags. The duplicate prototype for `ath11k_hal_reo_flush_cache_status()` is harmless but indicates header drift. Bit definitions for HE/OFDMA/radiotap fields need continuous validation against firmware output.

## Test signals
Monitor-mode captures should show accurate PPDU ids, rates, MCS/NSS, HE flags, RSSI, TSFT, duration, RU allocation, and FCS counters. RX stress should show correct buffer cookie/RBM extraction and no invalid descriptor warnings. Compile tests catch signature drift between `hal_rx.h` and `hal_rx.c`, while hardware traffic catches layout and endian mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.c

## Purpose
`hal_tx.c` implements TX-side HAL helpers for filling TCL data command descriptors, programming hardware DSCP-to-TID mapping tables, and preinitializing TCL data ring entries with the correct TLV tag/length. It converts DP-level transmit metadata into the exact descriptor fields consumed by the TCL hardware block.

## Important APIs and functions
`ath11k_hal_tx_cmd_desc_setup()` fills a `struct hal_tcl_data_cmd` from `struct hal_tx_info`: DMA address, return buffer manager, descriptor cookie, descriptor type, encapsulation/encryption type, search type, address-search flags, metadata command number, data length, packet offset, TID, LMAC id, DSCP table id, AST search index/hash, and optional mesh enable through hardware ops.

`ath11k_hal_tx_set_dscp_tid_map()` programs the default 64-entry DSCP map into a selected hardware DSCP/TID table. It enables programming access through `HAL_TCL1_RING_CMN_CTRL_DSCP_TID_MAP_PROG_EN`, packs eight 3-bit TID values into three bytes at a time, writes the resulting 24-byte table through HIF register writes, and disables programming access.

`ath11k_hal_tx_init_data_ring()` walks an already allocated TCL data SRNG and sets each entry's TLV header to `HAL_TCL_DATA_CMD` with `sizeof(struct hal_tcl_data_cmd)`.

## Control flow
Descriptor setup is a straight field-pack operation and has no allocation or locking of its own. DSCP map programming performs read-modify-write of the TCL common control register, sequential register writes for the table payload, then clears the programming-enable bit. Data-ring init obtains SRNG parameters and entry size from common HAL helpers, then advances through ring memory entry by entry.

## State and persistence
The file mutates DMA ring entries and device registers. `ath11k_hal_tx_cmd_desc_setup()` writes caller-provided descriptor memory. `ath11k_hal_tx_set_dscp_tid_map()` persists DSCP mapping in hardware until reset or reprogramming. `ath11k_hal_tx_init_data_ring()` initializes ring memory shared with hardware. There is no disk persistence and no private mutable static state beyond the constant default `dscp_tid_map`.

## Dependencies and integration
The implementation depends on `hal_desc.h`, `hal.h`, `hal_tx.h`, and `hif.h`. DP TX calls descriptor setup during TCL enqueue. DP init calls data ring initialization, and DP setup programs all DSCP/TID tables. Mesh handling is delegated to `ab->hw_params.hw_ops->tx_mesh_enable()`, preserving chip-specific descriptor behavior.

## Risks
Incorrect field packing can misroute TX buffers, break encryption/encapsulation, or corrupt completion cookies. DSCP table packing uses byte copies and `*(u32 *)&hw_map_val[i]`, which assumes safe unaligned access in this kernel context and little-endian layout matching hardware expectations. Register programming is not locally locked, so callers must avoid concurrent DSCP table writes. Mesh enable depends on a non-null hardware op when `enable_mesh` is true.

## Test signals
Useful signals are successful TX traffic across encapsulation modes, correct QoS/TID behavior under DSCP-marked packets, valid TX completions keyed by descriptor cookie, no TCL ring stalls, and mesh TX validation on chips that enable mesh descriptor fields. Register access errors typically surface as boot/setup failures or broken TX scheduling rather than compile errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.h

## Purpose
`hal_tx.h` declares the TX HAL interface used by DP TX and related REO command code. It defines the software input model for TCL data command descriptors and the parsed TX completion status structure used around WBM release descriptors.

## Important APIs, types, and data
`struct hal_tx_info` is the central input to `ath11k_hal_tx_cmd_desc_setup()`. It carries metadata flags, descriptor id/cookie, descriptor type, encapsulation and encryption type, DMA address, length, packet offset, checksum/control flags, address search behavior, AST hash/index, TID, LMAC id, DSCP/TID table index, mesh flag, and return buffer manager id.

`struct hal_tx_status` represents parsed TX status: WBM release source, TQM release reason/status, ACK RSSI, status flags, PPDU id, try count, TID, peer id, and rate stats. The header also defines status flag bits for first/last MSDU, A-MSDU membership, rate stats validity, LDPC/STBC, and OFDMA.

Declared functions are `ath11k_hal_tx_cmd_desc_setup()`, `ath11k_hal_tx_set_dscp_tid_map()`, `ath11k_hal_reo_cmd_send()`, and `ath11k_hal_tx_init_data_ring()`. The REO command send declaration is placed here for TX-side callers even though implemented in `hal_rx.c`.

## Control flow and integration
The header has no control flow. It integrates DP TX with HAL descriptor creation and lets DP command paths submit REO commands. `HAL_TX_STATUS_DESC_LEN` ties TX completion parsing to `struct hal_wbm_release_ring` from `hal_desc.h`.

## State and persistence
All state is caller-owned. `hal_tx_info` is transient per transmit descriptor, while `hal_tx_status` is transient per completion. Persistent device state is changed only by the functions declared here, especially DSCP/TID table programming and initialized TCL data rings.

## Dependencies
The header includes `hal_desc.h` and `core.h`, and it depends on enums for TCL descriptor type, encapsulation, encryption, WBM release source, and TQM release reason. Consumers must also include broader HAL definitions for `struct hal_srng` and `struct ath11k_hal_reo_cmd`.

## Risks
The main risk is semantic mismatch between DP-provided `hal_tx_info` fields and hardware descriptor fields. Missing or invalid `rbm_id`, AST index/hash, TID, LMAC id, or checksum flags can produce hard-to-debug TX drops. The placement of `ath11k_hal_reo_cmd_send()` in the TX header creates coupling to RX/REO implementation details.

## Test signals
Compile coverage validates consumers against the prototypes. Runtime validation should include TX enqueue/completion, QoS mapping, encrypted and unencrypted frames, mesh frames when supported, and REO command use from TX management paths. TX completion fields should map correctly to mac80211 status reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hif.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hif.h

## Purpose
`hif.h` defines the host interface abstraction for ath11k. It lets core, HAL, HTC, CE, debug, power-management, and bus-independent code call bus-specific operations through `ab->hif.ops` without knowing whether the device is PCI, AHB, or another transport.

## Important APIs, types, and data
`struct ath11k_hif_ops` is the core vtable. It contains operations for 32-bit register read/write, memory range read, IRQ and CE IRQ enable/disable, start/stop, power up/down, suspend/resume, HTC service-to-pipe mapping, MSI vector lookup, MSI address lookup, CE MSI index lookup, and coredump download.

The header then provides inline wrappers: `ath11k_hif_ce_irq_enable()`, `ath11k_hif_ce_irq_disable()`, `ath11k_hif_start()`, `ath11k_hif_stop()`, `ath11k_hif_irq_enable()`, `ath11k_hif_irq_disable()`, `ath11k_hif_power_up()`, `ath11k_hif_power_down()`, `ath11k_hif_suspend()`, `ath11k_hif_resume()`, `ath11k_hif_read32()`, `ath11k_hif_write32()`, `ath11k_hif_read()`, `ath11k_hif_map_service_to_pipe()`, MSI helpers, and `ath11k_hif_coredump_download()`.

## Control flow and integration
Most wrappers directly dispatch to the vtable. Optional operations either no-op or return `-EOPNOTSUPP`; suspend/resume default to success when absent. Core boot and shutdown use power/start/IRQ wrappers. HAL uses read/write wrappers for register programming. HTC service connection uses `ath11k_hif_map_service_to_pipe()`. Debugfs and coredump code use range read and coredump download. Bus drivers such as PCI/AHB populate concrete `ath11k_hif_ops`.

## State and persistence
This header owns no state. It routes calls through `struct ath11k_base`, whose HIF ops and bus-private state persist for the device lifetime. Side effects are entirely bus/device side effects: register access, IRQ state, power state, MSI configuration, and coredump transfer.

## Dependencies
The file includes `core.h` for `struct ath11k_base` and expects `ab->hif.ops` to be initialized before wrappers are used. It depends on bus-specific implementations to satisfy mandatory operations like read32/write32/start/stop/IRQ control and service mapping.

## Risks
Mandatory wrappers do not null-check all operations. If a bus backend fails to populate required functions, callers can crash. Optional fallbacks are intentionally permissive, which can hide missing suspend/resume or MSI behavior until runtime. Register read/write wrappers provide no synchronization; callers must use the correct ordering and locking. Incorrect service-to-pipe mapping breaks HTC/WMI/HTT traffic even if boot otherwise succeeds.

## Test signals
Boot on every supported bus is the main test. Signals include successful power-up/start, firmware boot, HTC target ready, service-to-pipe mappings for WMI/HTT, working interrupts/MSI, suspend/resume, debugfs memory reads, coredump download, and clean shutdown. Compile coverage should include all bus backends that instantiate `ath11k_hif_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.c

## Purpose
`htc.c` implements the ath11k HTC host-target control protocol over copy engine pipes. HTC wraps SKBs with endpoint headers, manages endpoint credit flow, receives control responses on endpoint 0, connects WMI/HTT services to target-assigned endpoints, handles HTC trailers/credit reports, and dispatches RX/TX completions to endpoint callbacks.

## Important APIs and functions
Exported APIs are `ath11k_htc_alloc_skb()`, `ath11k_htc_send()`, `ath11k_htc_tx_completion_handler()`, `ath11k_htc_rx_completion_handler()`, `ath11k_htc_wait_target()`, `ath11k_htc_connect_service()`, `ath11k_htc_start()`, and `ath11k_htc_init()`.

Important internal helpers include `ath11k_htc_prepare_tx_skb()` for header construction and sequence numbering, `ath11k_htc_process_credit_report()` and `ath11k_htc_process_trailer()` for trailer records, `ath11k_htc_suspend_complete()` and wakeup handling for suspend messages, `htc_service_name()` for diagnostics, endpoint reset/credit allocation helpers, and `ath11k_htc_build_tx_ctrl_skb()` for aligned EP0 control messages.

## Control flow
Initialization sets up the endpoint table, decides WMI endpoint count from preferred hardware mode, and connects the pseudo control service on EP0. During boot, `ath11k_htc_wait_target()` waits for a READY message delivered by RX completion; on timeout it services CE engines once and waits again. It parses credit count/size, validates them, applies a shadow-register special case, and divides credits among WMI control endpoints.

`ath11k_htc_connect_service()` either handles the pseudo control endpoint locally or sends an EP0 connect-service request, waits for a connect response, validates response id/status/eid/max size, fills endpoint state, maps service id to UL/DL pipes through HIF, and disables credit flow for non-WMI control services or hardware without credit flow. `ath11k_htc_start()` sends setup-complete-extended, setting the global disable-credit-flow flag when needed.

`ath11k_htc_send()` pushes an HTC header, optionally consumes endpoint credits under `tx_lock`, DMA maps the SKB, submits it to CE, and reverts DMA/credits/header on error. RX completion validates endpoint and payload length, processes trailers and credits, handles EP0 control/suspend/wakeup messages, otherwise invokes the endpoint RX callback and polls TX completion for interrupt-disabled CEs.

## State and persistence
Mutable state lives in `struct ath11k_htc`: endpoint array, `tx_lock`, control response buffer/length, completion, total credits, service allocation table, target credit size, and WMI endpoint count. Each endpoint persists service id, pipe ids, callbacks, max message sizes/depth, sequence number, credits, and credit-flow enable state. There is no disk persistence.

## Dependencies and integration
HTC depends on `debug.h`, `hif.h`, CE send/poll/service functions, DMA mapping APIs, SKB control block fields, completions, spinlocks, and `ab->hw_params`/WMI hardware mode. CE pipe tables call HTC RX/TX completion handlers. WMI and DP/HTT connect services through this layer, allocate HTC SKBs, and send messages through endpoint ids returned by service connection.

## Risks
Credit accounting is correctness-critical: underflow blocks sends, over-crediting can overrun target buffers, and only WMI control services keep credit flow enabled. EP0 control uses a single completion and shared response buffer, so connect/wait operations must remain serialized. Trailer parsing validates lengths but relies on target-provided data. The credit-report length warning says "too long" when checking too short, which is diagnostic drift. On `ath11k_htc_wait_target()`, the return value of `ath11k_htc_setup_target_buffer_assignments()` is ignored, so invalid WMI endpoint count would not immediately fail there. DMA mapping failure and CE send failure paths correctly restore credits/header, which is a key safety property.

## Test signals
Boot should show target ready with valid credits, successful WMI/HTT service connection, mapped UL/DL pipes, and setup complete. Runtime tests should include WMI command traffic, HTT data service traffic, credit starvation/replenishment behavior, suspend complete/NACK handling, wakeup events, DMA error injection if available, and CE interrupt-disabled poll paths. Warnings about invalid EID, invalid trailer length, service connect timeout, or HTC control reentrancy are high-value failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.h

## Purpose
`htc.h` defines the public HTC protocol contract for ath11k: wire headers, control message formats, service ids, endpoint ids, credit trailer records, service connection request/response structs, endpoint state, global HTC state, constants, and exported HTC APIs.

## Important APIs, types, and data
The wire header is `struct ath11k_htc_hdr`, with bit masks for endpoint id, flags, payload length, control bytes, and reserved bits. Message structs include READY, READY extended, connect service, connect service response, setup complete extended, generic HTC message, record header, credit report, and trailer record.

Enums define HTC message ids, protocol versions, connection flags/status codes, record ids, service groups, service ids, and endpoint ids. Notable services are reserved control, WMI control/data, WMI MAC1/MAC2 control, NMI, HTT data, IPA TX, packet log, and test raw streams.

`struct ath11k_htc_ep_ops` supplies endpoint callbacks for TX complete, RX complete, and credit availability. `struct ath11k_htc_svc_conn_req` and `struct ath11k_htc_svc_conn_resp` define the service connection API. `struct ath11k_htc_ep` persists per-endpoint service/callback/pipe/credit state. `struct ath11k_htc` owns all endpoint state, control response synchronization, credit allocation table, target credit size, and WMI endpoint count.

Declared APIs initialize HTC, wait for target READY, start HTC setup-complete, connect services, send SKBs, allocate HTC SKBs, and handle CE RX/TX completions.

## Control flow and integration
The header has no executable flow, but its declarations define the lifecycle implemented in `htc.c`: initialize endpoint state, wait for target ready, connect services over EP0, start the HTC session, send framed SKBs over CE pipes, receive framed SKBs, process trailers, and dispatch endpoint callbacks. CE uses the completion handler prototypes, while WMI/DP use service connection and send APIs.

## State and persistence
All persistent HTC runtime state is in `struct ath11k_htc` and its endpoint array. Credit counts and sequence numbers change as messages are sent and target credit reports arrive. Control responses are transiently stored in a fixed buffer guarded by a completion. No state is persisted to disk.

## Dependencies
The header includes kernel list/bug/SKB/timer headers and relies on `struct ath11k_base`. Implementations depend on HIF service-to-pipe mapping, CE transport, DMA mapping, completions, and `ab->hw_params.credit_flow`. Consumers must respect `ATH11K_HTC_MAX_LEN`, max control message length, endpoint count, and timeout constants.

## Risks
HTC wire layout and bit masks must match firmware exactly. Endpoint ids are small and `ATH11K_HTC_EP_UNUSED` is negative, so signed/unsigned handling matters. The fixed control response buffer requires response bounds checks in implementation. Credit-flow flags are per endpoint and must be matched with target service allocation. Callback pointers must be initialized before non-control RX/TX traffic is possible.

## Test signals
Compile coverage should catch API drift across WMI, DP, CE, and core. Runtime signals include target READY parsing, expected credit size/count, successful service connect responses, correct endpoint ids and max message lengths, credit reports waking blocked senders, EP0 suspend/wakeup handling, and stable WMI/HTT traffic without invalid endpoint or trailer warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.h -->
