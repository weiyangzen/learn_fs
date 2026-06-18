# subset-b-006544 SOF Intel research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/Kconfig

Purpose: this Kconfig file defines the Intel Sound Open Firmware driver feature graph for Atom ACPI platforms, HDA PCI platforms, optional HDA codec/link support, and SoundWire support. The top-level `SND_SOC_SOF_INTEL_TOPLEVEL` gate restricts the subtree to x86 or compile-test builds. The file then splits ACPI-era devices from PCI/HDA devices and uses internal helper symbols such as `SND_SOC_SOF_INTEL_COMMON`, `SND_SOC_SOF_HDA_GENERIC`, `SND_SOC_SOF_INTEL_CNL`, and `SND_SOC_SOF_INTEL_TGL` to share dependency selections.

Important symbols and dependencies: Baytrail, Broadwell, Merrifield, Skylake, KabyLake, Apollolake, Geminilake, Cannonlake, CoffeeLake, CometLake, IceLake, JasperLake, TigerLake, ElkhartLake, AlderLake, MeteorLake, LunarLake, PantherLake, and NovaLake are represented as user-visible platform toggles or internal family toggles. ACPI devices select `SND_SOC_SOF_ACPI_DEV`; PCI devices select `SND_SOC_SOF_PCI_DEV` through `SND_SOC_SOF_HDA_GENERIC` or family helpers. IPC protocol support is explicit: older Atom/BDW paths select IPC3, while HDA generations select IPC3, IPC4, or IPC4 only for newer ACE families.

Control flow and integration: the file is not runtime code, but it controls which objects are reachable in `Makefile` and which source-level operations are compiled. `SND_SOC_SOF_HDA_LINK`, `SND_SOC_SOF_HDA_AUDIO_CODEC`, `SND_SOC_SOF_INTEL_SOUNDWIRE`, and `SND_SOC_SOF_HDA_PROBES` gate large conditional blocks in the HDA bus, codec, DAI, and debug-probe files. SoundWire support deliberately depends on ACPI and SOUNDWIRE and avoids invalid `m` versus `y` combinations.

State and persistence behavior: configuration choices become build-time persistent kernel/module ABI decisions. A distro enabling broad HDA generic helpers builds large shared operation tables, codec probing, SoundWire helpers, and IPC protocol paths; disabling link or codec options compiles stubs and prevents the relevant runtime state from existing.

Risks: wrong `select` relationships can silently omit shared helpers, produce unresolved symbols, or enable runtime paths without their bus dependencies. The highest-risk edits are family-helper symbols because multiple user-visible platforms inherit them. Test signals include `allyesconfig`, `allmodconfig`, platform-specific randconfig, and checking that object lists match every selected symbol in the adjacent `Makefile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/Makefile

Purpose: this Makefile maps the Kconfig symbols in the same directory to loadable or built-in SOF Intel objects. It defines composite modules for ACPI Atom/Broadwell support, the shared HDA common layer, HDA generic glue, HDA link codecs, HDA multi-link, SoundWire bridge pieces, and PCI family drivers.

Important build products: `snd-sof-acpi-intel-byt-y` and `snd-sof-acpi-intel-bdw-y` are narrow ACPI modules. `snd-sof-intel-hda-common-y` is the large common module containing loader, stream, trace, DSP, IPC, controller, PCM, DAI, bus, telemetry, and tracepoint code, with optional `hda-probes.o`. `snd-sof-intel-hda-generic-y` adds `hda.o` and common ops. Per-family PCI modules pair discovery glue such as `pci-apl.o` or `pci-cnl.o` with generation-specific operation files such as `apl.o`, `cnl.o`, or `hda-loader-skl.o`.

Control flow and integration: the object graph mirrors the runtime architecture. Kconfig chooses a platform symbol, the Makefile emits the corresponding object, and the platform object installs `snd_sof_dsp_ops` and `sof_intel_dsp_desc` structures used by the SOF core. `CONFIG_SND_SOC_SOF_HDA_COMMON`, `CONFIG_SND_SOC_SOF_HDA_GENERIC`, and `CONFIG_SND_SOC_SOF_HDA` intentionally separate core HDA DSP support from generic PCI matching and legacy HDA codec support.

State and persistence behavior: no runtime state is stored here, but build outputs persist as module boundaries and namespace exports. Moving a source file between composite targets changes symbol visibility and module load ordering, especially for namespace-imported symbols.

Dependencies and risks: the risk is mismatching Kconfig and object membership. For example, enabling CNL-family ops requires the common HDA object that exports `hda_dsp_*`, `hda_ipc*`, and DAI helpers. Optional probes and SoundWire bridge objects must stay behind their config gates. Test signals are kernel module link success, `modpost` namespace warnings, and boot/probe logs confirming the selected platform module loads with the expected common module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/apl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/apl.c

Purpose: `apl.c` specializes the shared HDA SOF operations for Apollolake and Geminilake, which use cAVS 1.5+ HDA DSP hardware. It exports `sof_apl_ops_init()` and `apl_chip_info`, letting PCI discovery code clone common HDA behavior and install APL-specific IPC, debug, boot, and descriptor data.

Important APIs and types: `sof_apl_ops_init(struct snd_sof_dev *sdev)` copies `sof_hda_common_ops` into the global `sof_apl_ops`, then selects IPC3 or IPC4 handlers depending on `sdev->pdata->ipc_type`. IPC3 uses `hda_dsp_ipc_irq_thread`, `hda_dsp_ipc_send_msg`, `hda_ipc_dump`, and `hda_dsp_set_power_state_ipc3`. IPC4 allocates `struct sof_ipc4_fw_data`, sets the manifest offset, mtrace type, library-loader callback, `hda_dsp_ipc4_irq_thread`, `hda_dsp_ipc4_send_msg`, `hda_ipc4_dump`, and IPC4 power-state callback.

Control flow: initialization is table-driven. The function starts from common ops, installs protocol-specific hooks, calls `hda_set_dai_drv_ops()` to bind DAI callbacks, sets the APL debug map, and points firmware execution to `hda_dsp_cl_boot_firmware` with `hda_dsp_post_fw_run` and `hda_dsp_core_get`. `apl_chip_info` supplies the register layout, IPC request/ack masks, ROM status register, SSP count/base, D0I3 offset, cAVS quirk, and callbacks for boot, power-down, interrupts, and IPC IRQ detection.

State and persistence behavior: IPC4 setup stores heap-allocated private firmware data in `sdev->private` and relies on later HDA cleanup to free it. The descriptor is constant and shared. Runtime state is primarily held by the common HDA layer.

Dependencies, risks, and test signals: this file depends on `hda.h`, IPC4 private data, SOF extended manifest v4, and common HDA exports. Risks include leaking or misconfiguring `sdev->private` for IPC4, selecting the wrong mtrace type, or mismatching IPC registers in `apl_chip_info`. Test signals include successful IPC3 and IPC4 firmware boot, external IPC4 library load, DAI ops assignment, and debugfs region visibility for `hda`, `pp`, and `dsp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/apl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.c

Purpose: `atom.c` implements shared IPC, reset, run, dump, machine-selection, and DAI support for Atom-class SOF platforms using the older HiFi EP SHIM interface. Baytrail, Cherrytrail, Braswell, and Merrifield-style code can reuse these exported helpers.

Important APIs: exported functions include `atom_irq_handler()`, `atom_irq_thread()`, `atom_send_msg()`, `atom_get_mailbox_offset()`, `atom_get_window_offset()`, `atom_run()`, `atom_reset()`, `atom_dump()`, `atom_machine_select()`, `atom_set_mach_params()`, and the `atom_dai[]` SSP DAI table. Internal helpers `atom_host_done()` and `atom_dsp_done()` implement doorbell completion.

Control flow: the hard IRQ reads `SHIM_IPCX` and `SHIM_IPCD`, masks DONE or BUSY interrupts, and wakes the threaded IRQ. The thread processes DSP replies under `sdev->ipc_lock`, calls `snd_sof_ipc_process_reply()`, clears DONE, handles firmware-originated messages or panic magic, then acknowledges BUSY and unmasks the next interrupt. `atom_send_msg()` writes the host mailbox and rings `SHIM_BYT_IPCX_BUSY`. Reset stalls the DSP, sets reset/vector bits, then releases reset for firmware loading. Run clears stall and polls `PWAITMODE`.

State and persistence behavior: mailbox and window offsets are fixed to `MBOX_OFFSET`; panic/oops state is read from `sdev->dsp_oops_offset`. Machine selection mutates `sof_pdata->tplg_filename` and machine params. On BYT-CR systems, it rewrites topology names from the matched ACPI machine to an `ssp0` variant.

Dependencies and integration: this file depends on SOF IPC core helpers, Xtensa panic printing, ACPI machine tables, Intel DSP config, and Atom SHIM register definitions. It integrates with `byt.c` through `snd_sof_dsp_ops`.

Risks and test signals: interrupt races are the main risk, especially masking/unmasking DONE and BUSY around reply processing. Topology filename fixups assume a `.tplg` extension and can fail allocation. Test signals include IPC round trips, panic dump readability, BYT-CR SSP0 topology selection, suspend/resume interrupt unmask state, and all six exported SSP DAI names appearing as expected on Cherrytrail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.h

Purpose: `atom.h` is the shared register-layout and API contract for Atom HiFi EP SOF support. It collects DSP memory/peripheral offsets, BAR indexes, panic decoding, mailbox sizing, and function declarations consumed by `atom.c`, `byt.c`, and any other Atom-family platform glue.

Important definitions: it defines IRAM, DRAM, SHIM, mailbox, exception, DMAC, SSP, stack dump, and PCI BAR sizes. BAR indexes are `DSP_BAR`, `PCI_BAR`, and `IMR_BAR`. `PANIC_OFFSET(x)` extracts the high panic offset bits from an IPC value. The public prototypes cover IRQ handling, IPC send, mailbox/window offsets, run/reset/dump, ACPI machine selection, machine parameter assignment, and the exported `atom_dai[]` table.

Control flow and integration: because this is a header, it does not execute, but it fixes the low-level addressing assumptions used by the Atom operations. `byt.c` uses memory and peripheral constants for debugfs maps and MMIO BAR setup, while `atom.c` uses SHIM/mailbox constants for IPC and panic dump flow.

State and persistence behavior: constants here define persistent ABI-like hardware assumptions. A wrong offset would make state reads and writes hit the wrong register or memory window across every Atom platform using these helpers.

Dependencies, risks, and test signals: the header assumes `struct snd_sof_dev`, `struct snd_sof_ipc_msg`, `struct snd_soc_acpi_mach`, and `struct snd_soc_dai_driver` are visible to including C files. Risks include shared-name collisions for generic BAR constants and accidental drift from hardware manuals. Test signals are successful Atom firmware load, readable debugfs memory windows, working IPC panic decoding, and no compiler warnings for exported function prototypes or namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/bdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/bdw.c

Purpose: `bdw.c` is the complete ACPI platform driver and DSP operation implementation for Broadwell SOF. It handles MMIO mapping, PCI power setup, IPC, debug dumps, machine selection, DAI exposure, and ACPI probe registration for device `INT3438`.

Important APIs and structures: the file defines `bdw_probe()`, `bdw_run()`, `bdw_reset()`, `bdw_set_dsp_D0()`, `bdw_irq_handler()`, `bdw_irq_thread()`, `bdw_send_msg()`, mailbox/window offset helpers, `bdw_machine_select()`, `bdw_set_mach_params()`, `bdw_dai[]`, `sof_bdw_ops`, `bdw_chip_info`, `sof_acpi_broadwell_desc`, and `snd_sof_acpi_intel_bdw_driver`.

Control flow: probe maps LPE and PCI resources, records DSP and mailbox BARs, requests the platform IPC IRQ, forces the DSP into D0, sets a 31-bit DMA mask, and sets the firmware-ready mailbox offset. `bdw_set_dsp_D0()` is the hardware bring-up sequence: disable/enable gating bits, set PCI PM D0, configure clocks and SSP, reset the core, configure power gating, clear IPC registers, and enable interrupts. IPC handling follows the older SHIM model: the IRQ handler detects BUSY/DONE, the thread masks, processes replies or firmware messages/panics, and acknowledges via `bdw_host_done()` or `bdw_dsp_done()`.

State and persistence behavior: runtime state lives in mapped BAR pointers, `sdev->mmio_bar`, `sdev->mailbox_bar`, `sdev->dsp_oops_offset`, IRQ registration, ACPI selected topology, and machine params. Debugfs exposes DMAC, SSP, IRAM, DRAM, and SHIM windows.

Dependencies and integration: this driver depends on SOF ACPI probe infrastructure, Intel DSP driver selection, Xtensa dumps, SOF stream helpers, and ACPI machine tables. It imports the SOF Xtensa and ACPI namespaces.

Risks and test signals: Broadwell is explicitly less robust for DMA and suspend/resume, so power sequencing and interrupt mask handling are high risk. Test with ACPI driver selection arbitration, firmware boot, IPC reply/message handling, panic dump, no-codec topology fallback, runtime/system suspend, and DMA mask correctness on real BDW hardware or targeted emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/bdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/byt.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/byt.c

Purpose: `byt.c` provides the ACPI platform driver and operation tables for Baytrail, Baytrail-CR, Braswell, and Cherrytrail SOF devices. It combines Atom shared helpers with platform-specific resource mapping, debug maps, DMA mask setup, ACPI descriptors, and probe filtering.

Important APIs and structures: key functions are `byt_acpi_probe()`, `byt_suspend()`, `byt_resume()`, `byt_remove()`, `byt_reset_dsp_disable_int()`, and `sof_baytrail_probe()`. Important static objects include BYT and CHT debugfs maps, `sof_byt_ops`, `sof_cht_ops`, `byt_chip_info`, `cht_chip_info`, three `sof_dev_desc` instances for BYT, BYT-CR, and CHT, and the ACPI match table for `80860F28` and `808622A8`.

Control flow: `sof_baytrail_probe()` verifies the ACPI ID, consults `snd_intel_acpi_dsp_driver_probe()`, switches to the BYT-CR descriptor if board quirks match, and calls `sof_acpi_probe()`. `byt_acpi_probe()` gets chip info, forces a 31-bit DMA mask, maps LPE and optional IMR resources, requests the host IPC IRQ with Atom handlers, enables BUSY while masking DONE by default, and sets `sdev->dsp_box.offset`.

State and persistence behavior: descriptor data persists firmware path, topology path, default firmware filename, no-codec topology, IRQ/resource indexes, and IPC3-only support. Runtime state includes mapped DSP/IMR BARs, IRQ, mailbox offsets, and interrupt masks. Suspend, remove, and reset paths explicitly reset the DSP and disable both host and DSP interrupt directions.

Dependencies and integration: it depends on Atom helpers from `atom.c`, SOF ACPI device glue, ACPI machine tables, Intel DSP selection, and BYT-CR quirk detection.

Risks and test signals: IMR may be absent or bogus, and the code deliberately ignores BIOS sentinel base values. BYT-CR topology and IRQ-index differences are fragile. Test signals include correct descriptor selection, successful ioremap of LPE, optional IMR handling, IPC3 firmware load for `sof-byt.ri` and `sof-cht.ri`, debugfs region access, and suspend/resume preserving interrupt state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/byt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/cnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/cnl.c

Purpose: `cnl.c` specializes HDA common operations for Cannonlake-class cAVS 1.8 and JasperLake cAVS 2.0 platforms, including sideband IPC register handling, IPC4 support, debug dumps, and exported chip descriptors.

Important APIs: exported functions include `cnl_ipc_irq_thread()`, `cnl_ipc4_irq_thread()`, `cnl_ipc_send_msg()`, `cnl_ipc4_send_msg()`, `cnl_ipc_dump()`, `cnl_ipc4_dump()`, `sof_cnl_ops_init()`, and exported descriptors `cnl_chip_info` and `jsl_chip_info`. Internal helpers acknowledge target and initiator IPC channels through `cnl_ipc_host_done()` and `cnl_ipc_dsp_done()`, while `cnl_compact_ipc_compress()` encodes PM_GATE IPC3 messages into compact registers.

Control flow: IPC3 and IPC4 IRQ threads read sideband HIPCI/HIPCT registers, distinguish host acknowledgements from DSP-originated messages, handle replies only after firmware boot, route notifications through SOF IPC receive paths, and handle panic magic with boot-retry awareness. Send functions write mailbox payloads when needed, write extension registers, set BUSY in the primary register, and schedule D0I3 delayed work for non-PM IPCs. IPC4 transmit defers a message in `hdev->delayed_ipc_tx_msg` when the request register is busy and retries after ACK.

State and persistence behavior: `sof_cnl_ops_init()` clones common HDA ops and mutates the global `sof_cnl_ops`. IPC4 allocation stores `struct sof_ipc4_fw_data` in `sdev->private`, including manifest offset, mtrace type, and library loading callback. Chip descriptors persist register offsets, masks, SoundWire hooks, SSP layout, ROM timeout, and power callbacks.

Dependencies, risks, and test signals: this file depends on HDA common IPC/DSP helpers, IPC4 topology headers, tracepoints, SoundWire helpers, and the code loader. Risks include sideband register ack ordering, delayed IPC lifetime, compact PM_GATE encoding, and boot-panic recoverability classification. Test IPC3 and IPC4 boot, D0I3 PM_GATE transitions, delayed IPC send under busy conditions, SoundWire IRQ/wake handling, and JasperLake using CNL ops despite ICL lineage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/cnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ext_manifest.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/ext_manifest.h

Purpose: `ext_manifest.h` defines Intel cAVS-specific extended manifest platform configuration structures. These metadata entries live outside the signed firmware image and let the HDA code consume platform-specific firmware hints such as clock policy and mailbox sizes.

Important types: `enum sof_cavs_config_elem_type` defines tokens for empty entries, LPRO clock configuration, outbox size, and inbox size. `struct sof_ext_man_cavs_config_data` wraps a generic `struct sof_ext_man_elem_header` followed by a flexible array of `struct sof_config_elem` values and is marked packed to match firmware binary layout.

Control flow and integration: the header is consumed by `hda-loader.c`, specifically `hda_dsp_ext_man_get_cavs_config_data()`. That parser uses `container_of()` from a generic extended manifest element header, computes the element count from the header size, and handles these tokens.

State and persistence behavior: parsed values are firmware-provided persistent runtime configuration. Currently the LPRO token updates `struct sof_intel_hda_dev::clk_config_lpro`; inbox/outbox size tokens are recognized but ignored. Unsupported token types are logged.

Dependencies and risks: this header depends on `<sound/sof/ext_manifest.h>` for common manifest element definitions. Risks are binary compatibility and bounds: the flexible-array layout must match firmware exactly, and parser changes must validate `hdr->size` before walking elements. Test signals include loading firmware with cAVS platform config, confirming LPRO/HPRO debug logs, rejecting inconsistent element counts, and ensuring unknown tokens do not abort boot unless policy changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ext_manifest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-bus.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-bus.c

Purpose: `hda-bus.c` initializes and exits the SOF-owned HDA bus abstraction, with conditional support for HDA link and legacy HDA codec drivers. It bridges SOF device state to the ALSA HD-audio core.

Important APIs and types: `sof_hda_bus_init(struct snd_sof_dev *sdev, struct device *dev)` and `sof_hda_bus_exit(struct snd_sof_dev *sdev)` are exported. When HDA audio codec support is enabled, `bus_core_ops` supplies command, response, and link-power callbacks, and `sof_hda_bus_link_power()` customizes codec link power handling. `update_codec_wake_enable()` manages WAKEEN bits according to link power state.

Control flow: init selects one of three paths. With HDA link and codec support, it calls `snd_hdac_ext_bus_init()` with SOF-specific bus core ops and codec extension ops, and enables PIO command mode for ACE 2.0+ hardware. With HDA link but no codec support, it initializes an extended bus without codec ops. Without HDA link support, it manually initializes a minimal `hdac_bus` with device, stream list, IRQ sentinel, index, and register lock.

State and persistence behavior: bus init mutates `struct hdac_bus` inside SOF HDA private state, including stream lists, codec power tracking, command mode, and link power callbacks. Link power changes can release display-power references for iDisp and update WAKEEN for disabled codecs.

Dependencies and integration: it depends on ALSA HDA core, HDA codec, i915 display-power helpers, and `hda.h` SOF conversion helpers. It is called by common HDA probe/remove code outside this work item.

Risks and test signals: link-power state and WAKEEN programming are subtle, especially for display codec power reference symmetry. Minimal-bus mode must still satisfy stream code when HDA link support is compiled out. Test signals include codec command response success, no display power leaks on HDMI codec runtime suspend, codec wake from disabled links, and clean `snd_hdac_ext_bus_exit()` on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-codec.c

Purpose: `hda-codec.c` handles legacy HD-audio codec discovery, module binding, command I/O lifecycle, jack wake/check behavior, RIRB status handling, and i915 display audio power integration for SOF HDA platforms.

Important APIs: exported functions include `hda_codec_probe_bus()`, `hda_codec_detect_mask()`, `hda_codec_jack_wake_enable()`, `hda_codec_jack_check()`, command I/O init/resume/stop/suspend helpers, RIRB helpers, wakeup control, device removal, and optional i915 init/exit/display-power helpers. The module parameter `codec_mask` filters probed codec slots.

Control flow: `hda_codec_detect_mask()` reads `STATESTS` if no codec mask exists and applies the module filter. `hda_codec_probe_bus()` walks up to `HDA_MAX_CODECS`, probing each masked address. `hda_codec_probe()` sends a vendor-ID verb with retries, allocates `hdac_hda_priv`, creates an HDA codec device, marks display codecs as needing i915 audio power, chooses generic probing when requested, registers the device, and requests or attaches the codec module. Failure unregisters and drops the codec device.

State and persistence behavior: runtime state includes `bus->codec_mask`, `codec_powered`, command DMA state, WAKEEN/STATESTS/RIRBSTS hardware bits, codec private data, and i915 audio component references. Jack wake enable programs WAKEEN only for codecs with jack tables when enabling, and clears HD-audio codec WAKEEN when disabling.

Dependencies and integration: this file is compiled only with HDA audio codec support and optionally HDMI codec support. It relies on ALSA HDA codec core, module autoloading, SOF no-codec debug flags, and i915 HDA component helpers.

Risks and test signals: codec probing crosses firmware, BIOS, and module-autoload boundaries. Risks include leaked device references on attach failures, display power imbalance, RIRB interrupt races, and no-codec debug bypass divergence. Test signals include codec mask filtering, generic codec fallback, HDMI/iDisp probe with and without i915 component, jack wake from suspend, RIRB response processing, and clean codec removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-common-ops.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-common-ops.c

Purpose: `hda-common-ops.c` defines `sof_hda_common_ops`, the shared `struct snd_sof_dsp_ops` baseline for Skylake and newer HDAudio-based SOF platforms. Generation-specific files clone this table and override only the operations that differ.

Important fields: the table wires early/proper/late probe and remove to `hda_dsp_*`, block and mailbox I/O to generic SOF helpers, mailbox/window offsets to HDA IPC helpers, machine selection to HDA machine helpers, debug dumping to `hda_dsp_dump`, PCM operations to HDA DSP stream callbacks, firmware loading to raw firmware loading, pre-run and run to the HDA code-loader path, manifest parsing to `hda_dsp_ext_man_get_cavs_config_data`, trace callbacks, IPC client registration, DAI drivers to `skl_dai`, chain-DMA detection, PM callbacks, hardware info flags, and Xtensa architecture ops.

Control flow and integration: platform ops init functions in `apl.c`, `cnl.c`, and later family files copy this structure, install protocol-specific IPC send/IRQ/dump/power callbacks, and set platform debug maps or chip-specific boot functions. The common table makes HDA platforms behave consistently for probe, PCM, PM, firmware loading, and machine registration.

State and persistence behavior: the object itself is constant and exported, but consumers copy it into mutable per-family global operation structures. That copy pattern means later mutation affects the platform global ops used by devices of that family.

Dependencies and risks: the table depends on many exports from HDA controller, DAI, DSP, IPC, loader, trace, machine, and PCM files. Risks are missing default callbacks, stale function pointers after API changes, and accidental sharing of mutable per-family ops. Test signals include booting at least one IPC3 and one IPC4 HDA platform, PCM playback/capture, runtime/system suspend, trace start/stop, DAI registration count, and no unresolved symbol or namespace warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-common-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ctrl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ctrl.c

Purpose: `hda-ctrl.c` contains generic HDA controller reset, capability discovery, PP capability control, clock/power gating, chip initialization, and chip stop logic for SOF HDA platforms.

Important APIs: exported functions include `hda_dsp_ctrl_link_reset()`, `hda_dsp_ctrl_get_caps()`, `hda_dsp_ctrl_ppcap_enable()`, `hda_dsp_ctrl_ppcap_int_enable()`, `hda_dsp_ctrl_clock_power_gating()`, and `hda_dsp_ctrl_init_chip()`. `hda_dsp_ctrl_stop_chip()` is a common stop helper used by suspend/remove paths.

Control flow: reset writes `SOF_HDA_GCTL_RESET` and polls for entry or exit. Capability discovery performs a reset cycle, then walks the HDA linked-list capability pointer, recording PP, SPIB, DRSM, GTS, and multi-link capability BARs into `bus` and `sdev->bar[]`. Chip init enables codec wake, disables miscellaneous clock gating, clears wake/interrupt/stream status, resets the HDA controller, accepts unsolicited responses, optionally detects codecs, initializes command I/O, enables controller/global interrupts, programs the position buffer, resets multi-link LOSIDV state, and marks `bus->chip_init`. Stop disables stream and controller interrupts, clears status, stops command I/O, disables position buffer, and clears `chip_init`.

State and persistence behavior: persistent runtime state includes capability remap pointers, `bus->chip_init`, codec mask, position-buffer registers, command I/O state, and PCI gating bits. `hda->l1_disabled` affects whether DMI L1 state is re-enabled by clock/power gating.

Dependencies and integration: this file depends on HDA register helpers, codec helper functions, multi-link helpers, PCI update wrappers, and SOF stream lists. It imports HDA multi-link and codec namespaces.

Risks and test signals: reset and capability discovery order is hardware sensitive. Risks include failing to clear stale interrupts, programming position buffers while invalid, or enabling L1 against prior policy. Test signals are successful capability BAR discovery, stable codec detection after reset, no interrupt storms during init/stop, correct runtime suspend/resume chip_init transitions, and multi-link SoundWire/HDA link enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai-ops.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai-ops.c

Purpose: `hda-dai-ops.c` defines the per-widget DMA operation tables selected by `hda-dai.c` for HDA, SSP, DMIC, SoundWire/ALH, IPC3, IPC4, chain DMA, and dspless paths. It is the low-level link-DMA policy layer.

Important APIs and structures: the exported API is `hda_select_dai_widget_ops()`. Internal helpers assign and release `hdac_ext_stream` objects, calculate stream formats, map HDA links, set codec streams, manage IPC4 pipeline trigger ordering, and implement dspless stream lookups. Operation tables include `hda_ipc4_dma_ops`, `ssp_ipc4_dma_ops`, `dmic_ipc4_dma_ops`, `sdw_ipc4_dma_ops`, `hda_ipc4_chain_dma_ops`, `sdw_ipc4_chain_dma_ops`, `hda_ipc3_dma_ops`, `hda_dspless_dma_ops`, and `sdw_dspless_dma_ops`.

Control flow: stream assignment scans the HDA bus stream list under `bus->reg_lock`, chooses a compatible unlocked link stream, handles PROCEN format quirks by matching FE stream tags when needed, reserves host DMA for hostless streams, decouples host/link DMA, and records `link_substream`. IPC4 pre-trigger pauses pipelines before stop/suspend/pause, the trigger starts or clears the HDAC ext stream, and post-trigger transitions pipelines to running or updates `started_count`. Format calculators adapt HDA codec significant bits, generic physical width, and DMIC S16-as-S32 packing.

State and persistence behavior: operation selection is cached in `sdai->platform_private`. Stream state persists in DAI DMA data, `hext_stream->link_locked`, `link_prepared`, `link_substream`, saved LLP registers, and pipeline state. Dspless mode bypasses firmware pipeline state and uses host stream state.

Dependencies, risks, and test signals: the file depends on ASoC DPCM, HDAC extended streams, HDA multi-link helpers, IPC4 pipeline state APIs, and SOF topology private data. Risks include stream leaks, wrong stream-tag mapping, invalid pipeline state transitions, and null topology widgets. Test HDA codec playback/capture, SSP and DMIC on ACE 2.0+, SoundWire aggregated channel mapping, pause/resume delay accounting, chain DMA, dspless mode, and xrun restart paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai.c

Purpose: `hda-dai.c` implements ASoC DAI callbacks and DAI driver registration for SOF HDA platforms. It bridges topology widgets, HDA link DMA streams, IPC DAI configuration, SoundWire channel mapping, and platform DAI driver ops.

Important APIs: exported functions include `hda_dai_config()`, `sdw_hda_dai_hw_params()`, `sdw_hda_dai_hw_free()`, `sdw_hda_dai_trigger()`, `hda_set_dai_drv_ops()`, `hda_ops_free()`, `hda_dsp_dais_suspend()`, and the exported `skl_dai[]` DAI array. Internal callbacks cover HDA link DMA hw_params, cleanup, trigger, hw_free, prepare, non-HDA DAI setup, and suspend cleanup.

Control flow: `hda_dai_get_ops()` locates the DAPM widget for the CPU DAI and stream, obtains SOF widget/DAI private data, selects widget DMA ops via `hda_select_dai_widget_ops()`, validates mandatory ops, and caches them. HW params assigns or reuses a link stream, maps playback stream IDs to HDA links, configures codec DAI stream pointers, resets and formats the stream, marks it prepared, then calls topology DAI config with the stream tag. IPC4 non-HDA setup additionally fills copier DMA config TLVs with HDA DMA method and stream IDs. SoundWire setup resets and programs PCMSyCM channel maps and propagates TLVs across aggregated DAIs.

State and persistence behavior: state persists in DAI DMA data, `sdai->platform_private`, `hext_stream->link_prepared`, `host_reserved`, `sof_ipc4_copier` DMA config TLVs, SoundWire channel maps, `ipc4_data->nhlt`, and `sdev->private`. `hda_ops_free()` releases NHLT and IPC4 private data.

Dependencies and integration: it depends on ASoC DAPM/DPCM, Intel NHLT parsing, HDA multi-link helpers, IPC3/IPC4 topology ops, and the operation tables from `hda-dai-ops.c`.

Risks and test signals: null widgets and mismatched machine/topology DAI links are explicitly guarded. Risks include unbalanced link DMA cleanup on pause/suspend, incorrect SoundWire channel masks for aggregated devices, and forgetting to free NHLT/private IPC4 data. Test signals include prepare/hw_params idempotence, suspend during pause, IPC3 HW_FREE/PAUSE DAI config messages, IPC4 copier TLVs, SoundWire restart after xrun, and DAI names/channels from `skl_dai[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dsp.c

Purpose: `hda-dsp.c` is the core HDA DSP control and power-management implementation for SOF HDA platforms. It covers interface capability masks, chain-DMA support policy, DSP core reset/power/run, IPC interrupt enablement, D0I3/D3 power transitions, system and runtime suspend/resume, SoundWire interrupt helpers, shutdown recovery, secondary-core get, and ROM/FW debug dumps.

Important APIs: exported functions include `hda_get_interface_mask()`, `hda_is_chain_dma_supported()`, `hda_dsp_core_stall_reset()`, `hda_dsp_core_is_enabled()`, `hda_dsp_core_run()`, `hda_dsp_core_power_up()`, `hda_dsp_enable_core()`, `hda_dsp_core_reset_power_down()`, IPC interrupt enable/disable, IPC3/IPC4 power-state setters, suspend/resume/runtime PM functions, shutdown helpers, D0I3 work, secondary core get, SoundWire helpers, `hda_dsp_disable_interrupts()`, `hda_dsp_get_state()`, ROM-status dump, and `hda_dsp_dump()`.

Control flow: core control manipulates ADSPCS SPA/CPA/CRST/CSTALL bits with polling and post-read verification. Power-state changes validate allowed transitions, update D0I3C after CIP clears, send PM_GATE IPC flags, and revert the register on IPC failure. Suspend disables interrupts, synchronizes IRQs, enables jack wake, suspends multi-links, powers down DSP cores, disables PP capability interrupts, stops the HDA chip, sets low-power retention, resets the controller, and releases i915 display power. Resume powers display first, reinitializes the controller, restores links or boots from D3, and sets D0/D0I0 state.

State and persistence behavior: state spans `sdev->dsp_power_state`, `enabled_cores_mask`, per-core refcounts, `system_suspend_target`, `fw_state`, delayed D0I3 work, mic privacy work, `hda->skip_imr_boot`, SoundWire context, codec command state, PCI saved state for S0ix, and hardware registers. ROM status decoding maps FSR module, state, wait state, and error code tables for diagnostics.

Dependencies and integration: it depends on HDA controller helpers, IPC PM ops, codec helpers, SoundWire helpers, tracepoints, MTL/HDA register definitions, and Xtensa dump support.

Risks and test signals: this is high-risk power sequencing code. Watch for illegal state transitions, CIP timeouts, incomplete interrupt disable before suspend, IMR boot after memory loss, active DMA at shutdown, SoundWire wake floods, and secondary-core IPC rollback. Test runtime suspend/resume, S3 and S0ix, D0I3 streaming, firmware crash recovery, shutdown DMA flush, SoundWire lcount validation, core power refcounts, and readable ROM/FW state dumps on boot failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.c

Purpose: `hda-ipc.c` implements the common cAVS 1.5 HDA IPC register protocol and generic IPC4 variant used by shared HDA platforms. It handles message sending, delayed D0I3 scheduling, IRQ-thread reply/notification processing, mailbox/window offsets, stream position reads, IPC IRQ detection, dumps, and IPC4 transmit-busy checks.

Important APIs: exported functions include `hda_dsp_ipc_send_msg()`, `hda_dsp_ipc4_schedule_d0i3_work()`, `hda_dsp_ipc4_send_msg()`, `hda_dsp_ipc_get_reply()`, `hda_dsp_ipc4_irq_thread()`, `hda_dsp_ipc_irq_thread()`, `hda_dsp_check_ipc_irq()`, mailbox/window offset helpers, `hda_ipc_msg_data()`, `hda_set_stream_data_offset()`, `hda_ipc4_dsp_dump()`, `hda_check_ipc_irq()`, `hda_ipc_irq_dump()`, `hda_ipc_dump()`, `hda_ipc4_dump()`, and `hda_ipc4_tx_is_busy()`.

Control flow: IPC3 send writes the mailbox and sets HIPCI BUSY. IPC4 send checks the chip-specific request register; if busy, it stores `hdev->delayed_ipc_tx_msg`, otherwise writes payload to mailbox if present, writes extension and primary registers, and schedules D0I3 work for non-PM IPC4 messages. IRQ threads read DONE/BUSY registers, mask relevant interrupts, process replies under `ipc_lock`, route notifications through `snd_sof_ipc_msgs_rx()`, handle panic magic with boot retry awareness, acknowledge DSP or host done, and resend delayed IPC4 messages after ACK.

State and persistence behavior: mutable state includes current `sdev->msg`, reply/rx data pointers, stream mailbox position offsets, `hda->code_loading`, wait queue wakeups for CLDMA, `hdev->delayed_ipc_tx_msg`, D0I3 delayed work, and chip-specific IPC register fields.

Dependencies and integration: it depends on SOF IPC core, HDA DSP register definitions, telemetry dump code, tracepoints, and the code-loader CLDMA wait path.

Risks and test signals: risks include reply-before-FW_READY races, delayed IPC pointer lifetime, panic recoverability during boot attempts, stream private-data closure races, and interrupt masking order. Test IPC3 and IPC4 command/reply, firmware notifications, panic IRQ handling, CLDMA wakeups, D0I3 work scheduling suppression for PM messages, stream position mailbox offsets, and debug dumps after stuck IPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.h

Purpose: `hda-ipc.h` defines common sideband IPC register bit encodings for Cannonlake-style cAVS 1.8+ IPC and older cAVS 1.5 mapping, plus function prototypes for CNL IPC implementations.

Important definitions: the primary register contains a reserved doorbell bit, compact-message bit, response direction bit, and message type field. `HDA_IPC_PM_GATE` encodes the compact PM_GATE message type. The secondary register payload bits define PM behavior flags such as disabling DMA trace, preventing clock or power gating, marking active streaming, and reserved bit zero.

Control flow and integration: this header is used by `cnl.c` to compress IPC3 PM_GATE messages into sideband IPC registers and to expose CNL IPC helpers to other platform files. The definitions also document register mapping differences: primary maps to DIPCTDR/HIPCIDR in sideband IPC and DIPCT in cAVS 1.5, while secondary maps to DIPCTDD/HIPCIDD or DIPCTE.

State and persistence behavior: no runtime state is stored, but bit definitions are hardware ABI. Wrong masks or shifts would corrupt power-management IPCs and could leave DSP power gating, clock gating, or trace DMA in the wrong state.

Dependencies, risks, and test signals: the header assumes Linux bit macros and SOF/HDA types are included by consumers. Risks center on compact IPC PM flags because the DSP interprets them without mailbox payload. Test signals include CNL IPC3 PM_GATE D0I0/D0I3 transitions, trace DMA disabling during S0ix, IPC dump showing expected primary/secondary values, and compile coverage for exported CNL IPC prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader-skl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader-skl.c

Purpose: `hda-loader-skl.c` implements the Skylake-specific code-loader DMA path. Unlike newer HDA code that reuses HDAC stream abstractions, this file manually programs the CLDMA stream, BDL, SPB FIFO, interrupts, and ROM status polling for firmware download.

Important APIs: the exported entry point is `hda_dsp_cl_boot_firmware_skl()`. Internal helpers allocate DMA buffers, build a single-fragment BDL, clear/setup/run the CLDMA stream, configure SPB FIFO, enable/disable CLDMA interrupts, initialize the DSP core and ROM, copy firmware chunks into the DMA buffer, wait for CLDMA completion via `hda->waitq`, and clean up.

Control flow: boot initializes the DSP with `cl_dsp_init_skl()`, retries once on failure, waits for ROM INIT_DONE, strips the firmware to payload offset, copies it in chunks no larger than 32 pages, triggers CLDMA for each chunk, waits for interrupts except the last transfer, then polls for `FSR_STATE_ROM_BASEFW_ENTERED`. On success it stops and clears CLDMA, frees buffers, and returns the init core mask. On failure it dumps PCI/mailbox state, powers down the init core, stops CLDMA, cleans up, and returns the error.

State and persistence behavior: runtime state includes two temporary DMA buffers, CLDMA stream registers, SPB FIFO registers, ADSPIC CL_DMA interrupt bit, `hda->code_loading`, and the shared wait queue. Firmware payload offset is taken from `sdev->basefw`.

Dependencies and integration: this file depends on HDA DSP core helpers, SOF firmware metadata, low-level register access, and `hda_dsp_check_ipc_irq()` clearing `hda->code_loading` for CLDMA interrupts.

Risks and test signals: the single-fragment physical-memory assumption is deliberate but fragile. Risks include timeout waiting for code-loading interrupts, wrong BDL alignment, stale CLDMA interrupt status, and improper cleanup after partial load. Test signals include SKL firmware boot, oversized-but-valid firmware chunking, CLDMA timeout diagnostics, ROM status progression, and no DMA buffer leaks after retry/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader-skl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader.c

Purpose: `hda-loader.c` is the generic HDA code-loader implementation for newer HDA SOF platforms. It prepares HDAC extended streams for firmware or IPC4 library loading, initializes DSP ROM boot, supports IMR restore, manages persistent code-loader DMA buffers, handles ICCMAX boot, and parses Intel cAVS extended manifest data.

Important APIs: exported functions include `hda_cl_prepare()`, `cl_dsp_init()`, `hda_cl_trigger()`, `hda_cl_cleanup()`, `hda_cl_copy_fw()`, `hda_dsp_cl_boot_firmware_iccmax()`, `hda_dsp_cl_boot_firmware()`, `hda_dsp_ipc4_load_library()`, and `hda_dsp_ext_man_get_cavs_config_data()`. The module parameter `persistent_cl_buffer` controls whether code-loader DMA memory is retained across boots and library loads.

Control flow: cold boot prepares a playback code-loader stream with the stripped firmware payload, optionally copies payload into a persistent DMA buffer, retries ROM initialization up to `HDA_FW_BOOT_ATTEMPTS`, processes SoundWire wake events after ROM init on resume, triggers DMA, waits for `FW_ENTERED`, cleans up the stream, and returns the init core mask. IMR restore skips DMA when supported and valid, falling back to cold boot on failure. `cl_dsp_init()` powers up host-managed cores, sets SSP clock consumer/provider mode, sends ROM_CONTROL with stream tag, runs the init core, waits for IPC DONE, powers down non-boot cores, enables IPC interrupts, and waits for the requested ROM status.

State and persistence behavior: state includes `hda->cl_dmab`, `hda->iccmax_dmab`, `cl_dmab_contains_basefw`, `boot_iteration`, `booted_from_imr`, `skip_imr_boot`, enabled core mask, per-core refcounts, SoundWire wake state, and parsed `clk_config_lpro`. Library loading may resize the persistent DMA buffer and marks it as no longer containing base firmware.

Dependencies and integration: it depends on HDAC stream helpers, HDA DSP core/power functions, IPC4 firmware library messages, extended manifest structures, SoundWire wake processing, and SOF firmware payload validation.

Risks and test signals: risks include IMR boot after memory loss, stale persistent DMA content, library reload skipping when restore state is wrong, cleanup errors masking primary boot failures, ROM_CONTROL stream-tag errors, and manifest size parsing. Test cold boot, IMR boot fallback, IPC4 two-stage and single-step library loading, persistent buffer resize, ICCMAX boot cleanup/guardband restore, SoundWire wake processing after resume, and LPRO manifest parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader.c -->
