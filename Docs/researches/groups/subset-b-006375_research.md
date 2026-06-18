# subset-b-006375 HDA Core and Controller Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/common/sysfs.c -->
# sources/distributed-fs/ceph-client/sound/hda/common/sysfs.c

## Purpose
`sysfs.c` implements HD-audio codec sysfs exposure for identification, pin configuration, power accounting, optional live reconfiguration, hints, init verbs, and optional patch-firmware parsing. It is the user/debug-facing bridge from `struct hda_codec` state to sysfs attributes and to the `snd_hda_load_patch()` firmware parser used by controller drivers such as `snd-hda-intel`.

## Important APIs, Types, and Functions
The local `struct hda_hint` stores key/value pairs in one allocation where `val` points inside the `key` allocation. Exported APIs are `snd_hda_get_hint()`, `snd_hda_get_bool_hint()`, `snd_hda_get_int_hint()`, `snd_hda_load_patch()` under patch-loader builds, `snd_hda_sysfs_init()`, `snd_hda_sysfs_clear()`, and the exported `snd_hda_dev_attr_groups[]`.

Read-only/common attributes expose `vendor_id`, `subsystem_id`, `revision_id`, `afg`, `mfg`, vendor/chip/model strings, initial/driver pin configs, and power on/off accounting. With `CONFIG_SND_HDA_RECONFIG`, writable paths add `init_verbs`, `hints`, `user_pin_configs`, `reconfig`, and `clear`.

## Control Flow
Codec initialization calls `snd_hda_sysfs_init()`, which initializes `codec->user_mutex` and optional arrays. Attribute show/store callbacks recover the codec via `dev_get_drvdata()`. Reconfiguration stores parse user input into arrays or scalar/string fields, then `reconfig` resets the codec, reprobes its device, and re-registers the card; `clear` resets and frees user sysfs state.

Patch loading scans a firmware buffer line by line, switches parser mode on section tags such as `[codec]`, `[pincfg]`, `[verb]`, `[hint]`, `[model]`, and ID tags, then applies lines to the currently selected codec.

## State and Persistence Behavior
Persistent in-memory state lives in the codec object: `init_verbs`, `hints`, `user_pins`, model/chip/vendor strings, pin config arrays, and power accounting counters. It is protected by `codec->user_mutex` for array reads/writes. Reconfiguration state is not persisted across driver unload except through firmware/module configuration that replays it. Hint values are owned as part of the key allocation, so replacement frees only `hint->key`.

## Dependencies and Integration Points
This file depends on ALSA HDA codec structures, `snd_array`, sysfs device attributes, the codec reset/reprobe path, card registration, and optional firmware patch loading. It integrates with generic parser and codec drivers through exported hint lookup helpers and with controller drivers through `snd_hda_load_patch()`.

## Risks
The reconfiguration interface can reset and reprobe live hardware; callers must handle busy codecs and failures from `snd_hda_codec_reset()` or `device_reprobe()`. Patch parsing silently ignores invalid codec selections and parser helper errors in some modes. The hint limit is 1024 entries, and malformed `key=value` input can return `-EINVAL`. Firmware parser line buffers are bounded at 128 bytes, so long values are truncated.

## Test Signals
Useful signals are correct sysfs attribute presence for both reconfig and non-reconfig builds, stable output formatting for pin and verb arrays, successful hint parsing/replacement, no leaks across `clear`/reconfig, patch firmware selecting the intended codec address, and card reprobe/register success after `reconfig`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/common/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/Kconfig

## Purpose
This Kconfig file declares the selectable HD-audio controller drivers: PCI `snd-hda-intel`, NVIDIA Tegra, CIX IPBLOQ, and generic ACPI-described HDA controllers.

## Important APIs, Types, and Functions
There are no runtime APIs. The important symbols are `SND_HDA_INTEL`, `SND_HDA_TEGRA`, `SND_HDA_CIX_IPBLOQ`, and `SND_HDA_ACPI`. They select shared core support (`SND_HDA`) and, where needed, aligned MMIO or Intel DSP configuration support.

## Control Flow
Kconfig controls which controller modules are built and therefore which platform/PCI match tables can bind at runtime. Intel depends on `SND_PCI`; Tegra depends on `ARCH_TEGRA`; CIX depends on `ARCH_CIX || COMPILE_TEST`; ACPI depends on `ACPI`.

## State and Persistence Behavior
The file contributes build-time state only. Selected symbols persist in the generated kernel configuration and affect module availability and dependency closure.

## Dependencies and Integration Points
The symbols integrate controller implementations with the shared `sound/hda/core` module and platform-specific subsystems. Intel additionally selects `SND_INTEL_DSP_CONFIG`, allowing the PCI probe path to defer to SOF/SST drivers when appropriate.

## Risks
Incorrect dependencies can build drivers on platforms missing required bus, clock, reset, or ACPI support, or omit shared HDA pieces needed by the controller. The controller symbols are user-visible module choices and affect module names documented in help text.

## Test Signals
Config tests should verify each symbol builds as `y` and `m`, dependency selections pull in `SND_HDA`, Tegra/CIX select aligned MMIO, Intel selects DSP config, and module names match `snd-hda-intel`, `snd-hda-tegra`, `snd-hda-cix-ipbloq`, and `snd-hda-acpi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/Makefile

## Purpose
This Makefile maps controller Kconfig symbols to loadable HD-audio controller objects and sets include paths needed by controller implementations.

## Important APIs, Types, and Functions
No runtime APIs are defined. Object groups are `snd-hda-intel-y`, `snd-hda-tegra-y`, `snd-hda-cix-ipbloq-y`, and `snd-hda-acpi-y`, each containing the matching single C file.

## Control Flow
`obj-$(CONFIG_...)` entries include the controller object in the build when the matching Kconfig symbol is enabled. `subdir-ccflags-y` adds `../common` headers, and `CFLAGS_intel.o := -I$(src)` lets Intel tracepoint generation include `intel_trace.h` via `TRACE_INCLUDE_PATH .`.

## State and Persistence Behavior
Build metadata only; no runtime state. It persists indirectly in generated build artifacts and module object names.

## Dependencies and Integration Points
The Makefile integrates controller sources with Kbuild, the common HDA controller helpers, and Linux tracepoint generation for the Intel driver.

## Risks
Changing object names or trace include flags can break module names or tracepoint header generation. Missing the common include path would break controller compilation against `hda_controller.h`.

## Test Signals
Build all four controller symbols as modules and built-ins, confirm generated module names, and verify `intel.o` compiles with `CREATE_TRACE_POINTS` and `intel_trace.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/acpi.c -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/acpi.c

## Purpose
`acpi.c` is a platform-driver wrapper for Azalia-compatible HD-audio controllers described by ACPI objects rather than PCI. It creates an ALSA card, maps controller registers from platform resources, initializes the shared `azx` controller core, probes codecs, configures them, and registers the card.

## Important APIs, Types, and Functions
`struct hda_acpi` embeds `struct azx` and stores the ALSA card, platform device, MMIO base, async probe work, and optional `struct hda_data`. `struct hda_data` supplies ACPI-match-specific card naming and `azx->driver_caps`.

Key functions are `hda_acpi_probe()`, `hda_acpi_create()`, `hda_acpi_probe_work()`, `hda_acpi_init()`, `hda_acpi_dev_free()`, `hda_acpi_remove()`, `hda_acpi_shutdown()`, and system sleep callbacks. The match table currently includes NVIDIA ACPI IDs with `AZX_DCAPS_CORBRP_SELF_CLEAR`.

## Control Flow
Probe allocates `hda_acpi`, gets match data or defaults, creates an ALSA card, initializes work, creates the `azx` bus/device, stores the card in drvdata, and schedules `probe_work`. The work item initializes IRQ/MMIO/streams/chip, probes up to 8 codecs, configures codecs, registers the card, and marks `chip->running`.

## State and Persistence Behavior
Runtime state is held by the device-managed `hda_acpi`, the ALSA card, `azx` bus fields, stream DMA pages, and `chip->running`. Work cancellation and `snd_card_free()` drive teardown. System suspend/resume delegates to runtime PM force helpers and updates ALSA power state.

## Dependencies and Integration Points
The driver depends on platform resources from ACPI `_CRS`, ALSA core card/device lifecycle, shared `hda_controller.h` helpers, `azx_interrupt`, stream allocation, codec probing/configuration, and platform PM.

## Risks
Probe is asynchronous; failures inside `probe_work` return without directly surfacing to platform probe after the card object was installed. Resource parsing must expose one IRQ and one MMIO range. The `hda->data` fallback allocates zeroed data, so defaults must remain valid. Device free must cancel pending work before freeing streams and bus state.

## Test Signals
Test ACPI matching, IRQ/MMIO acquisition, nonzero codec mask after chip init, card names from `hda_data`, codec configuration, card registration, shutdown stopping a running chip, and suspend/resume power-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/cix-ipbloq.c -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/cix-ipbloq.c

## Purpose
`cix-ipbloq.c` supports the CIX Sky1 IPBLOQ HD-audio controller as a platform device. It wraps the generic `azx` HDA engine with CIX-specific reset, clock, reserved-memory, aligned-MMIO, polling, DMA address-offset, and runtime-PM policy.

## Important APIs, Types, and Functions
`struct cix_ipbloq_hda` embeds `struct azx`, device/MMIO pointers, one reset, and two clocks (`ipg`, `per`). Main functions are `cix_ipbloq_hda_probe()`, `cix_ipbloq_hda_create()`, `cix_ipbloq_hda_init()`, `cix_ipbloq_hda_probe_codec()`, runtime/system PM callbacks, remove, and shutdown.

## Control Flow
Probe allocates driver state, acquires reset and clocks, sets a 32-bit DMA mask, optionally binds reserved memory, creates an ALSA card, initializes `azx`, enables runtime PM, resumes the device, initializes MMIO/IRQ/streams/chip, probes/configures codecs, registers the card, and releases the runtime PM reference. Runtime resume enables clocks, toggles reset, and reinitializes the chip if already running.

## State and Persistence Behavior
Persistent runtime state is the embedded `azx`, clock/reset handles, bus flags, stream pages, and card private data. The bus is forced into polling/non-interrupt command handling because `RIRBSTS.RINTFL` cannot be cleared. `bus.core.addr_offset` applies a host-to-HDAC DMA address adjustment for Sky1.

## Dependencies and Integration Points
The driver depends on OF matching (`cix,sky1-ipbloq-hda`), Linux reset/clock frameworks, reserved memory, platform IRQ/MMIO resources, ALSA card lifecycle, and shared `azx` helpers.

## Risks
Runtime suspend disables clocks after stopping/resetting the link; resume error paths after enabling clocks or asserting reset do not explicitly undo prior steps in the same callback. Polling mode is required to avoid interrupt storms, so interrupt assumptions from generic code must not leak in. The fixed negative address offset and 32-bit DMA mask are platform-specific correctness points.

## Test Signals
Validate OF binding, clock/reset acquisition, reserved-memory optional behavior, codec detection, polling-mode operation without interrupt storms, runtime suspend/resume clock/reset sequencing, playback/capture after resume, and non-empty ALSA card registration with model-derived shortname.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/cix-ipbloq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/intel.c -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/intel.c

## Purpose
`intel.c` is the primary PCI HD-audio controller driver for Intel HDA and many compatible PCI controllers from AMD/ATI, NVIDIA, VIA, Creative, C-Media, Zhaoxin, Loongson, Glenfly, VMware, and generic class-code devices. It binds PCI IDs to `azx` driver capability flags, initializes PCI/MMIO/DMA/IRQ/streams, probes codecs, integrates optional i915/DRM display power, handles runtime/system PM, and applies many platform workarounds.

## Important APIs, Types, and Functions
The private state is `struct hda_intel` from `intel.h`, embedding `struct azx` plus delayed probe, pending IRQ work, power-save list linkage, VGA switcheroo flags, runtime-PM flags, i915 power requirements, and retry state.

Critical functions include `azx_probe()`, `azx_create()`, `azx_probe_continue()`, `azx_first_init()`, `azx_free()`, `azx_remove()`, `azx_shutdown()`, `azx_init_pci()`, `hda_intel_init_chip()`, `azx_acquire_irq()`, `check_position_fix()`, `assign_position_fix()`, `check_probe_mask()`, `check_msi()`, `azx_check_snoop_available()`, `set_default_power_save()`, `azx_runtime_suspend/resume/idle()`, `azx_suspend/resume()`, and optional vga_switcheroo helpers.

## Control Flow
PCI probe first checks PCI/DMI denylists and whether another Intel DSP driver should own the device. It allocates an ALSA card, creates the `azx` bus, optionally initializes i915/audio-component integration, registers vga_switcheroo, and schedules delayed probe unless the bound GPU is off.

`azx_probe_continue()` enables display power, runs first hardware initialization, probes codecs, optionally loads patch firmware through `snd_hda_load_patch()`, configures codecs with retry support for flagged devices, registers the card, enables runtime PM/autosuspend, adds the card to the power-save list, and completes `probe_wait`.

## State and Persistence Behavior
Runtime state spans module parameters, the global `probed_devs` bitmap, global `card_list`, PCI drvdata, `azx` stream/bus fields, i915 display-power refcounts, work items, and codec/cache state. Power-save parameter writes iterate active cards and update codec power-save timeouts. Runtime suspend stops streams/chip, enables WAKEEN bits, and display power is requested during resume/reset. `probe_retry` can keep requeueing delayed work up to 60 times.

## Dependencies and Integration Points
The driver depends on PCI, ALSA core, HDA core/controller helpers, `snd-intel-dsp-config`, runtime PM, DMI quirks, optional firmware loader, optional input beep, optional i915 component APIs, vga_switcheroo, Apple gmux, tracepoints in `intel_trace.h`, and a very large PCI ID table.

## Risks
The driver has high quirk density: wrong caps can break MSI, snoop/cacheability, DMA addressing, position reporting, stream tags, i915 binding, or codec probing. Asynchronous probe and vga_switcheroo require careful completion and teardown handling. Position IRQ workarounds depend on wall clock, LPIB/POSBUF/FIFO behavior, and `bdl_pos_adj`. Runtime PM can break HDMI ELD notifications or click/pop on denied platforms. The PCI ID table is broad, so generic matches must stay below more specific entries.

## Test Signals
Test representative Intel PCH/SKL/HDMI, AMD, NVIDIA, VIA, Loongson, and generic devices; MSI fallback via `disable_msi_reset_irq()`, codec probe masks, DSP-driver handoff, patch loading, i915 binding/display power, vga_switcheroo off/on transitions, suspend/resume/runtime PM, DMA pointer modes, delayed IRQ work, and power-save denylist behavior. Tracepoints should emit suspend/resume/runtime events with the expected card index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/intel.h -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/intel.h

## Purpose
`intel.h` defines the Intel PCI HDA driver's private wrapper structure around the shared `struct azx` controller.

## Important APIs, Types, and Functions
`struct hda_intel` embeds `struct azx chip` and adds work/completion/list members plus bitfield flags for pending IRQ warnings, probe continuation, runtime PM disablement, vga_switcheroo state, delayed init failure, resource-free status, i915 clock/power needs, and probe retry count.

## Control Flow
The header has no executable control flow. Its fields are consumed by `intel.c`: delayed probe uses `probe_work`/`probe_wait`, IRQ timing workaround uses `irq_pending_work`, power-save parameter updates use `list`, vga_switcheroo checks use the switcheroo flags, and teardown checks `freed`/`init_failed`.

## State and Persistence Behavior
The structure is allocated device-managed during PCI probe and lives as long as the ALSA card/PCI device binding. Its embedded `azx` is the object passed to most shared controller helpers.

## Dependencies and Integration Points
It depends on `hda_controller.h` for `struct azx`. The struct layout is the contract between the Intel controller implementation and the shared HDA core.

## Risks
Flag semantics are tightly coupled to asynchronous probe, PM, and teardown ordering. Misusing `container_of()` or failing to update completion/list state can deadlock switcheroo or leak power-save list entries.

## Test Signals
Build coverage with `intel.c`, delayed probe completion under success/failure, repeated remove during pending probe, power-save parameter iteration after card removal, and vga_switcheroo transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/intel_trace.h -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/intel_trace.h

## Purpose
`intel_trace.h` declares tracepoints for Intel HDA controller system and runtime power-management transitions.

## Important APIs, Types, and Functions
It defines trace system `hda_intel`, event class `hda_pm`, and events `azx_suspend`, `azx_resume`, `azx_runtime_suspend`, and `azx_runtime_resume`. Each event records `chip->dev_index`.

## Control Flow
`intel.c` defines `CREATE_TRACE_POINTS` before including this header, generating tracepoint definitions. PM callbacks call the trace events after suspend/resume actions.

## State and Persistence Behavior
No persistent driver state is created. Trace records are transient ftrace/perf data keyed by card index.

## Dependencies and Integration Points
It depends on Linux tracepoint infrastructure and `struct azx`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE intel_trace` must match the controller Makefile include path.

## Risks
Tracepoint ABI names are observable by tooling; renaming events can break scripts. Include guard and `define_trace.h` placement must remain in the standard tracepoint pattern.

## Test Signals
Compile with tracing enabled, verify generated trace events under `/sys/kernel/tracing/events/hda_intel/`, and confirm events fire during system and runtime suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/intel_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/tegra.c -->
# sources/distributed-fs/ceph-client/sound/hda/controllers/tegra.c

## Purpose
`tegra.c` implements the NVIDIA Tegra platform HD-audio controller driver. It adapts the shared `azx` controller core to Tegra IPFS/FPCI register programming, SoC-specific reset/clock topology, aligned MMIO, runtime PM, and Tegra-specific stream/capability workarounds.

## Important APIs, Types, and Functions
`struct hda_tegra_soc` describes per-SoC capabilities: reset lines, HDMI/codec clocks, input-stream presence, always-on power, and whether special IPFS init is required. `struct hda_tegra` embeds `azx`, device pointer, reset/clock arrays, MMIO pointer, probe work, and SoC data.

Main functions are `hda_tegra_probe()`, `hda_tegra_create()`, `hda_tegra_probe_work()`, `hda_tegra_first_init()`, `hda_tegra_init_chip()`, `hda_tegra_init()`, PM callbacks, remove, and shutdown.

## Control Flow
Probe allocates state, selects OF match data, creates an ALSA card, gathers reset and clock handles based on SoC flags, creates the `azx` bus, enables runtime PM, and schedules work. Probe work takes a runtime PM active guard, maps resources, initializes IPFS/FPCI if required, requests IRQ, derives stream counts, allocates stream pages, initializes the chip, probes/configures codecs, registers the card, marks it running, and sets power-save timeout.

## State and Persistence Behavior
State lives in the device-managed `hda_tegra`, ALSA card, `azx` bus/streams, reset/clock handles, and SoC descriptor. Runtime suspend stops the chip/link and disables clocks; runtime resume enables clocks, conditionally toggles resets before initial run, reinitializes the chip after resume, and clears WAKEEN bits.

## Dependencies and Integration Points
The driver depends on OF platform matching for Tegra30/194/234/264, reset and clock frameworks, platform IRQ/MMIO resources, ALSA core, HDA core/controller helpers, and runtime PM.

## Risks
SoC flags drive reset/clock counts; wrong match data can request nonexistent resources or skip required init. Tegra194 needs GCAP SDO override, Tegra234 fakes capture stream count to preserve descriptor offsets, and Tegra30 limits SDO striping. Runtime resume must preserve reset sequencing around first initialization versus normal resume.

## Test Signals
Validate each compatible string, resource acquisition, stream count derivation, Tegra194 SDO override, Tegra234 output descriptor offset workaround, Tegra30 striping limit, jack polling policy for non-always-on SoCs, runtime/system PM, and audio recovery after suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/controllers/tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/core/Kconfig

## Purpose
This Kconfig file declares shared HD-audio core symbols and Intel audio support helpers used by controller and codec drivers.

## Important APIs, Types, and Functions
Important symbols include `SND_HDA_CORE`, `SND_HDA_DSP_LOADER`, `SND_HDA_ALIGNED_MMIO`, `SND_HDA_COMPONENT`, `SND_HDA_I915`, `SND_HDA_EXT_CORE`, `SND_INTEL_NHLT`, `SND_INTEL_DSP_CONFIG`, `SND_INTEL_SOUNDWIRE_ACPI`, and `SND_INTEL_BYT_PREFER_SOF`.

## Control Flow
Selections define build inclusion: `SND_HDA_CORE` selects `REGMAP`; `SND_HDA_I915` selects component support; `SND_HDA_EXT_CORE` selects the base core; Intel DSP config selects ACPI NHLT, Intel NHLT, and SoundWire ACPI helpers when ACPI is enabled.

## State and Persistence Behavior
The file provides build-time configuration state. The selected symbols determine whether runtime code for regmap, i915 sync, extended HDA, DSP detection, and SoundWire ACPI is present.

## Dependencies and Integration Points
It integrates controller Kconfigs with shared HDA modules, DRM component sync, Intel DSP/SOF/SST selection, ACPI NHLT parsing, and SoundWire discovery.

## Risks
Incorrect symbol selection can produce link errors or missing runtime handoff. The Bay/Cherry Trail SOF preference option affects driver selection when both old SST and SOF are available.

## Test Signals
Run randconfig/allmodconfig builds around HDA, i915, extended core, ACPI, SoundWire, and Baytrail SOF/SST combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/core/Makefile

## Purpose
This Makefile assembles the shared `snd-hda-core` module, optional component/i915 helpers, the extended HDA submodule, and Intel DSP/SoundWire ACPI helper modules.

## Important APIs, Types, and Functions
Object lists define module composition: `snd-hda-core-y` includes bus, device, sysfs, regmap, controller, stream, array, HDMI channel-map, and trace support. Conditional objects add `component.o` and `i915.o`. Separate modules are `snd-intel-dspcfg` and `snd-intel-sdw-acpi`.

## Control Flow
Kbuild includes objects according to `CONFIG_SND_HDA_CORE`, `CONFIG_SND_HDA_COMPONENT`, `CONFIG_SND_HDA_I915`, `CONFIG_SND_HDA_EXT_CORE`, `CONFIG_SND_INTEL_DSP_CONFIG`, `CONFIG_SND_INTEL_NHLT`, and `CONFIG_SND_INTEL_SOUNDWIRE_ACPI`.

## State and Persistence Behavior
Build-only state. Runtime module boundaries affect symbol export availability and module load order.

## Dependencies and Integration Points
The file integrates base HDA code, tracepoint generation (`CFLAGS_trace.o := -I$(src)`), extended core under `ext/`, Intel DSP config, and SoundWire ACPI helper modules.

## Risks
Changing object composition can omit exported helpers used by controllers/codecs. Trace include paths must remain valid for generated trace definitions.

## Test Signals
Build with optional component/i915/ext/DSP/SoundWire combinations and verify exported symbols resolve for controller modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/array.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/array.c

## Purpose
`array.c` provides the tiny growable-array helper used throughout HDA code for dynamic lists such as init verbs, hints, pin configs, controls, and parser-generated structures.

## Important APIs, Types, and Functions
Exports are `snd_array_new()` and `snd_array_free()`. They operate on `struct snd_array`, whose fields include element size, used count, allocated count, allocation alignment, and raw list pointer.

## Control Flow
`snd_array_new()` validates `elem_size`, grows the backing allocation by `alloc_align` when full, zeroes the newly allocated tail, increments `used`, and returns the new element. It refuses growth beyond roughly 4096 elements. `snd_array_free()` frees the backing list and resets counters.

## State and Persistence Behavior
Array state is entirely caller-owned. The helper does not lock; callers must serialize access where needed, such as `codec->user_mutex` in sysfs reconfiguration.

## Dependencies and Integration Points
It depends on kernel slab allocation and ALSA bug macros. The exported functions are used by HDA sysfs, parser, codec, and control-building code.

## Risks
No element destructors are called, so callers must free nested allocations before `snd_array_free()`. Pointer arithmetic on `void *` relies on kernel C extensions. Callers must initialize `elem_size` and `alloc_align` correctly.

## Test Signals
Exercise initial allocation, growth, zero-initialized new slots, failure handling, free/reset behavior, and callers with nested allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/bus.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/bus.c

## Purpose
`bus.c` implements generic HD-audio core bus setup, verb execution dispatch, unsolicited event queuing, codec list membership, optional aligned MMIO helpers, and codec-link power delegation.

## Important APIs, Types, and Functions
Exports include `snd_hdac_bus_init()`, `snd_hdac_bus_exit()`, `snd_hdac_bus_exec_verb()`, `snd_hdac_bus_exec_verb_unlocked()`, `snd_hdac_bus_queue_event()`, `snd_hdac_bus_add_device()`, `snd_hdac_bus_remove_device()`, optional `snd_hdac_aligned_read/write()`, and `snd_hdac_codec_link_up/down()`.

## Control Flow
Bus init zeroes the bus, assigns ops or defaults, initializes lists/work/locks/waitqueues, sets default DMA type, IRQ `-1`, and SDO striping limit. Verb execution serializes on `cmd_mutex`, sends commands, handles `-EAGAIN` by draining pending responses, and fetches responses when requested. Unsolicited events are queued from interrupt context and processed by `unsol_work`, which dispatches to the bound HDA driver’s `unsol_event`.

## State and Persistence Behavior
State includes codec/stream/hlink lists, address table, codec power bits, command locks, unsol ring pointers, and bus ops. Codec add/remove updates list membership, address table, power bits, and codec count; removal flushes pending unsolicited work.

## Dependencies and Integration Points
The file depends on `struct hdac_bus`, `hdac_device`, `hdac_driver`, default controller command ops, Linux workqueues/locks, and tracepoints. Controllers call bus init/exit; codecs join through device initialization.

## Risks
Unsolicited event queue is fixed-size and overwrites by ring pointer progression if producers outrun work processing. Driver callbacks run outside the spinlock but require the codec still be registered. Link-power ops may be overridden by extended bus implementations.

## Test Signals
Test bus initialization invariants, verb serialization and `-EAGAIN` recovery, unsolicited event dispatch to the correct codec/driver, codec address collision rejection, removal flushing, and aligned MMIO helpers on aligned-MMIO platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/component.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/component.c

## Purpose
`component.c` provides the HDA-to-DRM audio component bridge used mainly for HDMI/DP audio. It lets HDA controller/codec code acquire display power, override codec wake, synchronize audio rate, query ELD/audio-enabled state, and register audio component callbacks.

## Important APIs, Types, and Functions
Exports are `snd_hdac_set_codec_wakeup()`, `snd_hdac_display_power()`, `snd_hdac_sync_audio_rate()`, `snd_hdac_acomp_get_eld()`, `snd_hdac_acomp_register_notifier()`, `snd_hdac_acomp_init()`, and `snd_hdac_acomp_exit()`. Internal component master ops are `hdac_component_master_bind()` and `_unbind()`.

## Control Flow
`snd_hdac_acomp_init()` allocates a devres `drm_audio_component`, stores audio ops, initializes a completion, adds a typed component match, and registers a component master. Master bind binds all components, validates DRM ops/device, pins the DRM module, calls optional audio `master_bind`, and completes waiters. Display power uses `bus->display_power_status` as a bitset and calls DRM `get_power`/`put_power` when transitioning between zero and nonzero.

## State and Persistence Behavior
State is stored in `bus->audio_component`, `display_power_status`, and `display_power_active`. The display-power cookie returned by DRM is retained until the last HDA user releases power. Devres owns the component allocation.

## Dependencies and Integration Points
It depends on Linux component framework, DRM audio component ops, module refcounting, HDA bus/device structs, and optional codec `audio_ops->pin2port` mapping.

## Risks
Power refcount transitions must stay balanced; exit warns and forcibly puts active power. Module pinning can fail. Port/pipe mapping differs by graphics driver and codec. Dynamic unbinding is intentionally prevented by module pinning, so lifetime assumptions are strict.

## Test Signals
Validate bind/unbind, module refcount behavior, display power get/put pairing across multiple codec/controller users, codec wake override calls during reset, ELD retrieval for mapped pins, and cleanup with active power.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/component.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/controller.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/controller.c

## Purpose
`controller.c` implements shared low-level HD-audio controller operations: CORB/RIRB command transport, PIO immediate command fallback, RIRB response parsing, capability discovery, link reset, interrupt control, chip start/stop, stream IRQ dispatch, DMA page allocation, and basic codec-link power bookkeeping.

## Important APIs, Types, and Functions
Exports include `snd_hdac_bus_init_cmd_io()`, `snd_hdac_bus_stop_cmd_io()`, `snd_hdac_bus_update_rirb()`, `snd_hdac_bus_send_cmd()`, `snd_hdac_bus_get_response()`, `snd_hdac_bus_parse_capabilities()`, `snd_hdac_bus_enter_link_reset()`, `snd_hdac_bus_exit_link_reset()`, `snd_hdac_bus_reset_link()`, `snd_hdac_bus_init_chip()`, `snd_hdac_bus_stop_chip()`, `snd_hdac_bus_handle_stream_irq()`, `snd_hdac_bus_alloc_stream_pages()`, `snd_hdac_bus_free_stream_pages()`, and `snd_hdac_bus_link_power()`.

## Control Flow
Chip init resets the link, clears interrupts, initializes command I/O, enables interrupts, programs position buffer DMA, and marks `chip_init`. Command I/O sets up CORB/RIRB in one DMA page. RIRB update consumes hardware write pointer entries, routes unsolicited events, wakes response waiters, and logs spurious responses. Link reset toggles `GCTL.RESET` with spec delays and reads `STATESTS` into `codec_mask`.

## State and Persistence Behavior
The bus owns CORB/RIRB buffers, response counters, last commands, position buffers, stream BDL pages, capability pointers, codec mask, and `chip_init`. DMA pages remain allocated until controller teardown. Command DMA state is also manipulated by the extended core.

## Dependencies and Integration Points
Controllers call these helpers during probe, PM resume, suspend, shutdown, and IRQ handling. The code depends on HDA register definitions, DMA allocation, spinlocks, waitqueues, and stream objects from `stream.c`.

## Risks
Hardware timing is delicate: CORBRP reset, RIRB waits, link reset delays, and interrupt clearing differ by controller. Polling and PIO command modes must stay coherent with bus flags. Stream IRQ ack callbacks must not run for stopped or unbound streams.

## Test Signals
Test CORB/RIRB command/response success and timeout paths, PIO mode, unsolicited events, codec discovery, capability parsing, chip init/stop idempotence, stream IRQ handling, DMA allocation/free, and PM cycles that reinitialize command buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/device.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/device.c

## Purpose
`device.c` implements the HD-audio codec core device model, including device initialization/registration, codec identity discovery, widget range/sysfs refresh, verb helpers, runtime PM wrappers, vendor naming, stream-format conversion, supported PCM querying, and power-state synchronization.

## Important APIs, Types, and Functions
Exports include `snd_hdac_device_init/exit/register/unregister()`, `snd_hdac_device_set_chip_name()`, `snd_hdac_codec_modalias()`, `snd_hdac_exec_verb()`, `snd_hdac_read()`, `_snd_hdac_read_parm()`, `snd_hdac_read_parm_uncached()`, `snd_hdac_override_parm()`, `snd_hdac_get_sub_nodes()`, `snd_hdac_refresh_widgets()`, `snd_hdac_get_connections()`, PM helpers, `snd_hdac_stream_format_bits()`, `snd_hdac_stream_format()`, `snd_hdac_spdif_stream_format()`, `snd_hdac_query_supported_pcm()`, `snd_hdac_is_supported_format()`, codec read/write wrappers, and power-state checks.

## Control Flow
Device init initializes the Linux device, links it to `snd_hda_bus_type`, adds it to the bus, reads vendor/subsystem/revision IDs, discovers AFG/MFG nodes, refreshes widgets, reads power caps and subsystem ID fallback, derives vendor/chip names, and leaves runtime PM active with a held reference. Registration adds the device and initializes widget sysfs under `widget_lock`.

## State and Persistence Behavior
State includes codec identity fields, AFG/MFG IDs, node ranges, widget sysfs state, vendor/chip strings, power caps, runtime PM counters, `in_pm`, and bus membership. Exit balances runtime PM, marks suspended, removes from bus, and frees names. Regmap may cache parameter and verb state.

## Dependencies and Integration Points
It depends on Linux device core, runtime PM, HDA regmap, widget sysfs, PCM params, and the HDA bus type. Codec drivers build on these helpers for probing, module aliases, verbs, format checks, and PM.

## Risks
Initialization performs hardware reads before full driver binding; failures must drop the device reference correctly. Connection-list parsing handles malformed codec data but can return zero on repeated nulls. PCM query code must match HDA format bits to ALSA formats and subformats correctly. PM helper misuse can deadlock recursive PM paths.

## Test Signals
Test codec registration/unregistration, modalias generation, widget sysfs refresh, vendor-name fallback, verb encoding bounds checks, connection-list short/long/range parsing, supported PCM/rate/format queries, PM reference balance, and power-state wait behavior on codecs that report errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/core/ext/Makefile

## Purpose
This Makefile builds the extended HDA core module used by ASoC/SOF-style HDA integrations that need bus, controller, and stream extensions.

## Important APIs, Types, and Functions
No runtime APIs are defined. The object group `snd-hda-ext-core-y` consists of `bus.o`, `controller.o`, and `stream.o`.

## Control Flow
`obj-$(CONFIG_SND_HDA_EXT_CORE)` includes `snd-hda-ext-core.o` when extended HDA core support is selected.

## State and Persistence Behavior
Build-only state. Runtime state is in the compiled extended core objects.

## Dependencies and Integration Points
It depends on `CONFIG_SND_HDA_EXT_CORE`, which selects the base HDA core in Kconfig. It integrates the ext subdirectory with Kbuild.

## Risks
Omitting any object breaks exported extended bus/link/stream symbols expected by ASoC HDA drivers.

## Test Signals
Build `SND_HDA_EXT_CORE` as module and built-in, and verify ext symbols resolve for consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/bus.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/ext/bus.c

## Purpose
`ext/bus.c` initializes and tears down an extended HD-audio bus and registers HDA drivers for ASoC-style extended devices (`HDA_DEV_ASOC`).

## Important APIs, Types, and Functions
Exports are `snd_hdac_ext_bus_init()`, `snd_hdac_ext_bus_exit()`, `snd_hdac_ext_bus_device_remove()`, `snd_hda_ext_driver_register()`, and `snd_hda_ext_driver_unregister()`. Internal wrappers adapt `struct device_driver` callbacks to `struct hdac_driver` probe/remove/shutdown methods.

## Control Flow
Extended bus init calls base `snd_hdac_bus_init()`, stores ext ops, assigns bus index 0, and marks command DMA active. Exit calls base exit and warns if hlink objects remain. Device removal iterates codec devices, unregisters them, and drops references. Driver register sets type to `HDA_DEV_ASOC`, uses `snd_hda_bus_type`, installs callback wrappers, and registers with the driver core.

## State and Persistence Behavior
State lives in the base `hdac_bus` plus `ext_ops`, `idx`, `cmd_dma_state`, and `hlink_list`. Driver registration mutates the supplied `hdac_driver` object before registering it.

## Dependencies and Integration Points
It depends on base HDA bus code, Linux driver core, and `sound/hdaudio_ext.h`. Consumers are extended HDA/ASoC codec drivers and controller integrations.

## Risks
The bus index is fixed at 0, with a FIXME for multi-bus systems. Exit only warns about leaked links; consumers must free them. Driver wrappers assume callbacks are valid when installed.

## Test Signals
Test ext bus init/exit, ASOC driver match/probe/remove/shutdown, device removal over multiple codecs, and no hlink leaks before exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/controller.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/ext/controller.c

## Purpose
`ext/controller.c` implements extended HD-audio controller helpers for processing-pipe capability, multilink discovery, link power/refcount control, stream ID routing to links, and codec-link power integration.

## Important APIs, Types, and Functions
Exports include `snd_hdac_ext_bus_ppcap_enable()`, `snd_hdac_ext_bus_ppcap_int_enable()`, `snd_hdac_ext_bus_get_ml_capabilities()`, `snd_hdac_ext_link_free_all()`, hlink lookup helpers by id/address/name, link power up/down/all, stream-id set/clear, `snd_hdac_ext_bus_link_get()`, `snd_hdac_ext_bus_link_put()`, and `snd_hdac_ext_bus_link_power()`.

## Control Flow
ML capability parsing reads link count, allocates `hdac_ext_link` objects, records link registers/capabilities/address masks, optional alternate-link IDs, initial refcount, and appends them to `hlink_list`. Link get increments refcount; a 0-to-1 transition starts command DMA if needed, powers the link, clears output stream routing, waits for codec status, and updates `codec_mask`. Link put powers down on 1-to-0 and stops command DMA when all links are off.

## State and Persistence Behavior
Persistent state is the hlink list, each link’s refcount, register base, capabilities, stream masks, and bus command-DMA state. `codec_powered` remains the generic power bitset and is synchronized with extended link up/down.

## Dependencies and Integration Points
The file depends on HDA extended register definitions, base command I/O helpers, `bus->mlcap` from capability parsing, and codec device names of the form `ehdaudio%dD%d`.

## Risks
Reference counting must not underflow; link get/put assume balanced codec/stream users. Command DMA is stopped when no links are up, so late commands require link reacquisition. Name parsing limits address to 0..31 and assumes stable device naming. ML capability pointer must be valid before use.

## Test Signals
Test ML capability parsing, hlink lookup modes, link power CPA polling, command-DMA start/stop across multiple links, stream ID routing registers, codec power transitions, and balanced refcounts under concurrent users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/stream.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/ext/stream.c

## Purpose
`ext/stream.c` implements extended HDA stream handling for decoupled host/link DMA paths, processing-pipe registers, stream assignment/release for PCM and compressed streams, and Apollo Lake-specific setup sequencing.

## Important APIs, Types, and Functions
Exports include `snd_hdac_ext_host_stream_setup()`, `snd_hdac_ext_stream_init_all()`, `snd_hdac_ext_stream_free_all()`, `snd_hdac_ext_stream_decouple_locked()`, `snd_hdac_ext_stream_decouple()`, `snd_hdac_ext_stream_start()`, `snd_hdac_ext_stream_clear()`, `snd_hdac_ext_stream_reset()`, `snd_hdac_ext_stream_setup()`, `snd_hdac_ext_stream_assign()`, `snd_hdac_ext_stream_release()`, and `snd_hdac_ext_cstream_assign()`.

## Control Flow
Stream init allocates `hdac_ext_stream` objects, assigns host setup callbacks, computes processing-pipe host/link register addresses when `ppcap` exists, and calls base stream init. Assignment supports coupled streams via base assignment, host streams by finding unopened streams and decoupling them, and link streams by finding unlocked link streams and decoupling them. Release recouples only when the paired host/link side is no longer in use.

## State and Persistence Behavior
Each ext stream tracks base `hstream`, processing-pipe addresses, decoupled state, host setup callback, link lock flag, and associated PCM/compress substream pointers. State is protected by `bus->reg_lock` for assignment/decoupling/release.

## Dependencies and Integration Points
The code depends on base HDA stream helpers, PCI IDs for Apollo Lake setup selection, processing-pipe capability registers, ALSA PCM/compress stream structures, and extended bus capability parsing.

## Risks
Processing-pipe operations require `bus->ppcap`; assignment returns NULL if unsupported. Decoupling/recoupling must respect simultaneous host and link users. Reset/setup functions poll hardware bits with bounded loops but do not report reset timeout errors. Apollo Lake setup relies on temporary coupling state.

## Test Signals
Test stream initialization/free, coupled/host/link assignment exhaustion, release recoupling rules, compressed stream assignment, start/clear/reset/setup register programming, APL host setup, and lock coverage under concurrent PCM open/close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/ext/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/hda_bus_type.c -->
# sources/distributed-fs/ceph-client/sound/hda/core/hda_bus_type.c

## Purpose
`hda_bus_type.c` registers the Linux `hdaudio` bus type and implements device/driver matching plus modalias uevents for HD-audio codec devices.

## Important APIs, Types, and Functions
Exports are `hdac_get_device_id()` and `snd_hda_bus_type`. Internal functions are `hdac_codec_match()`, `hda_bus_match()`, and `hda_uevent()`.

## Control Flow
At subsystem init, `hda_bus_init()` registers `snd_hda_bus_type`; module exit unregisters it. Match first checks device type against driver type, then calls a driver-specific match function if present, otherwise scans the driver ID table for matching vendor ID and optional revision ID. Uevent generation emits `MODALIAS=hdaudio:v...r...a...`.

## State and Persistence Behavior
Global state is the registered bus type. Per-device matching relies on `hdac_device` fields populated by `device.c`, especially vendor ID, revision ID, and type.

## Dependencies and Integration Points
The file depends on Linux driver core, module device tables, and `snd_hdac_codec_modalias()`. Codec drivers register against this bus, while userspace/module autoloading consumes the modalias.

## Risks
Matching is strict on type and vendor ID; missing revision wildcards or wrong device type prevents binding. The final unreachable `return 1` after the match branches is harmless but dead code.

## Test Signals
Test bus registration, modalias contents, driver ID table matching with and without revision IDs, custom match callbacks, type mismatch rejection, and module autoload for HDA codec aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/hda_bus_type.c -->
