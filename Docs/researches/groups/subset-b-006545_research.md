# Research: subset-b-006545

This grouped report covers the Intel SOF HDA platform files under `sources/distributed-fs/ceph-client/sound/soc/sof/intel/`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-mlink.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-mlink.c

Purpose: implements HDaudio multi-link and extended/alternate-link management for SOF HDA controllers when `CONFIG_SND_SOC_SOF_HDA_MLINK` is enabled. It discovers multi-link capability entries, models each as `struct hdac_ext2_link`, and exports helpers for SoundWire, SSP, DMIC, UAOL, and legacy HDA link power, synchronization, interrupt, stream mapping, offload, and microphone privacy handling.

Important APIs/types/functions: `struct hdac_ext2_link` extends `struct hdac_ext_link` with alternate-link metadata, capability flags, per-sublink refcounts, MMIO offsets, a shared `eml_lock`, and mic privacy state. `hda_bus_ml_init()` enumerates ML links from `bus->mlcap`; `hda_bus_ml_free()` releases them. Public helpers include `hdac_bus_eml_get_count()`, interrupt enable/check helpers, SoundWire sync helpers, `hdac_bus_eml_power_up*()`/`power_down*()`, `hdac_bus_eml_sdw_get/set_lsdiid*()`, `hdac_bus_eml_sdw_map_stream_ch()`, `hda_bus_ml_resume()`/`suspend()`, `hdac_bus_eml_*_get_hlink()`, `hdac_bus_eml_enable_offload()`, and mic privacy state helpers.

Control flow: enumeration reads `LCAP`/`LEPTR`, classifies regular versus alternate links, calculates SHIM/IP/vendor-specific offsets by `elid`, and adds links to `bus->hlink_list`. Power helpers locate a matching link, validate sublink range, adjust either the legacy link refcount or alternate sublink refcount, and only program SPA/CPA transitions on first get/last put. Synchronization helpers wrap LSYNCPRD/SYNCPU/CMDSYNC/SYNCGO registers and no-op when link sync is unsupported.

State and persistence: state is runtime-only in `bus->hlink_list`, `ref_count`, `sublink_ref_count[]`, and `mic_privacy_mask`. Suspend/resume only powers regular links based on refcounts; alternate-link callers are expected to reapply their own state. No persistent storage exists.

Dependencies and integration: depends on HDA register definitions and `sound/hda-mlink.h`; used by HDA probe, SoundWire, DAI, BPT, and LNL/ACE offload paths. Locking is split between locked and `_unlocked` exports so callers can batch operations with `hdac_bus_eml_get_mutex()`.

Risks and test signals: risks include negative/imbalanced refcounts, missing locking around `_unlocked` calls, unsupported `elid`, sublink mask validation, timeout-sensitive CPA/SYNCPU polling, and mic privacy state only being checked for active sublinks. Test by probing ML-capable ACE systems, suspend/resume, SoundWire stream channel mapping, offload enable/disable, mic privacy events, and failure injection for unsupported links/timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-mlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-pcm.c

Purpose: provides ALSA PCM-facing operations for generic Intel SOF HDA host DMA streams. It translates ALSA hw_params into HDA stream format fields, allocates a host DMA stream, configures BDL/SPIB policy, exposes pointer and ack callbacks, and releases streams on close.

Important APIs: `hda_dsp_get_mult_div()` and `hda_dsp_get_bits()` encode sample rate and width into SDnFMT bits. `hda_dsp_pcm_open()` selects a free `hdac_ext_stream`, applies runtime constraints, and stores `runtime->private_data`. `hda_dsp_pcm_hw_params()` sets `format_val`, buffer/period sizing, no-period-wakeup, calls `hda_dsp_stream_hw_params()`, configures SPIB depending on `disable_rewinds`, and reports `stream_tag`. `hda_dsp_pcm_trigger()`, `hda_dsp_pcm_pointer()`, `hda_dsp_pcm_ack()`, and `hda_dsp_pcm_close()` bridge ALSA callbacks to the lower stream engine.

Control flow: open finds the SOF PCM by DAI, adjusts pause/rewind/DMI-L1 flags from module parameters and PCM metadata, then calls `hda_dsp_stream_get()`. hw_params programs the stream descriptor and DMA format, while trigger delegates start/stop/pause to `hda_dsp_stream_trigger()`. Pointer prefers firmware IPC positions unless `hda->no_ipc_position` forces direct HDA position reads.

State and persistence: module parameters (`always_enable_dmi_l1`, `disable_rewinds`, `force_pause_support`) affect all streams for the module lifetime. Per-stream state lives in `hdac_stream` fields and the ALSA runtime private pointer.

Dependencies and integration: depends on `hda-stream.c`, SOF PCM objects, ASoC runtime lookup, and HDA format macros. It is exported in `SND_SOC_SOF_INTEL_HDA_COMMON` for platform ops and machine drivers.

Risks and test signals: risks include unsupported sample formats falling back silently, pause capability mismatches, stream leaks if close is skipped, SPIB behavior with rewinds disabled, and pointer source divergence. Test normal playback/capture, dspless S16/S32 constraints, no-period-wakeup, forced pause module parameter, disable-rewinds/appl_ptr ack, and IPC-position versus DPIB-position paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-probes.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-probes.c

Purpose: registers an HDA-backed SOF probes client that uses compressed capture streams for firmware/audio probes. It adapts the generic SOF probes client interface to HDA host DMA allocation, setup, trigger, and position accounting.

Important APIs: `hda_probes_register()` and `hda_probes_unregister()` register/unregister the `hda-probes` SOF client. `hda_probes_compr_startup()` obtains a capture/playback stream with `hda_dsp_stream_get()` and returns the stream tag. `hda_probes_compr_set_params()` programs S32 sample width, sample rate, channels, buffer, and period fields before calling `hda_dsp_stream_hw_params()`. `hda_probes_compr_trigger()` delegates to HDA stream trigger, and `hda_probes_compr_pointer()` reports `curr_pos`.

Control flow: startup allocates and binds `cstream->runtime->private_data`; set_params configures DMA; trigger starts/stops the descriptor; pointer is updated from interrupt-side compressed-byte accounting in `hda-stream.c`; shutdown puts the stream and clears private pointers.

State and persistence: runtime state is the compressed stream's private `hdac_ext_stream`, `hdac_stream->cstream`, `curr_pos`, and BDL/buffer fields. No persistent configuration is stored.

Dependencies and integration: depends on SOF client-probes, ALSA compressed stream APIs, and HDA stream exports. It is pulled into HDA client registration from `hda.c`.

Risks and test signals: risks include stream exhaustion (`-EBUSY`), format assumptions because compressed params lack bit depth, stale `private_data` on error, and correct `curr_pos` wrap accounting. Test client registration, probe capture start/stop, fragment elapsed callbacks, shutdown-after-failed-set_params, and stream reuse after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-sdw-bpt.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-sdw-bpt.c

Purpose: implements SoundWire Bulk Payload Transport helpers over HDA DMA. It prepares paired TX/RX HDA data streams, maps SoundWire channels, optionally programs IPC4 CHAIN_DMA when the DSP is active, starts asynchronous transfer, waits for IOC completion, and tears down resources.

Important APIs: `hda_sdw_bpt_get_buf_size_alignment()` computes FIFO-safe buffer alignment from requested bandwidth. `hda_sdw_bpt_open()` prepares playback and capture streams and writes PCMSyCM channel mapping. `hda_sdw_bpt_send_async()` starts both DMAs. `hda_sdw_bpt_wait()` waits up to `HDA_BPT_IOC_TIMEOUT_MS`, checks flushed positions, disables both DMAs, and returns timeout/disable errors. `hda_sdw_bpt_close()` deprepares streams. Internal `chain_dma_trigger()` sends IPC4 global CHAIN_DMA messages for RUNNING/PAUSED/RESET.

Control flow: open calculates channel counts from bandwidth at 192 kHz/32-bit, calls `hda_data_stream_prepare(... pair=true)`, decouples host/link DMA for DSP mode, and sets stream IDs on SoundWire playback links. send_async starts TX then RX, rolling TX back if RX fails. wait blocks on per-stream `ioc` completions produced by the stream IRQ path, verifies positions return to zero, then disables RX and TX. close deprepares RX then TX and releases CHAIN_DMA/resources.

State and persistence: state is limited to the two `hdac_ext_stream` objects, supplied BDL DMA buffers, PCMSyCM register mapping, link stream ID, and IPC4 CHAIN_DMA allocation. No state persists across close.

Dependencies and integration: depends on `hda_data_stream_prepare/cleanup`, `hda_cl_trigger`, `hdac_bus_eml_sdw_map_stream_ch()`, SoundWire multi-link helpers, SOF IPC4, and dspless mode checks.

Risks and test signals: risks include BPT requiring IPC4 for DSP mode, mismatched bandwidth-to-channel rounding, partially prepared TX/RX cleanup, IOC timeout, position flush timeout, paired stream link lock leaks, and incorrect PDI indices. Test BPT firmware transfers in dspless and DSP modes, forced failures at RX prepare/start, CHAIN_DMA reset on close, buffer alignment, and repeated open/send/wait/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-sdw-bpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-stream.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-stream.c

Purpose: is the lower HDA host DMA stream engine for SOF. It allocates and frees stream descriptors, builds BDLs, programs stream registers, controls SPIB/position reporting, handles start/stop/reset, dispatches stream interrupts, and supports both ALSA PCM and non-PCM data transfers such as firmware loading, tracing, probes, and BPT.

Important APIs: `hda_dsp_stream_init()` reads GCAP, allocates position/RIRB buffers and per-stream BDLs, and constructs `struct sof_intel_hda_stream` objects. `hda_dsp_stream_get()`/`pair_get()` and `put()`/`pair_put()` manage stream ownership and DMI L1 compatibility. `hda_dsp_stream_setup_bdl()` builds little-endian BDL entries with 4K boundary handling and IOC policy. `hda_dsp_stream_hw_params()`, `hda_dsp_iccmax_stream_hw_params()`, `hda_dsp_stream_trigger()`, and `hda_dsp_stream_hw_free()` program/reset/start/stop streams. Position and diagnostic exports include `hda_dsp_stream_get_position()`, `hda_dsp_get_stream_llp()`, and `hda_dsp_get_stream_ldp()`. `hda_data_stream_prepare()`/`cleanup()` wrap temporary raw DMA transfers.

Control flow: init creates stream objects ordered by capture then playback. Allocation scans `bus->stream_list` under `reg_lock`, marks `opened`, optionally locks paired link use, and applies DMI-L1 workaround on older IP. hw_params decouples host/link DMA when needed, clears RUN/STS, resets the stream, programs tag/CBL/FMT/LVI/BDL/posbuf/interrupts, then caches FIFO size. Interrupt handling reads INTSTS, clears per-stream STS, completes raw DMA `ioc`, reports PCM period elapsed when direct positions are used, or updates compressed stream byte counts. Cleanup disables SPIB/RUN, releases stream ownership, zeros BDL pointers/registers, and frees nonpersistent DMA buffers.

State and persistence: runtime state lives in `bus->stream_list`, per-stream `opened`, `running`, `link_locked`, `host_reserved`, BDL DMA pages, posbuf, SPIB/FIFO MMIO addresses, `curr_pos`, and `ioc` completions. Module parameter `position_quirk` selects position source for the module lifetime.

Dependencies and integration: used by PCM, compressed probes, trace, code loader, BPT, DAI code, and IRQ thread in `hda.c`. It depends on `sof_intel_hda_dev->no_ipc_position`, chip quirks, HDA/PP/SPIB bars, SOF IPC4 stream counts, and codec RIRB status handling.

Risks and test signals: risks include stream leaks, race-sensitive `opened`/`running` updates, uninitialized `link_stream` if paired put is misused, BDL entry limits, period_bytes zero split behavior, RUN/reset timeouts, DMI L1 disable/restore, position quirks, and raw DMA completion assumptions. Test stream allocation exhaustion, paired stream cleanup, firmware load DMA, trace DMA, PCM xrun/pause/stop, position quirk modes, compressed probes, suspend cleanup, and IRQ storms/missed interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-trace.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-trace.c

Purpose: provides DMA trace stream lifecycle support for SOF HDA platforms. It reserves a capture HDA stream, configures the trace DMA buffer, exposes its stream tag to firmware, triggers trace start/stop, and releases the stream.

Important APIs: `hda_dsp_trace_init()` obtains a DMI-L1-compatible capture stream and fills `sof_ipc_dma_trace_params_ext.stream_tag`; `hda_dsp_trace_prepare()` programs buffer size and calls `hda_dsp_stream_hw_params()`; `hda_dsp_trace_trigger()` delegates to `hda_dsp_stream_trigger()`; `hda_dsp_trace_release()` returns the stream.

Control flow: init allocates the stream first, then prepares BDL/registers. If prepare fails, it immediately puts the stream, clears `hda->dtrace_stream`, and resets stream_tag. Trigger assumes init succeeded and uses the stored stream. Release is idempotent only in the sense that it returns `-ENODEV` if no stream is open.

State and persistence: `sof_intel_hda_dev->dtrace_stream` is the only persistent runtime pointer. Buffer ownership belongs to the caller-supplied DMA buffer.

Dependencies and integration: relies on stream allocation/programming exports in `hda-stream.c` and is declared in `hda.h` for SOF trace ops.

Risks and test signals: risks include trigger-before-init null dereference, stream exhaustion, trace stream not released on higher-level error, and capture stream competition with PCM/probes. Test trace init/trigger/release, prepare failure cleanup, repeated trace sessions, and interaction with runtime PM/DMI L1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda.c

Purpose: is the generic Intel SOF HDA integration hub. It owns early PCI/HDA bus setup, DSP probe/remove, IRQ registration and dispatch, SoundWire ACPI/probe/startup, HDA codec/i915 cooperation, machine-driver and topology selection, client registration, and common pre/post firmware hooks.

Important APIs: `hda_dsp_probe_early()` validates PCI class, allocates `sof_intel_hda_dev`, maps the HDA BAR, initializes i915 and controller caps. `hda_dsp_probe()` registers DMIC, maps DSP BAR when not dspless, initializes streams, allocates MSI/legacy IRQ, initializes HDA/ML/SoundWire/codec capabilities, enables PP capability, and stores NHLT data. `hda_dsp_remove()` and `hda_dsp_remove_late()` unwind resources. SoundWire APIs include `sdw_callback`, ACE2.x callbacks, `hda_sdw_startup()`, IRQ/wake helpers, and mic privacy dispatch. `hda_machine_select()` selects I2S/DMIC, SoundWire, or generic HDA machines and fixes topology filenames using NHLT, codec, amp, DMIC, SSP, BT, and module parameters. `hda_pci_intel_probe()` gates SOF ownership through `snd_intel_dsp_driver_probe()`.

Control flow: probe_early sets the HDA bus base and controller caps. probe then initializes DMA/streams and IRQs before `hda_init_caps()` resets/starts the controller, enumerates multi-links, scans/probes SoundWire, probes HDA codecs, and powers down display if unused. The top-half IRQ disables global interrupts and wakes the thread; the thread handles stream/controller, IPC, SoundWire, wake, mic privacy, and codec state changes before re-enabling global interrupts. Machine selection tries ACPI machine tables, then SoundWire default generation for ACE2+, then HDA generic fallback.

State and persistence: state is held in `sof_intel_hda_dev`: descriptor, DMIC platform device, SDW context/ACPI info, NHLT table, trace stream, code-loading flags, delayed IPC pointer, IMR boot flags, D0i3 work, wait queue, and mic privacy work. Module parameters influence MSI, model, DMIC count, SSP MCLK, BT link mask, and SoundWire clock-stop quirks.

Dependencies and integration: integrates PCI SOF core, ASoC ACPI match tables, SoundWire Intel core, HDA codec/i915 helpers, NHLT parsing, multi-link helpers, stream engine, IPC ops selected by platform files, debugfs, and SOF clients.

Risks and test signals: risks include complex probe error unwinding, IRQ re-enable ordering, SoundWire link mask and generated default machine correctness, topology filename fixup conflicts, dspless versus DSP mode branch coverage, duplicate SoundWire startup on ACE2+ paths, and stale delayed work. Test PCI probe/remove on HDA-only, HDA+DMIC, I2S, SoundWire, mixed codec systems; MSI fallback; nocodec/debug module parameters; suspend/runtime PM; wake IRQs; generated SoundWire machines; and failure injection at stream/IRQ/SoundWire/i915/NHLT steps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda.h

Purpose: central public/private contract header for Intel SOF HDA support. It defines register offsets, bit masks, timeout constants, stream/data structures, helper conversions, exported function prototypes, SoundWire/codec stubs, platform descriptor externs, and DAI widget DMA operation hooks shared by the Intel HDA SOF files.

Important APIs/types: `struct sof_intel_dsp_bdl` describes BDL entries. `struct sof_intel_hda_dev` is the main HDA-private state embedded behind `sdev->pdata->hw_pdata`. `struct sof_intel_hda_stream` wraps `hdac_ext_stream` with SOF device pointer, host reservation, flags, and IOC completion. Inline helpers `sof_to_bus()`, `sof_to_hbus()`, `hstream_to_sof_hda_stream()`, and `bus_to_sof_hda()` define object relationships. `struct hda_dai_widget_dma_ops` abstracts DAI-specific DMA assignment, trigger, codec stream, format, and link operations.

Control flow role: this file does not execute logic, but it shapes control flow by declaring every HDA platform operation used by PCI descriptors, common ops, PCM/stream/probe/trace modules, code loaders, IPC handlers, power management, SoundWire support, codec/i915 integration, and machine selection.

State and persistence: state definitions include DMA buffers retained for firmware load, IMR boot flags, D0i3 work, SDW context, NHLT pointer, mic privacy work, delayed IPC message, and stream completions. Constants define module-wide behavior such as stream limits, BDL size, position quirks, and D0i3 delay.

Dependencies and integration: imports Linux completion/SoundWire/HDA/compress headers and SOF internals. Conditional inline stubs let the same code compile when HDA codec, HDMI/i915, probes, or SoundWire support is disabled.

Risks and test signals: risks include stale register definitions, mismatched prototypes across platform files, conditional stub behavior hiding missing feature coverage, stream/container assumptions, and ABI-like expectations from exported namespaces. Test signals are build coverage across config matrices, sparse/compile warnings, all platform PCI modules, and runtime validation of register offsets on multiple hardware generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/icl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/icl.c

Purpose: provides Ice Lake-specific SOF HDA DSP ops and chip descriptor. It layers ICL power/firmware behavior over common HDA ops, with IPC3/IPC4 selection and HPRO core handling.

Important APIs: `sof_icl_ops_init()` copies `sof_hda_common_ops`, selects IPC3 CNL or IPC4 CNL handlers, allocates IPC4 private data when needed, sets debug maps, post-fw-run, ICCMAX code-loader boot, stall callback, core_get, and DAI ops. `icl_dsp_post_fw_run()` starts SoundWire on first boot, marks IMR boot support if firmware reports D3 persistent, enables SDW interrupts, powers/stalls core 3 for HPRO mode, and reenables clock/power gating. `icl_chip_info` describes cores, IPC registers, ROM status, SSP/SDW bases, callbacks, and platform string.

Control flow: ops_init runs during PCI descriptor setup; firmware boot later calls post_fw_run, which conditionally performs first-boot SoundWire/IMR setup and always restores clock gating. `icl_dsp_core_stall()` masks requested cores to host-managed cores before setting CSTALL.

State and persistence: updates global `sof_icl_ops`, `sdev->private` for IPC4, `enabled_cores_mask`, core refcount for core 3, and `hdev->imrboot_supported`.

Dependencies and integration: depends on HDA common ops, CNL IPC handlers, IPC4 firmware data, SoundWire startup, and code loader helpers.

Risks and test signals: risks include static ops mutation across devices, IPC type branch coverage, core 3 HPRO power/refcount imbalance, and IMR support detection. Test ICL/JSL probe with IPC3 and IPC4, first/subsequent boot, LPRO/HPRO configs, SoundWire startup failure, and core stall validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/icl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.c

Purpose: adapts Meteor Lake-style IPC4 HDA ops for Lunar Lake/ACE2 with extended multi-link offload, SoundWire IRQ differences, and LNL chip descriptor data.

Important APIs: `sof_lnl_set_ops()` starts from `sof_mtl_set_ops()`, then overrides probe/remove/resume/runtime_resume to enable DMIC/SSP offload and overrides `post_fw_run`. `lnl_dsp_check_sdw_irq()`, `lnl_dsp_disable_interrupts()`, and `lnl_sdw_check_wakeen_irq()` provide descriptor callbacks. `lnl_chip_info` defines five cores, ACE2 IP version, LNL ROM status register, extended SoundWire link-count checks, MTL boot/power helpers, and LNL-specific IRQ hooks.

Control flow: probe/resume first runs common HDA behavior and then enables offload on SSP and DMIC alternate links with `hdac_bus_eml_enable_offload()`. remove disables offload before common remove. post_fw_run marks IMR boot support and creates `skip_imr_boot` debugfs without starting SoundWire again.

State and persistence: modifies multi-link offload register state, `imrboot_supported`, debugfs bool, and static ops passed by caller. No separate persistent LNL state is introduced.

Dependencies and integration: depends on `mtl.c`, `hda-mlink.c`, SoundWire global WAKESTS behavior, and HDA common probe/PM.

Risks and test signals: risks include offload enable/disable errors during PM, dspless path skipping overrides, wake IRQ detection range, and inherited MTL behavior mismatches. Test LNL probe/remove/runtime resume, offload bits for DMIC/SSP, SoundWire IRQ/wake, IMR boot debugfs, and dspless mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.h

Purpose: declares Lunar Lake-specific register offsets and exported helper prototypes used by LNL/NVL/PTL-adjacent SOF HDA code.

Important APIs/types: defines `LNL_DSP_REG_HFDSC` and `LNL_DSP_REG_HFDEC` for DSP core0 status/error, plus prototypes for `sof_lnl_set_ops()`, `lnl_dsp_check_sdw_irq()`, `lnl_dsp_disable_interrupts()`, and `lnl_sdw_check_wakeen_irq()`.

Control flow: no runtime logic; it enables PCI/platform files and later-generation descriptors to reuse LNL SoundWire and interrupt helpers.

State and persistence: none.

Dependencies and integration: consumed by `lnl.c` and `nvl.c`; relies on `struct snd_sof_dev` and `struct snd_sof_dsp_ops` declarations from included compilation units.

Risks and test signals: risks are limited to register offset drift and prototype mismatches. Build all LNL/NVL/PTL modules and verify ROM status/error dumps use the expected addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.c

Purpose: implements Meteor Lake/ACE IPC4 HDA DSP operations, interrupt control, firmware boot preparation, core power management, IPC send/thread handling, debug dump support, and MTL/ARL chip descriptors.

Important APIs: `sof_mtl_set_ops()` copies common HDA ops, installs MTL IPC thread/send/mailbox/window/debug/pre-post-fw/core ops, allocates `sof_ipc4_fw_data`, enables context save/library loading, and sets DAI ops. `mtl_enable_interrupts()`, `mtl_enable_ipc_interrupts()`, and `mtl_disable_ipc_interrupts()` manage host IPC/SoundWire interrupt masks. `mtl_dsp_pre_fw_run()` powers DSP subsystem/gated domains and ungates SoundWire I/O. `mtl_dsp_cl_init()` sends ROM purge/boot IPC, powers primary core, waits for ROM status, enables interrupts, and dumps on final failure. `mtl_ipc_irq_thread()` handles DONE replies, BUSY target messages, notifications, and delayed IPC resend. `mtl_power_down_dsp()` powers down core and subsystem.

Control flow: boot calls pre_fw_run, then code loader `cl_init`, then post_fw_run. IPC send writes mailbox payload, extension, then primary|BUSY unless TX is busy, in which case the message is stored in `hdev->delayed_ipc_tx_msg`. The IPC IRQ thread acknowledges DSP replies, processes FW/host messages, and retries delayed sends after ACK. Core_get/put powers primary core locally and delegates secondary core state to IPC PM ops.

State and persistence: persistent runtime state includes `sdev->private` IPC4 data, `delayed_ipc_tx_msg`, core masks/refcounts, IMR flags, and interrupt mask registers. Debugfs map exposes HDA/PP/DSP/fw_regs regions.

Dependencies and integration: used by PCI MTL/ARL and inherited by LNL/NVL/PTL layers. Depends on HDA common ops, IPC4 helpers, telemetry dump, SoundWire callbacks, and MTL register definitions in `mtl.h`.

Risks and test signals: risks include delayed IPC pointer lifetime, interrupt mask ordering, primary core ownership/power polling, ROM status timing workaround, dspless early returns, and final-attempt dump gating. Test firmware boot cold/IMR, IPC request/reply/notification/delayed send, PM core_get/put, SoundWire IRQ, ARL-S descriptor selection, and probe failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.h

Purpose: defines Meteor Lake/ACE register offsets, bit masks, SRAM/mailbox windows, ROM state codes, IMR flags, and prototypes for MTL helper functions used by MTL, ARL, LNL, NVL, and PTL-derived platform code.

Important APIs: register groups cover DSP subsystem power (`MTL_HFDSSCS`), power-gated domains (`MTL_HFPWRCTL*`/`PTL_HFPWRCTL2`), interrupt IP pointer, HDA D0i3, primary core controls, IPC initiator/target registers, host IPC/SoundWire interrupt enables, IRQ status, SRAM windows, ROM status/error registers, and ROM FSR state codes. Prototypes export IPC IRQ check, interrupt enable/disable, DSP power down, code-loader init, and `sof_mtl_set_ops()`.

Control flow role: no executable flow, but the constants are directly consumed by `mtl.c` boot, IPC, IRQ, and power sequences and by later platforms that reuse MTL helpers.

State and persistence: none in the header; constants identify hardware state registers used elsewhere.

Dependencies and integration: requires Linux bit macros through including files. Shared by MTL and descendants, so changes affect multiple PCI modules.

Risks and test signals: risks include wrong offsets across ACE generations and using PTL versus MTL power registers incorrectly. Test by building MTL/LNL/NVL/PTL, validating MMIO access does not read `U32_MAX`, and checking firmware boot/IRQ paths on each generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.c

Purpose: adds Nova Lake chip descriptors and ops binding for SOF HDA. It reuses Panther Lake ops while supplying NVL/NVL-S core counts and ACE4 descriptor metadata.

Important APIs: `sof_nvl_set_ops()` delegates directly to `sof_ptl_set_ops()`. `nvl_chip_info` and `nvl_s_chip_info` define four-core and two-core variants with ACE4 IP version, LNL ROM status register, MTL IPC registers, extended SoundWire lcount, LNL SDW/wake/interrupt callbacks, MTL boot/power helpers, and platform string `nvl`.

Control flow: PCI NVL descriptors call `sof_nvl_set_ops()` during probe, causing PTL-derived ops to be installed while `hda.c` uses the NVL chip descriptor for register offsets and feature decisions.

State and persistence: no private state; runtime state is inherited from HDA/MTL/PTL paths.

Dependencies and integration: depends on MTL, LNL, PTL, HDA common, IPC4, and multi-link/SoundWire definitions.

Risks and test signals: risks include assuming PTL ops fully match NVL, descriptor copy/paste errors between NVL and NVL-S, and ACE4-specific stream alignment/BT topology paths. Test both PCI IDs, firmware path selection, SoundWire, PM, IPC, dspless mode, and core count behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.h

Purpose: declares the Nova Lake ops initializer used by the NVL PCI module.

Important APIs: `sof_nvl_set_ops(struct snd_sof_dev *sdev, struct snd_sof_dsp_ops *dsp_ops)`.

Control flow: no executable code; it lets `pci-nvl.c` call the NVL ops setup while keeping implementation in `nvl.c`.

State and persistence: none.

Dependencies and integration: included by `pci-nvl.c` and `nvl.c`; implementation imports PTL namespace.

Risks and test signals: build coverage is the main signal. Any signature change must be synchronized with `pci-nvl.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-apl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-apl.c

Purpose: PCI binding module for Apollo Lake/Broxton and Gemini Lake SOF HDA devices.

Important APIs: defines `bxt_desc` and `glk_desc` `struct sof_dev_desc` entries with ACPI machine tables, APL chip info, IPC3+IPC4 support, dspless support, firmware/library/topology defaults, nocodec topology, `sof_apl_ops`, `sof_apl_ops_init`, and `hda_ops_free`. `sof_pci_ids` maps `HDA_APL` and `HDA_GLK` IDs. The `pci_driver` uses `hda_pci_intel_probe`, `sof_pci_remove`, and `sof_pci_shutdown`.

Control flow: module registration exposes the PCI IDs; probe is delegated to common HDA PCI selection and SOF PCI core, which then uses the descriptor for ops and firmware selection.

State and persistence: static descriptors and PCI ID table only.

Dependencies and integration: imports SOF PCI device helpers, APL HDA ops, Intel ACPI match tables, and HDA generic/common namespaces.

Risks and test signals: risks include wrong default firmware/topology paths, IPC default mismatch, or descriptor ops mismatch. Test APL/GLK PCI match, IPC3 default boot, IPC4 AVS firmware path, dspless mode, nocodec topology, and remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-apl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-cnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-cnl.c

Purpose: PCI binding module for Cannon Lake, Coffee Lake, and Comet Lake SOF HDA devices.

Important APIs: descriptor variants `cnl_desc`, `cfl_desc`, and `cml_desc` share CNL chip info/ops and IPC3 default with IPC4 support, dspless support, ACPI target states, firmware/library/topology paths, nocodec topology, and SoundWire alternate machine tables. `sof_pci_ids` maps LP/H/S PCI IDs to the appropriate descriptor. The PCI driver delegates probe/remove/shutdown to common SOF HDA/PCI helpers.

Control flow: PCI match selects a descriptor, `hda_pci_intel_probe()` confirms SOF ownership, and common probe consumes machine tables and firmware defaults.

State and persistence: static descriptors and ID table only.

Dependencies and integration: integrates CNL ops, HDA generic/common, SOF PCI core, and Intel ACPI machine tables including SoundWire variants.

Risks and test signals: risks are descriptor-level: wrong firmware name per SKU, alt machine mismatch, IPC4 AVS path coverage, and dspless selection. Test each PCI ID, machine matching with/without SoundWire, IPC3/IPC4 boot, and nocodec/dspless behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-cnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-icl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-icl.c

Purpose: PCI binding module for Ice Lake and Jasper Lake/N-series SOF HDA devices.

Important APIs: `icl_desc` uses ICL chip info, ICL ops, IPC3 default with IPC4 support, ICL machine and SoundWire alternate tables. `jsl_desc` uses JSL chip info but CNL ops/init, with IPC3 default and IPC4 AVS paths. `sof_pci_ids` maps ICL LP/H and ICL_N/JSL_N IDs. The PCI driver uses common HDA PCI probe and SOF PCI remove/shutdown.

Control flow: descriptor choice determines whether ICL-specific post-fw-run/HPRO behavior or CNL-derived JSL behavior is installed by SOF core.

State and persistence: static descriptors and ID table only.

Dependencies and integration: depends on ICL/CNL ops namespaces, HDA generic/common, SOF PCI, and ACPI match tables.

Risks and test signals: risks include JSL using CNL ops with JSL chip info, IPC type fallback, SoundWire alt machines on ICL only, and firmware path accuracy. Test all PCI IDs, IPC3 and IPC4 paths, ICL SoundWire, JSL no-alt-machine path, dspless/nocodec, and remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-icl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-lnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-lnl.c

Purpose: PCI binding module for Lunar Lake SOF HDA devices.

Important APIs: local static `sof_lnl_ops` is initialized by `sof_lnl_ops_init()` through `sof_lnl_set_ops()`. `lnl_desc` enables ACPI target states, LNL/SDW machine tables, LNL chip info, IPC4-only support, dspless and on-demand DSP boot, SOF IPC4 firmware/library/topology paths, and nocodec topology. PCI IDs currently map `HDA_LNL_P`.

Control flow: PCI probe selects `lnl_desc`; ops init creates an MTL-derived ops table with LNL overrides; common HDA probe handles on-demand boot/dspless branches.

State and persistence: static ops, descriptor, and ID table only.

Dependencies and integration: imports `lnl.h`, HDA generic/common, SOF PCI, and ACPI match tables.

Risks and test signals: risks include static ops shared across devices, on-demand DSP boot interactions with BPT/PCM, and descriptor firmware path mismatch. Test LNL PCI match, on-demand firmware boot, dspless mode, SoundWire machine matching, nocodec, and PM resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-lnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-mtl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-mtl.c

Purpose: PCI binding module for Meteor Lake and Arrow Lake SOF HDA devices.

Important APIs: `sof_mtl_ops_init()` installs MTL ops into static `sof_mtl_ops`. `mtl_desc`, `arl_desc`, and `arl_s_desc` specify ACPI target states, machine/SDW tables, chip info (`mtl_chip_info` or `arl_s_chip_info`), IPC4-only support, dspless support, SOF IPC4 firmware/library/topology paths, nocodec topology, ops init/free, and SKU-specific firmware names. PCI IDs map MTL, ARL-S, and ARL devices.

Control flow: common PCI probe selects a descriptor by device ID; SOF core initializes MTL ops; HDA common code consumes chip info for stream alignment, SoundWire, boot, and topology behavior.

State and persistence: static ops table, descriptors, and ID table.

Dependencies and integration: depends on `mtl.h`, HDA common/generic, SOF PCI, and Intel ACPI match tables.

Risks and test signals: risks include ARL versus ARL-S descriptor mixups, static ops reuse, firmware path mismatches, and dspless/IPC4-only assumptions. Test each PCI ID, MTL/ARL firmware selection, SoundWire alt machine selection, dspless mode, remove/shutdown, and PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-mtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-nvl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-nvl.c

Purpose: PCI binding module for Nova Lake and Nova Lake-S SOF HDA devices.

Important APIs: static `sof_nvl_ops` is initialized via `sof_nvl_set_ops()`. `nvl_desc` and `nvl_s_desc` define ACPI target states, NVL/SDW machine tables, NVL or NVL-S chip info, IPC4-only support, dspless and on-demand DSP boot, SOF IPC4 firmware/library/topology paths, and nocodec topology. PCI IDs map `HDA_NVL` and `HDA_NVL_S`.

Control flow: PCI match selects core-count/SKU descriptor; ops init delegates to PTL-derived ops through `nvl.c`; common HDA probe handles the rest.

State and persistence: static ops, descriptors, and PCI ID table.

Dependencies and integration: imports `nvl.h`, HDA common/generic, SOF PCI, and NVL ACPI match tables.

Risks and test signals: risks include descriptor comments/names drifting, PTL op compatibility, on-demand boot regressions, and NVL-S core count handling. Test both IDs, firmware path selection, SoundWire matching, dspless and on-demand boot, PM, and removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-nvl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-ptl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-ptl.c

Purpose: PCI binding module for Panther Lake and Wildcat Lake SOF HDA devices.

Important APIs: static `sof_ptl_ops` is initialized by `sof_ptl_set_ops()`. `ptl_desc` and `wcl_desc` provide ACPI target states, PTL/SDW machine tables, PTL/WCL chip info, IPC4-only support, dspless and on-demand DSP boot, SOF IPC4 firmware/library/topology paths, and nocodec topology. PCI IDs map PTL, PTL-H, and WCL.

Control flow: device ID selects PTL or WCL descriptor; ops init installs PTL platform ops; common HDA PCI probe and SOF core consume descriptor data.

State and persistence: static ops, descriptors, and ID table.

Dependencies and integration: imports `ptl.h`, HDA generic/common, SOF PCI, and Intel ACPI match tables. NVL reuses PTL ops via `nvl.c`.

Risks and test signals: risks include WCL using PTL machine/nocodec topology, PTL-H descriptor coverage, on-demand boot, and ops reuse by NVL. Test all IDs, firmware path selection, SoundWire, dspless, on-demand boot, and PM/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-ptl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-skl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-skl.c

Purpose: PCI binding module for Skylake and Kaby Lake SOF HDA devices using AVS/IPC4-only firmware support.

Important APIs: `skl_desc` and `kbl_desc` specify SKL chip info, SKL ops/init/free, IPC4-only support, dspless mode, firmware/topology paths, nocodec topology, and machine tables. PCI IDs map SKL_LP and KBL_LP. The `pci_driver` delegates to common HDA PCI probe/remove/shutdown and SOF PCI PM.

Control flow: PCI match selects SKL or KBL firmware path and machine table; common HDA probe handles driver ownership and generic stream/codec setup.

State and persistence: static descriptors and ID table only.

Dependencies and integration: depends on SKL HDA ops, HDA common/generic, SOF PCI, and ACPI match tables.

Risks and test signals: risks include IPC4-only assumption on older platforms, firmware path differences, and missing ACPI target state use compared with newer descriptors. Test SKL/KBL PCI IDs, AVS firmware boot, dspless/nocodec, machine matching, and remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-skl.c -->
