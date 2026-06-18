# Research: subset-b-004722

Grouped source research for the ath10k SDIO/SNOC, diagnostics, tracing, and RX descriptor subset. Each section preserves the source path and is intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/rx_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/rx_desc.h

Purpose: Defines the packed RX descriptor ABI used by ath10k HTT receive paths to interpret hardware/firmware metadata for MPDU/MSDU boundaries, decapsulation, checksum status, PHY/PPDU status, locationing, spectral/radar-related PHY errors, and high-latency firmware RX descriptors.

Important APIs, types, and definitions: The file exports descriptor structures such as `rx_attention`, `rx_frag_info`, `rx_mpdu_start`, `rx_mpdu_end`, `rx_msdu_start`, `rx_msdu_end`, `rx_ppdu_start`, `rx_ppdu_end`, `rx_pkt_end`, `rx_location_info`, `rx_phy_ppdu_end`, `fw_rx_desc_base`, and `fw_rx_desc_hl`. Bit definitions cover attention flags, MPDU peer/sequence/encryption fields, MSDU lengths, protocol/checksum offsets, decap formats, PPDU preambles, PHY error bits, RTT/locationing fields, and firmware forward/discard/inspect flags.

Control flow, state, and persistence: This header has no executable flow and owns no mutable state. Its packed layouts are consumed by RX parsing code and therefore act as persistent hardware/firmware contracts. Versioned variants distinguish WCN3990/current layouts from v1/QCA988x/QCA6174/QCA99x0/QCA9984 layouts.

Dependencies and integration points: Depends on Linux bit macros and little-endian integer types. It integrates with HTT RX handlers, monitor/status reporting, checksum offload interpretation, PN/security handling, spectral/PHY error processing, and tracing of HTT RX descriptors.

Risks: Any field offset, packing, endian conversion, or mask/LSB error can corrupt frame delivery, checksum status, decryption error reporting, peer accounting, radiotap metadata, or crash/debug analysis. The unions require callers to select the layout that matches `ar->hw_rev`. Some comments encode hardware semantics, so maintenance mistakes can silently break firmware compatibility.

Test signals: Build all supported ath10k hardware variants, receive encrypted and plaintext frames, A-MPDU/A-MSDU boundary cases, checksum pass/fail, FCS/MIC/decrypt errors, monitor-mode metadata, spectral/PHY error reports, WCN3990 receive paths, and trace dumps of HTT RX descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/rx_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/sdio.c

Purpose: Implements the ath10k SDIO host interface for QCA6174/QCA9377-style high-latency devices, including SDIO function configuration, mailbox RX/TX transport, BMI exchange, interrupt handling, power management, crash dump extraction, and SDIO driver probe/remove.

Important APIs and functions: The HIF implementation is exposed through `ath10k_sdio_hif_ops` with `tx_sg`, `diag_read`, `diag_write`, `exchange_bmi_msg`, `start`, `stop`, `start_post`, `get_htt_tx_complete`, `map_service_to_pipe`, `get_default_pipe`, `power_up`, `power_down`, and PM hooks. Major helpers include `ath10k_sdio_config()`, `ath10k_sdio_mbox_rxmsg_pending_handler()`, `ath10k_sdio_bmi_exchange_msg()`, `ath10k_sdio_prep_async_req()`, `ath10k_sdio_irq_handler()`, `ath10k_sdio_hif_tx_sg()`, `ath10k_sdio_hif_start()`, `ath10k_sdio_irq_disable()`, `ath10k_sdio_fw_crashed_dump()`, and the SDIO `probe`/`remove` callbacks.

Control flow: Probe creates the core, NAPI instance, IRQ register buffers, VSG and BMI buffers, a single-thread workqueue, request free list, RX queue, and mailbox geometry before registering ath10k as a high-latency bus. Power-up configures CCCR drive strength, async 4-bit IRQ mode, async interrupt delay, SDIO block size, enables the function, and disables interrupts. Start claims the SDIO IRQ, enables mailbox interrupts, sets mailbox 0 to the lower extended address, and toggles mailbox sleep. RX interrupt handling releases the SDIO host, repeatedly reads interrupt status and lookahead registers, allocates one or bundled skb groups, reads mailbox data via fixed-address block transfers, processes HTC trailers for additional lookaheads, queues real payloads to an async RX work item, then pushes pending TX. TX pads each skb to mailbox block size, picks the endpoint mailbox tail address, queues a bus request, and the workqueue writes it before notifying HTC completion.

State and persistence: Runtime state lives in `struct ath10k_sdio`: mailbox addresses/sizes, `swap_mbox`, bus request pool and async write queue, `rx_head`, `rx_pkts`, IRQ proc/enable shadows, `vsg_buffer`, `bmi_buf`, `is_disabled`, workqueue, sleep timer, and `mbox_state`. The driver persists no durable data, but host-interest flags from firmware select mailbox swapping, reduced TX completions, and crashdump mode. Sleep state transitions are timer-driven and depend on mailbox traffic.

Dependencies and integration points: Uses Linux MMC/SDIO APIs, ath10k core/HIF/HTC/HTT/MAC/BMI/coredump layers, mailbox register definitions, `targaddrs.h` host-interest offsets, workqueues, NAPI, and cfg80211/mac80211 upper layers through core registration. Crash dumps integrate with ath10k coredump memory layouts and may use BMI fast dump when firmware advertises it.

Risks: RX lookahead and bundle accounting is sensitive to HTC header lengths, padded lengths, trailer-only messages, and `ATH10K_SDIO_MAX_RX_MSGS`. Async TX completion happens after SDIO writes, so stop paths must drain queued requests without losing ownership. `ath10k_sdio_set_mbox_sleep()` claims the host and calls helpers that also claim the host, making host-lock expectations important. Crashdump reads occur around interrupt disable/enable and can trigger recovery. Several error paths start recovery on transport faults; tests need to distinguish recoverable SDIO errors from memory corruption or leaked skbs.

Test signals: Probe/remove AR6005 and QCA9377 SDIO IDs, SDIO suspend with wakeup, BMI command/response exchange, HTC control and HTT data pipe mapping with and without mailbox swap, single and bundled RX, malformed HTC lengths, trailer-only packets, async TX queue exhaustion, interrupt disable timeout, mailbox sleep/wake timer behavior, firmware crash dump with normal and fast-dump paths, and recovery after SDIO read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/sdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/sdio.h

Purpose: Defines SDIO mailbox constants, CCCR bit definitions, RX bundle limits, sleep-control constants, and private SDIO transport state used by `sdio.c`.

Important APIs and types: Exposes `ATH10K_HIF_MBOX_*`, `ATH10K_SDIO_MAX_BUFFER_SIZE`, `ATH10K_HTC_MBOX_MAX_PAYLOAD_LENGTH`, `ATH10K_SDIO_MAX_RX_MSGS`, sleep/RTC constants, `enum sdio_mbox_state`, `ath10k_sdio_bus_request`, `ath10k_sdio_rx_data`, IRQ register shadow structures, mailbox geometry structures, `struct ath10k_sdio`, and `ath10k_sdio_priv()`.

Control flow, state, and persistence: The header owns no flow, but its structures define the state machine used by SDIO HIF: request allocation/free queues, asynchronous write work, RX packet staging, IRQ shadow protection, mailbox swap metadata, VSG/BMI temporary buffers, disabled state, and sleep timer state.

Dependencies and integration points: Depends on Linux SDIO definitions and ath10k HTC endpoint IDs. It is consumed by `sdio.c` and indirectly by ath10k core/HIF code through `ar->drv_priv`.

Risks: Buffer-size constants bound both allocation and validation, so mismatches can truncate HTC payloads or overrun VSG bundle buffers. The `TODO` about replacing bus requests with `skb->cb` highlights lifetime/ownership complexity. Mutex/spinlock comments are part of the concurrency contract because SDIO memory copies can sleep.

Test signals: Compile SDIO builds, validate maximum HTC payload, RX bundle counts, mailbox address calculation, sleep state transitions, and interrupt register shadow writes under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/snoc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/snoc.c

Purpose: Implements the ath10k SNOC/platform bus driver for Qualcomm WCN3990, including CE pipe configuration, QMI firmware enable/disable, platform resources, power sequencing, NAPI/IRQ handling, MSA firmware memory setup, SSR modem notifications, crash dumping, and platform probe/remove/shutdown.

Important APIs and functions: Exposes HIF operations through `ath10k_snoc_hif_ops`, bus MMIO operations through `ath10k_snoc_bus_ops`, firmware indications through `ath10k_snoc_fw_indication()`, and crash dumps through `ath10k_snoc_fw_crashed_dump()`. Core helpers include CE RX/TX callbacks, `ath10k_snoc_hif_tx_sg()`, service-to-pipe mapping, `ath10k_snoc_hif_power_up()`, `ath10k_snoc_hif_start()`, `ath10k_snoc_napi_poll()`, `ath10k_snoc_resource_init()`, `ath10k_snoc_setup_resource()`, `ath10k_setup_msa_resources()`, `ath10k_fw_init()`, and platform `probe`/`remove`.

Control flow: Probe matches `qcom,wcn3990-wifi`, sets the 35-bit DMA mask, creates ath10k core with SNOC HIF ops, maps the `membase` resource, records CE IRQs, allocates CE pipes/NAPI, requests IRQs with `IRQF_NO_AUTOEN`, initializes regulators/clocks/pwrseq, allocates or maps the MSA region, configures firmware IOMMU mapping if a `wifi-firmware` child exists, starts QMI, and registers an MPSS SSR notifier. Power-up sequences pwrseq, regulators, clocks, QMI WLAN enable with CE target/service/shadow register config, RRI allocation, CE pipe init, and CE interrupt enable. IRQs disable their CE line, mark the CE bit pending, and schedule NAPI; NAPI services pending CEs, reenables CE interrupts, and drains HTT completions. RX callbacks unmap DMA, validate lengths, deliver skbs to HTC/HTT, and replenish buffers. Firmware ready indications register the core; firmware down indications mark recovery and crash flush.

State and persistence: `struct ath10k_snoc` holds platform device, ath10k core, firmware IOMMU device/domain/start address, MMIO mapping, target info, CE pipe/IRQ state, rx-post retry timer, pwrseq/regulator/clock handles, QMI client, SSR notifier, flags, XO calibration, and pending CE IRQ bitmap. MSA memory and IOMMU mappings persist for firmware lifetime. Recovery flags coordinate crash flush, WLAN disable, and IRQ behavior across restart/remove.

Dependencies and integration points: Uses Linux platform/OF, regulators, clocks, pwrseq, QMI WLFW, Qualcomm remoteproc SSR notifier, reserved memory, IOMMU APIs, DMA mapping, ath10k CE/HTC/HTT/core/coredump layers, and mac80211 NAPI integration. CE service maps bind HTC/WMI/HTT/pktlog traffic to specific copy engines.

Risks: CE ring DMA ownership must be precise during RX replenish, completion, cleanup, and recovery. IRQ disable/enable pairing spans hard IRQ and NAPI contexts. Firmware memory mapping has a likely-sensitive `mapped_mem_size` dependency during deinit, so initialization must keep mapped size consistent with `ar->msa.mem_size`. Probe unwind ordering is broad and must avoid leaked IRQs, IOMMU domains, QMI clients, or CE pipes. Recovery and debugfs crash injection intentionally alter WLAN disable behavior.

Test signals: Probe WCN3990 DT with and without pwrseq and reserved memory, CE IRQ delivery across all configured engines, HTT/WMI traffic over mapped pipes, NAPI budget behavior, RX replenish retry after allocation failure, suspend/resume wake IRQ, QMI firmware ready/down indications, modem SSR notifications, crash dump MSA capture, recovery after firmware down, and remove during recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/snoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/snoc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/snoc.h

Purpose: Declares SNOC-specific private structures, flags, and public hooks used by the WCN3990 platform transport.

Important APIs and types: Defines `ath10k_snoc_drv_priv`, `snoc_state`, `ath10k_snoc_pipe`, `ath10k_snoc_target_info`, `ath10k_snoc_ce_irq`, `enum ath10k_snoc_flags`, `struct ath10k_snoc`, `ath10k_snoc_priv()`, `ath10k_snoc_fw_indication()`, and `ath10k_snoc_fw_crashed_dump()`.

Control flow, state, and persistence: No executable control flow besides the private accessor. The structures describe persistent driver runtime state: CE pipe metadata and locks, firmware DMA/IOMMU mapping, MMIO memory, power resources, QMI client, SSR notifier, recovery flags, and pending CE IRQ bitmap.

Dependencies and integration points: Includes ath10k hardware, CE, and QMI headers plus Linux notifier types. It is shared between `snoc.c` and QMI/firmware notification paths.

Risks: Flag meanings (`REGISTERED`, `UNREGISTERING`, `MODEM_STOPPED`, `RECOVERY`, host-cap quirks) are cross-module coordination points; stale flag updates can cause double registration, skipped recovery, or incorrect WLAN disable. Pipe state embeds both CE and ath10k pointers, so teardown order matters.

Test signals: Compile SNOC builds, exercise firmware ready/down callbacks, CE pipe setup and cleanup, quirk parsing, and crash dump invocation through QMI/recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/snoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.c

Purpose: Implements optional ath10k spectral scan support, converting firmware PHY error FFT reports into relayfs sample records and providing debugfs controls for mode, sample count, and FFT bin count.

Important APIs and functions: Public functions are `ath10k_spectral_process_fft()`, `ath10k_spectral_start()`, `ath10k_spectral_vif_stop()`, `ath10k_spectral_create()`, and `ath10k_spectral_destroy()`. Internal helpers include `send_fft_sample()`, `get_max_exp()`, `ath10k_spectral_fix_bin_size()`, `ath10k_get_spectral_vdev()`, `ath10k_spectral_scan_trigger()`, and `ath10k_spectral_scan_config()`. Debugfs file operations back `spectral_scan_ctl`, `spectral_count`, and `spectral_bins`.

Control flow: WMI PHY error handling calls `ath10k_spectral_process_fft()`, which validates/fixes bin length, decodes FFT report registers, converts channel width to spectral sample conventions, fills an `fft_sample_ath10k`, interpolates the DC bin, and writes it to the relay channel. Debugfs writes under `conf_mutex` configure disabled/background/manual modes, trigger scans, or update count/bin settings. Creation opens a relay channel under the phy debugfs directory and creates control files; destroy closes the relay channel.

State and persistence: Mutates `ar->spectral.mode`, `ar->spectral.config.count`, `ar->spectral.config.fft_size`, `ar->spectral.rfs_chan_spec_scan`, and per-vif `spectral_enabled`. No durable persistence exists; settings reset in `ath10k_spectral_start()`.

Dependencies and integration points: Depends on `spectral_common.h`, ath10k debugfs state, WMI spectral enable/config commands, relayfs, and PHY error event parsing. It integrates with vif lifecycle through `ath10k_spectral_vif_stop()`.

Risks: FFT bin length, discard, and offset are hardware-parameter sensitive. The code rejects 80 MHz/64-bin samples due to known mismatch. Relay writes assume the generated TLV length fits the stack buffer. Debugfs commands require a valid vif and firmware WMI support; missing vifs return `-ENODEV`.

Test signals: Enable `CONFIG_ATH10K_SPECTRAL`, create/destroy debugfs files, switch disabled/background/manual modes, trigger scans, set invalid and valid bin counts, process 20/40/80 MHz FFT reports, verify DC interpolation and relay output, and stop a vif with active spectral scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.h

Purpose: Declares ath10k spectral scan mode/config types and feature-gated spectral APIs.

Important APIs and types: Defines `struct ath10k_spec_scan` with `count` and `fft_size`, `enum ath10k_spectral_mode`, and declarations or stubs for `ath10k_spectral_process_fft()`, `ath10k_spectral_start()`, `ath10k_spectral_vif_stop()`, `ath10k_spectral_create()`, and `ath10k_spectral_destroy()`.

Control flow, state, and persistence: The header has no state. With `CONFIG_ATH10K_SPECTRAL` disabled, all functions become no-op success stubs, preserving call-site simplicity.

Dependencies and integration points: Includes shared spectral sample definitions from `../spectral_common.h` and references ath10k/WMI PHY error types.

Risks: Stub behavior means feature-disabled builds silently ignore spectral data and setup. Any API signature drift must remain synchronized with `spectral.c` and WMI PHY error callers.

Test signals: Build with spectral enabled and disabled; verify callers compile and that disabled builds return success without creating debugfs/relay state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/spectral.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.c

Purpose: Implements ath10k firmware code swap support, allowing firmware code segments to reside in host DMA-coherent memory and communicating segment metadata to the target through BMI.

Important APIs and functions: Public functions are `ath10k_swap_code_seg_init()`, `ath10k_swap_code_seg_configure()`, and `ath10k_swap_code_seg_release()`. Internal helpers allocate coherent memory, parse the code-swap TLV/tail format, fill `ath10k_swap_code_seg_info`, and free the segment.

Control flow: Init checks firmware-provided code-swap data, allocates a bounded coherent buffer, parses one or more TLV payloads until a zero-length tail with a zeroed magic signature supplies the BMI write address, copies payload data into host memory, and stores the segment info on the firmware file. Configure writes the hardware info structure to the target address via BMI. Release frees coherent memory and clears code-swap fields from the firmware file.

State and persistence: State is attached to `fw_file->firmware_swap_code_seg_info`, with coherent virtual address, DMA address, target BMI write address, and hardware info fields. No durable persistence exists, but the target consumes the DMA bus address after BMI configuration.

Dependencies and integration points: Depends on ath10k core device DMA APIs, BMI memory write, firmware file parsing, and the code-swap structures declared in `swap.h`. Testmode UTF startup can also initialize/release code-swap firmware.

Risks: TLV length validation protects against malformed firmware blobs; a bad `size_log2` or DMA address truncation would break target fetches. Only one segment is supported. Release comments note that clearing `codeswap_data`/`codeswap_len` may be misplaced, which is a lifecycle risk if firmware ownership assumptions change.

Test signals: Firmware without code-swap data, valid code-swap TLV/tail parse, oversized image rejection, invalid TLV length, missing tail, BMI write failure, release after init failure, normal firmware startup, and UTF testmode startup with code-swap data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.h

Purpose: Defines firmware code-swap binary limits, packed TLV/tail/hardware-info structures, runtime segment state, and public code-swap lifecycle APIs.

Important APIs and types: Defines maximum swap binary length, magic size, maximum/supported segment counts, `ath10k_swap_code_seg_tlv`, `ath10k_swap_code_seg_tail`, `ath10k_swap_code_seg_item`, `ath10k_swap_code_seg_hw_info`, `ath10k_swap_code_seg_info`, and the init/configure/release prototypes.

Control flow, state, and persistence: No flow. The packed structures form the host/firmware ABI for code-swap metadata and DMA bus addresses.

Dependencies and integration points: References `struct ath10k_fw_file` and uses little-endian and DMA address types. Consumed by firmware loading, normal boot, and testmode UTF boot paths.

Risks: ABI packing and endianness must match firmware. `ATH10K_SWAP_CODE_SEG_NUM_SUPPORTED` is currently one despite room for 16 bus addresses, so adding multi-segment support requires implementation changes, not just constants.

Test signals: Compile firmware loader and testmode paths, validate structure sizes against firmware expectations, and boot firmware images with and without code-swap segments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/targaddrs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/targaddrs.h

Purpose: Defines target RAM host-interest addresses, the packed `host_interest` shared ABI, host-interest item offset macro, option/reset/ACS/power-save/WOW/SMPS bitfields, and board-data size constants for ath10k firmware coordination.

Important APIs and definitions: Key exports include `QCA988X_HOST_INTEREST_ADDRESS`, `HOST_INTEREST_MAX_SIZE`, `struct host_interest`, `HI_ITEM()`, host option bits, firmware mode/submode masks, SDIO ACS flags, SDIO crash dump enhancement flags, reset flags, console flags, WOW extension encode/decode macros, early allocation macros, power-save/SMPS macros, and board/ext-board data sizes for QCA988x/QCA6174/QCA9377/QCA99x0/QCA4019/WCN3990.

Control flow, state, and persistence: This header has no runtime flow. The structure layout and offsets are persistent firmware ABI: comments state fields must remain at fixed positions and additions belong at the end. Drivers access values through BMI or diagnostic windows during boot, SDIO start-post, crashdump, board-data upload, and feature negotiation.

Dependencies and integration points: Includes `hw.h` for target hardware definitions. It is used by SDIO, BMI/core firmware loading, board data setup, crash dumping, and host-interest feature/quirk negotiation.

Risks: Reordering or resizing `struct host_interest` breaks firmware compatibility. Some utility macros reference `HOST_INTEREST`, implying target-side use as well as host-side C use. Board-data constants must match firmware expectations. Misreading SDIO ACS or crashdump flags can route traffic to the wrong mailbox or choose an unsupported dump path.

Test signals: Boot each supported hardware family, board-data upload size checks, SDIO mailbox swap and reduced TX-completion acknowledgement, crashdump fast-dump negotiation, WOW/SMPS option programming, and compatibility with firmware revisions that add host-interest fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/targaddrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.c

Purpose: Implements nl80211 testmode support for ath10k UTF/FTM firmware, including firmware loading, UTF start/stop, raw WMI command injection, segmented TLV command transmission, and routing UTF WMI events back to userspace.

Important APIs and functions: Public entry points are `ath10k_tm_cmd()`, `ath10k_tm_event_wmi()`, and `ath10k_testmode_destroy()`. Major helpers handle unsegmented and segmented event emission, version replies, UTF firmware fetch (`ath10k_tm_fetch_firmware()`), UTF lifecycle (`ath10k_tm_cmd_utf_start()`, `__ath10k_tm_cmd_utf_stop()`), raw WMI sends, and TLV segmentation.

Control flow: `ath10k_tm_cmd()` parses netlink attributes, resets expected sequence state, and dispatches by command. UTF start requires the device to be OFF, fetches API 2 or legacy API 1 UTF firmware, reuses normal board/OTP data when needed, optionally initializes code-swap, enables `utf_monitor`, powers HIF in UTF mode, allocates an FTM event buffer, starts the core, and moves state to UTF. UTF stop reverses core/HIF/monitor/firmware/event-buffer state. WMI commands send user payloads directly with a provided WMI command ID. TLV commands segment up to `MAX_WMI_UTF_LEN` chunks into `wmi_ftm_cmd` frames and increment `ftm_msgref`. Incoming WMI events are consumed only while `utf_monitor` is set and are emitted through cfg80211 testmode, reassembling segmented FTM events into a bounded buffer.

State and persistence: Mutates `ar->state`, `ar->testmode.utf_monitor`, `expected_seq`, `data_pos`, `eventdata`, `ftm_msgref`, and `utf_mode_fw`. No durable persistence exists; firmware images are released on stop/destroy. `conf_mutex` protects lifecycle and command sends; `data_lock` protects event monitor state and segmented event buffer use.

Dependencies and integration points: Depends on cfg80211 testmode, netlink policies, ath10k firmware/core/HIF/WMI/TLV/swap layers, and normal firmware components for board/OTP reuse. It intercepts WMI events before normal mac80211 paths when UTF firmware is running.

Risks: Testmode exposes powerful firmware command injection and is only safe under `CONFIG_NL80211_TESTMODE`. Segmented event handling trusts sequence progression enough to append by current data position; out-of-order segments can produce bad user data though length is bounded. In `ath10k_tm_cmd_wmi()`, send failure path does not free the allocated skb locally, relying on WMI send ownership assumptions. UTF start failure unwinds several resources and must keep `utf_monitor`/firmware/code-swap/event buffer consistent.

Test signals: Get-version reply, UTF API 2 load and API 1 fallback, start while ON/UTF/OFF, stop while not UTF, raw WMI send with missing attrs, TLV segmentation across one and multiple chunks, segmented event reassembly boundaries, oversized event rejection, code-swap UTF firmware, destroy while UTF active, and builds with/without nl80211 testmode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.h

Purpose: Provides the public compile-time interface for ath10k nl80211 testmode support.

Important APIs and types: With `CONFIG_NL80211_TESTMODE`, declares `ath10k_testmode_destroy()`, `ath10k_tm_event_wmi()`, and `ath10k_tm_cmd()`. Without testmode, supplies inline no-op stubs returning no consumption or success.

Control flow, state, and persistence: The header owns no state. Its stubs let common call sites compile without ifdefs when testmode is disabled.

Dependencies and integration points: Includes `core.h` for ath10k/mac80211 types and is consumed by WMI event dispatch, cfg80211 testmode command registration, and teardown paths.

Risks: The disabled stub for `ath10k_tm_cmd()` returns success, so callers must ensure it is not exposed when cfg80211 testmode is unavailable. Prototype drift would break event consumption or command routing.

Test signals: Build both `CONFIG_NL80211_TESTMODE=y` and disabled configurations, verify WMI event paths do not consume events in disabled builds, and confirm cfg80211 testmode commands dispatch in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode_i.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode_i.h

Purpose: Defines the internal/userspace ath10k testmode ABI constants, netlink attributes, command numbers, and payload size limits.

Important APIs and types: Exports testmode version `1.0`, `ATH10K_TM_DATA_MAX_LEN`, `ATH_FTM_EVENT_MAX_BUF_LENGTH`, `enum ath10k_tm_attr`, and `enum ath10k_tm_cmd` values for get-version, UTF start/stop, raw WMI, and legacy TLV command mode.

Control flow, state, and persistence: No executable flow. The enum values are userspace ABI, including the intentional alias where `ATH10K_TM_CMD_TLV` shares value zero with get-version and is distinguished by presence of data.

Dependencies and integration points: Consumed by `testmode.c` netlink policy and userspace test tools using nl80211 testmode.

Risks: Changing enum values or versioning rules breaks userspace. The shared command value is subtle and requires parser logic to remain compatible. Payload limits must align with segmentation and event buffer code.

Test signals: Userspace compatibility tests for version reporting, command IDs, max input length enforcement, legacy TLV dispatch, and segmented FTM event buffer limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.c

Purpose: Implements ath10k thermal cooling and hwmon integration using firmware quiet-mode throttling and WMI temperature reads.

Important APIs and functions: Public functions are `ath10k_thermal_register()`, `ath10k_thermal_unregister()`, `ath10k_thermal_event_temperature()`, and `ath10k_thermal_set_throttling()`. It also defines `thermal_cooling_device_ops` callbacks and an hwmon `temp1_input` sysfs attribute.

Control flow: Registration checks `WMI_SERVICE_THERM_THROT`, creates a cooling device, adds a `cooling_device` symlink, initializes quiet period, and optionally registers an hwmon device if firmware and kernel config support temperature reads. Setting cooling state validates 0..100, stores the throttle state under `conf_mutex`, and sends WMI quiet-mode with duration as a percentage of quiet period when the device is ON. Reading temperature sends a WMI get-temperature command, waits up to five seconds for `wmi_sync`, and emits millidegrees Celsius. WMI temperature events store Celsius under `data_lock` and complete the waiter.

State and persistence: Mutates `ar->thermal.cdev`, `wmi_sync`, `throttle_state`, `quiet_period`, and `temperature`. No durable persistence exists; thermal state is runtime-only and depends on firmware service availability.

Dependencies and integration points: Uses Linux thermal cooling, sysfs, hwmon, ath10k WMI ops, firmware service map, `conf_mutex`, `data_lock`, and crash-flush flag handling.

Risks: Temperature reads fail when the device is off, during crash flush, or if firmware never completes the WMI request. Quiet-mode support depends on both service bit and WMI op presence. Unregister assumes a registered cooling device whenever the service bit is set, so partial registration failures need careful unwind.

Test signals: Register/unregister with and without thermal service, set throttle 0/50/100 and out of range, verify WMI quiet-mode parameters, read temperature success/timeout/offline/crash paths, hwmon disabled builds, and symlink cleanup after hwmon registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.h

Purpose: Defines ath10k thermal throttling constants, runtime thermal state, and feature-gated thermal APIs.

Important APIs and types: Defines quiet period defaults/minimum/start offset, hwmon name length, WMI sync timeout, max throttle percentage, `struct ath10k_thermal`, and declarations or no-op stubs for thermal register/unregister/event/throttling functions.

Control flow, state, and persistence: The header owns no flow. `struct ath10k_thermal` state is split between `conf_mutex`-protected throttle/quiet settings and `data_lock`-protected temperature.

Dependencies and integration points: Depends on Linux thermal reachability and ath10k core state. It is embedded in `struct ath10k` and used by WMI event handlers and device registration paths.

Risks: Stubbed disabled builds silently skip thermal support. Locking comments are part of the API contract; violating them can race sysfs, WMI events, and cooling callbacks.

Test signals: Compile with thermal enabled and disabled, validate structure initialization, WMI temperature event dispatch, and no-op behavior in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/trace.c

Purpose: Instantiates ath10k tracepoints by defining `CREATE_TRACE_POINTS`, including `trace.h`, and exporting the debug log tracepoint symbol.

Important APIs and functions: There are no normal functions. The file creates tracepoint definitions generated from `trace.h` and exports `__tracepoint_ath10k_log_dbg`.

Control flow, state, and persistence: No runtime control flow beyond tracepoint registration by the kernel tracing infrastructure. Tracepoint state is managed by ftrace/tracepoint core.

Dependencies and integration points: Depends on `trace.h`, Linux module/export support, and any ath10k file that calls `trace_ath10k_*` helpers. Exporting the debug tracepoint allows module visibility for debug logging.

Risks: This file must be compiled exactly once with `CREATE_TRACE_POINTS`; duplicate instantiation would cause link failures, while omission would leave unresolved tracepoint references when tracing is enabled.

Test signals: Build with `CONFIG_ATH10K_TRACING`, load the module, enable ath10k trace events in tracefs, and verify debug log tracepoint symbol export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/trace.h

Purpose: Defines ath10k trace events for logs, WMI commands/events/dbglog/diag, HTT stats/pktlog/TX, TX completion unref, frame headers/payloads, and HTT RX descriptors, with no-op stubs when ath10k tracing is disabled.

Important APIs and definitions: Provides `ath10k_frm_hdr_len()`, `TRACE_SYSTEM ath10k`, `ATH10K_MSG_MAX`, `DECLARE_EVENT_CLASS` templates for log/header/payload events, and `TRACE_EVENT`/`DEFINE_EVENT` instances such as `ath10k_log_err`, `ath10k_log_warn`, `ath10k_log_info`, `ath10k_log_dbg`, `ath10k_log_dbg_dump`, `ath10k_wmi_cmd`, `ath10k_wmi_event`, `ath10k_htt_stats`, `ath10k_wmi_dbglog`, `ath10k_htt_pktlog`, `ath10k_htt_tx`, `ath10k_txrx_tx_unref`, `ath10k_tx_hdr`, `ath10k_tx_payload`, `ath10k_rx_hdr`, `ath10k_rx_payload`, `ath10k_htt_rx_desc`, `ath10k_wmi_diag_container`, and `ath10k_wmi_diag`.

Control flow, state, and persistence: No persistent driver state. When tracing is disabled, macro overrides create inline no-op trace functions and `trace_*_enabled()` false helpers. When enabled, the header generates tracepoint metadata and dynamic-array copies for buffers.

Dependencies and integration points: Includes Linux tracepoint support and `core.h`; must be paired with `trace.c` for definition. It integrates with debug logging, WMI/HTT instrumentation, TX/RX paths, and tracefs consumers.

Risks: Dynamic array sizes use packet/buffer lengths, so callers must pass valid buffers. `ath10k_frm_hdr_len()` intentionally clamps header length to avoid short-frame overreads. Trace ABI changes can affect tooling that parses tracefs output. The custom `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` must remain correct for kernel trace generation.

Test signals: Build tracing enabled/disabled, enable each trace event class, send WMI/HTT traffic, trace short or FCS-error RX frames, verify payload/header splitting, and confirm no-op builds do not evaluate trace side effects unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.c

Purpose: Implements shared ath10k TX completion unreference/status reporting and HTT peer map/unmap bookkeeping used by RX/TX data paths.

Important APIs and functions: Public functions are `ath10k_txrx_tx_unref()`, `ath10k_peer_find()`, `ath10k_peer_find_by_id()`, `ath10k_wait_for_peer_created()`, `ath10k_wait_for_peer_deleted()`, `ath10k_peer_map_event()`, and `ath10k_peer_unmap_event()`. `ath10k_report_offchan_tx()` handles off-channel TX completion signaling.

Control flow: TX completion validates `msdu_id`, finds the pending skb under `htt->tx_lock`, decrements per-TXQ firmware queue count, frees the msdu ID, decrements pending TX, registers airtime, unmaps DMA for non-high-latency devices, completes any matching off-channel TX wait, fills mac80211 TX status flags based on HTT completion state and no-ack flags, reports ACK signal when valid, emits a tracepoint, and hands ownership to `ieee80211_tx_status_ext()`. Peer map events validate peer ID, find or allocate a peer under `data_lock`, add it to `ar->peers`, set `ar->peer_map[peer_id]`, set the peer bitmap, and wake waiters. Peer unmap clears the peer ID mapping, frees the peer when no IDs remain, and wakes waiters.

State and persistence: Mutates `htt->pending_tx`, HTT pending counters, TXQ `num_fw_queued`, skb DMA mappings, mac80211 TX status, `ar->offchan_tx_skb`, `ar->peer_map`, `ar->peers`, peer ID bitmaps, and `peer_mapping_wq`. State is runtime-only but must remain consistent across firmware HTT events and mac80211 queues.

Dependencies and integration points: Depends on ath10k core/HTT/MAC/debug, mac80211 TX status and airtime APIs, Linux IDR, DMA mapping, RCU, wait queues, and tracepoints from `trace.h`.

Risks: Invalid or duplicate firmware completion IDs can desynchronize pending TX. The code assumes send ownership and DMA mapping differ for high-latency buses. Off-channel completion guards against stale timeouts with pointer matching. Peer mapping updates require `data_lock`; callers relying on peer existence use a three-second wait and must handle crash flush.

Test signals: HTT TX completion ACK/NOACK/DISCARD, invalid and duplicate msdu IDs, high-latency versus DMA-unmap buses, airtime registration with TXQs, off-channel TX timeout race, peer map/unmap for multiple IDs per peer, out-of-range peer IDs, and wait-for-peer created/deleted timeout and crash-flush exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.h

Purpose: Declares shared ath10k TX completion and peer mapping APIs.

Important APIs and types: Exposes `ath10k_txrx_tx_unref()`, peer lookup helpers, peer create/delete wait helpers, and HTT peer map/unmap event handlers. It includes `htt.h` for HTT completion and peer event types.

Control flow, state, and persistence: No flow or state. The prototypes define how HTT event processing, MAC lifecycle, and data path code interact with TX completion and peer map state.

Dependencies and integration points: Consumed by HTT RX/TX event handlers and MAC peer lifecycle code. The APIs operate on `struct ath10k`, `struct ath10k_htt`, and firmware event payloads.

Risks: Callers of peer lookup helpers must hold `ar->data_lock`, as enforced in implementations. Misuse can race peer map/unmap events. TX unref ownership expectations must match HTT pending-ID allocation.

Test signals: Compile HTT event users, lockdep coverage around peer lookups, TX completion reporting, and peer wait helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.h -->
