# Research: subset-b-006543

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-utils-test.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-utils-test.c

Purpose: KUnit coverage for the ASoC bit-clock helpers in `soc-utils.c`, especially `snd_soc_tdm_params_to_bclk()` and the simpler `snd_soc_params_to_bclk()`.

Important APIs/types/functions: the test data table encodes sample rate, PCM format, channel count, optional TDM slot width/count, optional slot multiple, and expected BCLK. `test_tdm_params_to_bclk_one()` constructs a `snd_pcm_hw_params`, pins rate/channels/format, calls `snd_soc_tdm_params_to_bclk()`, and asserts the expected result. `test_tdm_params_to_bclk()` iterates all cases and also verifies that `slot_multiple == 1` behaves like no multiple. `test_snd_soc_params_to_bclk_one()` and `test_snd_soc_params_to_bclk()` cover the non-TDM override path.

Control flow: the suite is table-driven. Hardware params are initialized with `_snd_pcm_hw_params_any()`, constrained through ALSA helpers, and passed to the exported utility functions. Cases cover raw params-only BCLK, I2S-style rounding to a multiple of 2, fixed slot count, fixed slot width, and combined fixed slot width/count.

State and persistence: no persistent state. All `snd_pcm_hw_params` objects are stack-local. KUnit registers the suite through `kunit_test_suites()`.

Dependencies and integration points: depends on KUnit, ALSA PCM params helpers, and the ASoC utility exports. The tests are tied to PCM format bit widths and to the TDM helper's rounding semantics.

Risks: the table only uses valid PCM formats, so negative/error paths for invalid formats are not covered. Arithmetic overflow is not stressed. The tests assume unsigned comparison after converting `got_bclk`, which is fine for success cases but would obscure negative values if an error case were added.

Test signals: strong regression signal for expected BCLK math across common rates, formats, channels, slot widths/counts, and I2S slot rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-utils-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-utils.c

Purpose: common ALSA SoC utility helpers plus registration of the built-in dummy codec/platform used by machine drivers that need placeholder components.

Important APIs/types/functions: `snd_soc_ret()` filters expected negative returns and logs unexpected errors. `snd_soc_calc_frame_size()`, `snd_soc_params_to_frame_size()`, `snd_soc_calc_bclk()`, `snd_soc_params_to_bclk()`, and `snd_soc_tdm_params_to_bclk()` provide frame and bit-clock arithmetic. Dummy component definitions include `dummy_dma_hardware`, `dummy_platform`, `dummy_codec`, `dummy_dai`, `snd_soc_dummy_dlc`, `snd_soc_dai_is_dummy()`, `snd_soc_component_is_dummy()`, and `snd_soc_dlc_is_dummy()`. `snd_soc_util_init()` creates a faux device and `snd_soc_util_exit()` destroys it.

Control flow: BCLK helpers derive sample width from `params_format()` unless a TDM width override is supplied, derive slot count from channel count unless a TDM slot count is supplied, round slots up for `slot_multiple > 1`, then multiply rate by width by slots. The dummy open callback scans runtime components and only installs dummy DMA constraints when no other dummy platform is present and the link is not a back-end `no_pcm` link. The faux device probe registers dummy codec and platform components with devres-managed ASoC APIs.

State and persistence: global static dummy component/DAI structures and `soc_dummy_dev` persist for the module lifetime. Runtime state is otherwise owned by ASoC/faux-device infrastructure.

Dependencies and integration points: exports GPL symbols consumed throughout ASoC. It relies on ALSA PCM format helpers, DAI link/component iteration, faux devices, and devm component registration. Dummy components integrate with machine driver graph construction through `snd_soc_dummy_dlc`.

Risks: arithmetic helpers use `int`, so pathological rates/channels/slots could overflow. Dummy hardware constraints are intentionally broad and should not be used to model real hardware. `snd_soc_dlc_is_dummy()` treats either matching name or DAI name as dummy, which is convenient but could match incomplete descriptors.

Test signals: `soc-utils-test.c` directly validates the BCLK helpers. Dummy device behavior is primarily integration-tested by ASoC machine-driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sof/Kconfig

Purpose: top-level Kconfig menu for Sound Open Firmware support, enumeration transports, client/debug features, IPC versions, and vendor platform subtrees.

Important APIs/types/functions: defines `SND_SOC_SOF_TOPLEVEL`, transport symbols (`SND_SOC_SOF_PCI`, `SND_SOC_SOF_ACPI`, `SND_SOC_SOF_OF` plus internal `*_DEV` symbols), core `SND_SOC_SOF`, IPC symbols `SND_SOC_SOF_IPC3` and `SND_SOC_SOF_IPC4`, compress/probes/client symbols, and developer/debug options such as nocodec, strict ABI, IPC fallback, firmware trace, IPC flood/injector clients, retained DSP context, and probe workqueue.

Control flow: user-visible transport/platform selections select hidden implementation symbols. Developer options are gated behind `EXPERT && SND_SOC_SOF`, then further nested debug controls appear under `SND_SOC_SOF_DEBUG`. At the end, it sources AMD, i.MX, Intel, MediaTek, and Xtensa Kconfig files.

State and persistence: build-time configuration only. These symbols shape which objects compile and which runtime module parameters/features are available.

Dependencies and integration points: integrates with PCI, ACPI, OF, auxiliary bus, compressed audio, and vendor Kconfigs. `SND_SOC_SOF` selects topology and optional nocodec support.

Risks: many options are hidden and selected indirectly, so dependency mistakes can produce missing objects or unusable debug clients. Developer options can alter runtime behavior significantly, especially nocodec, strict ABI, fallback IPC version, and retained DSP context.

Test signals: build matrix coverage across PCI/ACPI/OF and IPC3/IPC4 is the main signal; runtime behavior is validated by platform probes and SOF firmware boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/Makefile

Purpose: object composition for the SOF core module, enumeration modules, clients, nocodec, utility object, and vendor subdirectories.

Important APIs/types/functions: `snd-sof-y` gathers core objects (`core.o`, `ops.o`, `loader.o`, `ipc.o`, `pcm.o`, `pm.o`, `debug.o`, `topology.o`, `control.o`, trace/audio/stream helpers, and `fw-file-profile.o`). IPC3 and IPC4 object lists are conditional. Client modules include IPC flood test, message injectors, kernel injector, and probes. Enumeration modules are `snd-sof-pci`, `snd-sof-acpi`, and `snd-sof-of`.

Control flow: Kconfig symbols decide which object lists are appended and which modules are emitted under `obj-*`. Vendor subdirectories are descended into through toplevel symbols.

State and persistence: build-time only; no runtime state.

Dependencies and integration points: ties the symbols from `Kconfig` to compiled driver code. The AMD and i.MX files in this research rely on the vendor subdir entries and shared `snd-sof.o`.

Risks: IPC object lists are conditionally appended with `ifneq ($(CONFIG_*),)`, so mixed built-in/module combinations need correct symbol propagation. Missing an object from `snd-sof-y` can break a shared exported callback without an obvious source-level error.

Test signals: kernel allmodconfig/allyesconfig and targeted SOF platform builds validate object coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/Kconfig

Purpose: AMD SOF platform configuration for Renoir, Vangogh, Rembrandt, ACP6.3, ACP7.0/7.1, common ACP support, probes, and SoundWire integration.

Important APIs/types/functions: `SND_SOC_SOF_AMD_COMMON` selects core SOF, IPC3, PCI device glue, AMD ACP config, Xtensa support, ACP probes, and ACPI match helpers. Per-platform symbols select the common layer. SoundWire baseline/support symbols select AMD SoundWire ACPI integration when available.

Control flow: `SND_SOC_SOF_AMD_TOPLEVEL` gates all AMD platform options and depends on X86 or compile-test. Per-platform PCI options depend on `SND_SOC_SOF_PCI` and `AMD_NODE`, then select common support. ACP63/ACP70 additionally select SoundWire link baseline.

State and persistence: build-time symbols only.

Dependencies and integration points: integrates with AMD ACP machine selection, PCI probing, ACPI machine tables, SoundWire, Xtensa DSP architecture support, and SOF debug probes.

Risks: the toplevel `depends on SOUNDWIRE_AMD || !SOUNDWIRE_AMD` keeps visibility independent of SoundWire but can hide missing runtime SoundWire coverage until specific symbols are selected. ACP probes are always selected by common support, so probe-client build dependencies must stay healthy.

Test signals: platform-specific module builds and PCI probe tests across revisions `ACP_RN_PCI_ID`, `ACP_VANGOGH_PCI_ID`, `ACP_RMB_PCI_ID`, `ACP63_PCI_ID`, and ACP70+.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/Makefile

Purpose: AMD SOF object composition for common ACP code and per-platform PCI/DAI modules.

Important APIs/types/functions: `snd-sof-amd-acp-y` contains `acp.o`, loader, IPC, PCM, stream, trace, and common ops files. `acp-probes.o` is conditional. Per-platform modules pair PCI glue with platform DAI ops (`pci-rn.o` plus `renoir.o`, etc.).

Control flow: each Kconfig symbol emits its corresponding module through `obj-*`. Common support is shared by all platform modules.

State and persistence: build-time only.

Dependencies and integration points: maps AMD Kconfig selections to the source files researched here. Common ACP symbols are exported in the `SND_SOC_SOF_AMD_COMMON` namespace and imported by per-platform modules.

Risks: a platform module depends on both its PCI file and ops-init file being linked together; mismatches would fail probe-time ops initialization or symbol resolution.

Test signals: build coverage for all AMD platform configs and module namespace import checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-common.c

Purpose: AMD ACP shared SOF DSP ops, panic/IPC dump helpers, and machine-driver selection including optional SoundWire matching.

Important APIs/types/functions: `amd_sof_ipc_dump()` prints scratch IPC flags and interrupt status. `amd_get_registers()` and `amd_sof_dump()` read Xtensa oops, panic info, and stack from ACP mailbox/scratch space. `amd_sof_machine_select()` selects ACPI machine tables or SoundWire alt machines and sets firmware/topology names. `sof_acp_common_ops` is the central `snd_sof_dsp_ops` template.

Control flow: machine selection first tries `desc->machines` with `snd_soc_acpi_find_machine()`, then SoundWire selection if enabled. SoundWire matching fetches slave info, compares link address tables, fills `mach_params`, and returns a matching machine. The ops table wires ACP probe/remove, register/block IO, firmware loading/run, IPC, PCM, trace, PM, debugfs, Xtensa arch support, and probe-client registration into SOF core.

State and persistence: no private persistent state beyond mutating `sdev->pdata` machine and file names. Uses `acp_dev_data` from probe for PCI revision and SoundWire context.

Dependencies and integration points: depends on `acp.h`, `acp-dsp-offset.h`, SOF core ops, ACPI machine tables, SoundWire AMD APIs, and Xtensa arch dump helpers.

Risks: SoundWire machine matching relies on ACPI link count and peripheral enumeration. Incorrect scratch offsets or oops header sizes can make dumps misleading; header size is bounded by `EXCEPT_MAX_HDR_SIZE`.

Test signals: successful SOF probe with ACPI or SoundWire machines, IPC timeout dump content, firmware panic dumps, and trace/probe-client registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-dsp-offset.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-dsp-offset.h

Purpose: register offset map for AMD ACP DMA, DSP, ATU, PGFSM, interrupt, SHA, scratch, cache, SoundWire, and wake/PME blocks.

Important APIs/types/functions: defines offsets for generic ACP DMA registers and ACP70-specific DMA layout, `ACP_DSP0_RUNSTALL`, ATU groups, soft reset/control, per-generation PGFSM/clkmux, interrupt status/control, hardware semaphores, I2S error reason registers, SHA DMA/PSP registers, scratch base, fusion runstall, cache windows, and ACP70 SoundWire wake/PME bits.

Control flow: no executable flow. These constants drive register programming in `acp.c`, firmware loading in `acp-loader.c`, IPC in `acp-ipc.c`, and stream PTE setup in `acp-stream.c`.

State and persistence: none directly. Constants represent hardware state addresses.

Dependencies and integration points: shared by all AMD ACP platform drivers and descriptor files. Per-chip descriptors select which offsets apply for each revision.

Risks: wrong offsets cause hardware misconfiguration, failed DMA, broken interrupts, or invalid power transitions. ACP70 has several register layout differences, so callers must branch correctly by PCI revision.

Test signals: hardware boot/probe success, DMA transfer completion, interrupt handling, SoundWire wake handling, and firmware trace/probe stream operation across supported ACP generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-dsp-offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-ipc.c

Purpose: AMD ACP IPC transport implementation between host and SOF firmware through scratch mailbox memory and DSP software interrupts.

Important APIs/types/functions: `acp_mailbox_write()`/`acp_mailbox_read()` wrap scratch memory access. `acp_sof_ipc_send_msg()` acquires the ACP hardware semaphore, writes host mailbox data, marks host message pending, triggers host-to-DSP interrupt, and releases the semaphore. `acp_sof_ipc_irq_thread()` handles DSP messages, replies, boot-time panic, runtime panic, and probe position interrupts. `acp_sof_ipc_msg_data()` reads stream or DSP mailbox data. `acp_set_stream_data_offset()` validates and stores per-stream position offsets.

Control flow: send path busy-waits on hardware semaphore, copies IPC payload into `host_box`, sets the host flag in scratch, triggers `DSP_SW_INTR_TRIG`, and unlocks. IRQ thread handles first boot specially, then checks `sof_dsp_msg_write` for incoming messages and `sof_dsp_ack_write` for replies. Replies are read from host mailbox except PM context-save/gate replies, where windows may be powered off and a synthetic success reply is used.

State and persistence: uses scratch IPC flags in `scratch_ipc_conf`, `sdev->msg`, `sdev->ipc_lock`, and per-stream `posn_offset`. Probe position state is stored in `adata->probe_stream->cstream_posn`.

Dependencies and integration points: SOF IPC core (`snd_sof_ipc_msgs_rx`, `snd_sof_ipc_reply`, panic handling), ACP scratch helpers from `acp.c`, compressed probe streams, and firmware-defined scratch mailbox layout.

Risks: semaphore acquisition is a spin/busy wait with fixed retry count. Reply size checks exempt probe commands, which need separate coverage. Position offsets must remain aligned and inside `stream_box`; bad firmware offsets are rejected. Boot-time mailbox windows differ before `FW_READY`.

Test signals: IPC round trips, PM IPC special cases, firmware panic IRQs, probe capture position updates, and timeout dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-loader.c

Purpose: ACP firmware block staging, PTE programming, DMA/SHA transfer setup, DSP run control, and signed-firmware loading support.

Important APIs/types/functions: `acp_dsp_block_write()` stages IRAM/DRAM/SRAM firmware blocks in coherent DMA buffers. `acp_dsp_block_read()` reads SRAM blocks from scratch. `configure_pte_for_fw_loading()` builds ATU PTEs for firmware buffers. `acp_dsp_pre_fw_run()` runs SHA DMA for code and plain DMA for DRAM/SRAM blocks, configures cache windows, and frees staging buffers. `acp_sof_dsp_run()` clears runstall. `acp_sof_load_signed_firmware()` requests separate code/data binaries for quirked signed firmware.

Control flow: block writes allocate buffers lazily by block type, copy firmware data, and record sizes/use flags. Pre-run computes code page count, programs PTEs, validates/transfers code through SHA DMA, optionally transfers DRAM and SRAM images, enables cache window for newer ACP revisions, and frees coherent buffers. Run writes `ACP_DSP0_RUNSTALL` and optional fusion DSP runstall when firmware debug is enabled.

State and persistence: transient DMA buffers and sizes live in `acp_dev_data` during firmware load. `is_dram_in_use`, `is_sram_in_use`, page counts, and quirk flags affect later pre-run behavior.

Dependencies and integration points: used through `sof_acp_common_ops`. Depends on PCI DMA APIs, SOF generic firmware loader, ACP DMA helpers in `acp.c`, register offsets, and firmware naming from PCI descriptors/quirks.

Risks: buffer size constants (`ACP_DEFAULT_DRAM_LENGTH`, `ACP_DEFAULT_SRAM_LENGTH`) must match firmware expectations. Signed firmware subtracts `ACP_FIRMWARE_SIGNATURE` from transfer size; incorrect quirking breaks validation. Error paths after allocations rely on later cleanup; repeated firmware load failures should be checked for leaks.

Test signals: firmware boot on normal and signed-image platforms, SHA DMA validation status, DRAM/SRAM section transfer completion, and runstall register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-pcm.c

Purpose: AMD ACP PCM callbacks for SOF streams: open/close, hardware params, and pointer reporting.

Important APIs/types/functions: `acp_pcm_open()` allocates an inactive `acp_dsp_stream` and stores it in ALSA runtime private data. `acp_pcm_hw_params()` configures stream PTEs, fills SOF platform stream params with physical stream offset/tag, enables continuous position updates, and writes buffer size into scratch. `acp_pcm_pointer()` reads `sof_ipc_stream_posn` and returns ALSA frames. `acp_pcm_close()` releases the stream.

Control flow: open selects a stream tag via `acp_dsp_stream_get()`. hw_params derives page count from DMA bytes and calls `acp_dsp_stream_config()`, then communicates stream tag and physical address to firmware. Pointer lookup finds the SOF PCM by DAI runtime, reads position data through IPC mailbox helpers, updates cached position, and converts host bytes to frames.

State and persistence: per-runtime private data points to a stream from `adata->stream_buf`. Scratch memory receives per-stream buffer sizes. Cached positions live in `snd_sof_pcm_stream`.

Dependencies and integration points: ALSA PCM runtime, SOF PCM lookup, ACP stream PTE helper, SOF IPC position offsets, and firmware stream box layout.

Risks: pointer returns 0 on lookup/read failure, which can hide errors but avoids crashing the PCM engine. Stream allocation has only eight slots shared with trace/probes. Buffer size scratch indexing assumes tags are 1-based and within `ACP_MAX_STREAM`.

Test signals: PCM open/hw_params/close sequences, playback/capture position accuracy, and stream exhaustion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-probes.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-probes.c

Purpose: SOF debug probe host callbacks for AMD ACP using compressed capture streams.

Important APIs/types/functions: `acp_probes_compr_startup()` allocates an ACP stream for probe capture and returns its stream tag. `acp_probes_compr_set_params()` maps the compressed runtime DMA buffer into ACP PTEs and writes buffer size to scratch. `acp_probes_compr_pointer()` reports cumulative captured bytes and sampling rate. `acp_probes_register()`/`acp_probes_unregister()` register the `acp-probes` SOF client.

Control flow: startup stores the compressed stream in the ACP stream and in runtime private data, and records `adata->probe_stream` for IRQ position updates. set_params configures stream pages similarly to PCM. IRQ handling in `acp-ipc.c` updates `cstream_posn` and calls `snd_compr_fragment_elapsed()`. shutdown releases the stream and clears references.

State and persistence: `adata->probe_stream` is a single active probe stream pointer. `stream->cstream`, runtime private data, and `cstream_posn` carry compressed capture state.

Dependencies and integration points: SOF client probes framework, ALSA compressed ops, ACP stream config, and probe position register described by chip descriptors.

Risks: only one probe stream is tracked globally. set_params releases the stream on config failure but startup state must remain consistent. Sampling rate is inferred from DAI capture rate bits and may be ambiguous if multiple rates are set.

Test signals: probe client registration, compressed probe startup/set_params/shutdown, position interrupts, and trace/probe stream resource contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-stream.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-stream.c

Purpose: ACP stream resource allocation and ATU/PTE programming for PCM, firmware trace, and probe DMA buffers.

Important APIs/types/functions: `acp_dsp_stream_config()` maps a stream tag 1-8 to an ATU group, scratch PTE array, and firmware-visible physical offset. `acp_dsp_stream_get()` allocates an inactive stream by requested or any tag. `acp_dsp_stream_put()` releases a stream. `acp_dsp_stream_init()` initializes stream tags and ownership.

Control flow: stream config switches on the stream tag to choose ATU registers and PTE scratch offsets. It writes the stream's firmware-visible physical offset into scratch `reg_offset[]`, enables the ATU group, writes one PTE per DMA page using `snd_sgbuf_get_addr()`, marks high dword valid, and invalidates ATU cache.

State and persistence: stream state lives in `acp_dev_data.stream_buf[]`: active flag, tag, DMA buffer, page count, runtime/substream/compressed stream pointers, register offset, and position offset.

Dependencies and integration points: used by PCM, trace, and probe paths. Relies on scratch layout in `scratch_reg_conf`, ATU registers, SG DMA buffer helpers, and firmware interpreting tag/offset arrays.

Risks: no locking protects stream allocation, so callers must serialize via ALSA/SOF lifecycle. Config writes as many pages as requested; scratch arrays have 16 PTEs per group, so callers must keep buffer pages within hardware/firmware assumptions. Invalid tags return `-EINVAL`.

Test signals: mapping validation for all stream tags, DMA buffer page counts, trace stream tag 8 reservation, and concurrent PCM/probe allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-trace.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-trace.c

Purpose: ACP firmware trace DMA stream setup and teardown.

Important APIs/types/functions: `acp_sof_trace_init()` reserves stream tag 8, assigns the trace DMA buffer, configures 16 pages, stores the stream in `adata->dtrace_stream`, and returns stream tag/physical offset in `sof_ipc_dma_trace_params_ext`. `acp_sof_trace_release()` releases that stream.

Control flow: init gets the fixed logger stream, configures PTEs with `acp_dsp_stream_config()`, and returns firmware parameters. On failure it releases the stream. Release looks up the saved stream and returns it to the pool.

State and persistence: `adata->dtrace_stream` persists while firmware trace is active. Stream tag 8 is reserved by convention for logging.

Dependencies and integration points: SOF core trace callbacks, ACP stream config, and firmware trace IPC parameters.

Risks: fixed tag 8 can conflict with other stream users if allocation discipline breaks. Release assumes `dtrace_stream` is valid; null-release behavior is not explicitly guarded.

Test signals: firmware trace enable/disable, trace DMA data flow, and stream resource release during remove/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.c

Purpose: low-level AMD ACP hardware management: DMA descriptors, PSP/SHA firmware validation, scratch access, power/reset/init, IRQ handling, SoundWire probing/wake handling, SOF probe/remove, and PM.

Important APIs/types/functions: `configure_and_run_dma()`, `configure_and_run_sha_dma()`, `acp_dma_status()`, `memcpy_from_scratch()`, `memcpy_to_scratch()`, `amd_sof_acp_suspend()`, `amd_sof_acp_resume()`, `amd_sof_acp_probe()`, and `amd_sof_acp_remove()` are exported/common callbacks. Internal helpers handle DMA descriptor programming, PSP mailbox commands, ACP power-on/reset/DSP-reset, memory init, IRQ top/thread handlers, SoundWire ACPI scan/probe/exit, and ACP70 wake events. DMI quirk `Valve Galileo` enables signed firmware and related behavior.

Control flow: probe allocates `acp_dev_data`, registers a `dmic-codec` platform device, maps BAR0, powers/resets/init ACP, requests threaded IRQ, optionally scans/probes SoundWire, defines mailbox/debug box offsets, applies DMI quirks, initializes memory and stream slots. IRQ top half handles DSP software interrupt, SoundWire IRQs, ACP error IRQs, and ACP70 wake/PME status; DSP IPC work is delegated to the thread after acquiring hardware semaphore. Suspend resets ACP or only DSP when SoundWire clock-stop is active; resume reinitializes or performs DSP reset based on saved SoundWire state.

State and persistence: `acp_dev_data` stores device pointer, firmware DMA buffers, mutex, SoundWire info/context, descriptors, stream pool, trace/probe stream pointers, quirk pointer, debug flag, PCI revision, and SoundWire wake/status booleans. Scratch mailbox content and hardware registers persist in ACP SRAM/registers across parts of the lifecycle.

Dependencies and integration points: PCI, platform device registration, AMD SMN/PSP mailbox functions, SoundWire AMD APIs, SOF ops/core, ACP descriptors, DMI, IRQ subsystem, DMA, runtime/system PM.

Risks: hardware sequencing is revision-sensitive. `configure_and_run_dma()` loops while `dsp_data_size >= 0`, which can produce a zero-length final descriptor when size is page-aligned. Scratch copy helpers operate in 32-bit units and assume aligned byte counts. SoundWire IRQ paths assume `adata->sdw` and `pdev[]` are valid when SDW status bits occur. Error paths must unregister DMIC/IRQ consistently.

Test signals: ACP power/reset polling, firmware SHA validation, DMA completion, IPC interrupt handling, SoundWire link discovery and wake, suspend/resume with and without clock-stop, DMI signed firmware path, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.h

Purpose: shared AMD ACP SOF definitions: constants, register-related masks, data structures, exported prototypes, and per-platform ops symbols.

Important APIs/types/functions: defines stream limits, BAR index, poll/timeouts, reset/power masks, SRAM/PTE/base addresses, PCI/revision IDs, PSP mailbox constants, scratch box sizes, SoundWire IRQ/wake constants, `enum clock_source`, DMA descriptor structures, `scratch_ipc_conf`, `scratch_reg_conf`, `acp_dsp_stream`, `sof_amd_acp_desc`, `acp_quirk_entry`, and `acp_dev_data`. It declares all common ACP callbacks for probe, loader, IPC, stream, PCM, trace, PM, debug dumps, probes, and machine selection.

Control flow: no direct flow. Inline `get_chip_info()` retrieves `sof_amd_acp_desc` from `snd_sof_pdata->desc->chip_info`.

State and persistence: `acp_dev_data` is the main persistent platform state for an ACP SOF device. `scratch_reg_conf` defines the firmware/host-shared SRAM layout for IPC flags, PTEs, DMA descriptors, per-stream offsets/sizes, and FIFOs.

Dependencies and integration points: includes SOF private/audio headers and Linux SoundWire AMD definitions. Provides the ABI between common ACP files and per-platform PCI/ops files.

Risks: host and firmware must agree exactly on scratch layout and constants. Revision IDs are used in switch statements throughout the implementation, so adding a new ACP revision requires updating both descriptors and branch conditions.

Test signals: compile coverage across all AMD modules, firmware boot using scratch layout, stream mapping, and namespace symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp63.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp63.c

Purpose: ACP6.3 platform DAI declarations and ops initialization.

Important APIs/types/functions: `acp63_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs with playback/capture capabilities. `sof_acp63_ops` is exported, and `sof_acp63_ops_init()` copies `sof_acp_common_ops` then attaches the DAI array/count.

Control flow: ops init is called by the SOF core through the PCI descriptor before probe validation. No runtime logic beyond copying the common ops template.

State and persistence: global `sof_acp63_ops` persists as the platform ops table. DAI capabilities are static.

Dependencies and integration points: paired with `pci-acp63.c`, common ACP ops, and ASoC DAI registration in the SOF core.

Risks: DAI capability mismatches with firmware topology or machine drivers cause PCM open/hw_params failures. Capture on I2S DAIs is intentionally limited to stereo.

Test signals: ACP63 probe, DAI registration, topology binding to `acp-sof-*` DAI names, and PCM parameter negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp63.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp70.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp70.c

Purpose: ACP7.0/7.1 platform DAI declarations and ops initialization.

Important APIs/types/functions: `acp70_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs. `sof_acp70_ops` is exported, and `sof_acp70_ops_init()` clones common ACP ops and supplies platform DAI drivers.

Control flow: same pattern as ACP63: static DAI capability table plus init-time ops template copy.

State and persistence: global ops table and static DAI array.

Dependencies and integration points: used by `pci-acp70.c` for ACP70/71/72 revisions. Relies on common ACP code for all hardware behavior.

Risks: same DAI/topology mismatch risks as ACP63. ACP70 hardware differences are mostly handled in descriptors/common code, so this file must stay aligned with those descriptor capabilities.

Test signals: ACP70/71/72 DAI registration, topology match, and PCM negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp70.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp63.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp63.c

Purpose: PCI binding and SOF descriptor for AMD ACP6.3 platforms.

Important APIs/types/functions: `acp63_chip_info` defines ACP6.x register offsets, interrupt registers, error registers, SRAM PTE offset, hardware semaphore, fusion runstall, probe register, SoundWire max link count/address, and register range. `acp63_desc` defines machine tables, alternate SoundWire machines, firmware/topology paths/names, IPC3 support, nocodec topology, ops pointer, and ops init. `acp63_pci_probe()` filters by PCI revision and AMD ACP config before calling `sof_pci_probe()`.

Control flow: PCI match accepts AMD ACP device ID, then probe rejects non-ACP63 revisions and non-SOF machine-config flags. Successful probes pass `acp63_desc` through `driver_data` to generic SOF PCI probe.

State and persistence: static descriptor data persists for module lifetime; runtime state is created by common ACP probe.

Dependencies and integration points: AMD machine config, ACPI machine tables, SoundWire alt machine tables, SOF PCI device glue, and ACP common namespace.

Risks: revision filtering is strict. Register range and SoundWire ACPI address must match firmware/ACPI; wrong descriptor fields break common probe or IRQ handling.

Test signals: PCI enumeration on ACP63, config flag gating, SoundWire ACPI scan, firmware `sof-acp_6_3.ri`, and topology selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp63.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp70.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp70.c

Purpose: PCI binding and SOF descriptor for AMD ACP7.0, ACP7.1, and ACP7.2 revisions.

Important APIs/types/functions: `acp70_chip_info` defines ACP70 register offsets, interrupt/error fields, SoundWire details, register range, and probe/fusion offsets. `acp70_desc` points to ACP70 ACPI machine tables and SoundWire alt tables with IPC3 firmware `sof-acp_7_0.ri`. `acp70_pci_probe()` allows revisions `ACP70_PCI_ID`, `ACP71_PCI_ID`, and `ACP72_PCI_ID`, then gates by AMD SOF config flags.

Control flow: PCI match enters revision switch, rejects unknown revisions, checks `snd_amd_acp_find_config()`, then delegates to `sof_pci_probe()`.

State and persistence: static chip and device descriptors only.

Dependencies and integration points: common ACP ops, SOF PCI glue, AMD ACPI machine tables, SoundWire support, and PM via `sof_pci_pm`.

Risks: one descriptor is shared for three revisions; any register/layout divergence beyond common branch handling would need descriptor or runtime updates. SoundWire wake/PME logic depends on ACP70-specific offsets.

Test signals: PCI probe on all accepted revisions, ACP70 wake interrupts, SoundWire machines, firmware/topology load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp70.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rmb.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rmb.c

Purpose: PCI binding and SOF descriptor for AMD Rembrandt ACP6.x platforms.

Important APIs/types/functions: `rembrandt_chip_info` provides ACP6.x PGFSM, interrupt, DSP software interrupt, error, SRAM PTE, semaphore, fusion runstall, and probe offsets. `rembrandt_desc` configures ACPI machine table, IPC3, firmware `sof-rmb.ri`, topology path, nocodec topology, and Rembrandt ops. `acp_pci_rmb_probe()` filters revision/config.

Control flow: probe requires `pci->revision == ACP_RMB_PCI_ID` and AMD config flag `FLAG_AMD_SOF` or `FLAG_AMD_SOF_ONLY_DMIC`, then delegates to `sof_pci_probe()`.

State and persistence: static descriptors.

Dependencies and integration points: SOF PCI glue, AMD machine config, Rembrandt DAI ops, common ACP driver.

Risks: no `.driver.pm` assignment unlike several other AMD PCI files, so PM behavior depends on generic defaults/module context. Strict revision gating prevents accidental binding but requires new revisions to be added elsewhere.

Test signals: Rembrandt PCI probe, firmware `sof-rmb.ri`, ACPI machine selection, and PM remove/probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rn.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rn.c

Purpose: PCI binding and SOF descriptor for AMD Renoir ACP3.x platforms.

Important APIs/types/functions: `renoir_chip_info` defines ACP3.x PGFSM, interrupt, DSP interrupt, error, I2S error, SRAM PTE, semaphore, clock mux, and probe offsets. `renoir_desc` selects ACPI machine table, IPC3 firmware `sof-rn.ri`, topology path, nocodec topology, and Renoir ops. `acp_pci_rn_probe()` filters revision/config before `sof_pci_probe()`.

Control flow: only revision `ACP_RN_PCI_ID` and AMD SOF config flags bind. The PCI driver uses `sof_pci_pm` for PM callbacks.

State and persistence: static descriptors only.

Dependencies and integration points: common ACP probe, Renoir DAI ops, AMD machine config, SOF PCI device layer.

Risks: ACP3.x has older register masks and PSP behavior, so descriptor fields must align with branches in common ACP code. Config flag gating means BIOS/ACPI machine config directly affects binding.

Test signals: Renoir device enumeration, firmware `sof-rn.ri`, DAI/topology match, runtime/system PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-vangogh.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-vangogh.c

Purpose: PCI binding and SOF descriptor for AMD Vangogh ACP5.x platforms.

Important APIs/types/functions: `vangogh_chip_info` names the chip, provides ACP5.x PGFSM/interrupt/DSP interrupt/SRAM PTE/semaphore/probe offsets. `vangogh_desc` configures Vangogh ACPI machine table, IPC3 firmware `sof-vangogh.ri`, topology path, nocodec topology, and Vangogh ops. `acp_pci_vgh_probe()` gates by revision/config.

Control flow: accepts only `ACP_VANGOGH_PCI_ID` and AMD SOF config flags, then delegates to `sof_pci_probe()`. PM uses `sof_pci_pm`.

State and persistence: static descriptors.

Dependencies and integration points: Vangogh ops add DMI-quirk overrides for signed firmware and post-run delay. Common ACP loader uses `.name = "vangogh"` for signed code/data firmware names.

Risks: quirked devices such as Steam Deck OLED depend on descriptor name and DMI data to select signed firmware filenames and delay behavior. Missing error/I2S offsets may limit common error reporting for this generation.

Test signals: Vangogh PCI probe, normal and DMI-signed firmware load, post firmware run delay on resume, and machine-table topology selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-vangogh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/rembrandt.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/rembrandt.c

Purpose: Rembrandt DAI capability table and ops initialization.

Important APIs/types/functions: `rembrandt_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs with rates/formats/channel constraints. `sof_rembrandt_ops_init()` copies common ACP ops and attaches the DAI array/count.

Control flow: static data is installed during ops init; all runtime callbacks come from common ACP ops.

State and persistence: global `sof_rembrandt_ops` and static DAI definitions.

Dependencies and integration points: paired with `pci-rmb.c`; DAI names must match firmware topology and machine drivers.

Risks: topology/DAI mismatch and stereo-only capture constraints on I2S controllers. Virtual DAI is playback-only.

Test signals: Rembrandt DAI registration, topology graph binding, PCM hw_params negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/rembrandt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/renoir.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/renoir.c

Purpose: Renoir DAI capability table and ops initialization.

Important APIs/types/functions: `renoir_sof_dai[]` defines BT, SP, DMIC, and SP virtual DAI entries. `sof_renoir_ops_init()` clones `sof_acp_common_ops` and sets `.drv`/`.num_drv`.

Control flow: ops init installs static DAIs; common ACP code handles all hardware behavior.

State and persistence: global `sof_renoir_ops` and static DAI table.

Dependencies and integration points: used by `pci-rn.c`, ASoC component registration, SOF topology DAI matching.

Risks: no HS DAI on Renoir. Capture constraints differ from playback; incorrect topology channel/rate assumptions fail negotiation.

Test signals: Renoir topology loading, DAI names `acp-sof-bt`, `acp-sof-sp`, `acp-sof-dmic`, and PCM parameter tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/renoir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/vangogh.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/amd/vangogh.c

Purpose: Vangogh DAI capability table and platform-specific ops tweaks for quirked firmware behavior.

Important APIs/types/functions: `vangogh_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs. `sof_vangogh_post_fw_run_delay()` delays after resume boot for quirked systems. `sof_vangogh_ops_init()` copies common ops, installs DAIs, and applies DMI quirk overrides for signed firmware loading and post-run delay.

Control flow: ops init checks `acp_sof_quirk_table`; signed firmware switches `.load_firmware` to `acp_sof_load_signed_firmware`, and post-run quirk sets `.post_fw_run`. Delay only runs when `!sdev->first_boot`.

State and persistence: global `sof_vangogh_ops`; quirk decisions are reflected in function pointers.

Dependencies and integration points: `pci-vangogh.c` descriptor, common ACP loader, DMI quirk table in `acp.c`, SOF core firmware run sequence.

Risks: DMI matching controls critical firmware path changes. Delay workaround is timing-sensitive and only applied after first boot.

Test signals: Vangogh boot/resume on quirked and non-quirked devices, signed firmware code/data file requests, and DAI topology binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/amd/vangogh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/compress.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/compress.c

Purpose: SOF compressed audio operations for ALSA compressed streams, including buffer/page-table setup, IPC params/triggers, data copy, elapsed notification, and timestamp reporting.

Important APIs/types/functions: `sof_compressed_ops` exports `.open`, `.free`, `.set_params`, `.get_params`, `.trigger`, `.pointer`, and `.copy`. Helpers include `snd_sof_compr_fragment_elapsed()`, `snd_sof_compr_init_elapsed_work()`, `sof_set_transferred_bytes()`, `create_page_table()`, copy helpers for playback/capture, and IPC setup in `sof_compr_set_params()`.

Control flow: open allocates `sof_compr_stream`, associates it with `snd_sof_pcm_stream`, and resets positions. set_params checks firmware ABI >= 3.22.0, boots DSP on demand, allocates SG pages, creates a page table, builds `sof_ipc_pcm_params` with codec data as ext data, sends `SOF_IPC_STREAM_PCM_PARAMS`, stores stream data offset, and marks prepared. trigger maps ALSA commands to SOF stream IPC commands. free sends PCM_FREE if prepared, cancels elapsed work, clears stream, and frees private data.

State and persistence: per-compressed-runtime `sof_compr_stream` stores codec params, sampling rate, channels, sample container bytes, and cumulative copied bytes. SOF PCM stream state holds cstream pointer, page table, posn, and prepared flag.

Dependencies and integration points: ALSA compressed framework, SOF IPC3 stream messages, SOF page-table helpers, PM/on-demand boot, and platform `set_stream_data_offset`.

Risks: set_params has several resource steps and returns without explicitly freeing compressed pages on later failures in this file. ABI gating protects unsupported firmware. Unknown trigger commands log but still send a base stream command, which may not be intended. Copy returns partial counts based on user-copy failures.

Test signals: compressed playback/capture open-set_params-trigger-copy-pointer-free, ABI rejection, wraparound copied byte accounting, and elapsed work scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/control.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/control.c

Purpose: generic ALSA kcontrol callbacks that delegate SOF mixer/switch/enum/bytes operations to IPC/topology-specific control handlers.

Important APIs/types/functions: `snd_sof_volume_get/put/info`, `snd_sof_switch_get/put`, `snd_sof_enum_get/put`, `snd_sof_bytes_get/put`, `snd_sof_bytes_ext_put`, `snd_sof_bytes_ext_volatile_get`, and `snd_sof_bytes_ext_get`.

Control flow: each get/put callback extracts `snd_sof_control` from topology private data, fetches `sdev`, gets topology ops via `sof_ipc_get_ops(sdev, tplg)`, and calls the matching control callback when present. Volume info computes type/count/min/max from `soc_mixer_control` and `num_channels`. Volatile ext get resumes the device, boots DSP if needed, calls the IPC-specific volatile getter, and autosuspends.

State and persistence: kcontrol values are held in `snd_sof_control` and firmware/topology-specific backing stores; this file mostly passes through. Runtime PM state is touched for volatile reads.

Dependencies and integration points: ALSA SoC control structures, SOF topology IPC ops, runtime PM, and DSP boot helper.

Risks: missing topology control callbacks silently return no change/zero for most operations, which can hide incomplete IPC implementations. `bytes_ext_put` only validates minimum TLV header size before delegation. Runtime PM errors are rate-limited but returned for volatile gets.

Test signals: mixer/switch/enum/bytes control get/put under IPC3 and IPC4 topology implementations, volatile read with runtime suspend, and volume-info type/range behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/core.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/core.c

Purpose: main SOF core device lifecycle: module overrides, firmware state tracking, machine selection, IPC/path profile selection, ops validation, DSP probe/boot, client/machine/component registration, remove/shutdown, and panic stack printing.

Important APIs/types/functions: module params override firmware/topology/lib paths and IPC type. `sof_debug_check_flag()`, `sof_print_oops_and_stack()`, and `sof_set_fw_state()` are exported helpers. Key lifecycle functions are `snd_sof_device_probe()`, `sof_probe_continue()`, `snd_sof_device_remove()`, `snd_sof_device_shutdown()`, `sof_machine_register()`, and `sof_machine_unregister()`. Internal helpers include `sof_machine_check()`, `sof_select_ipc_and_paths()`, `validate_sof_ops()`, `sof_init_sof_ops()`, and `sof_init_environment()`.

Control flow: device probe allocates `snd_sof_dev`, initializes lists/locks/timeouts, applies module overrides, initializes ops for the selected IPC type, runs early probe, and either schedules or directly runs `sof_probe_continue()`. Continue probes hardware, selects machine, resolves firmware/topology profile, creates platform driver, initializes debug/IPC, loads firmware, runs firmware, optionally starts trace, registers ASoC component/DAIs, registers machine and clients, and marks probe complete. Error unwind frees trace, firmware, IPC, debug, hardware, late resources, ops, and resets boot state. Remove cancels work, unregisters clients and machine, releases retained-D3 prevention, powers down/notifies DSP when booted, frees resources, and unloads firmware.

State and persistence: `snd_sof_dev` owns firmware state, power state, lists for PCM/widgets/routes/clients, locks, IPC object, debugfs, firmware profile paths, first-boot/probe-complete flags, and PM/debug flags. Machine selection mutates `snd_sof_pdata`.

Dependencies and integration points: ALSA SoC, SOF IPC/loader/PM/debug/topology subsystems, PCI/OF/ACPI platform descriptors, runtime PM, tracepoints, client framework, and firmware profile logic in `fw-file-profile.c`.

Risks: probe has a long multi-stage unwind path. IPC fallback can require ops reinitialization after hardware probe. Forced nocodec and DSPless debug modes alter normal machine/DSP behavior. Workqueue probing cannot propagate errors except logs. State transitions must stay synchronized with client notifications.

Test signals: probe/remove/shutdown on all bus types, firmware boot failure paths, machine selection/nocodec fallback, IPC override/fallback, runtime PM, client registration, and panic/oops logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/debug.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/debug.c

Purpose: SOF debugfs support for exposing DSP memory/register windows, firmware profile data, firmware state, memory usage, and exception/IPC dump handling.

Important APIs/types/functions: `snd_sof_debugfs_add_region_item_iomem()`, `snd_sof_debugfs_buf_item()`, `snd_sof_dbg_memory_info_init()`, `snd_sof_dbg_init()`, `snd_sof_free_debug()`, `snd_sof_dsp_dbg_dump()`, and `snd_sof_handle_fw_exception()`. Internal read paths include `sof_dfsentry_read()` and memory info IPC handling.

Control flow: debugfs reads validate position/count, align MMIO reads to 32-bit boundaries, optionally use cached buffers when debugfs cache is enabled and DSP is suspended, and copy data to userspace. `snd_sof_dbg_init()` creates `/sys/kernel/debug/sof`, exposes firmware/topology profile strings and IPC type, initializes the dfsentry list, adds platform debug regions, and exposes `fw_state`. Memory info lazily allocates a page buffer and sends a debug IPC after resuming/booting the DSP. Exception handling can retain D3 context, dumps IPC once, dumps DSP state once unless configured otherwise, and marks firmware trace crashed.

State and persistence: debugfs dentries hang off `sdev->debugfs_root`; entries are tracked in `sdev->dfsentry_list`. Optional cache buffers persist for D0-only windows. Dump suppression flags live in `sdev`.

Dependencies and integration points: Linux debugfs, runtime PM, SOF IPC debug memory command, platform debug maps, firmware trace crash handling, and platform-specific `ipc_dump`/`dbg_dump` ops.

Risks: debugfs may expose sensitive/register state and depends on correct access type. Reads while DSP is D3 are blocked unless cached/always-accessible. Memory info trusts firmware reply size after validation. D3 retention increments PM usage and must be balanced during remove.

Test signals: debugfs file creation/read in D0 and D3, memory_info IPC, firmware panic/IPC timeout logs, retained-context behavior, and debugfs cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/fw-file-profile.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/fw-file-profile.c

Purpose: build and validate the firmware/topology/library file profile for a selected SOF IPC type, including module overrides and fallback to other IPC versions.

Important APIs/types/functions: `sof_create_ipc_file_profile()` is exported. Internal helpers test firmware files and magic (`sof_test_firmware_file()`), test topology files (`sof_test_topology_file()`), detect generic loader use, build a profile for an IPC type, print missing-file guidance, and print selected profile info.

Control flow: profile creation first tries the requested IPC type. For each candidate, it chooses firmware path/name from overrides, postfixes, or descriptor defaults; if custom firmware is used with a generic loader, it opens the file, reads magic, and adjusts IPC type to match. It resolves library path and topology path/name, validates default firmware/topology when applicable, and clears allocated strings on failure. If requested IPC fails, fallback walks supported IPC types backward or from newest depending on `SND_SOC_SOF_ALLOW_FALLBACK_TO_NEWER_IPC_VERSION`.

State and persistence: output profile fields are pointers to module params, descriptor strings, or devm-allocated strings. The selected profile is copied into `snd_sof_pdata` by core code.

Dependencies and integration points: firmware loader APIs, SOF extended manifest magic values for IPC3/IPC4, SOF descriptors' default path/name arrays, module override profiles from `core.c`, and topology naming from machine selection.

Risks: direct cast of firmware data to `u32 *` assumes enough data for magic. Custom firmware can silently adjust IPC type, which then requires ops reinitialization in core. Dummy topology names are intentionally skipped. Fallback policy depends on build config and can mask missing requested-version files.

Test signals: default firmware/topology present/missing, override path/name cases, IPC magic mismatch, IPC fallback enabled/disabled, and debugfs `fw_profile` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/fw-file-profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sof/imx/Kconfig

Purpose: NXP i.MX SOF platform configuration for common OF support, i.MX8, and i.MX9.

Important APIs/types/functions: `SND_SOC_SOF_IMX_TOPLEVEL` gates NXP i.MX DSP support and depends on ARM64/compile-test plus SOF OF enumeration. `SND_SOC_SOF_IMX_COMMON` selects OF device glue, SOF core, IPC3, Xtensa, and compressed audio. `SND_SOC_SOF_IMX8` and `SND_SOC_SOF_IMX9` select common support and depend on their firmware/control frameworks.

Control flow: selecting a platform pulls in common i.MX support and the relevant platform driver.

State and persistence: build-time only.

Dependencies and integration points: OF device probing, i.MX DSP IPC, i.MX SCU or SCMI LMM management, Xtensa architecture, and compressed SOF support.

Risks: platform dependencies must match SoC firmware services. Common selection always enables compress support for i.MX.

Test signals: build coverage for i.MX8/i.MX9 and OF probe on matching device trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/imx/Makefile

Purpose: object composition for NXP i.MX SOF platform modules.

Important APIs/types/functions: builds `snd-sof-imx8.o` from `imx8.o`, `snd-sof-imx9.o` from `imx9.o`, and common support from `imx-common.o`.

Control flow: Kconfig symbols decide which platform/common objects are linked.

State and persistence: build-time only.

Dependencies and integration points: maps i.MX Kconfig to common and platform-specific source files.

Risks: platform modules depend on `imx-common.o` being built when selected; Kconfig handles this via `SND_SOC_SOF_IMX_COMMON`.

Test signals: module/built-in build for IMX8, IMX9, and common support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.c

Purpose: common NXP i.MX SOF hardware ops for IPC, memory mapping, clocks/power domains, suspend/resume, panic dumps, and generic i.MX DSP probe/remove.

Important APIs/types/functions: exported `imx8_dump()` and `sof_imx_ops`. Internal functions handle Xtensa oops reads, IPC request/reply callbacks, mailbox send, BAR/mailbox/window lookup, power-state bookkeeping, runtime/system PM, memory-region parsing from resources/reserved memory, IPC platform device registration, and cleanup.

Control flow: probe creates an `imx-dsp` platform device, optionally binds reserved DMA memory, registers devres cleanup, obtains IPC handle, maps memory regions declared by chip info, attaches power domains if needed, gets/enables clocks, installs IPC ops, sets mailbox BAR and boot mailbox offset, then calls chip-specific probe. IPC request checks panic code when supported before dispatching SOF messages. Suspend shuts down chip core, frees MU channels, disables clocks, and sets D3; resume reenables clocks, requests channels, normalizes runtime PM state if needed, and sets D0.

State and persistence: `imx_common_data` in `sdev->pdata->hw_pdata` stores IPC device/handle, clocks, power domains, and chip private data. `sdev->bar[]`, mailbox settings, and DSP power state are initialized here.

Dependencies and integration points: i.MX firmware DSP IPC, OF resources/reserved memory, power domains, clocks, SOF OF device layer, SOF mailbox/block helpers, Xtensa panic helpers, and chip ops from `imx8.c`/`imx9.c`.

Risks: resource names in device tree must match chip memory descriptors. Probe defers if IPC handle is not ready. Clock/channel handling must be balanced across PM and remove. `imx_get_bar_index()` only accepts IRAM/SRAM, so DRAM mappings are not usable through that callback.

Test signals: OF probe with memory resources/reserved memory, IPC doorbell round trips, firmware boot, panic dump, runtime/system suspend/resume, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.h

Purpose: common i.MX SOF declarations, chip abstraction types, descriptor/DAI helper macros, and inline chip-op dispatchers.

Important APIs/types/functions: `IMX_SOF_DEV_DESC()` builds a `sof_dev_desc` with IPC3 defaults and firmware/topology paths. `IMX_SOF_DAI_DRV_ENTRY*` macros define DAI capabilities. Types include `imx_ipc_info`, `imx_chip_ops`, `imx_memory_info`, `imx_chip_info`, and `imx_common_data`. Inline helpers call optional chip `probe`, `core_kick`, `core_shutdown`, and `core_reset`.

Control flow: header macros and inline dispatchers let platform files describe SoCs declaratively while common code invokes optional operations safely.

State and persistence: `imx_common_data` stores runtime platform state; `imx_chip_info` and `imx_memory_info` are static per-chip descriptors.

Dependencies and integration points: SOF OF device descriptors, SOF ops, Linux clocks/OF platform, and Xtensa panic interfaces.

Risks: macro-generated descriptors assume IPC3 and default path/name conventions. Platforms needing different IPC or paths must not use the simple macro blindly. `get_chip_info()` and `get_chip_pdata()` depend on correctly initialized `pdata`.

Test signals: compile-time descriptor generation for i.MX8/i.MX9, OF probe using generated descriptors, and DAI macro expansion in registered components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx8.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx8.c

Purpose: i.MX8-family SOF platform driver descriptors, DAI tables, memory maps, and chip-specific DSP boot/reset controls for i.MX8, i.MX8X, i.MX8M, and i.MX8ULP.

Important APIs/types/functions: chip ops include `imx8_run()`, `imx8x_run()`, `imx8_shutdown()`, `imx8m_reset()`, `imx8m_run()`, `imx8ulp_reset()`, and `imx8ulp_run()`. Probe helpers obtain SCU IPC, DAP/runstall reset, or syscon regmap. DAI arrays cover ESAI/SAI/MICFIL variants. `imx8_ops_init()` clones `sof_imx_ops`, adds Xtensa debug dump/arch ops, and attaches chip DAIs. `IMX_SOF_DEV_DESC()` creates descriptors for each compatible.

Control flow: OF match selects a descriptor by DSP compatible. Common probe maps memory/enables clocks then chip probe stores chip private control handles. Firmware loading occurs while the core is stalled/reset; core kick releases stall or starts CPU through SCU/syscon/SMC path depending on SoC. Machine selection uses board-compatible entries to choose topology and `asoc-audio-graph-card2`.

State and persistence: chip private data is SCU IPC handle, `imx8m_chip_data`, or regmap in `imx_common_data.chip_pdata`. Static chip info records IPC mailbox offsets, memory regions, DMA reserved flag for ULP, DAIs, and ops.

Dependencies and integration points: i.MX SCU services, ARM SMCCC, syscon/regmap, reset controls, OF machine matching, SOF OF probe/remove/PM, Xtensa debug support, and common i.MX ops.

Risks: boot control is SoC-specific and fragile: incorrect offset controls or reset/stall order can prevent firmware boot. Hard-coded DAP debug address is used for i.MX8M. ULP uses SMC return value for XRDC setup. Board-compatible topology selection must match device trees.

Test signals: OF probe for each compatible, firmware boot/kick/reset, topology selection per board compatible, panic dump, and DAI registration for SAI/ESAI/MICFIL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx9.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx9.c

Purpose: i.MX95/i.MX9 SOF platform driver descriptor using SCMI LMM control for the M7 core running SOF.

Important APIs/types/functions: `imx95_dai[]` exposes bidirectional `sai3`. `imx95_ops_init()` clones common i.MX ops and attaches DAIs. `imx95_chip_probe()` sets SCMI LMM reset vector from the SRAM resource. `imx95_core_kick()` boots the M7 logical machine. `imx95_core_shutdown()` forcefully shuts it down. `imx95_chip_info` defines mailbox/window offsets, DMA reserved flag, SRAM memory, DAIs, and chip ops.

Control flow: OF match for `fsl,imx95-cm7-sof` supplies the generated descriptor to `sof_of_probe()`. Common i.MX probe maps SRAM and calls chip probe to program reset vector. SOF core run invokes SCMI boot; suspend/remove invoke SCMI shutdown.

State and persistence: static descriptor/chip info and common i.MX runtime data. Reset vector is programmed in platform firmware through SCMI LMM.

Dependencies and integration points: SCMI i.MX LMM driver, OF resources, SOF OF device layer, common i.MX ops, and board machine compatible `fsl,imx95-19x19-evk`.

Risks: only one DAI is declared. `has_dma_reserved` is true while memory regions list only non-reserved SRAM, so device tree must still provide a reserved `dma` region for common probe. SCMI service availability is mandatory.

Test signals: i.MX95 OF probe, reset-vector programming, SCMI boot/shutdown, firmware mailbox offsets, topology `sof-imx95-wm8962.tplg`, and SAI3 PCM operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/imx/imx9.c -->
