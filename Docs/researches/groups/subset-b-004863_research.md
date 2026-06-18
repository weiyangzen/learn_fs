# Research Report: subset-b-004863

This grouped report covers the requested Mediatek MT7601U and Microchip WILC1000 wireless driver files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mcu.c

Purpose: Implements MT7601U MCU command transport, firmware loading, firmware DMA upload, and high-level MCU operations used by PHY calibration and register programming. It is the bridge between normal driver code and firmware-managed operations such as random/burst register writes, calibration, TSSI kicks, queue selection, and firmware startup.

Important APIs and functions: `mt7601u_mcu_init()` initializes the MCU path by loading firmware and setting `MT7601U_STATE_MCU_RUNNING`. `mt7601u_mcu_cmd_init()` selects MCU queue mode, allocates/submits the command response URB, and prepares completions. `mt7601u_mcu_cmd_deinit()` kills and frees the response URB. `mt7601u_mcu_calibrate()` and `mt7601u_mcu_tssi_read_kick()` expose calibration and TSSI operations. `mt7601u_write_reg_pairs()` and `mt7601u_burst_write_regs()` packetize register writes through in-band MCU commands. Internal helpers include `mt7601u_mcu_msg_alloc()`, `mt7601u_mcu_msg_send()`, `mt7601u_mcu_wait_resp()`, `mt7601u_load_firmware()`, and recursive firmware upload helpers.

Control flow: Firmware load first enables USB DMA, checks if firmware is already running, requests `mediatek/mt7601u.bin` then `mt7601u.bin`, validates the header lengths, resets and primes FCE/PBF/DMA registers, uploads ILM and DLM chunks, sends the IVB by vendor request, then polls `MT_MCU_COM_REG0` for a running marker. Runtime MCU commands allocate an skb, reserve DMA header space, write payload, wrap it as a command DMA descriptor, synchronously bulk-send it to the in-band command endpoint, and optionally wait for a matching command-done response sequence. Large register write batches recurse until all values have been sent, waiting only on the final command.

State and persistence: Mutable state is in `dev->mcu`: a mutex serializes commands, `msg_seq` supplies non-zero 4-bit response sequence ids, `resp` holds the persistent response DMA buffer/URB, and `resp_cmpl` gates command completion. Device state bits `MT7601U_STATE_REMOVED` and `MT7601U_STATE_MCU_RUNNING` short-circuit operations after removal or before firmware availability. `dev->tssi_read_trig` records an outstanding TSSI measurement kick.

Dependencies and integration points: Depends on USB helpers in `usb.c`, DMA wrapping in `dma.h`, register definitions in `regs.h`/`mcu.h`, firmware loading APIs, skb helpers, and tracepoints from `trace.h`. PHY code calls calibration/TSSI/register pair APIs. USB probe and hardware init call MCU initialization and command setup. Firmware upload relies on FCE DMA registers and vendor control transfers.

Risks: Firmware validation is length based and assumes the packed firmware layout matches `struct mt76_fw`; bad metadata rejects the image but subtle content corruption may only fail at runtime. Recursive upload and write helpers are small bounded recursions, but error paths must preserve buffer cleanup. MCU response handling depends on completion state and exact sequence matching; stale completions or wrong firmware event types cause retries/timeouts. Removal returns success for some sends to avoid teardown faults, so callers must not treat success after removal as completed hardware work.

Test signals: Probe with firmware present and absent, suspend/resume, command timeout paths, invalid firmware length/header tests, tracepoint observation of `mt_mcu_msg_send`, USB bulk errors, TSSI/calibration calls from PHY, and register-pair batches above `INBAND_PACKET_MAX_LEN` are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mcu.h

Purpose: Defines the MT7601U MCU register addresses, memory map bases, command ids, function ids, power modes, calibration ids, and exported MCU helper prototypes. It is the contract between firmware command construction in `mcu.c` and call sites such as PHY calibration.

Important APIs and types: `enum mcu_cmd` maps in-band firmware command types such as `CMD_FUN_SET_OP`, `CMD_BURST_WRITE`, `CMD_RANDOM_WRITE`, and `CMD_CALIBRATION_OP`. `enum mcu_function` defines function-select ids used by queue selection and TSSI setup. `enum mcu_calibrate` names calibration operations including R, DCOC, LOFT, TXIQ, RXIQ, TXDCOC, BW, and DPD. Constants such as `MT_MCU_IVB_SIZE`, `MT_MCU_DLM_OFFSET`, `MT_MCU_MEMMAP_BBP`, and `INBAND_PACKET_MAX_LEN` control firmware upload and in-band register access.

Control flow: This header does not execute logic, but its constants drive command payload layout and maximum command chunking in `mcu.c`. `MT_MCU_MEMMAP_BBP` and `MT_MCU_MEMMAP_RF` distinguish BBP/RF write spaces passed to MCU random-write commands.

State and persistence: It declares no persistent state. Its ids are persisted indirectly in firmware-visible command packets and calibration requests.

Dependencies and integration points: Forward-declares `struct mt7601u_dev` and exports `mt7601u_mcu_init()`, `mt7601u_mcu_cmd_init()`, `mt7601u_mcu_cmd_deinit()`, `mt7601u_mcu_calibrate()`, and `mt7601u_mcu_tssi_read_kick()`. Included by `mcu.c`, `phy.c`, and any code that needs firmware-mediated operations.

Risks: Command id values are firmware ABI. Renumbering or mixing memory map bases would silently target the wrong firmware operation or hardware register space. `INBAND_PACKET_MAX_LEN` must remain consistent with firmware command parsing limits.

Test signals: Build coverage catches missing prototypes. Runtime signals include successful firmware command initialization, calibration commands, and batch register writes that honor the packet maximum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mt7601u.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mt7601u.h

Purpose: Central MT7601U driver header. It defines the primary device object, queue objects, WCID/vif/sta private data, calibration state, shared constants, register access wrappers, and cross-file prototypes for init, MAC, PHY, TX, DMA, USB-backed register access, and utilities.

Important APIs and types: `struct mt7601u_dev` is the main adapter state, combining mac80211 handles, state bits, locks, endpoint maps, MCU state, TX/RX queues, work items, EEPROM data, channel/calibration state, and statistics. `struct mt7601u_mcu`, `struct mt7601u_tx_queue`, `struct mt7601u_rx_queue`, `struct mt7601u_freq_cal`, `struct mt76_wcid`, `struct mt76_vif`, and `struct mt76_sta` are key substructures. Inline wrappers `mt76_rr()`, `mt76_wr()`, `mt76_rmw()`, `mt76_set()`, and `mt76_clear()` provide mt76-style register access over local USB vendor requests.

Control flow: This header orchestrates module boundaries by declaring the functions used across init, USB probe, PHY channel setup, TX submission/status, DMA enqueue, and utility padding. State bits such as `MT7601U_STATE_INITIALIZED`, `REMOVED`, `WLAN_RUNNING`, `MCU_RUNNING`, `SCANNING`, `READING_STATS`, and `MORE_STATS` gate execution across teardown, scanning, MCU commands, and stat polling.

State and persistence: The header documents lock ownership: `lock` for WCID tx rate, `mac_lock` for mac80211 TX status/RX paths, `tx_lock` for TX queue/stat flags, `rx_lock` for RX queue, `con_mon_lock` for beacon/RSSI connection monitoring, `mutex` for mac80211 callback exclusivity, `vendor_req_mutex` for USB control register transactions, `reg_atomic_mutex` for BBP/RF indirect register access, and `hw_atomic_mutex` for critical hardware operations. Persistent runtime state includes endpoint arrays, EEPROM parameters, average RSSI EWMA, temperature/TSSI fields, channel bandwidth, PA mode, and stats.

Dependencies and integration points: Pulls Linux USB, completion, mutex, debugfs, average, and mac80211 APIs. Includes `regs.h` for register constants. It is included by nearly every MT7601U source file and is the local equivalent of a driver-wide ABI.

Risks: Because this header centralizes locking and state, changes to fields or lock semantics have broad concurrency impact. Several arrays have hardware-sized assumptions, such as `N_WCIDS`, endpoint counts, and queue entry counts. Inconsistent state-bit transitions can break teardown, scanning, TX status, or calibration scheduling.

Test signals: Full driver build, sparse/lockdep runs, open/close with concurrent TX/RX, scan/channel changes, suspend/resume, and TX status workqueue behavior are important integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mt7601u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/phy.c

Purpose: Implements MT7601U PHY/RF/BBP access, channel switching, initial and periodic calibration, temperature compensation, TSSI power tracking, AGC tuning, RSSI calculation, bandwidth changes, and connection-based frequency calibration.

Important APIs and functions: Public exports include `mt7601u_phy_init()`, `mt7601u_wait_bbp_ready()`, `mt7601u_phy_set_channel()`, `mt7601u_phy_recalibrate_after_assoc()`, `mt7601u_phy_get_rssi()`, `mt7601u_phy_con_cal_onoff()`, `mt7601u_bbp_set_bw()`, `mt7601u_bbp_set_ctrlch()`, `mt7601u_set_rx_path()`, `mt7601u_set_tx_dac()`, `mt7601u_agc_save()`, and `mt7601u_agc_restore()`. Internal helpers handle RF/BBP indirect read/write/RMW, VCO calibration, BBP temperature tables, channel 14 fixups, RX DC calibration, TSSI measurement math, AGC reset/tune, and delayed calibration work.

Control flow: PHY init caches PA mode registers, sets initial RF frequency offset, writes central/channel/VGA init tables, runs initial calibration, and initializes delayed work. Channel changes cancel periodic calibration, lock `hw_atomic_mutex`, compute 20/40 MHz channel plan and extension side, update BBP/MAC control-channel bits, write RF/BBP settings via MCU, program TX power, run VCO/BW filter calibration, apply channel 14 fixes, save `dev->chandef`, and reschedule calibration unless scanning. Periodic `cal_work` tunes AGC, performs TSSI calibration or temperature read, applies temperature compensation and DPD recalibration as needed, then requeues. Frequency calibration consumes beacon frequency offset under `con_mon_lock`, adjusts RF register 0:12, and requeues based on thresholds.

State and persistence: Uses persistent calibration fields in `struct mt7601u_dev`: `bw`, `chan_ext_below`, `raw_temp`, `curr_temp`, `dpd_temp`, `temp_mode`, `pll_lock_protect`, `tssi_*`, `prev_pwr_diff`, `rf_pa_mode`, `agc_save`, and `freq_cal`. `reg_atomic_mutex` serializes RF/BBP indirect access; `hw_atomic_mutex` protects critical channel transitions. Connection monitor state includes `avg_rssi`, `bcn_freq_off`, `bcn_phy_mode`, and `ap_bssid`.

Dependencies and integration points: Relies on MCU calibration/register write functions, EEPROM parameters and rate power tables, init value tables, RX descriptor fields, mac80211 channel definitions, tracepoints, and MAC helpers for control-channel configuration. It is invoked from hardware initialization, cfg/mac80211 channel callbacks, association handling, scanning, and RX beacon processing.

Risks: RF/BBP register programming is hardware-sensitive; incorrect sequencing can wedge PHY or corrupt calibration. TSSI math uses vendor-derived fixed-point conversions and saturation logic, making off-by-one or signedness errors risky for TX power. Channel 14 fixup mutates EEPROM-derived CCK power table entries at runtime. Delayed work must be canceled during channel changes and teardown to avoid touching removed hardware.

Test signals: BBP readiness, channel switch across 20/40 MHz plus/minus, channel 14 operation, scan channel hopping, association-triggered recalibration, periodic calibration traces (`temp_mode`, `read_temp`, `freq_cal_*`), RSSI reporting, and removal while delayed work exists are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/regs.h

Purpose: Provides MT7601U/MT76 register offsets, bit fields, queue identifiers, SRAM/key/beacon address maps, and cipher enum values used throughout the driver. It is the hardware register contract for USB control accesses, MCU firmware upload, MAC/PHY configuration, DMA, TX/RX status, and security table programming.

Important definitions: The file covers system and power registers (`MT_ASIC_VERSION`, `MT_CMB_CTRL`, `MT_WLAN_FUN_CTRL`), interrupt and WPDMA registers, USB DMA configuration, PBF/FCE registers, RF/BBP indirect access registers, MAC address/BSSID/filter/timing/protection registers, EDCA/WMM registers, TX power/ALC registers, RX filter bits, statistics/FIFO registers, BBP memory map helpers, WCID address/key/attribute/shared-key tables, beacon SRAM base, and `enum mt76_cipher_type`.

Control flow: No executable control flow exists here, but these constants define every hardware side effect in `usb.c`, `mcu.c`, `phy.c`, MAC code, DMA code, TX status code, and key-management paths. FIELD_GET/FIELD_PREP usage in other files depends on masks in this header matching hardware layout.

State and persistence: Register values configured through these definitions persist in the device until reset, suspend, firmware reinitialization, or explicit rewrite. Security tables and beacon SRAM offsets represent persistent on-chip state for active interfaces.

Dependencies and integration points: Includes `linux/bitops.h` and is included by `mt7601u.h`, which exposes it to the whole driver. Constants are used by vendor request register reads/writes, MCU command payloads, PHY calibration, queue setup, TX status parsing, and key setup.

Risks: Register headers are high-risk for silent regressions: a wrong mask or offset can affect unrelated hardware state with little compiler feedback. Shared names across MT76 variants include comments noting variant-specific meanings, so reuse across chips must be cautious. The incomplete-looking `#define MT_TXOP_CTRL` without value is inert unless referenced but should not be used.

Test signals: Compile coverage for referenced masks, probe ASIC revision, USB DMA/FCE firmware upload, MAC address/filter programming, EDCA configuration, TX status FIFO parsing, and encryption table operation all validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.c

Purpose: Instantiates MT7601U tracepoints by defining `CREATE_TRACE_POINTS` and including `trace.h`. It is the single compilation unit that emits tracepoint storage and metadata for the driver.

Important APIs and functions: There are no callable driver functions. The important behavior is conditional inclusion guarded by `__CHECKER__`, avoiding tracepoint creation for sparse/checker contexts while normal builds instantiate all trace events declared in `trace.h`.

Control flow: Build-time only. When compiled, it expands `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` definitions into tracepoint code.

State and persistence: Tracepoint definitions create kernel tracing metadata and callsites. They do not store persistent driver state by themselves.

Dependencies and integration points: Includes `linux/module.h` and local `trace.h`. Every `trace_*` call in MT7601U source files depends on this object being linked into the module.

Risks: Multiple files defining `CREATE_TRACE_POINTS` would cause duplicate symbols; this file correctly centralizes creation. If omitted from the build, trace calls would not resolve.

Test signals: Module build/link, ftrace/perf visibility of `mt7601u:*` events, and sparse builds with `__CHECKER__` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.h

Purpose: Declares MT7601U tracepoints for register access, USB URBs, MCU messages, vendor requests, EEPROM reads, RF/BBP access, temperature and frequency calibration, RX/TX descriptors, TX DMA/status, RX DMA aggregation, and key operations.

Important APIs and types: Defines reusable event classes such as `dev_reg_evtu`, `dev_rf_reg_evt`, `dev_bbp_reg_evt`, and `dev_simple_evt`. Events include `reg_read`, `reg_write`, `mt_submit_urb`, `mt_mcu_msg_send`, `mt_vend_req`, `ee_read`, `rf_read`, `rf_write`, `bbp_read`, `bbp_write`, `temp_mode`, `read_temp`, `freq_cal_adjust`, `freq_cal_offset`, `mt_rx`, `mt_tx`, `mt_tx_dma_done`, `mt_tx_status_cleaned`, `mt_tx_status`, `mt_rx_dma_aggr`, `set_key`, and `set_shared_key`.

Control flow: Tracepoints are passive callsite hooks. The header records selected arguments into trace entries with `TP_fast_assign` and formats them using `TP_printk`. `trace_mt_submit_urb_sync()` creates a stack `urb` shim to reuse the URB event for synchronous bulk transfers.

State and persistence: Trace events snapshot transient values: wiphy name, registers, descriptor fields, skb/station pointers, MCU checksum, firmware response state, and calibration values. They do not mutate driver state.

Dependencies and integration points: Includes `linux/tracepoint.h`, `mt7601u.h`, and `mac.h`; sets `TRACE_SYSTEM mt7601u`; includes `trace/define_trace.h` under the expected trace include path. Used across USB, MCU, PHY, RX, TX, EEPROM, and key code.

Risks: Tracepoint structs copy driver descriptors; changes to descriptor definitions must keep trace fields valid. The `mt_mcu_msg_send` event casts `skb->data` to `u32 *`, so callers must ensure command skb data is at least a descriptor word and aligned enough for the architecture or use-safe access. High-frequency tracing can add overhead if enabled.

Test signals: Enable each event under tracefs while exercising probe, register reads/writes, scan/channel changes, TX/RX, key setup, and calibration. Build tests catch stale field names after descriptor changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/tx.c

Purpose: Implements MT7601U mac80211 TX submission, TXWI construction, queue mapping, DMA enqueue handoff, TX status cleanup, retry inference, and WMM/EDCA queue configuration.

Important APIs and functions: `mt7601u_tx()` is the mac80211 `.tx` path. `mt7601u_tx_status()` strips DMA/TXWI padding and reports ACKed skb status to mac80211. `mt7601u_tx_stat()` drains hardware TX status FIFO via MAC helpers and reports rate/retry status. `mt7601u_conf_tx()` programs EDCA/WMM parameters. Internal helpers include `skb2q()`, `q2hwq()`, `mt7601u_push_txwi()`, `mt7601u_skb_rooms()`, and packet-id encode/decode helpers.

Control flow: TX starts by preserving original packet length in `status_driver_data`, ensuring skb headroom and 4-byte 802.11 header alignment, selecting WCID from station/vif/monitor context, pushing and filling a `mt76_txwi`, then enqueueing the skb to DMA. TXWI setup chooses rate control from mac80211 or cached WCID rate, sets ACK/no-sequence flags, configures AMPDU BA window/density, writes WCID, and encodes requested/probe rate in packet id. TX status work repeatedly fetches valid statuses, decodes packet id into retry/probe estimates, calls mt76 status reporting, and requeues if more statuses are likely.

State and persistence: Uses `dev->lock` for WCID rate reads, `dev->mac_lock` around mac80211 TX status callback, and `dev->tx_lock` for TX status state flags. `info->status.status_driver_data[0]` temporarily stores original skb length while DMA/TXWI overhead is present. Hardware EDCA registers persist until reconfigured.

Dependencies and integration points: Depends on mac80211 TX info/control structures, local MAC descriptor helpers from `mac.h`, DMA enqueue from `dma.c`, register definitions from `regs.h`, and tracepoints. The queue mapping uses mac80211 AC ids but reverses hardware priority order.

Risks: TX retry reporting is explicitly approximate because hardware status is limited; rate/retry accounting can be wrong for AMPDU or FIFO overflow. Header padding must be inserted and removed symmetrically or mac80211 receives corrupted skb data. Queue id validation falls back to BE, which avoids crash but can mask caller bugs. EDCA parameter conversion uses `fls()` on contention window values, so expectations must match hardware exponent encoding.

Test signals: Packet TX through all ACs, AMPDU and non-AMPDU traffic, no-ACK frames, rate-control probes, TX status traces, monitor/group/station WCID cases, and WMM parameter changes validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.c

Purpose: Provides the MT7601U USB driver entry point, USB endpoint discovery, coherent URB buffer helpers, vendor control register access, probe/disconnect/suspend/resume handling, and module metadata/device ids.

Important APIs and functions: Public helpers include `mt7601u_usb_alloc_buf()`, `mt7601u_usb_free_buf()`, `mt7601u_usb_submit_buf()`, `mt7601u_complete_urb()`, `mt7601u_vendor_request()`, `mt7601u_vendor_reset()`, `mt7601u_vendor_single_wr()`, `mt7601u_rr()`, `mt7601u_wr()`, `mt7601u_rmw()`, `mt7601u_rmc()`, `mt7601u_wr_copy()`, and `mt7601u_addr_wr()`. Driver callbacks are `mt7601u_probe()`, `mt7601u_disconnect()`, `mt7601u_suspend()`, and `mt7601u_resume()`.

Control flow: Probe allocates the mac80211-backed device, resets the USB device, stores interface data, allocates the vendor request scratch buffer, assigns bulk endpoints, waits for ASIC readiness, validates ASIC revision, warns if eFUSE is absent, initializes hardware, registers mac80211 device, and sets initialized state. Register reads/writes are implemented as serialized USB vendor control requests; 32-bit writes are split into two 16-bit writes. Bulk URB helpers fill coherent DMA URBs with endpoint-derived pipes and completion callbacks. Disconnect unregisters hardware, runs cleanup, drops the USB reference, destroys workqueue, and frees hw. Suspend cleans up; resume reinitializes hardware.

State and persistence: `dev->vend_buf` is a persistent 4-byte scratch buffer protected by `vendor_req_mutex`. Endpoint numbers and max packets are stored in `dev->in_eps`, `dev->out_eps`, `in_max_packet`, and `out_max_packet`. `MT7601U_STATE_REMOVED` is set on `-ENODEV` vendor request failures. Hardware state persists across register writes until reset or cleanup.

Dependencies and integration points: Integrates with USB core (`module_usb_driver`), mac80211 allocation/register/cleanup, hardware init code, MCU firmware loader, DMA and PHY/MAC functions through exported register access, and tracepoints for URB/vendor/register activity.

Risks: Endpoint assignment assumes exactly the expected number/order of bulk endpoints. Vendor reads/writes warn for offsets above 16 bits because the USB vendor protocol uses 16-bit offsets. `mt7601u_usb_alloc_buf()` returns a boolean failure and may leave one allocation present when the other fails; callers must free on failure, as seen in MCU init. Suspend cleanup and resume reinit must keep mac80211-facing state consistent.

Test signals: USB ID probe across supported devices, endpoint mismatch injection, ASIC revision mismatch, eFUSE warning, firmware load, suspend/resume/reset_resume, USB disconnect during register requests, and trace `mt_vend_req`/`mt_submit_urb` are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.h

Purpose: Declares MT7601U USB transport constants, firmware file name, vendor request ids, endpoint indices, USB-device conversion helper, URB error classifier, and USB/vendor helper prototypes.

Important APIs and types: `MT7601U_FIRMWARE` names `mt7601u.bin`; `MT_VEND_REQ_MAX_RETRY` and `MT_VEND_REQ_TOUT_MS` configure vendor control retry behavior. `enum mt_vendor_req` maps firmware/device-mode/write/read/FCE vendor commands. `enum mt_usb_ep_in` and `enum mt_usb_ep_out` define logical endpoint slots used after endpoint discovery. `mt7601u_to_usb_dev()` converts from driver device pointer to `usb_device`. `mt7601u_urb_has_error()` filters expected URB shutdown statuses.

Control flow: This header does not run logic. It defines how `usb.c` chooses pipes, how MCU/DMA code submits command/response buffers, and how upload paths classify URB completion status.

State and persistence: No state is declared here. Endpoint enum values index persistent arrays in `struct mt7601u_dev`.

Dependencies and integration points: Includes `mt7601u.h` for device and DMA buffer types. Included by USB, MCU, and DMA code.

Risks: Endpoint enum order must match hardware and `mt7601u_assign_pipes()` expectations. Treating `-ENOENT`, `-ECONNRESET`, and `-ESHUTDOWN` as non-errors is appropriate for teardown but would hide unexpected cancellations if used outside teardown-aware contexts.

Test signals: Build coverage, firmware upload via `MT_EP_OUT_INBAND_CMD`, MCU response reads via `MT_EP_IN_CMD_RESP`, normal disconnect/suspend URB cancellation, and vendor request retry behavior validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/util.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/util.c

Purpose: Provides small skb utilities to insert and remove 2-byte padding when 802.11 headers are not 4-byte aligned for MT7601U DMA/TXWI requirements.

Important APIs and functions: `mt76_insert_hdr_pad()` ensures a misaligned 802.11 header gets two zero padding bytes after growing headroom with `skb_cow()`. `mt76_remove_hdr_pad()` reverses the transformation by moving the header forward and pulling two bytes.

Control flow: TX calls `mt76_insert_hdr_pad()` before pushing TXWI/DMA metadata. TX status cleanup calls `mt76_remove_hdr_pad()` if the restored skb header length is not 4-byte aligned. Both functions use `ieee80211_get_hdrlen_from_skb()` to determine whether padding is needed.

State and persistence: The only mutated state is skb data/headroom/length. No driver global state is touched.

Dependencies and integration points: Depends on mac80211 header length parsing and skb memory manipulation. Used by `tx.c` around DMA descriptor handling.

Risks: Incorrect memmove offsets would corrupt the 802.11 header. Insert/remove must stay symmetric with TXWI stripping or mac80211 will see malformed frames in status callbacks. `skb_cow()` failure must be propagated to free/drop the skb, which `tx.c` does.

Test signals: TX frames with both aligned and misaligned 802.11 header lengths, status callback skb integrity, and sanitizer checks around skb headroom validate these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Kconfig

Purpose: Adds the top-level wireless vendor menu for Microchip devices and includes the WILC1000 driver Kconfig when the vendor category is enabled.

Important APIs and entries: `config WLAN_VENDOR_MICROCHIP` is a boolean menu gate defaulting to `y`. It sources `drivers/net/wireless/microchip/wilc1000/Kconfig` inside the `if WLAN_VENDOR_MICROCHIP` block.

Control flow: Kconfig evaluation presents Microchip wireless options only when the vendor selector is enabled. The selector itself does not build code; it controls visibility of child symbols.

State and persistence: The selected Kconfig values persist in the kernel `.config`. `WLAN_VENDOR_MICROCHIP=n` hides child prompts and prevents selecting WILC symbols through this menu.

Dependencies and integration points: Integrated from the parent wireless driver Kconfig tree. Child WILC1000 options define actual module/object inclusion.

Risks: If the source path is wrong, WILC1000 options disappear. Default `y` improves discoverability but still leaves actual driver tristates dependent on child selections.

Test signals: `menuconfig` visibility, `scripts/kconfig/conf` generation, and builds with vendor enabled/disabled validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Makefile

Purpose: Connects the Microchip wireless directory to the kernel build by descending into the WILC1000 subdirectory when `CONFIG_WILC1000` is enabled.

Important APIs and entries: `obj-$(CONFIG_WILC1000) += wilc1000/` is the only build rule.

Control flow: Kbuild evaluates the object directory rule and includes the child Makefile only for enabled WILC1000 builds.

State and persistence: No runtime state. Build output depends on `.config`.

Dependencies and integration points: Depends on child `wilc1000/Makefile` for actual object lists and bus-specific modules.

Risks: Since both SDIO and SPI select `WILC1000`, this top-level rule must remain keyed to the core symbol or bus-specific builds would miss shared objects.

Test signals: `CONFIG_WILC1000_SDIO=m/y` and `CONFIG_WILC1000_SPI=m/y` builds should enter this directory and compile the core plus bus objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Kconfig

Purpose: Defines WILC1000 core and bus-specific configuration symbols for SDIO, SPI, and optional SDIO out-of-band interrupt support.

Important APIs and entries: `config WILC1000` is the hidden/shared tristate core selected by bus drivers. `WILC1000_SDIO` depends on `CFG80211`, `INET`, and `MMC`, selects `WILC1000`, and describes SDIO operation. `WILC1000_SPI` depends on `CFG80211`, `INET`, and `SPI`, selects `WILC1000`, `CRC7`, and `CRC_ITU_T`. `WILC1000_HW_OOB_INTR` is a bool depending on SDIO.

Control flow: Users select an SDIO or SPI bus transport, which selects the shared core module. Bus symbols drive compilation of `sdio.o` or `spi.o`; the core symbol drives common cfg80211/netdev/HIF/wlan objects.

State and persistence: Configuration choices persist in `.config` and determine module availability, bus registration, and optional interrupt handling.

Dependencies and integration points: Integrated by the Microchip vendor Kconfig and the WILC1000 Makefile. Runtime code assumes cfg80211 and IP networking support, while bus modules rely on MMC or SPI subsystems.

Risks: The help text says Atmel WILC1000 and Wi-Fi-only 802.11n; WILC3000 firmware support appears in netdev code, so configuration wording may not fully describe all chip ids handled by core code. Missing CRC selections would break SPI protocol helpers.

Test signals: Kconfig dependency resolution for SDIO/SPI, allmodconfig/randconfig coverage, and builds with OOB interrupt enabled validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Makefile

Purpose: Defines Kbuild object composition for WILC1000 common core and SDIO/SPI bus modules.

Important APIs and entries: `obj-$(CONFIG_WILC1000) += wilc1000.o`; `wilc1000-objs` contains `cfg80211.o`, `netdev.o`, `mon.o`, `hif.o`, `wlan_cfg.o`, and `wlan.o`. `CONFIG_WILC1000_SDIO` builds `wilc1000-sdio.o` from `sdio.o`; `CONFIG_WILC1000_SPI` builds `wilc1000-spi.o` from `spi.o`.

Control flow: Kbuild links common objects into one core module/object and bus-specific shims separately. Bus modules use exported core symbols such as cfg80211 init and netdev interface creation.

State and persistence: No runtime state. Build composition is determined by `.config`.

Dependencies and integration points: Coordinates with Kconfig symbols and source files not all in this subset (`wlan.c`, `wlan_cfg.c`, `sdio.c`, `spi.c`). Module firmware declarations live in `netdev.c`.

Risks: Common object ordering generally does not matter, but missing `mon.o` or `hif.o` would break cfg80211 monitor/P2P or host-interface symbols. Bus-specific modules depend on core symbols being exported where needed.

Test signals: Modular and built-in builds for core plus SDIO/SPI combinations, modpost symbol checks, and clean link of `wilc1000.o` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/cfg80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/cfg80211.c

Purpose: Implements WILC1000 cfg80211 integration: wiphy creation/registration, scan/connect/disconnect, key management, PMKSA, AP operations, station management, P2P remain-on-channel and management TX/RX, virtual interface management, power/tx-power controls, host-interface initialization, and shared lock initialization.

Important APIs and functions: The `wilc_cfg80211_ops` table exposes callbacks including `scan`, `connect`, `disconnect`, `add_key`, `del_key`, `get_key`, `set_default_mgmt_key`, virtual interface add/delete/change, AP beacon/station operations, station queries, PMKSA operations, remain-on-channel, management TX, management registration updates, wakeup, and TX power. Public functions include `wilc_cfg80211_init()`, `wilc_cfg80211_register()`, `wilc_init_host_int()`, `wilc_deinit_host_int()`, `wilc_update_mgmt_frame_registrations()`, monitor init/deinit declarations, and management RX helpers.

Control flow: Scan converts cfg80211 channel requests to firmware channel numbers, chooses active/passive mode, and calls `wilc_scan()` with `cfg_scan_result()` callback. Connect translates crypto/auth/MFP settings, obtains and parses a BSS into firmware join parameters, sets BSSID/channel state, stores connection callback state in HIF, and calls `wilc_set_join_req()`. HIF callbacks later report connect/disconnect to cfg80211. Key operations translate TKIP/CCMP/AES-CMAC into firmware PTK/GTK/IGTK commands and cache key material for get/delete paths. AP and station callbacks set operation mode, beacon data, and station records. P2P code rewrites operating/channel-list attributes for concurrency, manages remain-on-channel cookies/timers, and sends management frames through the WILC TX queue.

State and persistence: `struct wilc_priv` holds scan request state, P2P listen state/cookies, associated BSS, PMKID list, cached keys, cfg80211 wireless_dev, and HIF driver pointer. `struct wilc_vif` stores firmware interface mode, BSSID, monitor flag, associated stations, connection flags, and external auth parameters. `struct wilc` stores global wiphy, bands, cipher suites, vif list, SRCU, locks, completions, workqueue, and bus hooks. Locks initialized here protect HIF access, vif list, tx/rx queues, config commands, deinit, and scan request lifecycle.

Dependencies and integration points: Depends on cfg80211/mac80211 management frame helpers, netdev lifecycle in `netdev.c`, firmware command builders in `hif.c`, firmware structs from `fw.h`, shared types in `netdev.h`, and queue transmit functions from `wlan.c`. Bus modules call `wilc_cfg80211_init/register` and create netdev interfaces.

Risks: Several key get/delete paths assume cached key pointers exist for requested indices; malformed userspace sequences could expose null dereferences if not guarded by cfg80211 behavior. P2P attribute rewriting mutates management frame buffers and requires careful bounds handling. Connection state spans cfg80211, vif fields, HIF timers, and firmware indications; missed cleanup can leave stale BSS references or request IE buffers. Interface concurrency is capped at two and relies on SRCU list discipline.

Test signals: cfg80211 scan completion/abort, WPA/WPA2/WPA3-SAE connection and external auth, disconnect during scan/connect, AP start/stop and station add/delete, monitor interface creation, P2P GO negotiation/invitation with concurrent STA channel, PMKSA add/delete/flush, key add/get/delete for GTK/PTK/IGTK, tx power bounds, and wiphy registration are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/cfg80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/cfg80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/cfg80211.h

Purpose: Declares the cfg80211-facing WILC1000 initialization, registration, host-interface, monitor, management RX, and helper functions shared by bus/core files.

Important APIs and functions: `wilc_cfg80211_init()` allocates and initializes the wiphy/core object. `wilc_cfg80211_register()` registers the wiphy. `wilc_init_host_int()` and `wilc_deinit_host_int()` manage per-netdev HIF state. `wilc_wfi_monitor_rx()`, `wilc_wfi_init_mon_interface()`, and `wilc_wfi_deinit_mon_interface()` cover monitor support. `wilc_update_mgmt_frame_registrations()` synchronizes cfg80211 management frame subscriptions. `wilc_get_wl_to_vif()` retrieves a vif from the global list. `wlan_deinit_locks()` tears down global locks.

Control flow: This header does not execute logic; it exposes functions implemented in `cfg80211.c`, `mon.c`, and related files to netdev and bus code.

State and persistence: No state is declared beyond included structures. Callers manipulate persistent `struct wilc`, `wilc_vif`, and netdev state through these APIs.

Dependencies and integration points: Includes `netdev.h`, so it brings in shared WILC state definitions and cfg80211/netdev types. Included by `netdev.c`, `mon.c`, and bus integration code.

Risks: Broad inclusion of `netdev.h` makes this a heavy header; changes can trigger large rebuilds and circular dependency risks. Prototype drift would break core/bus linkage.

Test signals: Build/modpost coverage, bus driver calls to cfg80211 init/register, monitor interface add/delete, and host interface open/close validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/cfg80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/fw.h

Purpose: Defines packed firmware ABI structures and limits for WILC1000 host-interface commands, association data, PMKID/key payloads, P2P NoA/OPP data, join parameters, external authentication parameters, and NVMEM bank addressing.

Important APIs and types: Key structs include `wilc_assoc_resp`, `wilc_pmkid`, `wilc_pmkid_attr`, `wilc_reg_frame`, `wilc_drv_handler`, `wilc_sta_wpa_ptk`, `wilc_ap_wpa_ptk`, `wilc_wpa_igtk`, `wilc_gtk_key`, `wilc_op_mode`, `wilc_noa_opp_enable`, `wilc_noa_opp_disable`, `wilc_join_bss_param`, and `wilc_external_auth_param`. Constants define maximum stations, rates, PMKIDs, scanned channels, and NVMEM bank layout. `get_bank_offset_from_bank_index()` computes bank metadata offsets.

Control flow: No runtime control flow beyond the inline bank offset helper. The structures are filled in `cfg80211.c` and `hif.c`, then passed to firmware via WID commands.

State and persistence: These packed payloads represent firmware-visible state such as security keys, operation mode, join BSS details, PMKID cache, and external auth status. NVMEM bank constants refer to persistent device storage metadata.

Dependencies and integration points: Includes `linux/ieee80211.h` for WLAN constants. Used by HIF command construction and cfg80211 join/key/auth paths.

Risks: Packed layouts are firmware ABI; changing field order, size, endian annotations, or max lengths can break firmware commands. Flexible-array key structs must be allocated with exact payload lengths to avoid truncation or overflow. NVMEM bank offset calculations must match chip storage layout.

Test signals: Association to WPA/WPA2/WPA3 networks, PMKID operations, PTK/GTK/IGTK installation, P2P NoA parsing, external auth, and NVMEM read/write users of bank offsets validate this ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/hif.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/hif.c

Purpose: Implements the WILC host interface: cfg80211 requests are converted into firmware WID set/get packets, asynchronous firmware indications are serialized through an ordered workqueue, scan/connect/ROC timers enforce timeouts, and firmware state is reflected back to cfg80211 callbacks.

Important APIs and functions: Public APIs include `wilc_scan()`, `wilc_set_join_req()`, `wilc_disconnect()`, `wilc_get_statistics()`, key installation functions (`wilc_add_ptk()`, `wilc_add_rx_gtk()`, `wilc_add_igtk()`), PMKID/MAC/channel/operation-mode setters, AP station/beacon functions, power/multicast/WoWLAN/tx-power functions, `wilc_init()`, `wilc_deinit()`, and firmware indication handlers `wilc_network_info_received()`, `wilc_gnrl_async_info_received()`, and `wilc_scan_complete_received()`. `wilc_parse_join_bss_param()` builds the packed firmware join parameter.

Control flow: Requests are usually built as one or more `struct wid` entries and sent with `wilc_send_config_pkt()`. Scan sets probe IE/SSID/channel/source WIDs, arms a timer, and later calls scan callbacks on network found/done/abort. Connect stores BSSID/IEs/security/auth/MFP, sends connect WIDs, enters waiting or external-auth state, and arms a connect timeout. Firmware async status either requests external auth, parses association response data, reports connection, or handles disconnection. P2P remain-on-channel sets a firmware flag/channel, records callbacks/cookie, and clears state on timer expiry. Async firmware buffers carry a vif id at the tail; handlers use SRCU to map ids back to vifs before queueing work.

State and persistence: `struct host_if_drv` stores scan request callbacks, connection info, remain-on-channel info, HIF state, associated BSSID, timers, `ifc_up`, and association response scratch. Work items use `struct host_if_msg`. Timers include scan, connect, remain-on-channel, and per-vif periodic RSSI. Request IE and response IE buffers are dynamically allocated and freed after connect completion or abort. HIF state values gate scanning, connecting, external auth, connected, and listen behavior.

Dependencies and integration points: Depends on shared WILC structs from `netdev.h`, firmware ABI structs from `fw.h`, cfg80211 BSS/IE parsing, WID ids and config transport from `wlan_if.h`/`wlan_cfg.c`/`wlan.c`, and netdev/cfg80211 callbacks in `cfg80211.c`. Uses SRCU and `deinit_lock` to avoid use-after-free across asynchronous firmware events.

Risks: Many paths allocate buffers for WID payloads and must free them on success and failure. Connection timeout and firmware indication races can double-report or free `req_ies` if state transitions are wrong. Async handlers trust buffer layout, including tail vif id and fixed offsets for status/network frames. `del_station()` callers should note `wilc_del_station()` is called even after `wilc_del_allstation()` with possibly null mac, intentionally broadcasting removal. Null HIF checks exist, but some callbacks assume `conn_result` is set.

Test signals: Scan timeout and firmware scan-complete, connect success/failure/timeout, SAE external auth handoff, disconnect while scanning/connecting, association response IE reporting, AP beacon/station operations, multicast filter updates, ROC expiry/cancel, periodic RSSI stats, key WID installation, and concurrent vif firmware indications validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/hif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/hif.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/hif.h

Purpose: Declares WILC host-interface modes, state enums, scan/connect event contracts, firmware configuration parameter structs, per-vif HIF state, and public HIF command APIs.

Important APIs and types: Defines WILC operation modes (`IDLE`, `AP`, `STATION`, `GO`, `CLIENT`), `host_if_state`, `scan_event`, `conn_event`, bus type flags, MAC status values, `rf_info`, `cfg_param_attr`, `wilc_rcvd_net_info`, `wilc_user_scan_req`, `wilc_conn_info`, `wilc_remain_ch`, and `host_if_drv`. Function prototypes cover key management, scan/connect/disconnect, config, AP operations, station operations, power/multicast/ROC/frame registration, operation mode, statistics, tx power, WoWLAN, external auth, firmware async indications, join param parsing, default management key, and disconnect handling.

Control flow: This header defines the callback contracts used between `cfg80211.c` and `hif.c`: scan callbacks receive event and optional network info, connection callbacks receive connect/disconnect event and MAC status, remain-on-channel callbacks receive vif/cookie. `host_if_drv` embeds timers and request state used by HIF implementation.

State and persistence: `host_if_drv` is allocated per opened netdev and persists until host-interface deinit. It stores current HIF state, associated BSSID, scan/connect/ROC timers, pending callback data, and association response buffer. `cfg_param_attr` flags persist only for one configuration command.

Dependencies and integration points: Includes `linux/ieee80211.h` and `wlan_if.h`, and forward-declares WILC private/vif/join types. Used by `netdev.h`, `cfg80211.c`, and `hif.c`.

Risks: State enum ordering is used by comparisons such as "scanning through before connected"; inserting states can affect logic. Callback pointer lifetimes are cross-file and timer-driven, so callers must clear them during deinit/abort. Max probed SSIDs and concurrent interfaces are firmware limits.

Test signals: Compile coverage and runtime tests for every cfg80211 operation that maps to a HIF function, especially scan/connect timers, multi-interface operation, and async firmware indications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/hif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/mon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/mon.c

Purpose: Implements WILC monitor-mode netdev support, including radiotap wrapping for received management frames and TX status callbacks, management TX from monitor frames, and monitor interface allocation/teardown.

Important APIs and functions: `wilc_wfi_monitor_rx()` delivers received/callback management frames to a monitor netdev with radiotap headers. `wilc_wfi_init_mon_interface()` allocates/registers an `ARPHRD_IEEE80211_RADIOTAP` netdev and links it to a real WILC netdev. `wilc_wfi_deinit_mon_interface()` unregisters it. Internal TX path functions include `wilc_wfi_mon_xmit()`, `mon_mgmt_tx()`, and `mgmt_tx_complete()`.

Control flow: RX checks monitor existence and running state, reads WILC host header metadata before the frame buffer to distinguish management TX callbacks from received frames, prepends the appropriate radiotap header, and injects via `netif_rx()`. Monitor TX strips the incoming radiotap header, special-cases broadcast deauth-style frames for local TX-status echo, routes management frames whose source equals BSSID through `wilc_wlan_txq_add_mgmt_pkt()`, and sends other frames through normal `wilc_mac_xmit()` on the real netdev.

State and persistence: `struct wilc_wfi_mon_priv` stores the backing real netdev. `wl->monitor_dev` persists while monitor mode is active. Allocated TX callback buffers persist until TX completion callback frees them.

Dependencies and integration points: Depends on cfg80211/netdev shared types, radiotap definitions, WILC host header flags (`HOST_HDR_OFFSET`, `WILC_PKT_HDR_OFFSET_FIELD`, `IS_MANAGMEMENT_CALLBACK`, `IS_MGMT_STATUS_SUCCES`), normal TX queue helpers, and `wilc_mac_xmit()` from `netdev.c`. Created/deleted by cfg80211 virtual interface operations.

Risks: RX reads `buff - HOST_HDR_OFFSET`, so callers must pass buffers with valid WILC host header space. Monitor TX returns error-like values from a `netdev_tx_t` path in some cases, which is not ideal for netdev semantics. Radiotap rate is hardcoded to 5. Management/data classification by source address equals BSSID is heuristic.

Test signals: Add/delete monitor interface, receive P2P/action/auth/probe frames, hostapd management TX callbacks, monitor-injected management frames, normal data forwarding through monitor, and teardown while monitor device exists are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/netdev.c

Purpose: Implements WILC net_device lifecycle, firmware loading/start/configuration, IRQ handling, TX queue thread, netdev operations, RX delivery, management RX fanout, interface allocation, global cleanup, and module firmware metadata.

Important APIs and functions: Exported/public functions include `wilc_mac_indicate()`, `wilc_wlan_set_bssid()`, `wilc_wlan_get_num_conn_ifcs()`, `wilc_frmw_to_host()`, `wilc_wfi_mgmt_rx()`, `wilc_netdev_cleanup()`, and `wilc_netdev_ifc_init()`. Netdev operations are `wilc_mac_open()`, `wilc_mac_close()`, `wilc_mac_xmit()`, `wilc_set_mac_addr()`, multicast list handling, and stats retrieval. Firmware path functions include `wilc_wlan_get_firmware()`, `wilc_firmware_download()`, `wilc_start_firmware()`, `wilc_init_fw_config()`, and `wilc_wlan_initialize()/deinitialize()`.

Control flow: Opening a netdev initializes host interface, initializes firmware/hardware if not already global-initialized, sets firmware operation mode and MAC address, reapplies management frame registrations, starts queues, and increments open interface count. Hardware initialization starts WILC WLAN core, TXQ kthread, IRQ or bus interrupt handling, requests/downloads firmware based on chip id, starts firmware and waits for sync completion, reads firmware version, and writes default WID configuration. TX queues netdev packets into the WILC WLAN TX queue and stops all open queues when queue depth exceeds the upper threshold; the TXQ kthread drains entries and wakes queues below the lower threshold. RX chooses a vif by 802.11 header/BSSID, allocates skb, sets protocol/checksum, updates stats, and calls `netif_rx()`. Closing disconnects, deinitializes host interface, and shuts down global hardware on last close.

State and persistence: Global `struct wilc` state includes firmware pointer, initialized flag, close flag, txq thread, completions, IRQ number, open interface count, vif list, queues, and bus hooks. Each `wilc_vif` stores BSSID, iftype, netstats, mac_opened, and private cfg80211/HIF state. Firmware configuration persists on the device until reset/reload. `nv_mac_address` is copied into each netdev, with the second interface locally administered bit set.

Dependencies and integration points: Depends on Linux netdevice, firmware loader, kthread, IRQ, cfg80211 host-interface functions, WILC bus functions through `hif_func`, WILC WLAN core/config functions in files outside this subset, and monitor/cfg80211 helpers. Bus drivers provide chip id, interrupt setup, and call interface creation/cleanup.

Risks: Initialization has many staged failure labels; leaks or partial interrupt/thread state are possible if ordering changes. `wilc_mac_close()` calls disconnect handling even for AP-like modes and depends on HIF cleanup robustness. RX interface selection is simple BSSID matching and may miss frames in unusual modes. TX flow control stops all open vifs based on shared queue depth. Firmware version string writes `firmware_ver[size] = '\0'`; this assumes returned size is within the fixed buffer.

Test signals: Open/close first and second interfaces, firmware missing/download failure/start timeout, IRQ and non-IRQ interrupt modes, TX flow-control thresholds, RX delivery in STA/AP modes, multicast filter programming, MAC address collision handling, suspend-like deinit, and cleanup with monitor/vifs active validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/netdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/netdev.h

Purpose: Defines shared WILC netdev/cfg80211 driver state, channel/rate/cipher tables, queue thresholds, TCP ACK filter structures, vif/global device objects, monitor private data, and core function prototypes.

Important APIs and types: `struct wilc_priv` embeds `wireless_dev`, scan/P2P/key/PMKID/cfg state, real monitor backing device, HIF pointer, and association information. `struct wilc_vif` represents one virtual interface with index, firmware iftype, BSSID, netdev stats, HIF state, timers, TCP ACK filter, cfg80211 private state, list node, BSS reference, and external auth parameters. `struct wilc` is the global device with wiphy, bus hooks, chip id, locks, completions, queues, firmware pointer, workqueue, bus data, monitor device, channels/rates/cipher suites, and NVMEM MAC. Static tables define 2.4 GHz channels, legacy bitrates, and cipher suites.

Control flow: The header supplies data structures used by `cfg80211.c`, `hif.c`, `netdev.c`, `mon.c`, and lower WLAN/bus files. The `wilc_for_each_vif` macro enforces SRCU-aware vif-list traversal. Function prototypes declare RX delivery, MAC indication, cleanup, management RX, BSSID setting, and interface creation.

State and persistence: Most WILC runtime state lives in these structs. Persistent fields include firmware/config state, queue heads, netdev stats, key caches, PMKIDs, associated stations, BSSID, per-vif timers, global lock/completion objects, firmware pointer, and copied channel/rate/cipher arrays registered with wiphy.

Dependencies and integration points: Includes cfg80211, radiotap, netdevice, GPIO, SRCU list, TCP, and WILC HIF/WLAN config headers. It is the common include for the WILC core and defines the contract with bus-independent WLAN queue/config code.

Risks: This header mixes static table definitions with struct declarations; because it is included in multiple C files, the static arrays are duplicated per translation unit, which is acceptable but worth noting for changes. The SRCU traversal macro requires callers to hold SRCU read lock. Queue thresholds and ACK filter sizes are fixed constants that influence flow control and memory use. Changing struct layouts affects driver-private data allocated by `alloc_etherdev()`.

Test signals: Multi-vif traversal under SRCU, interface allocation/free, cfg80211 wiphy band/cipher registration, TX/RX queue operation, ACK filter behavior, monitor interface state, and lockdep coverage around shared locks validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/netdev.h -->
