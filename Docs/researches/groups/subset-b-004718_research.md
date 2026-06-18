# Research: subset-b-004718

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_rx.c

## Purpose

`htt_rx.c` implements the target-to-host side of ath10k HTT. It owns low-latency RX ring allocation/refill, in-order physical-address RX delivery, high-latency SDIO/USB-style RX indications, RX descriptor decoding, decapsulation back into mac80211 frame formats, HTT event dispatch, TX completion demultiplexing, peer/TID security replay tracking, peer TX statistics ingestion, and the NAPI completion task that drains RX/TX work.

## Important APIs, Types, and Functions

- RX ring lifecycle: `ath10k_htt_rx_alloc()`, `ath10k_htt_rx_ring_refill()`, `ath10k_htt_rx_free()`, `ath10k_htt_rx_ring_free()`.
- RX buffer ownership helpers: `ath10k_htt_rx_netbuf_pop()`, `ath10k_htt_rx_amsdu_pop()`, `ath10k_htt_rx_pop_paddr()`, `ath10k_htt_rx_pop_paddr32_list()`, `ath10k_htt_rx_pop_paddr64_list()`.
- Frame metadata and decapsulation: `ath10k_htt_rx_h_ppdu()`, `ath10k_htt_rx_h_rates()`, `ath10k_htt_rx_h_channel()`, `ath10k_htt_rx_h_mpdu()`, `ath10k_htt_rx_h_undecap_*()`, `ath10k_htt_rx_h_csum_offload()`.
- Delivery paths: `ath10k_htt_rx_handle_amsdu()` for classic low-latency RX, `ath10k_htt_rx_in_ord_ind()` for in-order paddr indications, and `ath10k_htt_rx_proc_rx_ind_hl()` / `ath10k_htt_rx_proc_rx_frag_ind_hl()` for high-latency buses.
- HTT event dispatch: `ath10k_htt_t2h_msg_handler()` and wrapper `ath10k_htt_htc_t2h_msg_handler()`.
- Completion/statistics: `ath10k_htt_rx_tx_compl_ind()`, `ath10k_htt_rx_tx_fetch_ind()`, `ath10k_htt_rx_tx_mode_switch_ind()`, `ath10k_htt_fetch_peer_stats()`, `ath10k_fetch_10_2_tx_stats()`.
- Poll entry points: `ath10k_htt_rx_hl_indication()` and `ath10k_htt_txrx_compl_task()`.
- Operation selector: `ath10k_htt_set_rx_ops()` installs 32-bit, 64-bit, or high-latency RX ops.

## Control Flow

RX setup allocates a coherent paddr ring and shadow firmware index, initializes `netbufs_ring`, `skb_table`, queues, timer, and counters. Refill allocates aligned SKBs, clears descriptor attention flags, DMA maps each buffer, writes the physical address into the 32-bit or 64-bit ring, optionally hashes the SKB by paddr for in-order RX, then publishes the new alloc index after a memory barrier.

Classic low-latency firmware first sends RX indications that increment `num_mpdus_ready`. `ath10k_htt_txrx_compl_task()` drains queued mac80211 RX frames, processes in-order indications, then repeatedly calls `ath10k_htt_rx_handle_amsdu()` while MPDUs are ready. That handler pops all MSDUs in one A-MSDU, decodes PPDU status, optionally unchains multi-buffer raw MSDUs, filters invalid/no-channel/CAC frames, reconstructs 802.11 frames from firmware decap formats, queues MSDUs, updates station RX stats, and lets the NAPI task deliver them through `ieee80211_rx_napi()`.

In-order RX indications contain physical addresses and optional offload metadata. `ath10k_htt_rx_in_ord_ind()` validates the event, pops matching SKBs from the hash table, handles offloaded frames separately, extracts complete A-MSDUs from the list, then reuses the PPDU/filter/MPDU/enqueue pipeline. Any paddr-pop or A-MSDU extraction inconsistency marks `htt->rx_confused` and forces poll rescheduling.

High-latency RX receives the complete packet in the HTT indication SKB rather than the low-latency host ring. `ath10k_htt_t2h_msg_handler()` queues RX indications for later polling; `ath10k_htt_rx_hl_indication()` calls `ath10k_htt_rx_proc_rx_ind_hl()`, which strips HTT/firmware descriptor headers, derives signal/channel/status flags, synthesizes QoS control when required, reconstructs IV headers for PN checking cases, and delivers directly to mac80211. Fragment indications first decapsulate WEP/TKIP/CCMP headers, enforce unicast/no-retry/PN sequence checks, then pass through the same high-latency RX indication handler.

The HTT dispatcher maps firmware message IDs through `ar->htt.t2h_msg_types`, then handles version confirmation, peer map/unmap, management/data TX completions, security indications, RX fragment and in-order queues, ADD BA/DEL BA offload notifications, channel changes, TX fetch requests, mode-switch events, peer stats, pktlog, and unhandled-event warnings. It returns whether the caller should free the event SKB; queued RX/fetch paths retain ownership.

## State and Persistence Behavior

Persistent driver state is in `struct ath10k_htt` and peer/station objects, not on disk. Key mutable state includes `rx_ring.fill_cnt`, `rx_ring.sw_rd_idx`, `rx_ring.alloc_idx.vaddr`, `rx_ring.netbufs_ring`, `rx_ring.skb_table`, `rx_confused`, `rx_msdus_q`, `rx_in_ord_compl_q`, `rx_indication_head`, `tx_fetch_ind_q`, `num_mpdus_ready`, `txdone_fifo`, `rx_status`, and per-peer PN arrays. RX security indications update `peer->rx_pn[]` and clear PN history. TX completion handling updates pending TX references and station airtime/rate statistics.

DMA state is carefully paired: posted RX buffers are mapped `DMA_FROM_DEVICE` and unmapped when popped or freed; coherent rings and shadow indices are freed at RX teardown. The refill timer persists across memory pressure and reschedules until the desired fill level is restored. `rx_confused` is a sticky in-memory failure flag that prevents further RX pop work after ring corruption is detected.

## Dependencies and Integration Points

This file depends on ath10k core, HTC, HTT protocol structs, mac80211, WMI peer state, rx descriptor ops from hardware parameters, DMA APIs, SKB queues, ID/hash helpers, NAPI, tracepoints, and debug logging. It integrates with mac80211 via `ieee80211_rx_napi()`, BA session offload callbacks, TXQ scheduling, airtime registration, and rate/status update APIs. It integrates with firmware through HTT target-to-host messages and the host-populated RX paddr ring configured by `htt_tx.c`.

## Risks

- Descriptor and SKB pointer arithmetic is extensive. Incorrect `rx_desc_ops` offsets, decap alignment, or malformed firmware lengths can corrupt frame reconstruction or trigger drops.
- The RX ring can enter `rx_confused` on unexpected empty pops, incomplete descriptors, or paddr mismatches; recovery is limited to refusing further processing, with comments suggesting firmware restart may be needed.
- Replay checks are split between low-latency fragments and high-latency indications. Any peer/TID/security indication ordering bug can reject valid fragments or accept stale PN state.
- Some event handlers only warn on unexpected firmware structures, such as multiple HL MPDU ranges, unsupported TX inspect events, or malformed TX fetch records.
- `rx_status` is reused across frames/PPDUs and must be reset in precise places to avoid leaking stale rate/channel flags.
- TX completion RSSI/PPDU-duration parsing depends on optional padding and firmware flags; offset mistakes could misread completion payloads.

## Test Signals

Useful tests include RX ring allocation/refill/free under DMA mapping failure, RX under memory pressure and refill timer retry, malformed HTT event length checks, raw/native-wifi/ethernet/SNAP decapsulation cases, encrypted A-MSDU and fragmented CCMP/TKIP replay cases, in-order paddr RX on 32-bit and 64-bit targets, HL RX delivery with and without RSSI/channel, TX completion FIFO overrun behavior, TX fetch scheduling in push-pull mode, peer map/security indication ordering, and pktlog/peer stats parsing for legacy/HT/VHT rates. Runtime signals are `ath10k_warn()` ring corruption messages, `rx_crc_err_drop`, station RX/TX stats, tracepoints `trace_ath10k_htt_rx_desc`, `trace_ath10k_rx_hdr/payload`, `trace_ath10k_htt_stats`, and NAPI budget behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_tx.c

## Purpose

`htt_tx.c` implements host-to-target HTT setup and transmit submission. It allocates and frees TX descriptor memory, maintains pending MSDU IDs and pending-count backpressure, configures RX rings and fragment descriptor banks in firmware, sends HTT control commands, builds management/data TX commands for 32-bit, 64-bit, and high-latency targets, and supports firmware peer-flow-control TX fetch mode.

## Important APIs, Types, and Functions

- TXQ state: `ath10k_htt_tx_txq_recalc()`, `ath10k_htt_tx_txq_sync()`, `ath10k_htt_tx_txq_update()`, and internal `ath10k_htt_tx_txq_calc_size()`.
- Pending accounting: `ath10k_htt_tx_inc_pending()`, `ath10k_htt_tx_dec_pending()`, `ath10k_htt_tx_mgmt_inc_pending()`, `ath10k_htt_tx_mgmt_dec_pending()`, `ath10k_htt_tx_alloc_msdu_id()`, `ath10k_htt_tx_free_msdu_id()`.
- Memory lifecycle: `ath10k_htt_tx_start()`, `ath10k_htt_tx_destroy()`, `ath10k_htt_tx_stop()`, `ath10k_htt_tx_free()`, plus 32/64-bit txbuf and frag-desc alloc/free helpers.
- HTT commands: `ath10k_htt_h2t_ver_req_msg()`, `ath10k_htt_h2t_stats_req()`, `ath10k_htt_send_frag_desc_bank_cfg_*()`, `ath10k_htt_send_rx_ring_cfg_*()`, `ath10k_htt_h2t_aggr_cfg_msg_*()`, `ath10k_htt_tx_fetch_resp()`.
- TX submission: `ath10k_htt_mgmt_tx()`, `ath10k_htt_tx_hl()`, `ath10k_htt_tx_32()`, `ath10k_htt_tx_64()`.
- Operation selector: `ath10k_htt_set_tx_ops()` chooses high-latency, 32-bit, or 64-bit function table.

## Control Flow

Startup initializes `tx_lock` and `pending_tx`, skips descriptor allocation on high-latency buses, then allocates contiguous TX command buffers, optional continuous fragment descriptor banks, optional peer-flow-control TXQ state, and `txdone_fifo`. Teardown stops HTC HL traffic, force-completes all pending IDs with discard status, destroys the IDR, frees DMA/coherent buffers, unmaps TXQ state, and releases the completion FIFO.

Transmit pending accounting is lock-protected. When `num_pending_tx` reaches `max_num_pending_tx`, mac80211 TX is paused with `ATH10K_TX_PAUSE_Q_FULL`; dropping below the limit unlocks TX. Management probe responses are separately limited by `max_probe_resp_desc_thres`.

RX ring and fragment descriptor configuration commands are built as HTT H2T SKBs and sent through HTC. Ring setup fills firmware-visible ring base, firmware shadow index address, ring length, buffer size, descriptor offset table, and RX flags selecting MAC header, payload, PPDU/MPDU/MSDU descriptor sections, and RX classes. High-latency ring setup sends a minimal config without host DMA ring addresses.

Data TX has three implementations. The high-latency path prepends an HTT command header and TX descriptor directly to the MSDU SKB, reallocating headroom if needed, optionally allocating an HL MSDU ID, then sends with `ath10k_htc_send_hl()`. The 32-bit and 64-bit low-latency paths allocate an MSDU ID, append crypto MIC space for protected management/raw frames where firmware expects it, DMA-map the payload, fill a per-ID TX command buffer and fragment pointer, optionally use continuous fragment descriptor memory, set vdev/TID/checksum/offchannel flags, then bypass normal HTC TX by sending two SG items through `ath10k_hif_tx_sg()`: the prebuilt HTC+HTT header and a prefetch slice of the payload. Completion from `htt_rx.c` releases the ID and unmaps/free resources through txrx unref logic.

Peer-flow-control mode keeps a DMA-mapped shared queue-state table. TXQ depth is encoded as exponent/factor byte values, per-peer/TID bitmap bits mark non-empty queues, and sync increments a sequence number followed by `dma_sync_single_for_device()`. Firmware TX fetch indications are handled in `htt_rx.c`, which calls back into `ath10k_htt_tx_fetch_resp()`.

## State and Persistence Behavior

State is in memory under `struct ath10k_htt`: `pending_tx` IDR maps firmware MSDU IDs to SKBs, `num_pending_tx` and `num_pending_mgmt_tx` drive flow control, `txbuf` and `frag_desc` hold coherent TX descriptor banks, `tx_q_state` holds peer-flow-control metadata and a DMA address, `txdone_fifo` queues completions, and `tx_mem_allocated` prevents duplicate allocation. SKB control blocks persist DMA addresses until completion. No file-backed persistence exists.

## Dependencies and Integration Points

This file depends on HTC allocation/send APIs, HIF scatter-gather transmit, mac80211 TXQ APIs and TX control flags, ath10k MAC flow-control helpers, firmware feature bits, hardware params, DMA APIs, IDR, kfifo, and HTT protocol definitions. It integrates with `htt_rx.c` for TX completions, TX fetch requests, RX ring configuration, and selected operation tables. It integrates with firmware through H2T HTT messages and target-specific 32/64-bit descriptor layouts.

## Risks

- TX resource lifetime spans IDR entries, DMA mappings, SKBs, HTT completions, and optional HTC completions. Missing unmap/free on an error path would leak or double-release.
- 32-bit and 64-bit descriptor formats are parallel but not identical; continuous fragment descriptors and checksum offload flags differ.
- High-latency TX intentionally shares SKB ownership between mac80211 and HTC completion by taking an extra reference; regressions here can cause use-after-free or leaks.
- Management frame MIC padding is added based on protected/action/deauth/disassoc detection and cipher assumptions.
- TXQ shared-state writes require correct locking and DMA sync; stale sequence/count/map values can stall firmware fetch scheduling.
- RX ring config assumes coherent RX ring allocation already succeeded and that descriptor offset ops match the target hardware.

## Test Signals

Good coverage includes allocation failure at every TX buffer stage, DMA mapping failures, max pending TX lock/unlock transitions, management probe-response threshold behavior, protected management and raw frame MIC padding, 32-bit vs 64-bit SG descriptor contents, high-latency headroom reallocation, checksum offload flag emission, offchannel frequency field handling, peer-flow-control TXQ count/map/sequence updates, RX ring config command contents, fragment descriptor bank config with and without firmware peer-flow-control feature, and teardown with pending SKBs. Runtime signals include `trace_ath10k_htt_tx`, `trace_ath10k_tx_hdr/payload`, TX pause state, `txdone_fifo` warnings from RX completion, and HTT command send errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.c

## Purpose

`hw.c` supplies target-specific hardware tables and hardware operations for ath10k. It defines register base maps, Copy Engine register layouts, common per-chip values, QCA6174 clock parameters, survey counter conversion, coverage-class register programming, QCA6174 PLL bring-up, segmented firmware download through diagnostic access, and small operation hooks for HTT TX completion RSSI parsing.

## Important APIs, Types, and Functions

- Exported tables: `qca988x_regs`, `qca6174_regs`, `qca99x0_regs`, `qca4019_regs`, `wcn3990_regs`, `qca988x_values`, `qca6174_values`, `qca99x0_values`, `qca9888_values`, `qca4019_values`, `wcn3990_values`, `qcax_ce_regs`, `wcn3990_ce_regs`, `qca6174_clk`.
- Public functions: `ath10k_hw_fill_survey_time()` and `ath10k_hw_diag_fast_download()`.
- Hardware ops tables: `qca988x_ops`, `qca99x0_ops`, `qca6174_ops`, `qca6174_sdio_ops`, `wcn3990_ops`.
- Internal operations: `ath10k_hw_qca988x_set_coverage_class()`, `ath10k_hw_qca6174_enable_pll_clock()`, `ath10k_hw_map_target_mem()`, `ath10k_hw_diag_segment_msb_download()`, `ath10k_hw_diag_segment_download()`.

## Control Flow

Most of the file is static data consumed during device matching and bus setup. Register maps provide per-chip base addresses and interrupt masks. Value tables provide CE counts, MSI assignment limits, descriptor metadata masks, RTC state constants, and optional RFKill GPIO defaults. CE register structures describe how HIF code should program source/destination rings, watermarks, misc error interrupts, host interrupt enable bits, and command halt fields for qcax-style targets and WCN3990.

`ath10k_hw_fill_survey_time()` receives current and previous cycle counters, compensates for chip-specific wraparound behavior, marks survey time fields, and converts counts to milliseconds using `CCNT_TO_MSEC()`. For the shifted-all wraparound type, a wrap in the primary cycle counter suppresses busy-time reporting because relative busy time cannot be trusted.

`ath10k_hw_qca988x_set_coverage_class()` runs under `conf_mutex`, stores the requested coverage class if firmware is not started, otherwise reads MAC slot/ACK/CTS/PHY clock registers, verifies expected slot-time units, recalculates propagation-delay-adjusted register values, writes them through HIF, and raises firmware debug logging to WARN level when coverage class is nonzero so firmware resets can be noticed and corrected.

`ath10k_hw_qca6174_enable_pll_clock()` is a strict BMI register/memory sequence. It validates clock register addresses, reads efuse-selected reference clock index, programs PLL fraction/outdiv/settle/div/refdiv/nopwd/bypass bits, busy-waits for RTC sync twice, enables standard CPU clock, powers down PLL control bits as required, writes target clock init memory, and finally writes the target CPU frequency.

`ath10k_hw_diag_fast_download()` parses a segmented BMI firmware image. It validates magic and flags, iterates metadata records, sets start addresses, rejects unsupported BDDATA/EXEC markers, checks segment sizes, and writes each segment either directly through `ath10k_hif_diag_write()` or through `ath10k_hw_diag_segment_msb_download()` when a target address crosses the 1 MiB diagnostic window. The MSB mapper is reset to DRAM after special-region writes.

RSSI helper ops inspect HTT TX completion flags. WCN3990 uses different RSSI enable and padding bits, so it has a separate `wcn3990_ops` table.

## State and Persistence Behavior

The exported tables are immutable compile-time configuration. Runtime mutations are limited to `ar->fw_coverage` cache fields, survey output fields, firmware debug log settings, HIF/BMI target registers, and diagnostic memory writes. PLL and diag download operations affect target hardware/firmware boot state but do not persist on the host filesystem.

## Dependencies and Integration Points

This file depends on `core.h`, `hw.h`, HIF register access, WMI debug-log ops, BMI register/memory access, firmware segmented image definitions, and RX descriptor abstractions. Its data is consumed by bus drivers, CE setup, firmware download, reset/boot code, survey reporting, HTT TX completion parsing, and mac80211 coverage class handling through `hw_ops`.

## Risks

- Hardware tables are trusted constants. An incorrect base address, mask, CE count, or interrupt bit silently misprograms the device.
- Coverage-class programming bypasses firmware and assumes wave1 register layout and slot-time values; unexpected firmware register changes are only partially guarded.
- PLL bring-up uses a sensitive ordered sequence and busy-wait timeout. Refactoring or changing masks can produce boot failures that are hard to diagnose.
- Diagnostic fast download must split across 1 MiB windows correctly and restore the CPU address MSB. Truncated or malformed segmented images are rejected, but target writes are irreversible within a boot attempt.
- RSSI completion padding depends on firmware flags matching the completion layout used by `htt_rx.c`.

## Test Signals

Important tests include per-chip register/value table selection, CE setup register programming for qcax and WCN3990 layouts, survey time wraparound cases for all three wrap modes, coverage class when device is off vs on/restarted, invalid slot/phy clock register reads, QCA6174 PLL efuse index bounds and busy-wait timeout paths, segmented firmware images with begin/done/unsupported/truncated/oversized/cross-window records, and HTT TX RSSI flag/padding interpretation for WCN3990 vs non-WCN3990. Runtime signals include boot debug messages, coverage-class warnings, BMI/HIF write failures, survey time fields, and firmware download success/failure logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.h

## Purpose

`hw.h` is the central ath10k hardware contract header. It declares bus and hardware revision identities, firmware and board file naming constants, firmware/board IE formats, per-chip register/value structures, hardware parameter structures, operation hooks, target resource constants, register-address macros, and low-level bit masks used by bus, boot, HTT, WMI, LED, RFKill, survey, and diagnostic code.

## Important APIs, Types, and Declarations

- Hardware identity: `enum ath10k_bus`, `enum ath10k_hw_rev`, QCA/WCN device IDs, chip revision enums, firmware directory/version macros.
- Firmware formats: `struct ath10k_fw_ie`, `enum ath10k_fw_ie_type`, `enum ath10k_fw_wmi_op_version`, `enum ath10k_fw_htt_op_version`, board IE enums.
- Register/value tables: `struct ath10k_hw_regs`, `struct ath10k_hw_values`, `struct ath10k_hw_ce_*`, extern declarations for `qca*` and `wcn3990` tables.
- Runtime parameters: `struct ath10k_hw_params` captures feature flags, firmware directory/board sizes, RX descriptor ops, hardware ops, target capacities, descriptor mode, checksum/ring parameters, SAR/restart behavior, and bus quirks.
- Operation hooks: `struct ath10k_hw_ops` plus inline wrappers `ath10k_tx_data_rssi_get_pad_bytes()` and `ath10k_is_rssi_enable()`.
- Public functions: `ath10k_hw_fill_survey_time()` and `ath10k_hw_diag_fast_download()`.
- Macros: `QCA_REV_*()`, target resource constants for MAIN/10.x/TLV/HL/10.4 firmware, CE/MSI constants, register base/address/mask aliases, PLL masks, coverage-class registers, and diagnostic CPU address window helpers.

## Control Flow

This header has no executable control flow beyond two inline wrappers. It shapes control flow elsewhere by letting device match code populate `ar->hw_params`, `ar->regs`, and `ar->hw_values`, after which generic code accesses hardware through common macros such as `RTC_SOC_BASE_ADDRESS`, `CE_COUNT`, `PCIE_INTR_CE_MASK_ALL`, and `CCNT_TO_MSEC()`. Optional operations are called only when function pointers are non-NULL; missing RSSI hooks return zero.

The target-resource macros define firmware configuration payload sizes and limits sent by WMI startup code. The revision macros gate chip-specific code paths. The register macros abstract per-chip base addresses by expanding through `ar->regs`, while legacy/MBOX aliases preserve compatibility with older code using pre-ath10k naming.

## State and Persistence Behavior

The header defines state layouts but does not allocate persistent state. `struct ath10k_hw_params` instances persist per device in memory and drive feature behavior for the lifetime of the driver instance. Extern tables are read-only constants defined in `hw.c` or other compilation units. Macro reads depend on live `ar->regs`, `ar->hw_values`, and `ar->hw_params` pointers.

## Dependencies and Integration Points

`hw.h` depends on `targaddrs.h` and forward declarations for HTT and RX descriptor structs. It is included across ath10k core, bus, HTC/HTT, WMI, debug, firmware-loading, and hardware-control code. Its definitions connect firmware image parsing to loader code, hardware tables to bus register programming, target resource counts to WMI init, and HTT descriptor/RSSI behavior to RX/TX completion logic.

## Risks

- Many macros assume an `ar` variable is in scope, which is convenient but fragile for refactors.
- `QCA9377_1_0_DEVICE_ID` shares value with `QCA6174_3_2_DEVICE_ID`; callers must disambiguate by other context.
- `MISSING` placeholder aliases expand to zero and can be dangerous if used on unsupported paths.
- `struct ath10k_hw_params` is broad and feature-dense; adding a field requires auditing all hardware table initializers for correct defaults.
- Target constants encode firmware resource contracts. Mistakes can cause startup failures, peer/TID exhaustion, descriptor pool pressure, or mismatched firmware expectations.
- Register address macros mix absolute constants and table-derived addresses; using the wrong family path can silently program the wrong location.

## Test Signals

Tests should compile all bus/config combinations, validate hardware table initializers against `struct ath10k_hw_params` changes, exercise each `QCA_REV_*()` branch, verify WMI target resource payloads for MAIN/10.x/TLV/HL/10.4, confirm optional hw_ops wrappers with NULL/non-NULL callbacks, assert diagnostic window mask math, and catch accidental use of `MISSING` register aliases on active code paths. Build warnings, sparse/clang diagnostics, boot-time register access failures, and firmware startup resource errors are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.c

## Purpose

`leds.c` implements optional Linux LED class integration for ath10k devices with a firmware-controlled GPIO LED pin. It registers a per-wiphy LED class device, configures the target GPIO at start, and translates brightness changes into WMI GPIO output commands.

## Important APIs, Types, and Functions

- `ath10k_leds_register()` creates the LED name `ath10k-<wiphy>`, sets active-low/default-state metadata, assigns `brightness_set_blocking`, and registers `ar->leds.cdev`.
- `ath10k_leds_start()` configures `hw_params.led_pin` through WMI GPIO config/output, used after firmware start or restart.
- `ath10k_leds_unregister()` unregisters the LED class device.
- `ath10k_leds_set_brightness_blocking()` is the LED core callback and writes GPIO output when the device is ON.

## Control Flow

All public functions no-op when `ar->hw_params.led_pin == 0`, treating zero as unsupported. Registration fills label and `gpio_led`/`led_classdev` fields, then calls `led_classdev_register()` on the wiphy device. Start reconfigures the GPIO with no pull and disabled interrupt, then writes output high; comments note firmware can reset GPIO configuration, especially on QCA9984/QCA99XX. Brightness changes acquire `conf_mutex`, ignore requests unless the device state is `ATH10K_STATE_ON`, compute active-low GPIO state as `(brightness != LED_OFF) ^ active_low`, store it in `ar->leds.gpio_state_pin`, and call `ath10k_wmi_gpio_output()`.

## State and Persistence Behavior

State lives in `ar->leds`: label buffer, `wifi_led` metadata, `cdev`, and last `gpio_state_pin`. Registration persists with the LED subsystem until unregister. GPIO configuration persists in target firmware/hardware only until firmware or device reset, so `ath10k_leds_start()` reapplies it after start paths. No disk persistence exists.

## Dependencies and Integration Points

The file depends on Linux LED class APIs, wiphy device naming, ath10k core state, WMI GPIO config/output commands, and `hw_params.led_pin`. It is compiled only when `CONFIG_ATH10K_LEDS` enables the declarations in `leds.h`. It integrates with driver start/stop paths that call register/start/unregister.

## Risks

- LED support is keyed on `led_pin == 0`, so hardware using GPIO 0 as a valid LED would be impossible without changing the sentinel.
- Brightness writes while the device is not ON are silently ignored; callers rely on later start/reconfiguration to restore state.
- `ath10k_leds_start()` ignores return values from WMI GPIO operations and always returns success.
- Active-low is hard-coded to 1 in registration; board-specific polarity must be represented elsewhere or this may invert behavior.

## Test Signals

Useful tests include `CONFIG_ATH10K_LEDS=y/n` builds, register/start/unregister with `led_pin == 0`, LED class registration failure propagation, brightness OFF/non-OFF transitions with active-low polarity, writes ignored when `ar->state` is not ON, firmware restart calling `ath10k_leds_start()`, and WMI GPIO command tracing to confirm pin/config/output values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.h

## Purpose

`leds.h` declares the optional ath10k LED integration API and provides no-op inline fallbacks when LED support is disabled. It lets the rest of the driver call LED registration/start/unregistration unconditionally.

## Important APIs, Types, and Functions

- With `CONFIG_ATH10K_LEDS`: declares `ath10k_leds_unregister(struct ath10k *ar)`, `ath10k_leds_start(struct ath10k *ar)`, and `ath10k_leds_register(struct ath10k *ar)`.
- Without `CONFIG_ATH10K_LEDS`: defines inline no-op `ath10k_leds_unregister()` and inline success-returning `ath10k_leds_start()` / `ath10k_leds_register()`.
- Includes `core.h` for `struct ath10k`.

## Control Flow

The only control flow is compile-time. The preprocessor selects real declarations when LED support is enabled and inline stubs otherwise. Runtime callers do not need their own `#ifdef CONFIG_ATH10K_LEDS` guards.

## State and Persistence Behavior

The header has no state. In the disabled configuration, no LED state is allocated or registered by these functions. In the enabled configuration, state is managed by `leds.c` through `ar->leds`.

## Dependencies and Integration Points

This header is included by ath10k core/startup code that wants to call LED helpers independent of Kconfig. It depends on the build system providing `CONFIG_ATH10K_LEDS` and on `core.h` defining `struct ath10k` and LED-related members under the matching configuration.

## Risks

- Stub functions return success, so disabled LED support is intentionally indistinguishable from unsupported/no-op LED hardware to callers.
- Any caller expecting side effects from `ath10k_leds_start()` must remember that those effects vanish when the config is disabled.
- Header and `core.h` configuration guards must stay synchronized so `ar->leds` members are present when real functions are compiled.

## Test Signals

The main signals are successful builds with `CONFIG_ATH10K_LEDS=y` and `n`, no unresolved symbols in either mode, startup/register paths working without local `#ifdef`s, and no LED class device appearing when support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.h -->
