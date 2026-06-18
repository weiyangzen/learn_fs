# Research Group subset-b-006546

Grouped research for `subset-b-006546`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tgl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tgl.c

## Purpose
PCI glue for Intel Tiger Lake generation SOF HDA platforms and close derivatives: TGL-LP, TGL-H, Elkhart Lake, Alder/Raptor Lake desktop/mobile/N variants. It maps PCI IDs to `sof_dev_desc` records that drive generic SOF PCI/HDA probe, firmware/topology file selection, IPC version selection, ACPI machine matching, and platform ops initialization.

## Important APIs, Types, and Functions
The file defines static `sof_dev_desc` instances `tgl_desc`, `tglh_desc`, `ehl_desc`, `adls_desc`, `adl_desc`, `adln_desc`, `rpls_desc`, and `rpl_desc`. Each points at a chip descriptor from `tgl.c`, HDA ops from `sof_tgl_ops`, `sof_tgl_ops_init()`, and `hda_ops_free()`. `sof_pci_ids[]` binds Intel HDA PCI device IDs to those descriptors. The `snd_sof_pci_intel_tgl_driver` uses `hda_pci_intel_probe`, `sof_pci_remove`, `sof_pci_shutdown`, and `sof_pci_pm`.

## Control Flow, State, and Persistence
There is no mutable state in this file. Probe is delegated to the generic HDA PCI path, which receives the matched `sof_dev_desc` via PCI match data. The descriptor selects ACPI machine tables, alternate SoundWire tables where available, firmware and topology paths for IPC3 and IPC4, default firmware filenames, nocodec topology, DSP ops, and resource indexes. Runtime state is allocated by the PCI/HDA/SOF core after descriptor selection.

## Dependencies and Integration
Depends on Linux PCI and module APIs, SOF PCI device helpers, ACPI machine match tables, and `hda.h` exports. It integrates with `tgl.c` for DSP hardware descriptors and ops, generic HDA probe/remove/shutdown, firmware loading paths under `intel/sof*`, topology selection, SoundWire alternate machine matching, and DSP-less HDaudio mode.

## Risks and Test Signals
Main risks are table-driven mismatches: wrong `chip_info` for a PCI ID, incorrect firmware path for IPC4 platform subdirectory, ACPI machine table mismatch, or enabling `dspless_mode_supported` beyond HDaudio-only expectations. Test signals are successful PCI probe for every listed device ID, correct IPC3/IPC4 firmware filename selection, SoundWire alternate machine selection on SDW systems, nocodec fallback loading, suspend/resume through `sof_pci_pm`, and module namespace resolution for HDA generic/common/CNL and PCI helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tgl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tng.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tng.c

## Purpose
PCI platform driver for Intel Tangier/Edison SOF devices using the older Atom HiFi DSP path and IPC3 only. It supplies PCI resource mapping, IRQ setup, debugfs regions, firmware/topology defaults, Atom-specific DSP ops, and the single Tangier chip descriptor.

## Important APIs, Types, and Functions
`tangier_pci_probe()` is the local probe hook used by `sof_tng_ops`. It sets a 31-bit DMA mask, maps the LPE BAR by subtracting `IRAM_OFFSET`, optionally maps the IMR BAR, registers the Atom IRQ handler/thread, unmasks BUSY and masks DONE interrupts through `SHIM_IMRX`, and sets the default DSP mailbox offset. `sof_tng_ops` wires Atom run/reset/IPC/machine/stream/debug/firmware-loading callbacks into SOF core operations. `tng_chip_info`, `tng_desc`, `sof_tng_machines`, `tng_debugfs`, `sof_pci_ids[]`, and `snd_sof_pci_intel_tng_driver` are the data-driven integration surface.

## Control Flow, State, and Persistence
PCI match selects `tng_desc`, then generic `sof_pci_probe()` calls the descriptor ops. `tangier_pci_probe()` populates `sdev->num_cores`, `sdev->bar[DSP_BAR]`, optional `sdev->bar[IMR_BAR]`, `sdev->ipc_irq`, and `sdev->dsp_box.offset`. Persistent runtime state is held in `snd_sof_dev` and released by devm-managed mappings/IRQs and generic SOF PCI removal. Firmware loading uses memcpy-style block writes through generic iomem helpers and Atom ops.

## Dependencies and Integration
Depends on Atom DSP helpers (`atom_run`, `atom_reset`, `atom_send_msg`, IRQ handlers, mailbox/window offsets, DAI definitions, machine selection), `shim.h` register definitions, SOF PCI core, and Xtensa arch ops. It integrates with ACPI ID `INT343A`, `edison` machine driver selection, `sof-byt.ri`, `sof-byt.tplg`, and debugfs exposure for DMAC, SSP, IRAM, DRAM, and SHIM windows.

## Risks and Test Signals
Risks include the hard 31-bit DMA mask, BIOS IMR base sentinel handling, LPE BAR base arithmetic tied to `IRAM_OFFSET`, IRQ mask polarity errors, and reuse of Baytrail firmware/topology names for Tangier. Test signals include PCI probe on SST_TNG, valid LPE/IMR mappings, IRQ delivery through Atom handlers, firmware ready mailbox at `MBOX_OFFSET`, successful playback/capture over the three SSP DAIs, and debugfs region reads in D0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.c

## Purpose
Panther Lake/Wildcat Lake SOF HDA hardware descriptor and ops customization layer. It builds on Lunar Lake and Meteor Lake code while adding Panther Lake IPC4 microphone privacy handling through the SoundWire multi-link shim.

## Important APIs, Types, and Functions
`sof_ptl_set_ops()` calls `sof_lnl_set_ops()` and then installs `sof_ptl_set_mic_privacy()` into `struct sof_ipc4_fw_data`. Mic privacy helpers include `sof_ptl_check_mic_privacy_irq()`, `sof_ptl_process_mic_privacy()`, `sof_ptl_mic_privacy_work()`, and `sof_ptl_set_mic_privacy()`. Exported descriptors are `ptl_chip_info` and `wcl_chip_info`, both `sof_intel_dsp_desc` instances for ACE 3.0-class platforms.

## Control Flow, State, and Persistence
During ops initialization, the base LNL ops are installed and the IPC4 private data gains a callback for firmware-provided mic privacy capabilities. When capability data indicates DDZE is enabled and not forced, the driver programs the SoundWire mic privacy mask and initializes delayed work in `sof_intel_hda_dev`. IRQ checks and processing only accept alternate SoundWire link events (`AZX_REG_ML_LEPTR_ID_SDW`); the worker reads current privacy state and sends `sof_ipc4_mic_privacy_state_change()` to firmware. Runtime state is transient in `hdev->mic_privacy` and HDA bus registers.

## Dependencies and Integration
Depends on HDA register and multi-link APIs, IPC4 Intel mic privacy types, MTL/LNL HDA helpers, SoundWire wake/IRQ helpers, and HDA mlink namespace exports. `ptl_chip_info` and `wcl_chip_info` integrate with PCI platform descriptor files outside this item and reuse MTL/LNL IPC registers, ROM status, D0i3 offset, CL boot, power-down, and interrupt-disable callbacks.

## Risks and Test Signals
Risks include misinterpreting firmware capability bits, scheduling work after device teardown if privacy state is not deactivated elsewhere, missed privacy events when `alt` or `elid` filtering changes, and platform-specific core counts diverging between PTL and WCL. Test signals are IPC4 capability negotiation, SoundWire privacy mask programming with the expected DDZLS mask, IRQ-to-workqueue-to-firmware notification flow, suspend/remove cancellation behavior in adjacent HDA code, and successful boot on 5-core PTL and 3-core WCL variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.h

## Purpose
Small Panther Lake internal header for mic privacy capability bit definitions and the PTL ops setup entry point.

## Important APIs, Types, and Functions
Defines `PTL_MICPVCP_DDZE_FORCED`, `PTL_MICPVCP_DDZE_ENABLED`, `PTL_MICPVCP_DDZLS_SDW`, and `PTL_MICPVCP_GET_SDW_MASK(x)`. Declares `sof_ptl_set_ops(struct snd_sof_dev *sdev, struct snd_sof_dsp_ops *dsp_ops)`.

## Control Flow, State, and Persistence
The header has no state or runtime control flow. Its macros encode the firmware capability word interpretation used by `ptl.c`: whether DDZE is enabled, forced, and which SoundWire link mask should be programmed.

## Dependencies and Integration
Relies on generic kernel bit macros such as `BIT()` and `GENMASK()` from included translation units. It is included by PTL platform setup code and is part of the internal Intel SOF HDA integration boundary.

## Risks and Test Signals
The main risk is bitfield drift with firmware/HDA capability definitions; a wrong shift or mask would program the wrong SoundWire links for mic privacy. Build coverage of `ptl.c` and runtime capability dumps or privacy IRQ tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/shim.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/shim.h

## Purpose
Shared Intel SOF shim and descriptor header for older Atom/Baytrail/Broadwell-style DSP register definitions plus the common Intel DSP hardware descriptor used by HDA and non-HDA platform code.

## Important APIs, Types, and Functions
Defines `enum sof_intel_hw_ip_version`, SHIM register offsets (`SHIM_CSR`, `SHIM_IMRX`, `SHIM_IPCX`, etc.), SHIM bit fields for CSR/interrupt/IPC/clock/HMDC registers, audio DSP PCI register offsets and power-management bits, `SOF_INTEL_PROCEN_FMT_QUIRK`, `struct sof_intel_dsp_desc`, `struct sof_intel_stream`, extern declarations for Tangier ops/chip info, and `get_chip_info()`.

## Control Flow, State, and Persistence
No executable control flow except inline `get_chip_info()`, which returns `pdata->desc->chip_info`. The header defines layout for persistent platform metadata consumed throughout Intel SOF probe, boot, IPC, SoundWire, power-management, and debug paths. Descriptor callbacks encode hardware-specific behavior such as IPC IRQ checks, SoundWire IRQ processing, DSP power-down, interrupt disable, and code-loader initialization.

## Dependencies and Integration
Included by Atom/Tangier and other Intel SOF files. It integrates platform descriptors with generic SOF device descriptors, SHIM MMIO accessors, PCI PM register programming, SoundWire handling, HDA boot paths, and per-platform hardware IP version selection.

## Risks and Test Signals
Risks are ABI-like: register offsets and bit meanings must match the platform generation, and `sof_intel_dsp_desc` fields must be filled consistently by each platform file. Test signals are compile coverage across Intel platform modules, successful SHIM IPC interrupt mask/unmask, correct PCI power bits on legacy platforms, and platform descriptors reporting the expected core count, IPC registers, SoundWire bases, and hardware IP version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/shim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/skl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/skl.c

## Purpose
Skylake/Kabylake HDA DSP ops initializer and chip descriptor for IPC4-capable CAVS 1.5 platforms. It adapts common HDA ops to SKL SRAM mailbox/window placement, boot method, IPC4 interrupt handling, and debug mapping.

## Important APIs, Types, and Functions
`skl_dsp_ipc_get_window_offset()` maps window IDs to `0x8000 + 0x2000 * id`; `skl_dsp_ipc_get_mailbox_offset()` returns `0x9000`. `sof_skl_ops_init()` copies `sof_hda_common_ops`, allocates `struct sof_ipc4_fw_data`, sets manifest offset and mtrace type, installs IPC4 send/IRQ callbacks, DAI driver ops, debug maps, IPC dump, CL boot, and post-fw-run hooks. `sof_skl_ops` and `skl_chip_info` are exported in the HDA common namespace.

## Control Flow, State, and Persistence
Ops init mutates the global `sof_skl_ops` template and stores IPC4 private data in `sdev->private`. That private data persists for the device lifetime and informs IPC4 manifest parsing and tracing. Chip descriptor state is static and supplies IPC register offsets/masks, ROM status register, core masks, and power/interrupt callbacks to the HDA core.

## Dependencies and Integration
Depends on common HDA SOF ops, IPC4 private data, HDA IPC4 send/IRQ/dump helpers, SKL CL firmware boot, and SOF topology/audio code. It is selected by PCI descriptors for SKL-family devices and integrates with CAVS 1.5 firmware manifests (`SOF_MAN4_FW_HDR_OFFSET_CAVS_1_5`) and mtrace type.

## Risks and Test Signals
Risks include global ops mutation if multiple SKL-like devices were initialized concurrently, wrong SRAM window offsets breaking mailbox/debug windows, and CAVS 1.5 manifest offset drift. Test signals are IPC4 firmware boot, mailbox discovery at the expected SRAM offsets, HDA IPC4 IRQ traffic, debugfs `hda`/`pp`/`dsp` region reads, and clean power-down/interrupt-disable callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/skl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.c

## Purpose
IPC4 Intel telemetry dump helper that reads a firmware telemetry debug slot, validates Xtensa core dump metadata, and forwards register/stack information into the existing SOF oops and stack dump paths.

## Important APIs, Types, and Functions
Exports `sof_ipc4_intel_dump_telemetry_state(struct snd_sof_dev *sdev, u32 flags)`. It uses `sof_ipc4_find_debug_slot_offset_by_type()`, `sof_mailbox_read()`, `struct sof_ipc4_telemetry_slot_data`, `struct xtensa_arch_block`, `struct sof_ipc_dsp_oops_xtensa`, `sof_oops()`, and `sof_stack()`.

## Control Flow, State, and Persistence
The function chooses log level from `SOF_DBG_DUMP_OPTIONAL`, locates the telemetry slot, reads the slot header, validates separator, reads the architecture block, checks SOC and coredump IDs, logs toolchain type, allocates an Xtensa oops object with AR register storage, copies exception PC/cause/address/status/SAR and all AR registers, then emits oops and stack dumps. Allocations are temporary and freed on all visible paths.

## Dependencies and Integration
Depends on IPC4 debug slot metadata, Xtensa register constants, SOF mailbox IO, and generic SOF crash dump helpers. Exported in the HDA common namespace for Intel IPC4 HDA dump paths to call when firmware exposes telemetry data.

## Risks and Test Signals
Risks include trusting telemetry struct layout to match firmware, rejecting useful dumps on header ID mismatch, allocation failures silently dropping optional dump data, and reading stale mailbox slots after severe firmware crashes. Test signals are induced firmware exceptions with valid telemetry separator/SOC/header IDs, Zephyr and XCC toolchain cases, optional versus error-level dump flags, and malformed slot validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.h

## Purpose
Internal Intel IPC4 telemetry header defining the firmware Xtensa architecture block layout read from telemetry debug slots.

## Important APIs, Types, and Functions
Defines packed `struct xtensa_arch_block` with SOC, version, toolchain, PC, exception cause/address, SAR, PS, compare register, AR register array, and loop registers. Declares `sof_ipc4_intel_dump_telemetry_state()`.

## Control Flow, State, and Persistence
No runtime logic. The packed struct is an ABI contract with firmware telemetry payloads; fields are copied into the generic SOF Xtensa oops format during dump handling.

## Dependencies and Integration
Includes IPC4 telemetry definitions and relies on Xtensa constants such as `XTENSA_CORE_AR_REGS_COUNT`. Used by `telemetry.c` and Intel HDA IPC4 dump code.

## Risks and Test Signals
Risks are layout and endian assumptions in a packed firmware-facing struct. Test signals are successful parsing of real firmware core dumps, struct-size compatibility with debug slot payloads, and compile-time coverage when Xtensa register count changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/tgl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/tgl.c

## Purpose
Tiger Lake-family HDA DSP ops and hardware descriptors. It adapts common HDA SOF operations for IPC3 or IPC4, firmware boot, debug regions, core power management, SoundWire handling, and chip metadata for TGL, TGL-H, EHL, and ADL-S.

## Important APIs, Types, and Functions
`sof_tgl_ops_init()` copies `sof_hda_common_ops` into global `sof_tgl_ops` and selects IPC3 or IPC4 callbacks based on `sdev->pdata->ipc_type`. IPC3 uses CNL IRQ/send/dump handlers and IPC3 power-state handling. IPC4 allocates `sof_ipc4_fw_data`, sets manifest offset, mtrace type, context-save support, external library loader, CNL IPC4 IRQ/send/dump handlers, IPC4 DSP dump, and IPC4 power-state handling. `tgl_dsp_core_get()` and `tgl_dsp_core_put()` manage primary and secondary core power through HDA or IPC PM ops. Descriptors include `tgl_chip_info`, `tglh_chip_info`, `ehl_chip_info`, and `adls_chip_info`.

## Control Flow, State, and Persistence
Ops initialization mutates the global ops table and optionally stores IPC4 private data on `sdev->private`. Runtime core-get powers primary core locally and secondary cores via firmware IPC when available; core-put asks firmware to disable a core before resetting/powering down the primary core. Static chip descriptors define core counts, IPC registers, ROM status, SSP and SoundWire bases, D0i3 offset, code-loader init, power-down, and interrupt-disable callbacks.

## Dependencies and Integration
Depends on HDA common ops, CNL IPC3/IPC4 helpers, IPC4 private data, HDA IPC4 library loading, SoundWire common helpers, CL boot with ICCMAX, and DAI driver setup. It is consumed by PCI descriptor files such as `pci-tgl.c`.

## Risks and Test Signals
Risks include global ops mutation across devices, IPC type conditionals leaving required callbacks unset, secondary-core state relying on IPC PM ops availability, and descriptor differences being subtle across related platforms. Test signals are IPC3 and IPC4 boot on TGL-class hardware, external IPC4 library loading, core enable/disable on primary and secondary cores, SoundWire IRQ/wake processing, D0i3 transitions, and debugfs region accessibility including IPC4 `fw_regs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/tgl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/tracepoints.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/tracepoints.c

## Purpose
Tracepoint definition unit for Intel SOF trace events.

## Important APIs, Types, and Functions
Defines `CREATE_TRACE_POINTS`, includes `<trace/events/sof_intel.h>`, and exports `sof_intel_hda_irq` with `EXPORT_TRACEPOINT_SYMBOL()`.

## Control Flow, State, and Persistence
No runtime control flow beyond tracepoint registration generated by the trace event header. The exported tracepoint becomes available for other modules and tracing infrastructure.

## Dependencies and Integration
Depends on the Linux tracepoint framework and the SOF Intel trace event header. Integrated by HDA IRQ instrumentation that emits `sof_intel_hda_irq`.

## Risks and Test Signals
Risks are limited to duplicate `CREATE_TRACE_POINTS` definitions or trace event header drift. Test signals are successful module link, tracepoint visibility under tracing tools, and IRQ trace emission when HDA interrupt paths fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/tracepoints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/iomem-utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/iomem-utils.c

## Purpose
Generic SOF MMIO, mailbox, and firmware block memory helpers used by platform `snd_sof_dsp_ops` implementations that expose memory-mapped DSP resources.

## Important APIs, Types, and Functions
Exports `sof_io_write()`, `sof_io_read()`, `sof_io_write64()`, `sof_io_read64()`, `sof_mailbox_write()`, `sof_mailbox_read()`, `sof_block_write()`, and `sof_block_read()`. Block helpers use `snd_sof_dsp_get_bar_index()` to map firmware block types to SOF BAR indexes.

## Control Flow, State, and Persistence
Register helpers directly call `writel/readl/writeq/readq`. Mailbox helpers calculate addresses from `sdev->bar[sdev->mailbox_bar] + offset` and use `memcpy_toio/fromio`. `sof_block_write()` writes aligned 32-bit words via `__iowrite32_copy()` and handles trailing 1-3 bytes by read-modify-write of the final word; `sof_block_read()` copies from IO memory. No state is owned here; all addressing state is in `snd_sof_dev`.

## Dependencies and Integration
Depends on Linux IO accessors, non-atomic 64-bit IO helpers, SOF ops, and platform BAR mapping. Used by IPC mailboxes, firmware loaders, debug reads, and platform ops tables such as Tangier and HDA variants.

## Risks and Test Signals
Risks include unaligned trailing-byte source access in `sof_block_write()`, missing bounds checks against BAR sizes, endianness assumptions, and writeq availability on target architectures. Test signals are firmware memcpy loading with non-word-sized blocks, mailbox read/write validation, KASAN/UBSAN around trailing writes, and successful block reads from SRAM/debug regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/iomem-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc.c

## Purpose
Generic SOF IPC core that selects IPC3 or IPC4 ops, serializes outbound messages, tracks replies, exposes common IPC send helpers, and shuts IPC down safely during device removal.

## Important APIs, Types, and Functions
Exports `sof_ipc_send_msg()`, `sof_ipc_tx_message()`, `sof_ipc_set_get_data()`, `sof_ipc_tx_message_no_pm()`, `snd_sof_ipc_get_reply()`, `snd_sof_ipc_reply()`, `snd_sof_ipc_init()`, and `snd_sof_ipc_free()`. Important state lives in `struct snd_sof_ipc`, `struct snd_sof_ipc_msg`, `ipc->tx_mutex`, `sdev->ipc_lock`, `msg->waitq`, `msg->ipc_complete`, and `ipc->disable_ipc_tx`.

## Control Flow, State, and Persistence
`snd_sof_ipc_init()` allocates IPC state, initializes serialization and waitqueue state, selects `ipc3_ops` or `ipc4_ops` from `sdev->pdata->ipc_type`, validates mandatory op groups, calls optional init, then stores the ops. `sof_ipc_send_msg()` requires firmware boot complete and TX enabled, initializes the shared message object under spinlock, points `sdev->msg` at it, and invokes the platform send op. Replies are read by IPC-version-specific `get_reply()` and completed by `snd_sof_ipc_reply()`. `snd_sof_ipc_free()` disables TX under the mutex and calls optional IPC exit.

## Dependencies and Integration
Depends on `sof-priv.h`, `sof-audio.h`, SOF platform ops, and compiled IPC3/IPC4 support. It is the integration point between higher-level PCM/control/topology code and low-level HDA/Atom/other transport send/receive callbacks.

## Risks and Test Signals
Risks include single shared message state requiring strict TX serialization, unexpected replies being ignored, firmware-state checks rejecting late cleanup IPCs, and missing mandatory ops causing probe failure. Test signals are IPC flood tests, timeout handling, reply-size validation in IPC3/IPC4, removal while IPCs are in flight, and probe failure paths for unsupported IPC versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-control.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-control.c

## Purpose
IPC3 topology control implementation for ALSA mixer, switch, enum, and bytes controls. It maps ALSA kcontrol get/put/update callbacks to SOF IPC3 component value/data messages and maintains local control caches.

## Important APIs, Types, and Functions
Core helper `sof_ipc3_set_get_kcontrol_data()` builds `SOF_IPC_COMP_SET/GET_VALUE` or `SOF_IPC_COMP_SET/GET_DATA` messages for a control's component. User-facing callbacks include volume/switch/enum get/put, bytes get/put, TLV bytes ext get/put, and volatile ext get. Notification and setup helpers include `sof_ipc3_refresh_control()`, `snd_sof_update_control()`, `sof_ipc3_control_update()`, `sof_ipc3_widget_kcontrol_setup()`, and `sof_ipc3_set_up_volume_table()`. These are exported through `tplg_ipc3_control_ops`.

## Control Flow, State, and Persistence
Control state persists in `snd_sof_control`: `ipc_control_data`, optional `old_ipc_control_data`, volume table, channel count, `comp_data_dirty`, max sizes, and component ID. Get paths refresh dirty controls from firmware when runtime PM is active. Put paths update local cache and send to firmware if active. Binary ext put validates TLV header, command ID, ABI magic/version, and data length, while keeping a backup so rejected firmware updates can restore the last known good data. Firmware notifications locate the matching widget/kcontrol, validate payload size, update local cache or mark it dirty, and notify ALSA.

## Dependencies and Integration
Depends on SOF topology control lists, widget setup mutexes, runtime PM state, IPC3 `set_get_data`, ALSA control/TLV APIs, ABI helpers, and mixer volume conversion helpers. Integrated by `ipc3-topology.c` through `tplg_ipc3_control_ops`.

## Risks and Test Signals
Risks include stale cached values when widgets are not set up, binary control size mismatches, firmware notification index/type mismatches, backup allocation size assumptions, and runtime-PM-dependent synchronization gaps. Test signals include mixer/switch/enum round trips, bytes and bytes-ext ABI rejection/rollback, volatile get from DSP, firmware-initiated control notifications, static widget readback, and suspend/resume with dirty control refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-dtrace.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-dtrace.c

## Purpose
IPC3 firmware DMA trace support. It allocates host DMA trace buffers, exposes debugfs trace/filter files, starts/stops firmware trace DMA, handles position updates, drains trace data to userspace, and cleans up on suspend, crash, resume, and free.

## Important APIs, Types, and Functions
Defines `enum sof_dtrace_state` and `struct sof_dtrace_priv`. Filter helpers parse semicolon-separated entries into `sof_ipc_trace_filter_elem` arrays and send `SOF_IPC_TRACE_FILTER_UPDATE`. Trace buffer helpers include `sof_dtrace_set_host_offset()`, `sof_dtrace_avail()`, `sof_wait_dtrace_avail()`, `dfsentry_dtrace_read()`, `ipc3_dtrace_enable()`, `ipc3_dtrace_init()`, `ipc3_dtrace_posn_update()`, `ipc3_dtrace_fw_crashed()`, `ipc3_dtrace_release()`, `ipc3_dtrace_suspend()`, `ipc3_dtrace_resume()`, and `ipc3_dtrace_free()`. Ops are exported as `ipc3_dtrace_ops`.

## Control Flow, State, and Persistence
Initialization allocates a DMA page table and scatter-gather trace buffer, creates a compressed page table for firmware, creates debugfs entries on first boot, initializes a waitqueue, and sends trace DMA parameters to firmware. Enable chooses legacy or extended DMA params based on firmware ABI, initializes platform trace host resources, sends params, then starts host tracing. Firmware position messages atomically update `host_offset` and wake readers. Read wraps file position modulo buffer size, waits for available data, syncs DMA for CPU, and copies to user. Release/stop may send `TRACE_DMA_FREE` for ABI >= 3.20, stops host trace, marks draining, and wakes readers.

## Dependencies and Integration
Depends on debugfs, ALSA DMA buffer helpers, SOF page-table creation, platform trace callbacks from `ipc3-priv.h`, IPC no-reply sends, runtime PM and firmware boot for filter updates, and `ipc3.c` trace message dispatch.

## Risks and Test Signals
Risks include leaked `elems` on parse errors inside `trace_filter_parse()`, unbounded reader sleep until firmware position update or crash/stop, DMA coherency mistakes, ABI-specific free behavior, and races around trace state/host offset. Test signals are debugfs trace reads across buffer wrap, filter write parsing and rejection, suspend D0 versus deeper suspend, firmware crash waking readers with `-EIO`, ABI 3.7 extended params, ABI 3.20 DMA free, and overflow logging from position updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-dtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-loader.c

## Purpose
IPC3 firmware validation, extended manifest parsing, and generic firmware module/block loading into DSP memory.

## Important APIs, Types, and Functions
Manifest element handlers include `ipc3_fw_ext_man_get_version()`, `ipc3_fw_ext_man_get_windows()`, `ipc3_fw_ext_man_get_cc_info()`, `ipc3_fw_ext_man_get_dbg_abi_info()`, and `ipc3_fw_ext_man_get_config_data()`. Parser/loader helpers include `ipc3_fw_ext_man_size()`, `sof_ipc3_fw_parse_ext_man()`, `sof_ipc3_parse_module_memcpy()`, `sof_ipc3_load_fw_to_dsp()`, and `sof_ipc3_validate_firmware()`. Exported loader ops are `ipc3_loader_ops`.

## Control Flow, State, and Persistence
Validation checks payload offset, firmware signature, and file-size consistency. Extended manifest parsing first verifies magic, size, and version, then iterates bounded element headers and dispatches version/window/compiler/debug/config/platform config handlers. Version and flags populate `sdev->fw_ready`; windows and compiler info populate SOF device caches/debugfs through IPC3 helpers. Firmware loading locates the SOF firmware header after any manifest payload offset, selects a platform custom module loader or generic memcpy loader, iterates modules, and writes IRAM/DRAM/SRAM blocks after size/type/alignment checks.

## Dependencies and Integration
Depends on Linux firmware objects, SOF firmware/header formats, IPC3 ready/window/compiler helpers from `ipc3.c`, debug memory info initialization, platform extended manifest parsing, and `snd_sof_dsp_block_write()`. Used by generic IPC initialization through `ipc3_ops.fw_loader`.

## Risks and Test Signals
Risks include malformed firmware integer bounds, extended manifest size trusting `head->full_size` after initial checks, unsupported block types silently skipped for reserved ranges, alignment rejection of non-word block sizes, and config token behavior partly TODO for IPC message size. Test signals are invalid signature/size tests, manifest version incompatibility, mixed element parsing, memory usage scan token triggering debug memory info, block-write failure injection, and custom platform module loader selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-pcm.c

## Purpose
IPC3 PCM operations for hw_params, hw_free, trigger, and DAI link fixup. It converts ALSA PCM/runtime parameters and platform stream parameters into IPC3 stream messages and constrains backend DAI links from topology data.

## Important APIs, Types, and Functions
`sof_ipc3_pcm_hw_params()` builds `sof_ipc_pcm_params`, sends `SOF_IPC_STREAM_PCM_PARAMS`, receives `sof_ipc_pcm_params_reply`, and stores the firmware position offset. `sof_ipc3_pcm_hw_free()` sends `SOF_IPC_STREAM_PCM_FREE` when a stream was prepared. `sof_ipc3_pcm_trigger()` maps ALSA trigger commands to IPC3 trigger commands. `sof_ipc3_pcm_dai_link_fixup()` constrains formats/rates/channels from `sof_dai_private_data`; `ssp_dai_config_pcm_params_match()` selects SSP topology config by sample rate. Ops are exported as `ipc3_pcm_ops`.

## Control Flow, State, and Persistence
Per-stream state lives in `snd_sof_pcm` stream fields: component ID, page table address, position offset, prepared flags, and runtime PCM params. Hw_params fills buffer page count, DMA address, stream tag, format, rate, channel count, period bytes, no-position/continuous-position flags, and optional physical address override. DAI fixup mutates ALSA hw_params intervals and DPCM trigger order based on DAI type and cached topology config.

## Dependencies and Integration
Depends on ALSA PCM params, SOF PCM lookup helpers, IPC send helpers, page-table DMA setup created elsewhere, DAI private data from `ipc3-topology.c`, and platform stream params from platform drivers. Integrates with HDA/ALH/SSP/DMIC/AMD/i.MX/MediaTek DAI types through shared topology structures.

## Risks and Test Signals
Risks include format mapping gaps, ABI-specific no-position handling, stale or missing DAI private data, SSP config selection by rate only, and backend trigger-order mutations affecting DPCM sequencing. Test signals are hw_params/free/trigger for playback and capture, supported formats S16/S24_4LE/S32/FLOAT, no IPC position on old and new ABI firmware, DAI link fixup for every supported DAI type, and invalid topology data rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-priv.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-priv.h

## Purpose
Private IPC3 header tying together IPC3 PCM, topology, control, firmware loader, tracing, ready-message helpers, RX dispatch, and platform trace callback wrappers.

## Important APIs, Types, and Functions
Declares `ipc3_pcm_ops`, `ipc3_tplg_ops`, `tplg_ipc3_control_ops`, `ipc3_loader_ops`, `ipc3_dtrace_ops`, `sof_ipc3_get_ext_windows()`, `sof_ipc3_get_cc_info()`, `sof_ipc3_validate_fw_version()`, `ipc3_dtrace_posn_update()`, and `sof_ipc3_do_rx_work()`. Inline wrappers `sof_dtrace_host_init()`, `sof_dtrace_host_release()`, and `sof_dtrace_host_trigger()` call optional platform trace ops from the selected descriptor.

## Control Flow, State, and Persistence
The header owns no persistent state. The inline wrappers make platform trace callbacks optional and return success when unsupported, allowing generic IPC3 dtrace code to run on platforms without host-specific trace setup.

## Dependencies and Integration
Includes `sof-priv.h` and is included by IPC3 core, topology, loader, control, PCM, and dtrace files. It is the internal contract that lets `ipc.c` use `ipc3_ops` as a coherent ops aggregate.

## Risks and Test Signals
Risks include missing declarations when new IPC3 sub-ops are added, optional trace wrappers hiding unsupported platform functionality, and descriptor ops accessed through `sdev->pdata->desc->ops` rather than runtime-mutated ops. Build coverage of all IPC3 objects and trace init on platforms with and without trace callbacks are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-topology.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-topology.c

## Purpose
IPC3 topology translation layer. It parses ALSA topology tokens into SOF IPC3 component, pipeline, route, control, and DAI configuration messages; sets up and tears down DSP widgets and routes; handles keyword-detect DAPM events; and rebuilds/static-tears-down pipelines across verification and suspend/resume.

## Important APIs, Types, and Functions
Defines token tables for PCM, pipeline, scheduler, component, core, UUID, buffers, volume, SRC/ASRC/process, DAI links, HDA/SSP/ALH/DMIC/ESAI/SAI/AFE/ACP/MICFIL/ACP_SDW families, exposed as `ipc3_token_list`. Widget setup helpers include `sof_comp_alloc()`, host/tone/mixer/pipeline/buffer/SRC/ASRC/mux/PGA/process/DAI setup functions, `sof_ipc3_widget_setup()`, and free counterparts. DAI link loaders include HDA, SAI, ESAI, MICFIL, ACP DMIC/BT/SP/HS/SDW, AFE, SSP, DMIC, and ALH. Pipeline/control operations include `sof_ipc3_route_setup()`, control load/setup/free helpers, keyword-detect PCM/trigger/DAPM handlers, `sof_ipc3_complete_pipeline()`, `sof_ipc3_dai_config()`, `sof_ipc3_set_up_all_pipelines()`, `sof_ipc3_tear_down_all_pipelines()`, `sof_ipc3_parse_manifest()`, and `sof_ipc3_link_setup()`. Ops are exported as `ipc3_tplg_ops`.

## Control Flow, State, and Persistence
Topology load creates per-widget private IPC payloads and per-DAI private config (`sof_dai_private_data`) from topology tuples/hw configs. Widget setup sends component, pipeline, buffer, or DAI IPCs to firmware; route setup sends buffer-to-component connections; completion sends `PIPE_COMPLETE`. DAI config persists current hardware config and mutates flags/link DMA/ALH stream IDs during hw_params, triggers, and hw_free. Suspend/verification teardown frees non-scheduler widgets first, handles paused pipelines, then frees schedulers and clears route setup flags. Static pipeline restore recreates widgets, routes, and completion state while respecting firmware ABI differences and dynamic pipeline flags.

## Dependencies and Integration
Depends on ALSA topology token APIs, SOF topology helpers (`sof_update_ipc_object`, widget/route setup wrappers, control lists), IPC3 control ops, PCM params, firmware ABI/version fields, DPCM trigger semantics, and platform-specific DAI formats. Integrated by `ipc3_ops.tplg`, ALSA card topology loading, PCM hw_params/hw_free, and PM suspend/resume.

## Risks and Test Signals
Risks are high because this file bridges topology ABI to firmware ABI: token size/count mismatches, DAI type coverage gaps, ALH index base conversion, SSP validation limits, DMIC ABI backward compatibility, process private data exceeding IPC message size, static versus dynamic pipeline restore differences, and firmware-version-specific scheduler handling. Test signals include topology ABI compatibility tests, topology load for every widget and DAI type, route setup only for IPC3-supported buffer/component links, keyword-detect DAPM start/stop, DAI_CONFIG flag preservation, suspend/resume with running and paused streams, dynamic pipeline override debug flags, and first-boot topology verification/teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3.c

## Purpose
Core IPC3 implementation for SOF. It logs and sends IPC3 messages, waits for replies, handles oversized control payload chunking, parses firmware-ready mailbox data, dispatches inbound notifications, implements IPC3 PM messages, and aggregates IPC3 ops.

## Important APIs, Types, and Functions
Important functions include `ipc3_log_header()`, `sof_ipc3_get_reply()`, `ipc3_wait_tx_done()`, `ipc3_tx_msg_unlocked()`, `sof_ipc3_tx_msg()`, `sof_ipc3_set_get_data()`, `sof_ipc3_get_ext_windows()`, `sof_ipc3_get_cc_info()`, `ipc3_fw_parse_ext_data()`, `ipc3_get_windows()`, `sof_ipc3_validate_fw_version()`, `ipc3_fw_ready()`, stream handlers `ipc3_period_elapsed()` and `ipc3_xrun()`, message dispatchers `ipc3_stream_message()`, `ipc3_comp_notification()`, `ipc3_trace_message()`, exported `sof_ipc3_do_rx_work()`, `sof_ipc3_rx_msg()`, and PM helpers for core state, context save/restore, and PM gate. `ipc3_ops` aggregates topology, PM, PCM, loader, dtrace, TX/RX, data transfer, and reply operations.

## Control Flow, State, and Persistence
TX paths optionally resume DSP to D0, serialize on `ipc->tx_mutex`, install shared message state via generic `sof_ipc_send_msg()`, wait on the message waitqueue, copy replies, and handle timeout as firmware exception. Large control data is split into chunks no larger than `ipc->max_payload_size`, with `msg_index`, `num_elems`, and `elems_remaining` tracking progress. Firmware-ready handling reads the ready struct from SRAM on first boot, validates ABI, parses extended data, sets inbox/outbox/stream/debug mailbox regions, adds debugfs windows, and allocates the reply buffer. RX reads headers/messages from the outbox, validates size, dispatches FW_READY, component control notifications, stream positions/XRUNs, trace DMA positions, and client IPC notifications. PM helpers send IPC3 context/core/gate commands.

## Dependencies and Integration
Depends on SOF IPC/control/stream UAPI headers, trace events, IPC3 topology/control/PCM/loader/dtrace ops, SOF mailbox/window/block IO, ALSA PCM/compress notifications, client IPC dispatcher, and platform send/mailbox callbacks. It is selected by `snd_sof_ipc_init()` for `SOF_IPC_TYPE_3`.

## Risks and Test Signals
Risks include IPC timeout recovery correctness, reply-size validation, chunked control offset arithmetic, firmware-ready extended data bounds, mailbox window mismatch between manifest and firmware, and inbound message size validation. Test signals are IPC flood and timeout tests, firmware ABI strict/non-strict compatibility, FW_READY with manifest and mailbox windows, stream period/XRUN notifications, control notifications, trace DMA position updates, core enable/disable IPCs, context save/restore, PM gate IPC in low-power states, and debug payload dump paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3.c -->
