<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/core.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/core.h

## Purpose
Private coordination header for the Intel CATPT LPT/WPT AudioDSP driver. It ties together device-level state, IPC state, SRAM allocation, DMA helpers, firmware boot/context preservation, DSP power control, ALSA platform registration, and stream runtime tracking.

## APIs, Types, and Functions
Defines `struct catpt_dev`, `struct catpt_ipc`, `struct catpt_ipc_msg`, `struct catpt_spec`, `struct catpt_module_type`, and `struct catpt_stream_runtime`. Public internal entry points include SRAM helpers `catpt_sram_init()`, `catpt_sram_free()`, `catpt_request_region()`, IPC initialization and send helpers, DMA setup/copy helpers, DSP power/clock/IRQ helpers, firmware boot and context-store helpers, `catpt_coredump()`, ALSA component registration, stream lookup and position update helpers, and `catpt_arm_stream_templates()`. `CATPT_IPC_RET()` normalizes positive firmware status codes to `-EREMOTEIO`.

## Control Flow, State, and Persistence
`struct catpt_dev` persists the whole driver instance: MMIO bases, IRQ, platform spec, firmware-ready completion, DRAM/IRAM resource trees, scratch allocation, mixer metadata, loaded module metadata, SSP device formats, stream list, mutexes, Dx context, and coherent Dx buffer. `struct catpt_ipc` persists mailbox sizing, firmware-ready config, reply buffer, completions, and serialization locks. Stream runtime state persists per ALSA substream, including DSP stream info, persistent memory allocation, page-table buffer, and allocated/prepared flags.

## Dependencies and Integration
Includes `messages.h` and `registers.h`, Linux DW DMA definitions, IRQ types, ALSA memalloc/uapi headers, and exposes `catpt_attr_groups` for device registration. It is included by all CATPT implementation files and forms the private ABI between the ACPI platform driver, DSP/loader/IPC code, and PCM component.

## Risks and Test Signals
Risks include shared state coupling across PM, IPC, firmware restore, and PCM paths; positive firmware return codes leaking without `CATPT_IPC_RET()`; resource-tree lifetime bugs; and stream-list locking assumptions during Dx transitions. Test signals are build coverage of all CATPT objects, successful probe/firmware boot, suspend/resume with streams, ALSA stream open/close, IPC timeout paths, and coredump generation after firmware fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/device.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/device.c

## Purpose
ACPI platform driver for Intel Low Power AudioDSP on Lynx Point and Wildcat Point platforms. It owns device discovery, MMIO mapping, IRQ registration, runtime/system PM sequencing, board machine registration, and initial assembly of DSP, DMAC, firmware, and ALSA platform components.

## APIs, Types, and Functions
Main entry points are `catpt_acpi_probe()`, `catpt_acpi_remove()`, PM callbacks `catpt_suspend()`, `catpt_resume()`, `catpt_runtime_suspend()`, and `catpt_runtime_resume()`, plus helpers `catpt_do_suspend()`, `catpt_register_board()`, `catpt_probe_components()`, and `catpt_dev_init()`. It defines ACPI machine tables for LPT/WPT, `catpt_spec` descriptors `lpt_desc` and `wpt_desc`, ACPI IDs `INT33C8` and `INT3438`, and registers `catpt_acpi_driver`.

## Control Flow, State, and Persistence
Probe validates that Intel DSP policy selects SST/CATPT, allocates `catpt_dev`, initializes resources from the matched spec, maps LPE and PCI BARs, coerces a 31-bit DMA mask for firmware context storage, allocates a coherent DRAM-sized Dx buffer, gets the IRQ, installs threaded DSP IRQ handlers, powers the DSP, probes DW DMA, boots firmware once, registers the ALSA component, enables autosuspend runtime PM, and then spawns the matching board platform device. Suspend enters firmware Dx D3 over IPC, stalls the DSP, stores firmware memdumps, module states, and stream contexts through DMA, then powers down. Resume powers up, reboots firmware in restore mode, and reapplies cached SSP formats.

## Dependencies and Integration
Depends on ACPI, PCI/platform resources, DMA mapping, IRQs, runtime PM, `snd_intel_acpi_dsp_driver_probe()`, ASoC ACPI machine matching, and all CATPT core subsystems. The registered board uses `mach->mach_params.platform = "catpt-platform"` to bind to the CATPT ALSA component registered by `pcm.c`.

## Risks and Test Signals
Risks include suspend intentionally ignoring `catpt_do_suspend()` failures for system sleep, firmware restore depending on valid Dx context and coherent buffer contents, runtime PM interactions while module unload is in progress, board registration after PM enable, and per-platform offset/mask correctness in `catpt_spec`. Test signals are ACPI probe on `INT33C8`/`INT3438`, successful firmware first boot, child board creation, runtime autosuspend/resume with active and inactive streams, reprogrammed SSP formats after resume, and clean remove after runtime PM disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/dsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/dsp.c

## Purpose
Low-level DSP, DMA, power, clock, SRAM power-gating, register-default, and coredump support for the CATPT driver. It bridges Linux DMAEngine/DW DMA with the AudioDSP memory map and programs platform PCI/SHIM controls for D0/D3 and low-power clock transitions.

## APIs, Types, and Functions
Exports `catpt_dma_request_config_chan()`, `catpt_dma_memcpy_todsp()`, `catpt_dma_memcpy_fromdsp()`, `catpt_dmac_probe()`, `catpt_dmac_remove()`, `catpt_dsp_update_srampge()`, `catpt_dsp_stall()`, `lpt_dsp_pll_shutdown()`, `wpt_dsp_pll_shutdown()`, `catpt_dsp_update_lpclock()`, `catpt_dsp_power_down()`, `catpt_dsp_power_up()`, and `catpt_coredump()`. Internal helpers include DMA channel filtering/configuration, `catpt_dma_memcpy()`, SRAM-gate register updates, DSP reset, low-power clock selection, register default writes, and dump-section construction.

## Control Flow, State, and Persistence
DMA requests select a memory-copy channel whose device matches `cdev->dev`, configure 4-byte bus widths and 16-beat bursts, then use demand-mode HMDC bits around synchronous `dmaengine_prep_dma_memcpy()` transfers. SRAM power gating derives active blocks from child resources, inverts hardware ON-as-zero masks, disables core clock gating while changing SRAM gates, and performs a dummy read on newly enabled blocks. Power down resets/stalls the DSP, selects 24 MHz SSP clocks, moves to low-power clock, disables MCLK, restores SHIM/SSP defaults, gates clocks/SRAM, and sets PCI D3hot. Power up reverses that sequence, ungates SRAM, restores defaults/MCLK/high clock, releases reset, and unmasks IPC interrupts. Coredump snapshots firmware hash, IRAM, DRAM, SHIM, SSP, and DMA registers into a structured `dev_coredumpv()` payload.

## Dependencies and Integration
Uses Linux DMAEngine, DW DMA, firmware/coredump APIs, PCI PM bits, PXA SSP register offsets, CATPT register macros, and CATPT resource trees. Called by probe/remove, firmware loader, suspend/resume, stream allocation/free, and IPC core-dump notification handling.

## Risks and Test Signals
Risks include hard-coded DMA engine `CATPT_DMA_DEVID = 1`, address masking with `CATPT_DMA_DSP_ADDR_MASK`, clock-gate/SRAM sequencing sensitivity, unchecked return values in some power paths, dummy-read dependence after SRAM enable, and coredump size/hash parsing assumptions. Test signals are DMA transfer success in firmware load and Dx store/restore, correct SRAM gating when streams and scratch regions are allocated, stable D0/D3 transitions, low-power clock toggling when streams prepare/pause, and usable devcoredump payloads after firmware core-dump request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/ipc.c

## Purpose
Mailbox IPC transport for host-to-DSP CATPT commands, immediate replies, delayed replies, firmware-ready notification, stream position/glitch notifications, and firmware coredump requests.

## APIs, Types, and Functions
Exports `catpt_ipc_init()`, `catpt_dsp_send_msg_timeout()`, `catpt_dsp_send_msg()`, `catpt_dsp_irq_handler()`, and `catpt_dsp_irq_thread()`. Important internals include `catpt_ipc_arm()`, `catpt_ipc_msg_init()`, `catpt_dsp_send_tx()`, `catpt_wait_msg_completion()`, `catpt_dsp_do_send_msg()`, `catpt_dsp_notify_stream()`, `catpt_dsp_copy_rx()`, and `catpt_dsp_process_response()`.

## Control Flow, State, and Persistence
Initialization sets default 300 ms timeout, locks, and completions but leaves IPC not ready until firmware sends a ready notification. Firmware ready provides inbox/outbox offsets and sizes, allocates the RX buffer, copies config into `ipc->config`, marks IPC ready, and completes `cdev->fw_ready`. Sends are serialized by `ipc->mutex`; the spinlock clears reply state, copies payload to outbox, and sets IPCC busy. Completion waits first for immediate done, then for delayed busy reply if the initial response status is `CATPT_REPLY_PENDING`. IRQ top half handles host-done replies through IPCC and wakes the threaded handler for DSP-busy messages through IPCD; the thread handles notifications, delayed replies, coredump requests, and interrupt unmasking.

## Dependencies and Integration
Depends on CATPT packed message formats, MMIO mailbox helpers, tracepoints, Linux completion/locking, and stream helpers from `pcm.c`. The firmware loader waits on `fw_ready`, message wrappers in `messages.c` use `catpt_dsp_send_msg()`, and stream notifications call back into ALSA position handling.

## Risks and Test Signals
Risks include IPC becoming permanently not ready on timeout with recovery left as TODO, reply payload copying only for success status, request/reply size validation tied to firmware outbox size, delayed reply timeout ambiguity, and notifications for streams already removed. Test signals are firmware-ready completion, successful command/reply traces, delayed reply handling for stream messages, position notifications driving period elapsed, timeout path disabling IPC, and coredump request path producing a dump without IRQ storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/loader.c

## Purpose
Firmware image parser/loader and Dx context store/restore implementation for CATPT. It manages SRAM resource allocation, loads module blocks into IRAM/DRAM through DMA, records module metadata, preserves firmware and stream state over D3, and coordinates boot completion.

## APIs, Types, and Functions
Exports `catpt_sram_init()`, `catpt_sram_free()`, `catpt_request_region()`, `catpt_store_streams_context()`, `catpt_store_module_states()`, `catpt_store_memdumps()`, `catpt_boot_firmware()`, and `catpt_first_boot_firmware()`. Internal firmware structures are `catpt_fw_hdr`, `catpt_fw_mod_hdr`, and `catpt_fw_block_hdr`; helper paths include `catpt_restore_streams_context()`, `catpt_restore_memdumps()`, `catpt_restore_fwimage()`, `catpt_load_block()`, `catpt_restore_basefw()`, `catpt_restore_module()`, `catpt_load_module()`, `catpt_restore_firmware()`, `catpt_load_firmware()`, `catpt_load_image()`, and `catpt_load_images()`.

## Control Flow, State, and Persistence
SRAM is modeled as root resources with child allocations; firmware module blocks optionally reserve regions during initial load, and loaded module metadata stores entry point, persistent size, scratch size, and instance-state window. Initial boot stalls the DSP, requests firmware, verifies `$SST` signatures, copies the image to coherent DMA memory, loads each module/block, releases stall, waits up to 250 ms for firmware ready, updates SRAM power gating, restricts reserved DRAM areas, queries mixer stream info, arms stream templates, and allocates shared scratch. Restore boot reloads IRAM, overlays saved firmware-image memory ranges, restores memory dumps, restores module instance blocks from `dxbuf`, and then restores per-stream persistent contexts.

## Dependencies and Integration
Uses Linux firmware loading, DMA coherent allocation, resource trees, CATPT DMA helpers, firmware IPC ready notification, `catpt_ipc_get_mixer_stream_info()`, `catpt_arm_stream_templates()`, and register offset conversion helpers. Called from probe and resume after DSP power-up and before ALSA stream operation resumes.

## Risks and Test Signals
Risks include trusting firmware header block sizes and offsets, no global image-size boundary validation while walking modules, `catpt_request_region()` assuming existing child ordering and a non-empty child list for some paths, state restore depending on firmware-provided Dx memory info, and entry point adjustment by subtracting 4. Test signals are valid/invalid firmware signature handling, first boot loading all modules and arming templates, DRAM/IRAM resource maps after load, suspend/resume with offload/capture streams, memdump range filtering, and restore failure propagation before SSP reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.c

## Purpose
Typed IPC command wrappers for CATPT firmware global, stream, and stage messages. The file converts ALSA/driver state into packed firmware payloads and delegates transport to `catpt_dsp_send_msg()`.

## APIs, Types, and Functions
Exports firmware/version and stream-control functions: `catpt_ipc_get_fw_version()`, `catpt_ipc_alloc_stream()`, `catpt_ipc_free_stream()`, `catpt_ipc_set_device_format()`, `catpt_ipc_enter_dxstate()`, `catpt_ipc_get_mixer_stream_info()`, `catpt_ipc_reset_stream()`, `catpt_ipc_pause_stream()`, `catpt_ipc_resume_stream()`, `catpt_ipc_set_volume()`, `catpt_ipc_set_write_pos()`, and `catpt_ipc_mute_loopback()`. Local packed payloads include `catpt_alloc_stream_input`, `catpt_set_volume_input`, and `catpt_set_write_pos_input`.

## Control Flow, State, and Persistence
Most wrappers build a `union catpt_global_msg` or `union catpt_stream_msg`, set a payload pointer/size, and optionally provide a reply buffer. `catpt_ipc_alloc_stream()` is the most complex path: it builds an allocation payload with path/type/PCM format/ring info, DSP offsets for persistent and scratch memory, and a flex-array module list inserted into the expected firmware layout via `memmove()`. Replies populate firmware-owned stream IDs and MMIO register addresses that later persist in `struct catpt_stream_runtime` or `struct catpt_mixer_stream_info`.

## Dependencies and Integration
Depends on `messages.h` packed ABI definitions, resource offset conversion, and the IPC transport in `ipc.c`. Called from firmware boot (`get_mixer_stream_info`), suspend (`enter_dxstate`), resume/BE setup (`set_device_format`), stream lifecycle (`alloc/free/reset/pause/resume`), ALSA volume controls (`set_volume`), offload ring updates (`set_write_pos`), and loopback mute controls.

## Risks and Test Signals
Risks include packed bitfield layout portability, allocation payload reordering around the flexible module array, assuming persistent/scratch resources are valid and firmware-addressable, positive firmware statuses requiring caller-side `CATPT_IPC_RET()`, and bool size/layout in packed stage payloads. Test signals are IPC traces matching expected headers and payload sizes, successful stream allocation for each topology template, valid volume/register updates, set-write-position behavior for offload playback, and Dx entry returning a populated context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.h

## Purpose
Firmware IPC ABI definition for CATPT. It declares message headers, status values, stream/pin/path/module identifiers, audio formats, ring/memory descriptors, stream and mixer reply structures, SSP format descriptors, Dx context descriptors, notification payloads, and IPC wrapper prototypes.

## APIs, Types, and Functions
Key types include `union catpt_global_msg`, `union catpt_stream_msg`, `union catpt_notify_msg`, `struct catpt_fw_version`, `struct catpt_audio_format`, `struct catpt_ring_info`, `struct catpt_module_entry`, `struct catpt_stream_info`, `struct catpt_ssp_device_format`, `struct catpt_dx_context`, `struct catpt_mixer_stream_info`, `struct catpt_fw_ready`, `struct catpt_notify_position`, and `struct catpt_notify_glitch`. Macros `CATPT_MSG()`, `CATPT_GLOBAL_MSG()`, `CATPT_STREAM_MSG()`, and `CATPT_STAGE_MSG()` initialize packed headers.

## Control Flow, State, and Persistence
The header carries no executable state but defines the binary layout persisted across host/DSP mailboxes, firmware boot config, Dx save/restore records, stream IDs, and firmware register addresses. Packed structs ensure mailbox payloads match DSP expectations; enums determine how PCM stream templates map to firmware modules and pin IDs.

## Dependencies and Integration
Included by all CATPT files through `core.h` or directly. Its definitions integrate firmware command wrappers, IPC response parsing, PCM stream creation, sysfs firmware-version reads, and coredump firmware-info extraction.

## Risks and Test Signals
Risks include compiler-dependent packed bitfield ordering, ABI drift from firmware, accidental enum renumbering, `CATPT_CHANNELS_MAX` and `SAVE_MEMINFO_MAX` mismatches, and bool packing in payload structs outside this header. Test signals are stable compile-time structure sizes on supported architectures, firmware accepting all command headers, correct stream IDs/register addresses in replies, valid firmware-ready mailbox offsets, and notification parsing for position/glitch events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/pcm.c

## Purpose
ASoC platform component and DAI implementation for CATPT PCM, offload, capture, loopback, Bluetooth, and SSP backend paths. It translates ALSA stream lifecycle and controls into firmware IPC stream allocation, ring setup, volume/mute updates, and backend device-format configuration.

## APIs, Types, and Functions
Defines `struct catpt_stream_template`, topology templates for system/offload/capture/loopback/Bluetooth streams, FE DAI ops, BE DAI ops, component controls/widgets/routes, and DAI drivers. Exports `catpt_stream_find()`, `catpt_stream_update_position()`, `catpt_arm_stream_templates()`, and `catpt_register_plat_component()`. Important internals include `catpt_get_stream_template()`, `catpt_stream_hw_id()`, `catpt_stream_volume_regs()`, `catpt_arrange_page_table()`, channel map/config helpers, DAI startup/shutdown/hw_params/hw_free/prepare/trigger callbacks, volume and mute control callbacks, `catpt_dai_pcm_new()`, and component PCM/pointer callbacks.

## Control Flow, State, and Persistence
Startup allocates per-stream runtime state, a one-page firmware page table, and persistent DSP DRAM, then updates SRAM power gating. `hw_params()` builds `catpt_audio_format`, lays out an SG page table in the firmware-required packed PFN format, fills ring info, calls `catpt_ipc_alloc_stream()`, applies cached mixer/stream controls, and links the stream into `cdev->stream_list`. Prepare resets and pauses the DSP stream. Trigger start/resume updates low-power clock and resumes the stream; offload playback sends an initial write position, and position notifications continue half-buffer write-position updates. Stop/suspend/pause pauses the DSP stream and may mark the stream unprepared. `hw_free()` removes the stream from the list, resets/frees it in firmware, and keeps cached control values for later application.

## Dependencies and Integration
Depends on ALSA SoC component/DAI/PCM APIs, SG DMA buffers, runtime PM, CATPT firmware IPC wrappers, stream templates armed by the loader, and board machine links that reference `catpt-platform` and BE DAI names `ssp0-port`/`ssp1-port`. Backend `pcm_new` computes SSP device format from codec DAI channels and sends `SET_DEVICE_FORMATS` under runtime PM.

## Risks and Test Signals
Risks include non-obvious firmware page-table packing, lock ordering between stream controls and notifications, stream ID versus pin ID assumptions, volume controls using compound-literal private storage, unimplemented WAVES controls returning success without behavior, offload half-buffer write-position assumptions, and backend format choices based only on codec capture channel maximums. Test signals are ALSA open/hw_params/prepare/trigger/hw_free for all FE DAIs, pointer updates from firmware registers, offload playback progression, volume/mute changes before and after stream allocation, SSP0 I2S/TDM and SSP1 Bluetooth setup, runtime PM around BE setup, and suspend/resume with active prepared streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/registers.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/registers.h

## Purpose
MMIO register map, bit definitions, reset defaults, memory-layout helpers, and typed access macros for CATPT SHIM, PCI, DMA, SSP, mailbox, SRAM, and DSP/host address conversion.

## APIs, Types, and Functions
Defines SHIM offsets (`CS1`, `ISC`, `IMC`, `IPCC`, `IPCD`, `CLKCTL`, `HMDC`), PCI offsets (`PMCS`, `VDRTCTL0`, `VDRTCTL2`), LPT/WPT SRAM-gate/APLL bits, SSP reset defaults, memory sizes and block counts, DSP DRAM offset conversion macros, and helpers such as `catpt_shim_addr()`, `catpt_dma_addr()`, `catpt_ssp_addr()`, `catpt_inbox_addr()`, `catpt_outbox_addr()`, `catpt_readl_shim()`, `catpt_updatel_shim()`, `catpt_readl_poll_shim()`, `catpt_readl_pci()`, and `catpt_updatel_pci()`.

## Control Flow, State, and Persistence
The header has no runtime state. Its constants determine how platform specs are interpreted, how power/clock/IPCC/IPCD control flow reaches hardware, how mailbox offsets received from firmware become host MMIO addresses, and how DSP DRAM addresses are converted for IPC payloads and DMA.

## Dependencies and Integration
Includes Linux bitops, iopoll, and PCI PM register definitions. Used by every CATPT implementation file for register I/O, power sequencing, DMA address construction, firmware loading, IPC, coredump, and sysfs/PCM register reads.

## Risks and Test Signals
Risks include incorrect platform-specific masks, read-modify-write races in simple update macros, address macro misuse with unvalidated firmware mailbox offsets, and conversion macros assuming only the `0x400000` DSP DRAM alias bit differs. Test signals are stable probe/power sequences, correct IRQ/IPCC/IPCD behavior, successful firmware memory copies, accurate coredump register sections, and no MMIO faults from mailbox or stream register addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/sysfs.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/sysfs.c

## Purpose
Device sysfs attributes for exposing CATPT firmware version and firmware information string.

## APIs, Types, and Functions
Defines read-only attributes `fw_version` and `fw_info`, exported through `catpt_attr_groups`. `fw_version_show()` resumes the device, sends `GET_FW_VERSION`, autosuspends again, and prints `type.major.minor.build`. `fw_info_show()` prints the firmware-ready `ipc.config.fw_info` string cached during boot.

## Control Flow, State, and Persistence
`fw_version` is live firmware state and requires runtime PM plus IPC readiness. `fw_info` is cached state from the firmware-ready mailbox and does not resume the DSP. Attribute groups are attached to the platform driver so the files exist for the CATPT device after probe.

## Dependencies and Integration
Depends on runtime PM, `catpt_ipc_get_fw_version()`, `CATPT_IPC_RET()`, and the `catpt_dev` stored as driver data. The attribute group is referenced by `device.c` in the platform driver definition.

## Risks and Test Signals
Risks include `fw_info` being read before firmware-ready data is meaningful on partial probe failure, `fw_version` returning raw runtime PM errors, and IPC failures after autosuspend/resume. Test signals are sysfs reads before and after runtime suspend, correct version formatting, and non-empty firmware info after first boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/trace.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/trace.h

## Purpose
Tracepoint definitions for CATPT IRQ and IPC diagnostics, including request/reply/notification headers and optional payload hex dumps.

## APIs, Types, and Functions
Defines trace system `intel_catpt`, event class `catpt_ipc_msg`, events `catpt_irq`, `catpt_ipc_request`, `catpt_ipc_reply`, `catpt_ipc_notify`, and conditional event `catpt_ipc_payload`. The payload event stores a dynamic byte array and prints a hex dump when data and size are non-zero.

## Control Flow, State, and Persistence
The header has no driver state. `device.c` defines `CREATE_TRACE_POINTS` before including it, while IPC paths call tracepoints around MMIO header reads/writes and payload copies. Trace data is transient through ftrace/perf rather than persisted by the driver.

## Dependencies and Integration
Depends on Linux tracepoint infrastructure and must keep `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` aligned with the local header. Used primarily by `ipc.c` and included once with tracepoint creation by `device.c`.

## Risks and Test Signals
Risks include trace header include-path breakage if files move, payload trace overhead when enabled, and accidental mismatch between traced headers and actual mailbox direction. Test signals are successful build of trace events, visible events under `/sys/kernel/tracing/events/intel_catpt`, and correlated request/reply/payload traces during firmware boot and stream operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/Makefile

## Purpose
Kbuild recipe for Intel ASoC ACPI machine-match support objects and the separate SDCA quirk helper module.

## APIs, Types, and Functions
Builds `snd-soc-acpi-intel-match-y` from per-generation match tables (`byt`, `cht`, `hsw-bdw`, `skl`, `kbl`, `bxt`, `glk`, `cnl`, `cfl`, `cml`, `icl`, `tgl`, `ehl`, `jsl`, `adl`, `rpl`, `mtl`, `arl`, `lnl`, `ptl`, `nvl`, `hda`), SoundWire mockup tables, SSP common helpers, and `sof-function-topology-lib.o`. Builds `snd-soc-acpi-intel-sdca-quirks-y` from `soc-acpi-intel-sdca-quirks.o`.

## Control Flow, State, and Persistence
No runtime state is held here. Object inclusion controls which exported match arrays and helper symbols are available when `CONFIG_SND_SOC_ACPI_INTEL_MATCH` or `CONFIG_SND_SOC_ACPI_INTEL_SDCA_QUIRKS` is enabled.

## Dependencies and Integration
Integrated by the Linux ASoC Intel common Kbuild. The match object is consumed by Intel SOF/SST/HDA selection code via exported `snd_soc_acpi_intel_*` arrays; the SDCA quirk object exports a namespaced helper used by newer SoundWire match tables.

## Risks and Test Signals
Risks include omitting a generation object from the aggregate, building tables that reference helper symbols not included in the same object, or enabling SDCA machine checks without the quirk module. Test signals are allmodconfig/allyesconfig builds, modpost exported-symbol validation, and probe-time availability of expected generation tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-adl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-adl-match.c

## Purpose
Alder Lake ACPI machine-match tables for Intel ASoC/SOF platforms, covering SSP/I2S codec combinations and a broad set of SoundWire link-address topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_adl_machines[]` and `snd_soc_acpi_intel_adl_sdw_machines[]`. The file defines codec lists for ES83x6, MAX98357A, RT5682/RT5682S, RT1019P, and LT6911 HDMI, plus SoundWire endpoint/address/link descriptors for RT711/RT711-SDCA, RT1308, RT1316, RT714, CS42L43, CS35L56, MAX98373, and RT5682 combinations.

## Control Flow, State, and Persistence
There is no executable runtime state. Match ordering and `.id`/`.comp_ids`/`.machine_quirk` entries select machine drivers and topology names for boards with codecs on SSP buses. SoundWire entries use `.link_mask` and `.links` to require specific active links and endpoint groupings; selected entries bind to `sof_sdw` with explicit `sof-adl-*.tplg` files.

## Dependencies and Integration
Depends on ASoC ACPI match headers and SSP common topology suffix support. The arrays are consumed by Intel SOF/SST platform code during ACPI enumeration; SoundWire descriptors feed the SOF SoundWire machine driver.

## Risks and Test Signals
Risks include overlapping codec IDs where array order changes board selection, incorrect link masks for ADL/ADL-P variants, topology filename drift, and endpoint group-position mistakes for aggregated amplifiers. Test signals are ACPI matching on ADL boards, SOF topology load for each listed codec combination, SoundWire device enumeration matching expected links, and audio playback/capture on SSP and SoundWire designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-adl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-arl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-arl-match.c

## Purpose
Arrow Lake ACPI match data for SSP codec boards and SoundWire topologies, including newer function-topology support for CS42L43/CS35L56 and RT722/RT1320 configurations.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_arl_machines[]` and `snd_soc_acpi_intel_arl_sdw_machines[]`. Defines SSP codec lists for ES83x6, RT5682, and LT6911 HDMI, endpoint/address descriptors for CS42L43, CS35L56, RT711/RT711-SDCA, RT722, RT1316, and RT1320, and multiple `snd_soc_acpi_link_adr` arrays with `sof_sdw_get_tplg_files` hooks.

## Control Flow, State, and Persistence
Static tables select machine drivers/topologies based on ACPI HID/codec lists or SoundWire link masks. Several SoundWire matches share topology filenames while function topology expansion derives additional topology files from endpoint/function data. No mutable state persists in this file.

## Dependencies and Integration
Depends on ASoC ACPI match headers, SSP common helpers, and `sof-function-topology-lib.h`. Integrated by the Intel ACPI match aggregate and consumed by SOF platform and SoundWire machine selection.

## Risks and Test Signals
Risks include function topology metadata mismatching physical endpoints, shared topology filenames hiding hardware differences, missing LT6911 companion checks for SSP HDMI designs, and link-mask collisions among CS42L43/CS35L56 variants. Test signals are ARL ACPI match selection, generated function topology file list correctness, SoundWire link enumeration, and validation of headset, speaker aggregation, HDMI-SSP, and RT722/RT1320 playback/capture paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-arl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-bxt-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-bxt-match.c

## Purpose
Broxton/Apollo Lake ACPI machine-match table for legacy SST/SOF I2S designs, with a DMI quirk for Apollo Lake RVP1A.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_bxt_machines[]`. Defines `apl_table`, `apl_quirk()`, codec companion lists for ES83x6 and MAX98357A/DMIC, and machine entries for ALC298, DA7219/MAX98357A, PCM512x, WM8804, TDF8532, and ES8336 dynamic topology naming.

## Control Flow, State, and Persistence
Machine selection is table-driven. The `INT34C3` TDF8532 entry invokes `apl_quirk()`, which checks DMI for Intel Apollo Lake RVP1A and rewrites `mach->id` from `dmi_id->driver_data` when needed. ES8336 uses topology quirk masks so topology suffixes are derived at runtime.

## Dependencies and Integration
Depends on Linux DMI and ASoC ACPI matching. Consumed by Intel platform driver selection during ACPI enumeration for BXT/APL systems.

## Risks and Test Signals
Risks include DMI-specific ID mutation affecting later matches, companion codec detection for DA7219/MAX98357A boards, and dynamic ES8336 topology suffix mismatch. Test signals are DMI quirk behavior on RVP1A, correct machine driver selection for each HID, SOF topology load, and playback/capture/DMIC validation on Apollo Lake boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-bxt-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-byt-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-byt-match.c

## Purpose
Bay Trail ACPI machine-match table for tablet/laptop audio codecs, including DMI overrides for systems whose ACPI IDs are ambiguous or incorrect.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_baytrail_machines[]`. Defines DMI callbacks for RT5672 and Point of View P1006W overrides, static override machines `byt_rt5672` and `byt_pov_p1006w`, `byt_quirk()`, codec companion lists for RT5640/WM5102/DA7213/RT5645, and machine entries for RT5640, RT5651, WM5102, DA7213, ES8316, RT5682, RT5645, MAX98090, CX2072x, and optional nocodec.

## Control Flow, State, and Persistence
The first RT5640-compatible entry can call `byt_quirk()`, which runs the DMI table and returns a different static machine descriptor for known systems. Otherwise matching proceeds through ACPI HID or companion codec lists. No state persists except the selected machine data passed to the platform driver.

## Dependencies and Integration
Depends on Linux DMI, ASoC ACPI match helpers, and optional `CONFIG_SND_SOC_INTEL_BYT_CHT_NOCODEC_MACH`. Used by Intel Bay Trail SST/SOF platform selection.

## Risks and Test Signals
Risks include broad DMI matches selecting the wrong override, wildcard companion IDs taking precedence over more specific entries, optional nocodec exposure on production systems, and topology filenames shared with Cherry Trail-era drivers. Test signals are DMI-quirked device probes, ACPI matching for each codec HID, SOF topology load, and audio routing validation on known Bay Trail tablets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-byt-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cfl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cfl-match.c

## Purpose
Placeholder Coffee Lake ACPI match definitions for Intel ASoC/SOF machine selection.

## APIs, Types, and Functions
Exports empty sentinel-only arrays `snd_soc_acpi_intel_cfl_machines[]` and `snd_soc_acpi_intel_cfl_sdw_machines[]`.

## Control Flow, State, and Persistence
No runtime control flow or persistent state exists. The empty arrays allow generation-specific lookup code to reference Coffee Lake tables even when no board-specific matches are listed.

## Dependencies and Integration
Depends on ASoC ACPI match headers and the Intel match aggregate. Platform code can iterate these arrays and simply terminate on the first zero entry.

## Risks and Test Signals
Risks are mainly omission risks: Coffee Lake boards requiring non-HDA/non-generic matches will not bind through these arrays. Test signals are build/export success and fallback to other generic/HDA machine selection where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cfl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cht-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cht-match.c

## Purpose
Cherry Trail ACPI machine-match table for codec-heavy tablet designs, with DMI quirks for Surface 3, missing ES8316 devices, and Lenovo Yoga Tab3 X90 ACPI irregularities.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_cherrytrail_machines[]`. Defines `cht_quirk()`, `cht_ess8316_quirk()`, `lenovo_yt3_x90_quirk()`, DMI tables, static replacement machine descriptors, companion codec lists for RT5640/RT5670/RT5645/DA7213, and entries for RT5672, RT5645, MAX98090, NAU8824, DA7213, ES8316, RT5640, RT5682, RT5651, CX2072x, PCM512x, Lenovo SST-ID fallback, and optional nocodec.

## Control Flow, State, and Persistence
Table matching is mostly static, but selected entries run DMI checks that can replace the matched machine, skip an ES8316 entry when the codec is not actually present, or match Lenovo hardware by SST ID when the codec is missing from ACPI. The selected `snd_soc_acpi_mach` data persists only as machine-driver configuration.

## Dependencies and Integration
Depends on Linux DMI, ASoC ACPI matching, and optional nocodec Kconfig. Used by Cherry Trail SST/SOF platform drivers and machine drivers shared with Bay Trail/Cherry Trail codecs.

## Risks and Test Signals
Risks include broad SST-ID fallback matching unintended systems, ES8316 skip logic suppressing valid boards with similar DMI, order-sensitive wildcard codec lists, and optional nocodec selection. Test signals are probe outcomes on Surface 3, Lenovo Yoga Tab3 X90, ES8316 CherryTrail devices, and standard RT56xx/DA7213/MAX98090 boards, plus topology load and audio path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cht-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cml-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cml-match.c

## Purpose
Comet Lake ACPI match tables for SSP/I2S codec boards and SoundWire RT700/RT711/RT1308/RT1316/RT714 topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_cml_machines[]` and `snd_soc_acpi_intel_cml_sdw_machines[]`. Defines codec lists for ES83x6, RT1011, RT1015, MAX98357A, and MAX98390 speaker companions; SoundWire endpoints/address descriptors; and link arrays `cml_rvp`, `cml_3_in_1_default`, `cml_3_in_1_mono_amp`, and `cml_3_in_1_sdca`.

## Control Flow, State, and Persistence
SSP matching is order-sensitive for multiple `10EC5682` RT5682 entries: companion speaker codec lists must be tested before the bare RT5682 fallback. SoundWire entries select `sof_sdw` and topology files based on link masks and codec descriptors. No mutable state is stored by the file.

## Dependencies and Integration
Depends on ASoC ACPI match helpers and SoundWire machine descriptors. Consumed by Comet Lake SOF platform selection and the shared SOF SoundWire machine driver.

## Risks and Test Signals
Risks include changing order of the RT5682 entries, mismatch between companion codec list and topology filename, SDCA versus non-SDCA endpoint confusion, and stale link masks. Test signals are CML board matching with RT5682 plus each amplifier type, DA7219 amplifier variants, ES8336 dynamic topology suffixes, and SoundWire 3-in-1/mono/RT700 playback-capture validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cml-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cnl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cnl-match.c

## Purpose
Cannon Lake ACPI machine-match data for RT274/ES8336 SSP designs and early SoundWire/mockup topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_cnl_machines[]` and `snd_soc_acpi_intel_cnl_sdw_machines[]`. Defines an ES83x6 codec list, an RT5682-on-link2 SoundWire address array, and SDW mockup links reused from `soc-acpi-intel-sdw-mockup-match.h`.

## Control Flow, State, and Persistence
Static machine arrays select `cnl_rt274` or dynamic ES8336 topology names for SSP boards. SoundWire entries select `sof_sdw` topologies for RT5682 link2 or mockup headset/amplifier/mic layouts. No runtime state is stored.

## Dependencies and Integration
Depends on ASoC ACPI match headers and the SoundWire mockup descriptor header. Used by Cannon Lake SOF platform matching and test/mockup SoundWire enumeration.

## Risks and Test Signals
Risks include ES8336 topology prefix using a CML filename stem, mockup entries matching only synthetic/test devices, and link2 assumptions for RT5682. Test signals are CNL ACPI matching, topology suffix generation for ES8336, SoundWire mockup matching in validation setups, and RT274/RT5682 stream tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cnl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ehl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ehl-match.c

## Purpose
Elkhart Lake ACPI match table for the RT5660 machine driver.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_ehl_machines[]` with one `10EC5660` entry mapping to `ehl_rt5660` and `sof-ehl-rt5660.tplg`.

## Control Flow, State, and Persistence
No executable control flow or persistent state exists beyond the static match entry and sentinel. ACPI HID matching selects the machine data for platform probe.

## Dependencies and Integration
Depends on ASoC ACPI match headers and the Intel match aggregate. Consumed by EHL SOF platform selection.

## Risks and Test Signals
Risks are limited to boards needing companion-codec or topology variants not represented by the single entry. Test signals are RT5660 EHL probe, topology load, and playback/capture validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ehl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-glk-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-glk-match.c

## Purpose
Gemini Lake ACPI match table for ALC298, DA7219/MAX98357A, RT5682/MAX98357A, CS42L42/MAX98357A, and ES8336 audio designs.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_glk_machines[]`. Defines codec lists for ES83x6, MAX98357A companion, and RT5682/RT5682S headset codecs, with `snd_soc_acpi_codec_list` quirks on companion-dependent entries.

## Control Flow, State, and Persistence
Static entries match ACPI HID or companion codec lists. ES8336 uses topology quirk masks so SSP number, SSP MSB, and DMIC count are appended at runtime. No mutable state is kept.

## Dependencies and Integration
Depends on ASoC ACPI match helpers. Used by GLK SOF/SST platform selection and corresponding machine drivers/topologies.

## Risks and Test Signals
Risks include companion MAX98357A detection failures, CS42L42 HID encoding differences, RT5682 versus RT5682S companion matching, and dynamic ES8336 topology suffix drift. Test signals are machine selection for each listed codec combination, topology load, speaker/headset/DMIC function, and fallback behavior when amplifier companions are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-glk-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hda-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hda-match.c

## Purpose
Generic HDA DSP machine-match table for Intel platforms using the `skl_hda_dsp_generic` machine driver.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_hda_machines[]` with a wildcard-style entry using `drv_name = "skl_hda_dsp_generic"` and topology prefix `sof-hda-generic`; `SND_SOC_ACPI_TPLG_INTEL_DMIC_NUMBER` controls runtime topology suffix generation.

## Control Flow, State, and Persistence
No runtime state exists. The entry provides generic machine data when platform selection chooses HDA DSP instead of a codec-specific SSP/SoundWire machine.

## Dependencies and Integration
Depends on ASoC ACPI Intel match helpers. Consumed by Intel DSP configuration paths that fall back to HDA generic SOF topology selection.

## Risks and Test Signals
Risks include overly broad matching when a board-specific topology is required, incorrect DMIC-count suffix generation, and topology mismatch for systems with unusual HDMI/DMIC arrangements. Test signals are generic HDA SOF probe, topology filename selection for 0/2/4 DMIC variants, and HDMI/analog/DMIC stream validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hda-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hsw-bdw-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hsw-bdw-match.c

## Purpose
Haswell/Broadwell ACPI machine-match table for legacy Intel SST/SOF audio boards using RT286, RT5650, RT5677, and RT5640 codecs.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_broadwell_machines[]` with entries for `INT343A`/`bdw_rt286`, `10EC5650`/`bdw-rt5650`, `RT5677CE`/`bdw-rt5677`, and `INT33CA`/`hsw_rt5640`, each with corresponding `sof-bdw-*.tplg` topology names.

## Control Flow, State, and Persistence
The file is static descriptor data; ACPI HID matching selects the machine driver and topology. No mutable state or quirk callback is present despite including DMI.

## Dependencies and Integration
Depends on ASoC ACPI match headers and is linked into the Intel match aggregate. Used by HSW/BDW CATPT/SST/SOF machine selection paths.

## Risks and Test Signals
Risks include stale topology naming for Haswell entries using Broadwell prefixes, unused DMI include indicating possible historical quirk removal, and lack of companion-codec disambiguation. Test signals are machine selection on HSW/BDW systems and successful topology load/playback/capture for each codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hsw-bdw-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-icl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-icl-match.c

## Purpose
Ice Lake ACPI match tables for RT274, RT5682, ES8336 SSP designs and SoundWire RT700/RT711/RT1308/RT715 topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_icl_machines[]` and `snd_soc_acpi_intel_icl_sdw_machines[]`. Defines ES83x6 codec matching, SoundWire endpoint/address descriptors for RT700, RT711, RT1308, and RT715, and link arrays `icl_rvp`, `icl_3_in_1_default`, and `icl_3_in_1_mono_amp`.

## Control Flow, State, and Persistence
Static ACPI entries select SSP machine drivers/topologies, with ES8336 using runtime topology suffix masks. SoundWire entries select `sof_sdw` and topologies based on link masks for default 3-in-1, mono-amplifier, or RT700-only designs.

## Dependencies and Integration
Depends on ASoC ACPI match helpers and the Intel match aggregate. Consumed by ICL SOF machine selection and SoundWire machine probing.

## Risks and Test Signals
Risks include incorrect RT1308 stereo aggregation endpoint metadata, ES8336 suffix mismatch, and ambiguous SoundWire link masks if firmware reports unexpected devices. Test signals are ICL ACPI matching, topology load for RT274/RT5682/ES8336, SoundWire 3-in-1 and RT700 probe, and playback/capture/headset/mic validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-icl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-jsl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-jsl-match.c

## Purpose
Jasper Lake ACPI match table for DA7219, RT5682/RT5682S, CS42L42, RT5650, ES8336, and several speaker-amplifier companion variants.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_jsl_machines[]`. Defines codec lists for ES83x6, MAX98373, RT1015, RT1015P, MAX98360A, RT5650, and RT5682/RT5682S. Uses `snd_soc_acpi_codec_list` and `.quirk_data` to distinguish machine/topology variants with shared headset codec IDs.

## Control Flow, State, and Persistence
Matching is static but order and `.quirk_data` matter for shared IDs such as `DLGS7219` and RT5682-compatible companions. ES8336 uses runtime topology suffix generation for SSP/DMIC variation. No mutable state is stored.

## Dependencies and Integration
Depends on ASoC ACPI match helpers and the Intel match aggregate. Used by JSL SOF platform selection and board machine drivers.

## Risks and Test Signals
Risks include companion codec list ordering selecting the wrong amplifier topology, reusing `sof-jsl-rt5682-rt1015.tplg` for RT1015 and RT1015P variants, and ES8336 suffix mismatch. Test signals are matching each DA7219/RT5682 amplifier variant, RT5650 probe, topology load, and speaker/headset/DMIC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-jsl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-kbl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-kbl-match.c

## Purpose
Kaby Lake ACPI match table for I2S codec boards, including RT286/NAU88L25/MAX98357A/MAX98927/RT5663/DA7219/RT5660/MAX98373 variants.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_kbl_machines[]`. Defines companion codec lists `kbl_codecs`, `kbl_poppy_codecs`, `kbl_5663_5514_codecs`, and DA7219 amplifier lists for MAX98357A, MAX98927, and MAX98373. Entries map ACPI IDs to KBL machine drivers and, for SOF-capable entries, topology filenames.

## Control Flow, State, and Persistence
Static ACPI matching selects the first entry whose HID and companion-codec quirk match. No runtime state exists; selected machine data carries driver names, topology names, and quirk data.

## Dependencies and Integration
Depends on ASoC ACPI matching and `snd_soc_acpi_codec_list`. Consumed by KBL SST/SOF platform selection and machine drivers.

## Risks and Test Signals
Risks include overlapping MAX98927/DA7219 entries, missing topology filenames on legacy SST-only entries, companion-list ordering problems, and RT5660 alternative HID handling. Test signals are machine selection for KBL reference and Chromebook-style boards, topology load where present, and amplifier/headset playback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-kbl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-lnl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-lnl-match.c

## Purpose
Lunar Lake ACPI SoundWire match data, with placeholder SSP machine array and extensive descriptors for mockup, RT71x/RT13xx, CS42L43/CS35L56, RT712/RT713/RT722, and SDCA-quirked topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_lnl_machines[]` and `snd_soc_acpi_intel_lnl_sdw_machines[]`. Defines endpoint/address arrays for CS42L43, CS35L56, RT711-SDCA, RT712/RT712-VB, RT1712, RT722, RT1316, RT1318, RT1320, RT713, RT714, and multiple link arrays. Some entries call `sof_sdw_get_tplg_files`; RT712-VB/RT713-VB entries use `snd_soc_acpi_intel_sdca_is_device_rt712_vb`.

## Control Flow, State, and Persistence
The normal machine array is sentinel-only, so SoundWire matching is the substantive path. Static link masks and address arrays select `sof_sdw` topology files. Mockup entries provide synthetic/test layouts. SDCA entries can be skipped at match time by the machine-check callback when enumerated peripherals do not expose the expected RT712-VB quirk.

## Dependencies and Integration
Depends on ASoC ACPI matching, SOF function topology library, SDCA quirk helper, and SoundWire mockup descriptors. Integrated by the Intel match aggregate and SOF SoundWire machine driver.

## Risks and Test Signals
Risks include missing non-SoundWire LNL board entries, machine-check behavior depending on `sdw_intel_ctx` shape, topology function-file generation drift, and many near-overlapping link masks. Test signals are LNL SoundWire enumeration for each supported topology, SDCA RT712-VB filter acceptance/rejection, function topology file list validation, and audio tests for CS42L43/CS35L56, RT722-only, RT1320, and mockup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-lnl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-mtl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-mtl-match.c

## Purpose
Meteor Lake ACPI match data for SSP/I2S codec boards and a large set of SoundWire topologies spanning Realtek, Cirrus, TI, Maxim, mockup, SDCA, and function-topology-enabled designs.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_mtl_machines[]` and `snd_soc_acpi_intel_mtl_sdw_machines[]`. SSP entries cover ES83x6, RT5682/RT5682S, CS42L42, DA7219, NAU8825, RT5650, and LT6911 HDMI, with topology quirk masks for dynamic amplifier/codec/DMIC suffixes. SoundWire descriptors cover RT711/RT712/RT712-VB/RT713/RT714/RT722/RT1316/RT1318/RT1712/RT1713, MAX98373, TAS2783, CS42L42, CS42L43, CS35L56, CS35L63, MAX98363, and mockup layouts.

## Control Flow, State, and Persistence
Static ACPI/companion-codec entries choose SSP machine drivers. SoundWire entries match link masks and address arrays to `sof_sdw` topologies; several entries call `sof_sdw_get_tplg_files` to augment base topology selection. RT712-VB entries use `snd_soc_acpi_intel_sdca_is_device_rt712_vb` as a machine check. No table state is mutated by this file.

## Dependencies and Integration
Depends on SoundWire Intel context types, SDCA definitions, ASoC ACPI matching, SSP common helpers, SOF function topology library, SDCA quirks, and SoundWire mockup descriptors. It is one of the central inputs to MTL SOF machine selection.

## Risks and Test Signals
Risks include high overlap among link masks, wrong topology for variants sharing filenames, SDCA filter false positives/negatives, endpoint aggregation mistakes for multi-amp Cirrus designs, and stale SSP topology suffix masks. Test signals are ACPI machine selection for each SSP board class, SoundWire match ordering across RT/Cirrus/TI/Maxim/mockup entries, generated function topology files, RT712-VB quirk filtering, and full playback/capture/jack/DMIC/speaker validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-mtl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-nvl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-nvl-match.c

## Purpose
Nova Lake placeholder ACPI match data with SoundWire mockup topology entries for early validation.

## APIs, Types, and Functions
Exports sentinel-only `snd_soc_acpi_intel_nvl_machines[]` and `snd_soc_acpi_intel_nvl_sdw_machines[]` containing three `sof_sdw` entries based on mockup headset/two-amp/mic, headset/one-amp/mic, and mic/headset/one-amp link arrays.

## Control Flow, State, and Persistence
No mutable runtime state exists. SoundWire mockup entries match synthetic link masks and select reused NVL topology filenames for validation.

## Dependencies and Integration
Depends on ASoC ACPI match headers and `soc-acpi-intel-sdw-mockup-match.h`. Integrated into the Intel match aggregate for early platform bring-up/testing.

## Risks and Test Signals
Risks include mockup-only coverage not matching production NVL hardware, topology filenames inherited from older RT711/RT1308/RT715 patterns, and no SSP machine entries. Test signals are build/export success, mockup SoundWire enumeration, and SOF topology load in NVL validation environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-nvl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ptl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ptl-match.c

## Purpose
Panther Lake ACPI match data for SSP codec boards and ordered SoundWire topologies covering mockup, Realtek SDCA, CS42L43/CS35L56, RT722/RT1320, and RT712-VB/RT713-VB variants.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_ptl_machines[]` and `snd_soc_acpi_intel_ptl_sdw_machines[]`. Defines SSP codec lists for RT5682/RT5682S, ES83x6, and LT6911 HDMI, endpoint/address descriptors for CS42L43, CS35L56, RT711-SDCA, RT712-VB, RT713-VB, RT722, and RT1320, plus link arrays for multi-link speaker/headset layouts. Several entries use `snd_soc_acpi_intel_sdca_is_device_rt712_vb` and/or `sof_sdw_get_tplg_files`.

## Control Flow, State, and Persistence
The file explicitly notes that order in `snd_soc_acpi_intel_ptl_sdw_machines[]` matters. Static link masks are matched in table order, with mockup and more-specific SDCA/CS/RT topologies preceding fallback-style entries. SSP entries use codec-list quirks and runtime topology suffix masks for dynamic configurations.

## Dependencies and Integration
Depends on ASoC ACPI matching, SSP common helpers, SOF function topology library, SDCA quirks, and SoundWire mockup descriptors. Integrated by PTL SOF platform selection and the SOF SoundWire machine driver.

## Risks and Test Signals
Risks include reordering SoundWire entries and changing match outcomes, SDCA machine-check context mismatch, topology filename reuse across hardware variants, and many similar endpoint group definitions for aggregated speakers. Test signals are PTL table-order regression tests, RT712-VB/RT713-VB quirk filtering, function topology file generation, and audio validation across mockup, RT722/RT1320, CS42L43/CS35L56, SSP RT5682/ES8336, and HDMI-SSP designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ptl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-rpl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-rpl-match.c

## Purpose
Raptor Lake ACPI match tables for SSP codec boards and SoundWire RT711/RT1316/RT1318/RT714/CS42L43 topologies.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_rpl_machines[]` and `snd_soc_acpi_intel_rpl_sdw_machines[]`. Defines endpoint/address/link descriptors for RT711, RT711-SDCA, RT1316, RT1318, RT714, CS42L43, and CRB/RVP layouts, plus codec lists for RT5682, ES83x6, MAX98357A, and LT6911 HDMI.

## Control Flow, State, and Persistence
Static SSP entries select RPL machine drivers and topology names, using companion-codec quirks or topology suffix masks for RT5682/ES8336/generic codec designs. SoundWire entries use link masks and descriptor arrays to choose `sof_sdw` topology files for 4-link, 3-link, 2-link, and link-specific CRB/RVP designs. No mutable state is stored.

## Dependencies and Integration
Depends on ASoC ACPI matching and SSP common helpers. Consumed by RPL SOF platform selection and SoundWire machine driver setup.

## Risks and Test Signals
Risks include link-mask overlap with ADL-derived topologies, incorrect topology selection for RT1316 versus RT1318 amplifier generations, generic RT5682 fallback ordering, and HDMI topology naming differences. Test signals are RPL SSP and SoundWire machine selection, topology load for each listed `.sof_tplg_filename`, and validation of headset, speaker aggregation, DMIC, and HDMI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-rpl-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.c

## Purpose
Helper module for Intel ASoC ACPI SoundWire/SDCA machine checks. It filters SoundWire machine-table entries based on enumerated SDCA peripheral quirks, currently to distinguish RT712-VB-capable devices.

## APIs, Types, and Functions
Exports namespaced symbol `snd_soc_acpi_intel_sdca_is_device_rt712_vb(void *arg)` in namespace `SND_SOC_ACPI_INTEL_SDCA_QUIRKS`. The function expects `arg` to be `struct sdw_intel_ctx *`, iterates `ctx->peripherals->array`, and returns true if `sdca_device_quirk_match(..., SDCA_QUIRKS_RT712_VB)` succeeds.

## Control Flow, State, and Persistence
The helper has no persistent state. At match time, SoundWire machine entries pass an Intel SoundWire context instead of a traditional `snd_soc_acpi_mach` pointer; a false return causes the candidate entry to be skipped.

## Dependencies and Integration
Depends on `linux/soundwire/sdw_intel.h`, `sound/sdca.h`, ASoC ACPI headers, and imports namespace `SND_SOC_SDCA`. Used by newer MTL/LNL/PTL SoundWire match tables through `.machine_check`.

## Risks and Test Signals
Risks include the non-traditional callback argument type, null or partially populated peripheral context, namespace/import mismatches, and false matches if SDCA quirk metadata changes. Test signals are module build/modpost namespace checks, RT712-VB entries matching only when expected peripherals are present, and fallback entries matching when the quirk is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.h

## Purpose
Small header declaring Intel ASoC ACPI SDCA quirk helpers used by SoundWire machine-match tables.

## APIs, Types, and Functions
Declares `bool snd_soc_acpi_intel_sdca_is_device_rt712_vb(void *arg);` and provides an include guard.

## Control Flow, State, and Persistence
No runtime state or logic exists in the header. It defines the compile-time contract for match tables that want to gate entries on RT712-VB SDCA quirk detection.

## Dependencies and Integration
Included by MTL/LNL/PTL match files and implemented by `soc-acpi-intel-sdca-quirks.c`. The declaration intentionally uses `void *` to match the generic machine-check callback shape.

## Risks and Test Signals
Risks include declaration/implementation drift, users forgetting the providing object/namespace, and the opaque argument hiding the required `sdw_intel_ctx` type. Test signals are successful builds of all users and correct runtime selection of SDCA-quirked SoundWire entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdca-quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.c

## Purpose
Reusable SoundWire mockup ACPI link descriptors for Intel ASoC machine tables. These support validation and bring-up without real codec hardware by describing synthetic headset, amplifier, microphone, and multifunction mockup devices.

## APIs, Types, and Functions
Exports four descriptor arrays: `sdw_mockup_headset_1amp_mic[]`, `sdw_mockup_headset_2amps_mic[]`, `sdw_mockup_mic_headset_1amp[]`, and `sdw_mockup_multi_func[]`. Internal static data defines single and aggregated endpoints, multifunction jack/amp/DMIC endpoints, mockup SoundWire ADR devices for headset, amp, mic, and multifunction devices, and link masks for the exported layouts.

## Control Flow, State, and Persistence
The file is static descriptor data. Platform generation tables reference exported arrays in their `snd_soc_acpi_mach.links` fields; match logic then treats the synthetic ADR/link layout like real SoundWire devices. No mutable state is kept.

## Dependencies and Integration
Depends on ASoC ACPI and Intel match headers. Included in the Intel match aggregate and referenced by CNL/MTL/LNL/NVL/PTL match files for mockup `sof_sdw` entries.

## Risks and Test Signals
Risks include synthetic ADR values colliding with real devices, endpoint grouping not matching the topology reused by a generation, typo-prone `name_prefix` strings, and mockup entries matching ahead of production entries if ordering is wrong. Test signals are SoundWire mockup enumeration, expected link-mask matching, topology load for mockup entries, and absence of mockup matches on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.h

## Purpose
Header exposing reusable SoundWire mockup link descriptors to Intel generation-specific ACPI match tables.

## APIs, Types, and Functions
Declares extern arrays `sdw_mockup_headset_1amp_mic[]`, `sdw_mockup_headset_2amps_mic[]`, `sdw_mockup_mic_headset_1amp[]`, and `sdw_mockup_multi_func[]` with type `const struct snd_soc_acpi_link_adr`.

## Control Flow, State, and Persistence
No runtime state or logic exists. The header establishes the compile-time interface for match files to reuse mockup topology descriptors.

## Dependencies and Integration
Included by CNL, MTL, LNL, NVL, PTL, and other match files that reference mockup layouts. The implementation lives in `soc-acpi-intel-sdw-mockup-match.c`.

## Risks and Test Signals
Risks include declaration/definition drift and use without linking the mockup object into `snd-soc-acpi-intel-match-y`. Test signals are successful builds of all referencing match files and correct mockup matching under SoundWire test configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-sdw-mockup-match.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-skl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-skl-match.c

## Purpose
Skylake ACPI match table for early Intel I2S machine drivers using ALC286, NAU88L25/SSM4567, and NAU88L25/MAX98357A combinations.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_skl_machines[]`. Defines `skl_codecs` companion codec list for `10508825` and `MX98357A`, then provides entries for `INT343A` -> `skl_alc286s_i2s`, `INT343B` -> `skl_n88l25_s4567`, and `MX98357A` -> `skl_n88l25_m98357a`.

## Control Flow, State, and Persistence
Static ACPI and companion-codec matching selects the machine driver. No SOF topology filenames or mutable state are present, reflecting legacy SST-era machine data.

## Dependencies and Integration
Depends on ASoC ACPI matching and `snd_soc_acpi_codec_list`. Consumed by Skylake Intel platform audio driver selection.

## Risks and Test Signals
Risks include companion codec ambiguity between NAU88L25 plus SSM4567/MAX98357A variants, lack of SOF topology metadata in this table, and ordering sensitivity between HIDs and companion IDs. Test signals are SKL ACPI match selection, correct legacy machine driver binding, and playback/capture on ALC286 and NAU88L25 amplifier designs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-skl-match.c -->
