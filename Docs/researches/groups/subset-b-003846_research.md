# subset-b-003846 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/core.c

Purpose: implements the Intel Trace Hub core bus. It registers the `intel_th` bus, allocates controller instances from PCI/ACPI resources, creates synthetic Trace Hub subdevices, exposes output character devices, and brokers trace activation between output drivers and the GTH switch.

Important APIs/types/functions: `intel_th_driver_register()`/`intel_th_driver_unregister()` wrap Linux driver registration for `struct intel_th_driver`. `intel_th_alloc()` builds an `struct intel_th`, char-device major, IRQ handler, runtime-PM setup, and subdevices. `intel_th_free()` tears that tree down. `intel_th_output_enable()` lets the GTH instantiate output devices discovered from hardware port types. `intel_th_trace_enable()`, `intel_th_trace_switch()`, `intel_th_trace_disable()`, and `intel_th_set_output()` are the cross-driver control API used by MSU/PTI/STH.

Control flow: module init creates debugfs support then registers the bus. Parent controller drivers call `intel_th_alloc()`, which normalizes resources, requests IRQs, and calls `intel_th_populate()`. Population creates GTH and source devices immediately, but defers most output devices until the GTH driver probes and asks for matching output types. Output device sysfs `active` toggles call `intel_th_output_activate()`/`intel_th_output_deactivate()`, which hold module and runtime-PM references, optionally run parent controller activation hooks, prepare the GTH port, then call the output driver's `activate()` or generic GTH enable path.

State and persistence: all state is in kernel memory: IDA controller IDs, `th->thdev[]`, subdevice resource copies, output assignment state, active flags, runtime-PM state, char-device references, and optional host-mode flag. No on-disk persistence exists. Host mode suppresses local output enumeration/configuration.

Dependencies and integration: depends on the Linux device model, bus/driver core, char-device registration, PM runtime, DMA masks, debugfs, IRQ APIs, and Intel TH register/resource definitions from `intel_th.h`. It integrates with parent PCI/ACPI drivers, GTH switch callbacks, output file operations from MSU/PTI-like drivers, and source devices such as STH.

Risks: probe/remove ordering is delicate because outputs are children of the switch and may be dynamically created by GTH probe. Output activation must balance module refs, runtime-PM refs, controller hooks, and trace disable paths. IRQ dispatch assumes output devices with bound drivers; regressions can produce NULL-driver races. Resource rebasing and `.end == 0` whole-BAR semantics are easy to break for new subdevices.

Test signals: boot/probe with representative Intel TH PCI IDs, verify `intel_th` bus devices and `/dev/intel_thN/msc*` nodes, toggle output `active`, exercise MSU reads and STH source routing, unload drivers under open output fds, and test host-mode and no-GTH-driver defer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.c

Purpose: optional Intel TH debugfs bootstrap. It creates and removes the top-level `intel_th` debugfs directory used by debug-capable Intel TH code.

Important APIs/types/functions: exports global `struct dentry *intel_th_dbg`. `intel_th_debug_init()` calls `debugfs_create_dir("intel_th", NULL)` and normalizes error pointers to NULL. `intel_th_debug_done()` removes the directory and clears the global.

Control flow: `core.c` calls init before bus registration and done during module exit. There are no per-device operations here.

State and persistence: only a transient debugfs dentry pointer. debugfs is non-persistent and may be absent depending on kernel config and mount state.

Dependencies and integration: compiled when `CONFIG_INTEL_TH_DEBUG` is enabled via `debug.h`; depends on debugfs and the Intel TH core lifecycle.

Risks: limited. Consumers must tolerate `intel_th_dbg == NULL`. The directory is shared global state, so later debugfs entries must not outlive core teardown.

Test signals: with `CONFIG_INTEL_TH_DEBUG=y/m`, check `/sys/kernel/debug/intel_th` appears after module load and disappears after unload; with debugfs unavailable, verify init does not fail the Intel TH bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.h

Purpose: compile-time abstraction for Intel TH debugfs support.

Important APIs/types/functions: declares `intel_th_dbg`, `intel_th_debug_init()`, and `intel_th_debug_done()` when `CONFIG_INTEL_TH_DEBUG` is set; otherwise provides no-op inline versions of the init/done functions.

Control flow: lets core code call debug init/teardown unconditionally without `#ifdef` blocks in the caller.

State and persistence: no state unless debug support is compiled, in which case `debug.c` owns the global dentry.

Dependencies and integration: included by `core.c` and `debug.c`; relies on Kconfig to decide whether the debug implementation exists.

Risks: consumers must not reference `intel_th_dbg` unless the config path declares it. Adding debugfs child creation outside the same config guard would fail to build.

Test signals: build both with and without `CONFIG_INTEL_TH_DEBUG`; ensure callers link and the no-op path produces no unresolved symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.c

Purpose: implements the Intel TH Global Trace Hub switch driver. It discovers GTH output ports, assigns output devices to ports, configures per-master routing, starts/stops trace capture, and exposes sysfs controls for masters and output-port parameters.

Important APIs/types/functions: `struct gth_device` owns MMIO base, output descriptors, master routing array, dynamic sysfs groups, and `gth_lock`. `struct gth_output` tracks one physical port, its type, bound output descriptor, and masters assigned to it. Core callbacks are `intel_th_gth_probe()`, `assign()`, `unassign()`, `set_output()`, `prepare()`, `enable()`, `trig_switch()`, and `disable()`. Register helpers include `gth_output_set/get()`, `gth_smcfreq_set/get()`, and `gth_master_set()`.

Control flow: probe maps GTH/TSCU/CTS registers. If host mode or debugger scratchpad says the device is externally controlled, it avoids reset and sysfs export. Otherwise it resets GTH, reads each physical port type, asks the Intel TH core to instantiate matching output drivers, then creates `outputs/` and `masters/` sysfs groups. Trace enable programs all assigned masters to the output port, marks the output active, optionally resyncs TSCU, updates scratchpad bits, and asserts store-enable. Disable clears master routing, waits for GTH and output pipeline-empty, clears scratchpad, and stops capture. `trig_switch()` drives CTS to switch MSC multiblock windows.

State and persistence: all state is in memory plus volatile hardware registers: `master[]`, output master bitmaps, bound output pointers, active flags, scratchpad bits, output port config, SWDEST routing, SCR/SCR2 force-store controls, and CTS/TSCU registers.

Dependencies and integration: depends on Intel TH core bus callbacks and register definitions from `gth.h`/`intel_th.h`. It integrates with output drivers through `struct intel_th_output`, with STH through `intel_th_set_output()`, and with sysfs for manual routing.

Risks: GTH reset refuses to run if a debugger is active; callers must honor host mode. Spinlocked sysfs writes can reprogram active routing live. Timeout loops for pipeline empty and CTS trigger only debug-log on timeout, so hardware faults may silently degrade data. `set_output()` has a fixed default port 0 and notes this is not configurable.

Test signals: probe on hardware with multiple port types, inspect `outputs/*_port` and `masters/*`, route a source master to MSC/PTI, toggle output active, exercise MSU multiblock switch, and validate host/debugger-in-use path hides capture configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.h

Purpose: register and bitfield definitions for the Intel TH GTH switch, TSCU, and CTS trigger sequencer.

Important APIs/types/functions: defines `enum intel_th_output_parm` symbolic output controls, GTH register offsets (`GTHOPT`, `SWDEST`, `SCR`, `SCR2`, `STAT`, scratchpads), TSCU control/status bits, CTS event/action/status/control offsets, and wait-loop depths.

Control flow: no executable flow; `gth.c` uses these constants to reset ports, route masters, control store-enable, wait for pipeline-empty, resync timestamping, and trigger MSC window switches.

State and persistence: describes volatile MMIO state only.

Dependencies and integration: included by `gth.c`; relies on common Linux bit macros and Intel TH offset macros from `intel_th.h`.

Risks: incorrect offsets or masks directly misprogram hardware. The CTS/TSCU area is included in the GTH resource by `core.c`, so offset changes must stay aligned with subdevice resource windows.

Test signals: compile coverage plus hardware smoke tests for sysfs output parameters, GTH reset, TSCU resync, and CTS switch triggering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/intel_th.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/intel_th.h

Purpose: central private Intel TH header defining bus device/driver types, controller state, capability quirks, output descriptors, resource offsets, scratchpad bits, and core APIs.

Important APIs/types/functions: `struct intel_th_device` represents SOURCE, OUTPUT, or SWITCH subdevices. `struct intel_th_output` is the switch/output handshake object. `struct intel_th_driver` defines probe/remove plus switch, output, file, IRQ, and source callbacks. `struct intel_th` holds parent controller state including subdevices, resources, IRQs, char major, hub pointer, and controller activation hooks. Inline helpers include `intel_th_device_get_resource()`, `intel_th_output_assigned()`, `to_intel_th_parent()`, `to_intel_th()`, and `to_intel_th_hub()`.

Control flow: no standalone execution; it shapes all Intel TH driver interactions. Parent drivers allocate `struct intel_th`; child drivers register `struct intel_th_driver`; output and source drivers use the exported trace and routing helpers.

State and persistence: defines in-memory topology and volatile hardware resource layout. Quirk bits (`tscu_enable`, `multi_is_broken`, `has_mintctl`, `host_mode_only`) persist only as static driver data selected by PCI/ACPI IDs.

Dependencies and integration: depends on Linux device, resource, IRQ, and file-operation types. It integrates the core, GTH, MSU, PTI/LPP, STH, PCI, and optional ACPI frontend.

Risks: because this header encodes object ownership and callback contracts, changes can break several modules at once. Parent/child conversions are type-sensitive; misuse of `to_intel_th()` on output devices depends on correct parent linkage.

Test signals: all Intel TH modules should build; probe/remove and output activation should be tested for every callback combination; static analysis should check resource array bounds and callback NULL handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/intel_th.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu-sink.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu-sink.c

Purpose: example pluggable MSU software sink buffer. It registers an `msu_buffer` named `sink` that allocates multiblock windows and immediately unlocks windows when notified ready, effectively discarding/looping trace data.

Important APIs/types/functions: `struct msu_sink_private` tracks device and a bounded table of SG tables. `msu_sink_assign()` forces `MSC_MODE_MULTI`. `msu_sink_alloc_window()` allocates coherent page-sized SG entries. `msu_sink_free_window()` frees them. `msu_sink_ready()` calls `intel_th_msc_window_unlock()`. `module_intel_th_msu_buffer(sink_mbuf)` registers with the MSU buffer registry.

Control flow: when users write `sink` to an MSC `mode` sysfs file, MSU calls assign, then allocates windows through the sink. During capture, when a window fills, MSU calls `ready()` and this sink returns the window to rotation without external processing.

State and persistence: per-assignment memory tracks up to `MAX_SGTS` SG tables. No persistent state or user-visible storage.

Dependencies and integration: depends on public `<linux/intel_th.h>` MSU buffer hooks, DMA coherent allocation, scatterlists, and the MSU driver's window-unlock export.

Risks: allocation error paths in `msu_sink_alloc_window()` do not free already allocated blocks on mid-loop failure, so this is best treated as example/test code. It assumes multiblock mode and bounded window count.

Test signals: load module, switch MSC mode to `sink`, allocate windows, enable tracing long enough to cycle windows, confirm no stop-on-full if IRQ/window unlock callbacks run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu-sink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu.c

Purpose: Intel TH Memory Storage Unit output driver. It manages MSC capture buffers, single and multiblock modes, output character-device read/mmap, sysfs configuration, interrupt-driven window rotation, and a registry for external MSU buffer providers.

Important APIs/types/functions: `struct msc` is per-output state; `struct msc_window` describes multiblock windows; `struct msc_iter` tracks reader iteration; `struct msu_buffer_entry` backs the sink registry. Public exports are `intel_th_msu_buffer_register()`, `intel_th_msu_buffer_unregister()`, and `intel_th_msc_window_unlock()`. Core operations include `msc_configure()`, `msc_disable()`, buffer allocation/free helpers, `msc_buffer_iterate()`, `intel_th_msc_activate()/deactivate()`, IRQ handler `intel_th_msc_interrupt()`, and sysfs stores for `mode`, `nr_pages`, `wrap`, `win_switch`, and `stop_on_full`.

Control flow: probe maps MSU/MSC registers, initializes default mode (`multi` unless quirked), lists, mutexes, and user count. Users select mode and allocate pages through sysfs. Opening the char device installs a read iterator only when capture is not enabled. Activating output configures BAR/size/mode/wrap/burst, initializes interrupts, asks GTH to route/enable tracing, and calls external buffer activation. Disable stops GTH, captures write pointer/wrap state for single mode, disables MSC, notifies buffer readiness, restores original BAR/size, and clears status. In multiblock IRQ mode, filled windows transition INUSE to LOCKED, the next READY window is programmed through a GTH switch trigger, and external buffers later unlock windows.

State and persistence: `user_count` is a tri-state lifetime guard: -1 no buffer, 0 allocated idle, positive active readers/mappings/capture/locked windows. `buf_mutex` serializes buffer configuration. Multiblock windows have lockout state READY/INUSE/LOCKED, SG tables, hardware descriptors, and page offsets. Single mode tracks wrap and size after disable. State is volatile; trace data lives only in allocated DMA pages or external buffers.

Dependencies and integration: depends on Intel TH output callbacks, GTH trace controls, DMA/scatterlist APIs, x86 cache attribute APIs when available, char-device read/mmap, sysfs, workqueues, IRQ dispatch from core, and the public Intel TH MSU buffer interface.

Risks: concurrency is high-risk: readers, mmap users, capture activation, IRQ window switches, external buffers, and sysfs reconfiguration all coordinate through atomics, mutexes, and spinlocks. Wrong lockout transitions can stop capture or leak `user_count`. DMA/cache attribute handling is architecture-sensitive. `do_irq` setup appears inverted around missing IRQ resource and should be verified against resource numbering. Timeouts and no-interrupt hardware can reduce sink-buffer support. Removal notes a FIXME for open output character devices during parent detach.

Test signals: single-mode allocate/read/mmap with and without wrap, multiblock allocate multiple window sizes, IRQ-driven capture with external `sink`, stop-on-full behavior, manual `win_switch`, capability checks for CAP_SYS_RAWIO, reconfiguration while busy returning `-EBUSY`, unload under open fd, and hardware with `multi_is_broken` quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu.h

Purpose: MSU/MSC register offsets, bit definitions, multiblock descriptor layout, and descriptor helper routines.

Important APIs/types/functions: defines MSU global and MSC0/MSC1 offsets, status/control bits (`MSC_EN`, `MSC_WRAPEN`, `MSC_MODE`, `MSC_LEN`, `MSCSTS_PLE`, interrupt bits), `struct msc_block_desc`, descriptor size constants, software/hardware tag bits, and helpers `msc_data_sz()`, `msc_total_sz()`, `msc_block_sz()`, `msc_block_wrapped()`, and `msc_block_last_written()`.

Control flow: no standalone execution. `msu.c` uses the constants to program capture and interpret hardware-written descriptors while iterating captured data.

State and persistence: describes volatile register state and in-memory/DMA block descriptor fields populated by hardware.

Dependencies and integration: included by `msu.c`; relies on Linux bit macros and page constants.

Risks: descriptor size math affects user-visible read offsets. Off-by-one or mask changes can corrupt multiblock iteration, window sizing, and wrap detection.

Test signals: compile coverage, multiblock capture validation against expected block descriptor tags, wrap/last-block handling, and pipeline-empty wait path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/msu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci.c

Purpose: PCI frontend for Intel Trace Hub controllers. It matches Intel NPK PCI IDs, enables the PCI device, maps BAR resources, allocates IRQ vectors, selects hardware quirks, and delegates subdevice creation to `intel_th_alloc()`.

Important APIs/types/functions: `intel_th_pci_probe()` and `intel_th_pci_remove()` are the `pci_driver` callbacks. `intel_th_pci_activate()`/`deactivate()` manipulate PCI config register `NPKDSC_TSACT` for TSCU-capable devices. Static `intel_th_drvdata` instances describe `multi_is_broken` and 2.x capabilities. `intel_th_pci_id_table[]` maps many Intel device IDs to quirk data.

Control flow: probe enables and claims PCI regions, maps config and STH software BARs, optionally records the RTIT BAR, allocates up to eight IRQ vectors, builds an Intel TH resource array, calls `intel_th_alloc()`, installs parent activate/deactivate hooks, and sets bus mastering. Remove frees the Intel TH core tree and IRQ vectors.

State and persistence: stores `struct intel_th` as PCI drvdata. Quirk selection is static from device ID. No persistent storage.

Dependencies and integration: depends on PCI managed resource APIs, MSI/MSI-X/INTx vector allocation, Intel TH core allocation, and `pci_ids.h`.

Risks: resource array order must match `enum th_mmio_idx`; wrong BAR assumptions break subdevice windows. IRQ vector allocation failure is tolerated only if negative path is considered; vector resource numbering must stay aligned with MSU expectations. Activate and deactivate both set `NPKDSC_TSACT`, which should be verified against hardware semantics.

Test signals: probe on IDs with and without RTIT BARs, no-IRQ systems, TSCU-capable and 1.x quirk devices, runtime trace activation, remove/unload, and `lspci`/sysfs device topology checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci_ids.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci_ids.h

Purpose: local Intel NPK/Trace Hub PCI device ID definitions used by `pci.c`.

Important APIs/types/functions: defines `PCI_DEVICE_ID_INTEL_NPK_*` constants for multiple Intel generations and PCH/CPU variants, from older Broxton/Apollo/Kaby families through newer Meteor/Nova/Panther Lake IDs.

Control flow: no runtime logic. The constants feed `PCI_DEVICE_DATA(INTEL, NPK_..., drvdata)` entries in the PCI ID table.

State and persistence: none.

Dependencies and integration: included only by the Intel TH PCI driver. Names must match the `PCI_DEVICE_DATA` macro's expected `PCI_DEVICE_ID_INTEL_*` expansion.

Risks: stale or incorrect IDs prevent driver binding or apply wrong quirks. The file comment says Intel TH debugging despite containing PCI IDs, which can mislead maintainers.

Test signals: build the PCI ID table, verify module aliases with `modinfo`, and confirm probe on hardware for newly added IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.c

Purpose: Intel TH PTI and LPP output drivers. They program the PTI control register, expose sysfs tuning for port width/free-running clock/clock divider, and optionally choose LPP destination.

Important APIs/types/functions: `struct pti_device` tracks MMIO base, bound TH device, mode, clock settings, pattern generator, and LPP destination state. `pti_width_mode()` maps human-visible widths to register mode codes. `intel_th_pti_activate()` programs `REG_PTI_CTL` then enables GTH tracing. `intel_th_pti_deactivate()` disables GTH tracing and clears the register. Separate `intel_th_driver` objects register names `pti` and `lpp`.

Control flow: probe maps one MMIO resource, allocates state, reads initial hardware config, normalizes default mode/divider, and stores drvdata. Sysfs writes update in-memory state. Activation composes `PTI_CTL` from state and GTH output type, then asks the core/GTH to enable routing.

State and persistence: volatile `pti_device` settings persist while the driver is bound; hardware register state is read at probe and rewritten on activation. No persistent storage.

Dependencies and integration: depends on Intel TH output-driver callbacks, GTH routing through `intel_th_trace_enable/disable()`, and register definitions from `pti.h`.

Risks: `clock_divider_store()` stores the numeric divisor rather than log2 code while show prints `1u << clkdiv`; this should be checked against intended ABI. PTI/LPP share probe/activate code but differ in sysfs attributes and destination bits. No locking protects sysfs updates against activation.

Test signals: register both `pti` and `lpp`, read defaults from hardware, set legal/illegal widths and clock dividers, choose LPP destination only when present, activate/deactivate output, and inspect `REG_PTI_CTL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.h

Purpose: PTI/LPP register offset and bit definitions.

Important APIs/types/functions: defines `REG_PTI_CTL` plus PTI enable, free-running clock, mode, clock divider, pattern-generator, LPP-present, destination, active, and busy bits. Also defines LPP destination enum bits for PTI and EXI.

Control flow: no executable logic; `pti.c` composes and decodes `REG_PTI_CTL` with these masks.

State and persistence: describes volatile PTI/LPP register state.

Dependencies and integration: included by `pti.c`.

Risks: header guard is named `__INTEL_TH_STH_H__`, duplicating `sth.h`'s guard name. If both headers are included in one translation unit in the wrong order, PTI definitions can be skipped or STH definitions hidden. Current files avoid that collision, but it is a maintainability risk.

Test signals: compile translation units including PTI and STH headers together to expose guard collision, and hardware tests for mode/destination bit programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.c

Purpose: Intel TH Software Trace Hub source driver. It registers Intel TH STH hardware as a generic STM device and implements packet writes into STH MMIO channels.

Important APIs/types/functions: `struct sth_device` holds control MMIO, channel MMIO, physical channel base, device pointer, embedded `struct stm_data`, and master count. `sth_stm_packet()` translates generic STP packet requests into Intel TH STH register writes. `sth_stm_mmio_addr()` supplies mmap-able channel MMIO. `sth_stm_link()` routes an STP master through GTH with `intel_th_set_output()`. `intel_th_sw_init()` reads STH capabilities.

Control flow: probe maps STH control and channel resources, initializes `stm_data` callbacks and metadata, reads master/channel ranges, then calls `stm_register_device()`. Generic STM writers later call `sth_stm_packet()` for DATA/FLAG/USER/MERR/global packets. Remove unregisters the STM device.

State and persistence: STH state is volatile: MMIO mappings, STM device registration, hardware capability ranges, and GTH master routing created during link callbacks.

Dependencies and integration: bridges Intel TH source devices to the generic STM subsystem in `drivers/hwtracing/stm`. Depends on `linux/stm.h`, STH register/channel layout from `sth.h`, and Intel TH GTH routing.

Risks: packet size is rounded down to a power of two; unsupported or zero sizes can drop writes. 32-bit builds clamp writes above 4 bytes. `sth_stm_mmio_addr()` requires page-aligned channel ranges. Routing relies on GTH driver presence and policy-driven STM links.

Test signals: register STH as `/sys/class/stm`, create STM configfs policy, write through STM char device and STM sources, mmap channel range, validate generated STP packets, and test master ranges from hardware capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.h

Purpose: Intel TH STH register offsets and channel MMIO structure.

Important APIs/types/functions: defines STH capability/global packet register offsets and `struct intel_th_channel`, whose fields represent data, marked data, timestamped data, user, flag, and master-error write locations.

Control flow: no runtime logic. `sth.c` indexes this channel array by master/channel and writes appropriate fields for STP packets.

State and persistence: describes hardware MMIO layout; no persistent state.

Dependencies and integration: included by `sth.c`.

Risks: header guard collides with `pti.h` (`__INTEL_TH_STH_H__`), so combined inclusion can suppress one header. Channel struct packing and field sizes must match hardware exactly.

Test signals: build with independent include ordering, packet-write tests for each field, and mmap address validation against `sizeof(struct intel_th_channel)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Kconfig

Purpose: Kconfig entry for the HiSilicon PCIe Tune and Trace driver.

Important APIs/types/functions: defines `CONFIG_HISI_PTT` as a tristate named "HiSilicon PCIe Tune and Trace Device". It depends on ARM64 or 64-bit compile-test, plus PCI, DMA, I/O memory, and perf events.

Control flow: selecting the option allows `Makefile` to build `hisi_ptt.o`. The help text describes an RCiEP device that tunes PCIe traffic and traces TLP headers to memory.

State and persistence: Kconfig selection persists in kernel build config only; no runtime state.

Dependencies and integration: integrates with kernel build system and the perf/PCI/DMA prerequisites used by `hisi_ptt.c`.

Risks: missing dependency constraints would cause build failures on unsupported architectures. Overly narrow constraints can hide compile-test coverage.

Test signals: build `=y`, `=m`, and `=n` on ARM64 and COMPILE_TEST 64-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Makefile

Purpose: build rule for the HiSilicon PTT hwtracing driver.

Important APIs/types/functions: `obj-$(CONFIG_HISI_PTT) += hisi_ptt.o`.

Control flow: kbuild compiles and links `hisi_ptt.c` when the Kconfig symbol is enabled.

State and persistence: no runtime state.

Dependencies and integration: relies on `Kconfig` symbol and normal kbuild object naming.

Risks: minimal; object name must match source file.

Test signals: kernel build with `CONFIG_HISI_PTT=m/y` produces `hisi_ptt.o` or module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.c

Purpose: HiSilicon PCIe Tune and Trace driver. It exposes tuning controls through sysfs, registers a perf AUX PMU for tracing PCIe TLP headers, manages DMA trace buffers and interrupts, and dynamically publishes filters for root ports/requesters under the managed PCIe core.

Important APIs/types/functions: tune attributes use `hisi_ptt_tune_attr_show/store()`. Trace lifecycle uses `hisi_ptt_trace_start()`, `hisi_ptt_trace_end()`, `hisi_ptt_update_aux()`, and `hisi_ptt_isr()`. Filter lifecycle uses `hisi_ptt_alloc_add_filter()`, sysfs create/remove helpers, PCI bus notifier `hisi_ptt_notifier_call()`, delayed work `hisi_ptt_update_filters()`, and initial bus walk `hisi_ptt_init_filters()`. Perf hooks include `event_init`, `setup_aux`, `free_aux`, `start`, `stop`, `add`, `del`, and CPU hotplug migration.

Control flow: probe rejects non-identity IOMMU mappings, enables PCI BAR 2, sets 64-bit coherent DMA, registers MSI, allocates four coherent 4 MiB hardware trace buffers, reads supported BDF range, walks the PCI bus to seed filters, registers a PCI hotplug notifier, registers a node-local perf PMU named from SICL/core IDs, and creates sysfs filter attributes. Perf start validates config fields, begins AUX output, configures filter/direction/type/format, resets DMA, zeroes buffers, unmasks interrupts, and enables trace. Interrupts copy a full hardware buffer into perf AUX and rotate to the next buffer. Stop disables trace, waits idle, copies residual bytes from write-status, and updates perf state.

State and persistence: volatile `struct hisi_ptt` stores trace control, current CPU, DMA buffer descriptors, filter lists, port mask, notifier/work items, locks, FIFO, and PMU object. Sysfs attributes reflect current in-memory filter/tune state. Trace data persists only in perf AUX buffers supplied by userspace.

Dependencies and integration: depends on PCI, DMA coherent allocation, perf AUX infrastructure, cpuhotplug, MSI interrupts, IOMMU identity mapping, sysfs attribute groups, PCI bus notifier, kfifo, workqueues, and bitfield helpers.

Risks: direct DMA requirement means systems with translated IOMMU domains cannot trace. `hisi_ptt_pmu_add()` returns 0 for CPUs outside the device node without starting, which users must interpret carefully. Interrupt/AUX buffer updates assume enough AUX space and stop trace on failure. Filter list updates can overflow the small FIFO under heavy hotplug. Tune registers are serialized by `tune_lock`; perf trace by `pmu_lock`; filter/sysfs by `filter_lock`, so lock ordering should remain simple. IRQ affinity and CPU hotplug migration are correctness-sensitive.

Test signals: probe on supported Huawei device, reject non-identity IOMMU, inspect PMU format/cpumask/filter/tune groups, run `perf record -e hisi_ptt*/.../` with legal and illegal filters, force AUX buffer exhaustion, handle PCI hotplug add/remove, CPU offline during active trace, and tune read/write timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.h

Purpose: private declarations, register definitions, perf config masks, constants, and state structures for the HiSilicon PTT driver.

Important APIs/types/functions: defines `DRV_NAME`, all tuning/trace/status/location register offsets and masks, DMA buffer counts/sizes/timeouts, perf config bit masks, filter group names, and the core structures `hisi_ptt_tune_desc`, `hisi_ptt_dma_buffer`, `hisi_ptt_trace_ctrl`, `hisi_ptt_filter_desc`, `hisi_ptt_filter_update_info`, `hisi_ptt_pmu_buf`, and `struct hisi_ptt`.

Control flow: no standalone execution. `hisi_ptt.c` uses these definitions to program hardware, validate perf configs, publish sysfs filters, allocate AUX mappings, and manage hotplug updates.

State and persistence: describes runtime state stored in `struct hisi_ptt`, including filter lists, delayed work, PMU, locks, DMA buffers, BDF range, and trace session fields. No on-disk persistence.

Dependencies and integration: includes PCI, perf, kfifo, mutex/spinlock, notifier, workqueue, cpumask, and device headers. `to_hisi_ptt()` converts a `struct pmu` back to device state.

Risks: register masks and bitfield widths define ABI-visible perf config parsing. The `direction`, `filter`, `format`, and `type` bitfields in `hisi_ptt_trace_ctrl` must hold validated values exactly. DMA buffer size/count constants drive both hardware programming and AUX-space requirements.

Test signals: compile-time checks through `hisi_ptt.c`, perf format sysfs content, trace start with boundary config values, and hardware register programming inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Kconfig

Purpose: Kconfig menu for the generic System Trace Module framework, framing protocols, dummy test device, and kernel trace sources.

Important APIs/types/functions: `CONFIG_STM` selects `CONFIGFS_FS`. Suboptions include `STM_PROTO_BASIC`, `STM_PROTO_SYS_T`, `STM_DUMMY`, `STM_SOURCE_CONSOLE`, `STM_SOURCE_HEARTBEAT`, and `STM_SOURCE_FTRACE` with `TRACING` dependency for ftrace.

Control flow: enabled symbols control which objects the STM Makefile builds and which modules are available for policy/protocol/source testing.

State and persistence: build configuration only.

Dependencies and integration: integrates STM with configfs, Linux tracing, console, and module selection.

Risks: defaulting protocol drivers to `STM` changes module availability and autoload expectations. Missing `CONFIGFS_FS` would break policy creation, hence selected by core.

Test signals: config/build matrix for each protocol/source, especially `STM_SOURCE_FTRACE` with and without `TRACING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Makefile

Purpose: kbuild rules for STM core, protocols, dummy driver, and source modules.

Important APIs/types/functions: builds `stm_core` from `core.o policy.o`; maps protocol objects to `stm_p_basic.o` and `stm_p_sys-t.o`; maps optional drivers to `dummy_stm.o`, `stm_console.o`, `stm_heartbeat.o`, and `stm_ftrace.o`.

Control flow: kbuild uses enabled Kconfig symbols to decide which composite objects/modules to build.

State and persistence: no runtime state.

Dependencies and integration: must stay aligned with Kconfig symbol names and source filenames.

Risks: object renames or missing composite rules break module names used by autoload, especially `request_module_nowait("stm_p_basic")` in core.

Test signals: build each symbol as module and built-in; verify resulting module names match runtime request strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/console.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/console.c

Purpose: STM source module that forwards kernel console messages to a linked STM device.

Important APIs/types/functions: static `stm_console` embeds `stm_source_data` and `struct console`. `stm_console_write()` calls `stm_source_write()`. Link/unlink callbacks register and unregister the console. Module init/exit register/unregister the STM source device.

Control flow: when users link the `console` STM source to an STM device through sysfs, the source link callback registers a console named `stm_console` with `CON_PRINTBUFFER`; console writes then flow to STM channel 0. Unlink removes the console.

State and persistence: one static source/console object; console registration exists only while linked.

Dependencies and integration: depends on generic STM source APIs and Linux console subsystem. Requires an STM policy and source link before output works.

Risks: registering with `CON_PRINTBUFFER` can emit backlog on link. Console context constraints mean `stm_source_write()` must remain low-overhead and safe for console write paths.

Test signals: register module, link source to STM, confirm kernel messages appear in trace, unlink and verify console removed, test relink without duplicate console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/core.c

Purpose: generic System Trace Module class infrastructure. It registers STM devices and STM source devices, manages character device writes/mmap/ioctls, allocates STP master/channel ranges from configfs policies, brokers framing protocol drivers, and provides source-to-device links.

Important APIs/types/functions: exported APIs include `stm_register_device()`, `stm_unregister_device()`, `stm_source_register_device()`, `stm_source_unregister_device()`, `stm_source_write()`, `stm_register_protocol()`, `stm_unregister_protocol()`, `stm_lookup_protocol()`, `stm_put_protocol()`, and `stm_data_write()`. Key structures are `struct stm_device`, `struct stm_source_device`, `struct stm_output`, `struct stm_file`, `struct stp_master`, and `struct stm_protocol_driver`.

Control flow: module init registers `stm` and `stm_source` classes, initializes configfs policy support, SRCU, and protocol list, then requests the basic protocol module when configured. Hardware drivers call `stm_register_device()` with `stm_data`; source modules call `stm_source_register_device()`. Users create configfs policies binding a device and protocol, then either open the STM char device or link a source. Writes auto-assign a policy by task name/default if needed, copy user data, runtime-resume the STM device, and call the active protocol's `write()` callback. Source writes use SRCU to safely dereference the linked STM device and protocol path.

State and persistence: state is volatile kernel memory plus configfs directory state created by users. STM devices maintain policy pointer, selected protocol, master/channel bitmaps, linked source list, char major, and runtime-PM autosuspend state. Source devices maintain an RCU-protected link pointer and one `stm_output`.

Dependencies and integration: depends on configfs policy helpers in `policy.c`, Linux char-device and mmap infrastructure, PM runtime, SRCU, `uapi/linux/stm.h` ioctls, and hardware-provided `stm_data` callbacks. Intel TH STH and Coresight STM are typical hardware providers; console/ftrace/heartbeat are source providers.

Risks: lock ordering across `policy_mutex`, configfs subsystem mutex, `mc_lock`, output locks, `link_mutex`, `link_lock`, and source `link_lock` is important. Master/channel allocation requires power-of-two widths via bitmap regions. Source unlink uses SRCU and retry on link changes; mistakes can produce use-after-free. Char-device mmap requires exact assigned width and hardware page-aligned MMIO. `stm_core_exit()` calls SRCU cleanup before class unregister/configfs exit, which should be checked for active users.

Test signals: register dummy and hardware STM devices, create/remove configfs policies with both protocols, char write/ioctl/mmap flows, source link/unlink races, module unload with active sources, master/channel exhaustion, runtime-PM autosuspend, and ftrace/console high-frequency writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/dummy_stm.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/dummy_stm.c

Purpose: test STM device provider that discards packets and optionally fails links, useful for STM class/configfs/source testing without hardware.

Important APIs/types/functions: `dummy_stm_packet()` returns the packet size, optionally trace-printing under local DEBUG. Module parameters control `nr_dummies`, `fail_mode`, `master_min`, `master_max`, and `nr_channels`. `dummy_stm_link()` can reject channels based on `fail_mode`.

Control flow: init validates parameters, allocates names `dummy_stm.N`, fills `stm_data`, and registers each with `stm_register_device()`. Exit unregisters and frees names.

State and persistence: static array of up to 32 `stm_data` objects and allocated names. No trace data persistence.

Dependencies and integration: depends on generic STM core APIs and UAPI master/channel limits.

Risks: intended for testing; parameter combinations can create very large channel spaces. Failure injection is channel-bit based and should not be confused with hardware behavior.

Test signals: create policies against dummy devices, write through char/source paths, validate master/channel bounds, test link failures using `fail_mode`, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/dummy_stm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/ftrace.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/ftrace.c

Purpose: STM source that exports kernel ftrace records to a linked STM device.

Important APIs/types/functions: static `stm_ftrace` embeds `stm_source_data` and `struct trace_export`. `stm_ftrace_write()` sends trace records using CPU-indexed channels. Link/unlink callbacks register/unregister the ftrace export. Init sets `nr_chans` to a power-of-two number of possible CPUs.

Control flow: when the source is linked to an STM device, it registers a trace export for functions, events, and markers. Trace callbacks run with preemption disabled and write to `STM_FTRACE_CHAN + cpu`, relying on the source's channel allocation width to cover CPUs.

State and persistence: one static source/export object; active only while linked.

Dependencies and integration: depends on `CONFIG_TRACING`, trace export APIs, STM source APIs, and STM policy allocation wide enough for all possible CPUs.

Risks: high-frequency trace path must remain `notrace` and low overhead. Channel count grows with `num_possible_cpus()` and may fail on devices/policies with too few channels. CPU-indexed channel mapping assumes stable CPU IDs below allocated width.

Test signals: link ftrace source, enable function/event tracing, confirm per-CPU channel output, test large CPU-count systems, unlink under active tracing, and use `p_sys-t` ftrace-compatible SBD path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/heartbeat.c

Purpose: STM source test module that periodically emits a static heartbeat message through linked STM devices.

Important APIs/types/functions: `struct stm_heartbeat` embeds source data, hrtimer, and active flag. Module parameters `nr_devs` and `interval_ms` control number of source devices and period. `stm_heartbeat_hrtimer_handler()` writes the heartbeat and rearms while active.

Control flow: init creates up to 32 named sources `heartbeat.N`, initializes hrtimers, and registers source devices. Linking a source starts its hrtimer. Unlinking clears active and cancels the timer. Exit unregisters all and frees names.

State and persistence: static array plus allocated names; timer activity exists only while linked. No persistent trace data.

Dependencies and integration: depends on STM source APIs and high-resolution timers.

Risks: very low intervals can generate substantial trace traffic. Timer handler writes from hrtimer context, so STM source write path must remain context-appropriate. Error cleanup interleaves unregister/free labels and should be regression-tested.

Test signals: register multiple heartbeat sources, link/unlink, observe periodic trace messages, vary interval, validate invalid `nr_devs`, and unload while timers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_basic.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_basic.c

Purpose: basic STM framing protocol driver for compatibility with older STM setups.

Important APIs/types/functions: `basic_write()` sends payload data through `stm_data_write()` with timestamp on the first packet, then emits a FLAG packet. `basic_pdrv` registers protocol name `p_basic`.

Control flow: module init registers the protocol with the STM core; exit unregisters it. STM policies without explicit protocol fall back to `p_basic` if available. Writes use the assigned master/channel plus optional channel offset.

State and persistence: no per-output private state. Protocol registration lives in the STM core list while module is loaded.

Dependencies and integration: depends on STM protocol registration and hardware `packet()` callbacks.

Risks: no metadata beyond STP framing and final FLAG, so consumers need only STP decoding but lose richer identification. Write errors before FLAG leave an incomplete frame.

Test signals: create policy using `p_basic`, write from char device and sources, verify timestamped first packet and trailing FLAG, unload protocol after policy unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_sys-t.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_sys-t.c

Purpose: MIPI SyS-T framing protocol driver for STM. It wraps STM payloads with SyS-T headers, GUIDs, optional length/timestamps, optional clock sync messages, and ftrace-compatible Structured Binary Data framing.

Important APIs/types/functions: enums and macros encode SyS-T message type/severity/subtype/option fields. `struct sys_t_policy_node` stores per-policy UUID and interval settings. `struct sys_t_output` snapshots policy settings per output and tracks jiffies for periodic metadata. Configfs attributes expose `uuid`, `do_len`, `ts_interval`, and `clocksync_interval`. `sys_t_write()` is the protocol write path; helpers include `sys_t_clock_sync()`, `sys_t_header()`, and `sys_t_write_data()`.

Control flow: protocol registration provides private policy-node storage and output open/close callbacks. Policy-node creation generates a UUID by default. Output open copies policy settings into per-output private data. Each write may first emit a clock-sync frame if due, builds a SyS-T header from source type and options, emits timestamped header, GUID, optional length, optional timestamp, payload data, and final FLAG. Ftrace sources are treated specially by converting the first 64 bits to a SyS-T SBD ID64-compatible header before sending remaining data.

State and persistence: policy values live in configfs objects while the policy exists; per-output private state is allocated on channel assignment and freed on output close. Jiffies timestamps throttle periodic SyS-T metadata. No on-disk persistence beyond userspace-created configfs state.

Dependencies and integration: depends on STM protocol driver API, configfs merged policy attributes, UUID helpers, ktime, jiffies, and STM source type values.

Risks: interval attributes are copied at output-open time, so later policy changes may not affect already assigned outputs. Ftrace compatibility assumes minimum buffer length and bit layout. `u16 length = count` truncates payload lengths above 65535 when `do_len` is enabled. Metadata insertion can alter bandwidth and timing.

Test signals: create `p_sys-t` policy, inspect/change configfs attributes, write normal and ftrace sources, verify GUID/header/FLAG layout, test length option with large payloads, test timestamp and clock-sync intervals, and unload after output close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_sys-t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/policy.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/policy.c

Purpose: configfs policy manager for STM master/channel allocation. It lets users bind one STM device to one framing protocol and create named policy nodes containing allowed master/channel ranges and protocol-specific attributes.

Important APIs/types/functions: `struct stp_policy` links a configfs group to an STM device. `struct stp_policy_node` stores range limits and protocol-private data. Exported helpers include `stp_policy_node_priv()`, `to_pdrv_policy_node()`, `stp_policy_node_get_ranges()`, `stp_policy_unbind()`, `stp_policy_node_lookup()`, `stp_policy_node_put()`, `stp_configfs_init()`, and `stp_configfs_exit()`. `get_policy_node_type()` merges generic and protocol-specific configfs attributes.

Control flow: configfs root `stp-policy` accepts group names shaped like `<device>[:<protocol>].<policy>`. Creation finds the STM device, looks up the protocol, ensures no policy is already bound to that STM, stores protocol/device references, and initializes the policy group. Child groups create `stp_policy_node` objects with default full device ranges and protocol-private initialization. Attribute writes validate ranges against the bound STM device. Lookup walks slash-separated policy node names while holding the configfs subsystem mutex, returning a referenced node for allocation.

State and persistence: configfs objects are in-kernel state controlled by userspace directory operations. A policy holds references to the STM device and protocol until unbound/released. Policy-node private data persists while the configfs node exists.

Dependencies and integration: depends on STM core device/protocol lookup, configfs, module refs, and protocol attribute composition. `core.c` calls lookup/put while assigning outputs.

Risks: one-policy-per-STM enforcement means conflicting configfs groups must fail cleanly. Locking with configfs `su_mutex` and STM `policy_mutex` protects device/protocol links; order changes can deadlock. Policy release currently returns before `kfree(policy)` when already unbound, which should be checked for leak potential. Node lookup keeps the subsystem mutex held until `stp_policy_node_put()`, so callers must always put.

Test signals: create valid/invalid policy names, explicit and fallback protocols, nested nodes, range updates at boundaries, output assignment by node path, policy removal while sources are linked, and leak/lockdep tests around unbind/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/stm.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/stm.h

Purpose: private STM framework header shared by core, policy, and protocol modules.

Important APIs/types/functions: declares policy/configfs helpers, `struct stp_master`, `struct stm_device`, `struct stm_output`, `struct stm_file`, `struct stm_source_device`, and `struct stm_protocol_driver`. It also declares device/protocol lookup and data-write functions used across STM modules.

Control flow: no standalone execution. It defines the internal contracts used when devices register, policies allocate outputs, protocols format writes, and sources link to devices.

State and persistence: structures describe volatile kernel state: device policy/protocol pointers, master bitmaps, source links, output allocations, and protocol private output state.

Dependencies and integration: includes configfs and relies on public `linux/stm.h` types included by users. It is the main integration point between `core.c`, `policy.c`, `p_basic.c`, and `p_sys-t.c`.

Risks: fields are protected by different locks documented in implementation files; header-only changes must preserve those locking assumptions. `stm_protocol_driver.write()` may be called from sensitive tracing contexts, so protocol implementations must avoid unsafe behavior.

Test signals: full STM build, protocol registration/unregistration, policy creation with protocol-private attributes, source link/write, and static analysis for lock-protected field access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/stm/stm.h -->
