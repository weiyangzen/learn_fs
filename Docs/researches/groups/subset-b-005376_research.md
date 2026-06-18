# subset-b-005376 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/zynqmp_power.c -->
# sources/distributed-fs/ceph-client/drivers/soc/xilinx/zynqmp_power.c

## Purpose
Implements the Xilinx Zynq UltraScale+ MPSoC and Versal power-management platform driver. It receives firmware-originated suspend, shutdown, and subsystem-restart events through the Xilinx event manager, an IPI mailbox, or a legacy interrupt path, then translates those callbacks into Linux poweroff, suspend-to-RAM, or restart actions. It also exposes a `suspend_mode` sysfs knob that programs the platform firmware suspend mode.

## Important APIs, Types, and Functions
Important local types are `struct zynqmp_pm_work_struct`, which wraps a work item plus callback arguments, and `struct zynqmp_pm_event_info`, a devres-managed record for firmware event registrations. The central entry points are `zynqmp_pm_probe()` and `zynqmp_pm_remove()`. Callback and bottom-half paths include `suspend_event_callback()`, `subsystem_restart_event_callback()`, `ipi_receive_callback()`, `zynqmp_pm_isr()`, `zynqmp_pm_init_suspend_work_fn()`, and `zynqmp_pm_subsystem_restart_work_fn()`. Sysfs handlers are `suspend_mode_show()` and `suspend_mode_store()`. `register_event()` and `unregister_event()` wrap `xlnx_register_event()` / `xlnx_unregister_event()` for devres cleanup.

## Control Flow
Probe first checks the PM firmware API version against `ZYNQMP_PM_VERSION`. It prefers event-manager registration for `PM_INIT_SUSPEND_CB`; when that succeeds it also queries family info and registers `PM_NOTIFY_CB` for `EVENT_SUBSYSTEM_RESTART` on the correct ACPU node for Versal or Versal Net. If the event manager is unavailable with `-EACCES` or `-ENODEV`, probe falls back to a DT `mboxes` receive channel with `ipi_receive_callback()`, or a threaded IRQ with `zynqmp_pm_isr()`. Suspend/shutdown callbacks queue work on `system_dfl_wq`; the work function calls `orderly_poweroff(true)` for shutdown reasons and `pm_suspend(PM_SUSPEND_MEM)` for power requests. Subsystem restart work first narrows firmware shutdown scope with `zynqmp_pm_system_shutdown(...SETSCOPE_ONLY, ...SUBSYSTEM)` and then calls `kernel_restart(NULL)`.

## State and Persistence Behavior
Global runtime state is small: pointers to the suspend and restart work objects, one global mailbox receive channel, and the selected `suspend_mode`. Event-manager registrations persist through devres records and unregister automatically through `unregister_event()`. The sysfs `suspend_mode` value is in-memory only, but storing a new value immediately calls `zynqmp_pm_set_suspend_mode()` so the firmware state changes with it. Work items retain the last copied firmware callback arguments only until their queued bottom halves execute. The driver does not persist anything to disk.

## Dependencies and Integration Points
The driver depends on the Xilinx ZynqMP firmware API (`xlnx-zynqmp.h`), the Xilinx event manager, mailbox IPI messages, OF platform probing, Linux suspend/reboot APIs, and sysfs device attributes. Its DT match is `xlnx,zynqmp-power`. It integrates with system power management by converting PMU firmware callbacks into generic Linux `pm_suspend()`, `orderly_poweroff()`, and `kernel_restart()` requests.

## Risks
The removal path appears to call `mbox_free_channel(rx_chan)` only when `rx_chan` is false, which is likely inverted and can leak a requested channel or attempt to free `NULL`. The mailbox callback copies `sizeof(msg->len)` bytes from `msg->data` into the payload array rather than using the callback payload size, so callback parsing depends on the mailbox message layout. The global work pointers and global `rx_chan` make multiple instances unsafe. Event-manager callbacks drop events while work is already pending, so repeated firmware notifications may coalesce without payload queuing. Suspend/restart actions are privileged and system-wide; bad firmware callback data directly affects machine power state.

## Test Signals
Useful checks include probing with event manager available, probing through mailbox fallback, probing through interrupt fallback, sysfs show/store of `standard` and `power-off`, firmware callback delivery for `SUSPEND_SYSTEM_SHUTDOWN` and `SUSPEND_POWER_REQUEST`, subsystem restart event delivery on Versal and Versal Net node IDs, error paths for unsupported PM API/family, module remove with an active mailbox channel, and suspend/restart behavior under repeated callback storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/xilinx/zynqmp_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soundwire/Kconfig

## Purpose
Defines the Kconfig surface for the SoundWire subsystem and the in-tree AMD, Cadence, Intel, Qualcomm, and generic bandwidth-allocation components. It controls whether the SoundWire bus core and platform master drivers are built and which helper libraries are selected.

## Important APIs, Types, and Functions
The primary symbol is `SOUNDWIRE`, a tristate menuconfig gated by `ACPI || OF` and `SND_SOC_SDCA_OPTIONAL`. Driver symbols are `SOUNDWIRE_AMD`, `SOUNDWIRE_CADENCE`, `SOUNDWIRE_INTEL`, `SOUNDWIRE_QCOM`, and `SOUNDWIRE_GENERIC_ALLOCATION`. `SOUNDWIRE_AMD` and `SOUNDWIRE_INTEL` select `SOUNDWIRE_GENERIC_ALLOCATION`; Intel additionally selects `SOUNDWIRE_CADENCE` and `AUXILIARY_BUS`; Cadence selects `CRC8`; Qualcomm implies `SLIMBUS`.

## Control Flow
Kconfig has no runtime control flow. At configuration time, enabling `SOUNDWIRE` opens the subordinate driver symbols. Selecting AMD or Intel pulls in the generic allocation module, while Intel also pulls in the Cadence library used by Intel-specific master drivers. Build dependencies enforce ACPI/OF discovery support and ASoC integration for master drivers that expose DAIs.

## State and Persistence Behavior
State is the generated kernel configuration. Tristate values persist in `.config` and affect module linkage through the Makefile. No runtime state is defined here.

## Dependencies and Integration Points
This file feeds `drivers/soundwire/Makefile`, the bus core, ASoC master drivers, and optional libraries. The `SND_SOC_SDCA_OPTIONAL` dependency ties SoundWire enablement to the SDCA helper configuration used by modern audio codecs. The Intel constraints include compatibility expressions for SOF HDA multi-link support and aligned HDA MMIO.

## Risks
Incorrect selects or dependencies can produce missing symbols at link time or hide required drivers from platform configurations. The hidden `SOUNDWIRE_CADENCE` and `SOUNDWIRE_GENERIC_ALLOCATION` symbols are library-like; direct user selection is not intended. Because AMD and Intel select generic allocation, changes to that library affect multiple drivers. Qualcomm only implies SLIMBUS, so builds without SLIMBUS must still compile.

## Test Signals
Configuration matrix tests should cover built-in and module builds for `SOUNDWIRE`, AMD, Intel, Qualcomm, and Cadence-selected-by-Intel paths; ACPI-disabled and OF-only builds; debugfs/IRQ-domain optional objects through Makefile conditionals; and `allyesconfig`, `allmodconfig`, and minimal ASoC configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soundwire/Makefile

## Purpose
Builds the SoundWire bus core, optional helper modules, and platform master drivers according to the Kconfig symbols. It defines how the subsystem source files are grouped into kernel modules or built-in objects.

## Important APIs, Types, and Functions
`soundwire-bus-y` groups the core files: `bus_type.o`, `bus.o`, `master.o`, `slave.o`, `mipi_disco.o`, `stream.o`, `sysfs_slave.o`, and `sysfs_slave_dpn.o`. Optional additions are `debugfs.o` under `CONFIG_DEBUG_FS` and `irq.o` under `CONFIG_IRQ_DOMAIN`. `soundwire-generic-allocation-objs` contains `generic_bandwidth_allocation.o`. Driver aggregates are `soundwire-amd-y := amd_init.o amd_manager.o`, `soundwire-cadence-y := cadence_master.o`, `soundwire-intel-y := intel.o intel_ace2x.o intel_ace2x_debugfs.o intel_auxdevice.o intel_init.o dmi-quirks.o intel_bus_common.o`, and `soundwire-qcom-y := qcom.o`.

## Control Flow
The Makefile has build-time flow only. `obj-$(CONFIG_SOUNDWIRE)` emits the bus module. `obj-$(CONFIG_SOUNDWIRE_GENERIC_ALLOCATION)`, `obj-$(CONFIG_SOUNDWIRE_AMD)`, `obj-$(CONFIG_SOUNDWIRE_CADENCE)`, `obj-$(CONFIG_SOUNDWIRE_INTEL)`, and `obj-$(CONFIG_SOUNDWIRE_QCOM)` emit their respective objects. Optional debugfs and IRQ objects are appended to the core bus object list only when their configs are enabled.

## State and Persistence Behavior
There is no runtime state. The generated state is the object graph and module boundaries: the bus core is separated from generic allocation, AMD, Cadence, Intel, and Qualcomm modules unless those are linked built-in by configuration.

## Dependencies and Integration Points
This file is the build integration point for all SoundWire sources in this directory. It mirrors the Kconfig library relationships: AMD links `amd_init.o` and `amd_manager.o` together; Intel links `dmi-quirks.o` into the Intel module rather than the core bus; Cadence is a library object selected by Intel and usable by other platform glue.

## Risks
Moving a source between aggregates changes module ownership and symbol availability. Optional `debugfs.o` and `irq.o` alter exported behavior only when config symbols are enabled, so missing stubs in `bus.h` or callers can break non-debug or non-IRQ-domain builds. Intel-specific `dmi-quirks.o` being in the Intel aggregate means core ACPI discovery cannot rely on those remaps unless the Intel module is enabled.

## Test Signals
Useful signals include clean `M=drivers/soundwire` builds for builtin and module variants, builds with and without `CONFIG_DEBUG_FS` and `CONFIG_IRQ_DOMAIN`, symbol export resolution for generic allocation and Cadence helpers, and module load order for `soundwire-bus`, `soundwire-generic-allocation`, `soundwire-amd`, `soundwire-cadence`, `soundwire-intel`, and `soundwire-qcom`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.c

## Purpose
Provides the AMD SoundWire initialization library used by an ACP/DSP parent driver to create and start per-link `amd_sdw_manager` platform devices. It enables ACP SoundWire pads, registers manager child devices from ACPI and hardware resources, starts each manager, and reports discovered SoundWire peripherals back to the caller.

## Important APIs, Types, and Functions
Exported namespace functions are `sdw_amd_probe()`, `sdw_amd_exit()`, and `sdw_amd_get_slave_info()` in namespace `SOUNDWIRE_AMD_INIT`. Internal helpers are `amd_enable_sdw_pads()`, `sdw_amd_probe_controller()`, `sdw_amd_startup()`, and `sdw_amd_cleanup()`. The file consumes `struct sdw_amd_res`, `struct sdw_amd_ctx`, `struct acp_sdw_pdata`, and `struct amd_sdw_manager` from `sdw_amd.h`, plus `amd_sdw_manager_start()` from `amd_init.h`.

## Control Flow
`sdw_amd_probe()` calls `sdw_amd_probe_controller()` to validate resources, fetch the ACPI device, enable pads according to `link_mask`, allocate a context, and register one `amd_sdw_manager` platform device per enabled link. Each child receives the shared ACP MMIO resource, ACPI fwnode, instance number, ACP revision, and ACP shared-register lock. If any registration fails, already-created platform devices are unregistered and the context is freed. After child creation, `sdw_amd_startup()` fetches each child's `amd_sdw_manager` drvdata and calls `amd_sdw_manager_start()`. `sdw_amd_exit()` unregisters child devices and frees the optional peripheral list plus context. `sdw_amd_get_slave_info()` walks every enabled manager bus and returns a flex-array list of `struct sdw_slave *`.

## State and Persistence Behavior
The persistent runtime object is `struct sdw_amd_ctx`, which records link count, link mask, registered child platform devices, and a lazily allocated peripheral list. Pad state is programmed in ACP registers by clearing pulldown bits and enabling keeper bits. Platform devices own their own manager state after registration. `sdw_amd_get_slave_info()` allocates `ctx->peripherals` each time it succeeds; callers must account for previous allocation if called repeatedly.

## Dependencies and Integration Points
The library depends on ACPI, platform-device registration, MMIO register access, and AMD ACP resources supplied by a parent driver. It integrates with `amd_manager.c` through the platform driver name `amd_sdw_manager`, the platform data structure, and `amd_sdw_manager_start()`. It exports symbols for external ACP/DSP drivers rather than registering an independent bus.

## Risks
The `sdw_res` resource is allocated with cleanup scope and passed to `platform_device_register_full()`, relying on the platform core to copy resources before the scoped pointer is freed. `sdw_pdata` and `pdevinfo` are stack arrays, also relying on registration copying platform data. Pad enablement supports only link masks 1, 2, or 3. `sdw_amd_get_slave_info()` does not free an existing `ctx->peripherals` before allocating a new one. Startup failures after some managers have started are returned without cleanup in `sdw_amd_probe()`, so parent error handling must call `sdw_amd_exit()`.

## Test Signals
Key tests include ACPI resource discovery, link masks for SDW0, SDW1, and both links, unsupported link masks, platform-device registration failure injection, manager startup failure, probe/exit leak checks, ACP pad register programming, and `sdw_amd_get_slave_info()` with zero, one, and multiple slaves across both links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.h

## Purpose
Provides private declarations shared by the AMD SoundWire init library and manager driver. It exposes the manager startup function and a small MMIO read-modify-write helper used for ACP shared registers.

## Important APIs, Types, and Functions
The header declares `int amd_sdw_manager_start(struct amd_sdw_manager *amd_manager);` and defines `amd_updatel(void __iomem *mmio, int offset, u32 mask, u32 val)`. It includes `<linux/soundwire/sdw_amd.h>` for `struct amd_sdw_manager` and AMD SoundWire resource definitions.

## Control Flow
There is no standalone control flow. Callers use `amd_updatel()` to read a 32-bit register, clear bits in `mask`, OR in `val`, and write the result back. `amd_init.c` calls `amd_sdw_manager_start()` after creating a platform device whose driver has populated drvdata.

## State and Persistence Behavior
The helper mutates MMIO register state directly. It has no locking of its own; callers must hold the appropriate ACP shared lock where required. The function does not cache state or validate masks.

## Dependencies and Integration Points
This header ties `amd_init.c` and `amd_manager.c` together and depends on Linux I/O accessors. `amd_updatel()` is used for ACP pad and interrupt-control registers in both AMD source files.

## Risks
Because `amd_updatel()` is a raw read-modify-write helper, concurrent callers can lose updates unless they use `acp_sdw_lock` around shared ACP registers. The helper accepts any offset and mask, so incorrect constants directly program hardware. The declaration creates a private compile-time dependency from the init library to the manager driver.

## Test Signals
Compile coverage for `soundwire-amd.o`, register writes under single-link and dual-link startup, lockdep review around shared ACP register updates, and failure injection around `amd_sdw_manager_start()` users are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_manager.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/amd_manager.c

## Purpose
Implements the AMD ACP SoundWire manager platform driver. It registers an `sdw_bus`, performs immediate command transfers, configures bus frame shape and data ports, exposes ASoC CPU DAIs, handles ACP SoundWire status interrupts, and implements runtime/system suspend through clock-stop or power-off sequences.

## Important APIs, Types, and Functions
The exported intra-module API is `amd_sdw_manager_start()`. Probe/remove are `amd_sdw_manager_probe()` and `amd_sdw_manager_remove()`. Hardware setup helpers include `amd_sdw_clk_init_ctrl()`, `amd_init_sdw_manager()`, `amd_enable_sdw_manager()`, `amd_disable_sdw_manager()`, `amd_enable_sdw_interrupts()`, `amd_disable_sdw_interrupts()`, `amd_sdw_set_frameshape()`, and device/wake helpers. SoundWire bus operations are `amd_sdw_xfer_msg()`, `amd_sdw_read_ping_status()`, `amd_sdw_compute_params()`, `amd_sdw_port_params()`, `amd_sdw_transport_params()`, and `amd_sdw_port_enable()`. ASoC DAI operations are `amd_sdw_hw_params()`, `amd_sdw_hw_free()`, `amd_set_sdw_stream()`, and `amd_get_sdw_stream()`. PM paths are `amd_pm_prepare()`, `amd_suspend()`, `amd_suspend_runtime()`, and `amd_resume_runtime()`.

## Control Flow
Probe maps the ACP register resource, selects per-revision/per-instance port counts, initializes `sdw_bus` ops, sets the controller/link identity, registers the bus with `sdw_bus_master_add()`, registers CPU DAIs, stores drvdata, and initializes interrupt/status work items. `amd_sdw_manager_start()` programs the initial clock divider and frame shape, resets the manager, unmasks interrupts, enables the manager, and enables runtime PM unless firmware marked the link disabled. SoundWire transfers are serialized by the core bus lock; each byte is encoded into AMD immediate command upper/lower words, written to command registers, polled for a valid response, and decoded as ACK/NACK/ignored/timeout. Status interrupts read 0-to-7 and 8-to-11 status-change registers, process wake or peripheral-request events, update `amd_manager->status`, and schedule work that calls `sdw_handle_slave_status()`. Stream setup flows from ASoC `.set_stream()` to `.hw_params()`, which creates an `sdw_stream_config` and one port config, then the stream framework calls AMD compute/port callbacks to program offsets, sample intervals, hstart/hstop, channel masks, and word length.

## State and Persistence Behavior
Persistent state lives in `struct amd_sdw_manager`: ACP and per-manager MMIO bases, `sdw_bus`, interrupt/status work, shared ACP lock, per-device status array, ACP revision, link instance, port counts, `port_offset_map`, wake/power mode masks, `clk_stopped`, and per-DAI runtime pointers. The static `next_offset[AMD_SDW_MAX_MANAGER_COUNT]` inside `amd_sdw_compute_params()` persists across compute calls and manager instances, influencing dynamic block offsets for 12 MHz data rate cases. Runtime PM state persists through autosuspend and `clk_stopped`; power-off mode resets the bus and clears slave status on resume.

## Dependencies and Integration Points
The driver depends on the SoundWire core, SoundWire stream framework, generic `sdw_compute_slave_ports()`, ASoC DAI registration, AMD ACPI link subproperties, ACP MMIO registers, and the parent-created platform device from `amd_init.c`. It reads standard master properties through `sdw_master_read_prop()` and AMD-specific fwnode properties such as `amd-sdw-enable`, `amd-sdw-wakeup-enable`, and `amd-sdw-power-mode`.

## Risks
Immediate command polling and response clearing are timing-sensitive; missed `IMM_RES_VALID` transitions can wedge command I/O. `amd_sdw_compute_params()` uses a static `next_offset` that is not reset on stream teardown or bus reset, so repeated stream reconfiguration may exhaust offsets or create stale layout. Register-array indexing depends on `p_params->num` and `params->port_num` matching the per-revision port count; most callbacks trust those values. Several clock-stop error paths log and return 0, which can hide failures from PM callers. ACP shared-register access requires `acp_sdw_lock`; not every ACP access is protected because some fields are per-manager or PM-specific. Power-off resume invokes `amd_init_sdw_manager()` without checking its return before continuing.

## Test Signals
Validation should cover probe on ACP63 SDW0/SDW1 and ACP70/71/72, disabled-link firmware properties, immediate read/write and paged register transactions, enumeration after status interrupts, PING fallback during device0 enumeration, ASoC playback/capture stream add/remove, port programming for every DAI, 12 MHz and 24 MHz bus cases, runtime clock-stop, runtime power-off with bus reset/re-enumeration, host wake on ACP70+, system suspend/resume, work cancellation on remove, and repeated stream open/close checking `port_offset_map` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_manager.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/amd_manager.h

## Purpose
Defines AMD ACP SoundWire manager register offsets, bit masks, timing constants, port limits, and per-revision DAI-to-register maps used by `amd_manager.c`. It is the hardware programming contract for AMD SoundWire managers.

## Important APIs, Types, and Functions
The key type is `struct sdw_manager_dp_reg`, mapping a manager port to frame-format, sample-interval, hctrl, offset, and lane/channel-enable registers. The file defines ACP common registers (`ACP_PAD_PULLDOWN_CTRL`, `ACP_SW_PAD_KEEPER_EN`, `ACP_EXTERNAL_INTR_*`, wake registers), manager registers (`ACP_SW_EN`, `ACP_SW_FRAMESIZE`, immediate command/response, status masks, BPT/BRA registers), command/response bitfields, interrupt masks, PM and wake masks, DPN frame/offset/channel fields, and arrays `acp63_sdw0_dp_reg`, `acp63_sdw1_dp_reg`, `acp70_sdw_dp_reg`, and `sdw_manager_reg_mask_array`.

## Control Flow
The header has no runtime flow, but `amd_manager.c` selects an array based on ACP revision and manager instance. Those arrays drive every data-port register write during stream parameter setup and channel enable/disable. Interrupt setup uses `sdw_manager_reg_mask_array` to select the ACP external interrupt bit for SDW0 or SDW1.

## State and Persistence Behavior
Despite being a header, it defines `static` register-map arrays in every translation unit that includes it. In this build it is included by `amd_manager.c`, so the arrays are private copies. The constants model persistent hardware layout and must stay aligned with ACP revisions. No software state is stored here beyond compile-time data.

## Dependencies and Integration Points
Includes `linux/soundwire/sdw_amd.h` for manager counts and revision/instance definitions. It is tightly coupled to AMD ACP register documentation and the DAI numbering used by the AMD DMA and ASoC paths. The comments document required CPU DAI to manager port mapping for SDW0 and SDW1.

## Risks
Incorrect offsets, masks, or DAI array ordering can route audio to the wrong ACP data port or corrupt shared ACP state. The register-map arrays are `static` in a header, which is safe for single use but undesirable if included by multiple C files. Port counts must match the arrays; any new ACP revision needs explicit mapping. Bit masks for wake, device state, and interrupts affect suspend/resume reliability.

## Test Signals
Review ACP register writes during playback/capture on every port, compile with all AMD-supported revisions, verify SDW0 six-DAI and SDW1 two-DAI mapping, validate external interrupt masks for both instances, and test suspend/resume wake masks and device-state programming on ACP70+.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/amd_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/bus.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/bus.c

## Purpose
Implements the core SoundWire bus runtime: master registration/deletion, synchronous and deferred register transfers, paged register addressing, slave enumeration and device-number assignment, slave status/alert handling, clock-stop orchestration, DPN interrupt mask programming, bus clock scaling helpers, and BPT dispatch wrappers.

## Important APIs, Types, and Functions
Exported master lifecycle APIs are `sdw_bus_master_add()` and `sdw_bus_master_delete()`. Transfer APIs include `sdw_transfer()`, `sdw_transfer_defer()`, `sdw_fill_msg()`, `sdw_nread_no_pm()`, `sdw_nwrite_no_pm()`, `sdw_read_no_pm()`, `sdw_write_no_pm()`, `sdw_nread()`, `sdw_nwrite()`, `sdw_read()`, `sdw_write()`, `sdw_update()`, and broadcast test helpers. Enumeration and status APIs include `sdw_extract_slave_id()`, `sdw_compare_devid()`, `sdw_handle_slave_status()`, and `sdw_clear_slave_status()`. Power helpers include `sdw_bus_prep_clk_stop()`, `sdw_bus_clk_stop()`, and `sdw_bus_exit_clk_stop()`. BPT APIs are `sdw_bpt_send_async()`, `sdw_bpt_wait()`, and `sdw_bpt_send_sync()`.

## Control Flow
`sdw_bus_master_add()` assigns a bus ID, creates the master device, validates bus ops and bandwidth allocation, initializes locks/lists, reads master properties, initializes debugfs, reserves special SoundWire device numbers, creates IRQ mappings, discovers slaves through ACPI or OF, and initializes bus frequency/bank defaults. Register I/O builds `struct sdw_msg`, handles optional SCP address paging, serializes transfers with `msg_lock`, retries through master `xfer_msg`, and maps SoundWire command responses to Linux errno values. Enumeration starts when status for device0 is attached: `sdw_program_device_num()` reads DEVID registers on enumeration address 0, matches firmware-created slaves, assigns a sticky nonzero device number, and waits for later nonzero attachment. Status handling first marks fallen-off devices unattached, then handles device0 enumeration, then processes nonzero devices as unattached, alert, or attached. Alert handling reads SCP and port interrupt registers, clears handled bits, completes port-ready completions, invokes nested IRQs or driver `interrupt_callback()`, and loops until interrupts settle.

## State and Persistence Behavior
Global state is `sdw_bus_ida`. Per-bus state includes assigned device-number bitmap, slave list, master runtime list, current/next bank, current/max data rate, clock-stop timeout, defer message, lockdep keys, and debugfs. Per-slave state mutated here includes `dev_num`, `dev_num_sticky`, status, probed flag callbacks, completions for enumeration/initialization/port readiness, first-interrupt flag, and unattach request. Runtime PM references are taken around user-facing slave register access and alert handling.

## Dependencies and Integration Points
This file depends on `struct sdw_master_ops` supplied by platform master drivers, firmware discovery helpers in `mipi_disco`/ACPI/OF code, IRQ-domain helpers, sysfs/debugfs support, SoundWire register definitions, and slave driver callbacks from `struct sdw_driver`. Cadence and AMD managers call into these APIs for enumeration/status and clock stop. Codec drivers consume exported read/write/update functions and receive status/interrupt callbacks through the bus.

## Risks
Enumeration is race-sensitive: device0 assignment intentionally returns early to avoid skipping state-machine stages, so interrupt/PING behavior must retrigger status handling. `sdw_fill_msg()` truncates the address into a 16-bit field after validating page rules, so paging support must be correct. Some list traversal in status paths checks `bus->assigned` under lock but calls `sdw_get_slave()` without holding `bus_lock`, relying on stable bus lifetime. Alert clearing loops can miss or over-clear implementation-defined bits if masks are wrong. Clock-stop paths tolerate `-ENODATA` for missing devices but other errors can leave slaves partially prepared. BPT support depends entirely on master callbacks and validates only aggregate byte count/device number.

## Test Signals
Important tests include bus add/delete with ACPI and OF slave discovery, lockdep with multiple buses, simple and paged register reads/writes across page boundaries, transfer retry thresholds, mockup-device I/O behavior, device0 enumeration with multiple peripherals, attach/unattach/alert transitions, slave driver update-status and interrupt callbacks, DP0/DPN port-ready completion, clock-stop prepare/stop/exit for simple and non-simple slaves, dynamic clock base/scale programming for SDCA, and BPT sync/async error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/bus.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/bus.h

## Purpose
Defines private SoundWire core declarations shared across bus, discovery, debugfs, IRQ, stream, and master-library code. It supplies message structures, BPT structures, stream runtime structures, helper prototypes, and small inline fillers for transport and port parameters.

## Important APIs, Types, and Functions
Important types are `struct sdw_msg`, `struct sdw_bpt_section`, `struct sdw_bpt_msg`, `struct sdw_port_runtime`, `struct sdw_slave_runtime`, `struct sdw_master_runtime`, and `struct sdw_transport_data`. It declares discovery and device APIs (`sdw_acpi_find_slaves()`, `sdw_of_find_slaves()`, `sdw_slave_add()`, `sdw_master_device_add()`), debugfs APIs with stubs, transfer APIs, DPN interrupt configuration, broadcast test helpers, status clearing, modalias generation, and `sdw_compute_slave_ports()`. Inline helpers `sdw_fill_xport_params()` and `sdw_fill_port_params()` populate stream programming structures.

## Control Flow
The header does not execute independently. Its stubs make non-ACPI and non-debugfs builds compile by returning `-ENOTSUPP` or doing nothing. Runtime code uses `sdw_msg` to pass fully prepared register commands to master drivers, `sdw_bpt_msg` for bulk transport, and the runtime list structures to compute and apply stream parameters.

## State and Persistence Behavior
The declared runtime structures are embedded in `struct sdw_stream_runtime` and bus/slave lists. Their state persists for the lifetime of stream configuration and records port numbers, channel masks, transport/port parameters, lanes, directions, and list membership. `sdw_msg` and `sdw_bpt_msg` are transient command descriptors.

## Dependencies and Integration Points
This header is the local bridge between generic SoundWire core code, master drivers such as AMD/Cadence/Intel/Qualcomm, debugfs, IRQ-domain support, and stream/bandwidth allocation. It assumes public SoundWire types and constants from `<linux/soundwire/sdw.h>` are already visible through includers.

## Risks
Changing structure fields or helper semantics affects multiple modules in one directory. The `sdw_msg.addr` field is 16-bit while APIs accept larger addresses with paging, so callers must use `sdw_fill_msg()`. Debugfs and ACPI stubs must remain signature-compatible with enabled implementations. Runtime list nodes require strict ownership to avoid list corruption during stream add/remove.

## Test Signals
Compile matrix coverage with ACPI enabled/disabled, debugfs enabled/disabled, and IRQ-domain enabled/disabled is essential. Runtime signals include stream add/remove list integrity, correct transport/port parameters passed into master port ops, paged message transfers, BPT message submission, and slave status clearing after master reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/bus_type.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/bus_type.c

## Purpose
Implements the Linux device-model bus type for SoundWire slave devices. It matches slave devices to `sdw_driver` ID tables, probes/removes/shuts down slave drivers, emits modalias uevents, registers the SoundWire bus at init, and exposes driver registration helpers.

## Important APIs, Types, and Functions
The exported bus object is `sdw_bus_type`. Exported functions are `__sdw_register_driver()` and `sdw_unregister_driver()`, plus `sdw_slave_modalias()` used elsewhere. Local functions include `sdw_get_device_id()`, `sdw_bus_match()`, `sdw_slave_uevent()`, `sdw_bus_probe()`, `sdw_bus_remove()`, `sdw_bus_shutdown()`, `sdw_bus_init()`, and `sdw_bus_exit()`.

## Control Flow
Driver matching compares a slave's manufacturer ID, part ID, optional SoundWire version, and optional class ID against the driver's ID table. Probe requires firmware description, validates the ID again, attaches a power domain without powering up, allocates a per-bus slave index, calls the driver probe, reads slave properties, creates IRQ-domain mapping if requested, initializes dynamic DPN sysfs attributes, normalizes clock-stop timeout, marks the slave probed, and notifies the driver of current status if the bus was already active. Remove clears `probed`, calls driver remove, and frees the index. Module init creates debugfs root and registers the bus through `postcore_initcall`.

## State and Persistence Behavior
The bus type is global. Per-slave persistent state changed here includes `index`, `probed`, `prop`, `clk_stop_timeout`, and IRQ/sysfs setup. `slave_ida` on the bus allocates a stable index for the slave during its bound lifetime. Power-domain attachment persists until device teardown, although explicit detach is not present in this file.

## Dependencies and Integration Points
Depends on Linux device model, module driver registration, power domains, SoundWire public type helpers, IRQ mapping, sysfs attribute groups, and debugfs initialization. Slave codec/function drivers use `module_sdw_driver()`-style wrappers that eventually call `__sdw_register_driver()`. The core bus add path creates devices that bind through this bus type.

## Risks
If `dev_pm_domain_attach()` succeeds and a later IDA allocation or driver probe fails, this file returns without an explicit power-domain detach. Probe failure after IDA allocation frees the ID but does not undo any partial side effects inside driver probe beyond the driver's own error handling. Firmware node checks intentionally reject devices without ACPI/OF descriptions unless ACPI is disabled and OF node exists, which affects synthetic devices. Late status notification errors are warnings, so codec initialization may be deferred or incomplete without failing probe.

## Test Signals
Test driver matching for version/class wildcard and exact cases, modalias uevent strings, driver registration without probe callback, probe/remove failure injection around power-domain attach and IDA allocation, late probe after bus already reports attached, dynamic sysfs DPN creation, domain IRQ mapping, shutdown callback dispatch, and bus init/exit with debugfs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/bus_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/cadence_master.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/cadence_master.c

## Purpose
Implements the shared Cadence SoundWire master library used by platform-specific master drivers, especially Intel. It provides register access, command FIFO transfers, interrupt handling, slave status work, clock initialization/stop/restart, port/PDI programming, debugfs controls, ASoC stream runtime helpers, and Cadence-specific Bulk Register Access/Bulk Payload Transport buffer helpers.

## Important APIs, Types, and Functions
Core exported functions include `sdw_cdns_probe()`, `sdw_cdns_init()`, `sdw_cdns_soft_reset()`, `sdw_cdns_exit_reset()`, `sdw_cdns_enable_interrupt()`, `sdw_cdns_clock_stop()`, `sdw_cdns_clock_restart()`, `sdw_cdns_is_clock_stop()`, `cdns_xfer_msg()`, `cdns_xfer_msg_defer()`, `cdns_read_ping_status()`, and `cdns_bus_conf()`. Stream/PDI exports include `sdw_cdns_pdi_init()`, `sdw_cdns_alloc_pdi()`, `sdw_cdns_config_stream()`, and `cdns_set_sdw_stream()`. Debugfs export is `sdw_cdns_debugfs_init()`. BPT/BRA exports include bandwidth and buffer-size calculators, DMA buffer preparation, and read/write response checkers.

## Control Flow
`sdw_cdns_probe()` initializes completions, port ops, locks, and status work. `sdw_cdns_init()` programs clocks, resets command FIFOs, enables command accept, disables wake blocking, disables auto bus release, sets normal IP operation, and defers config update to the caller. Command transfers optionally program SCP address pages, split messages into up to eight FIFO commands, set RX FIFO watermark, write command words, wait for `tx_complete`, then decode ACK/NACK/read data from `response_buf`; deferred transfers support one message and complete from the IRQ path. `sdw_cdns_irq()` filters invalid interrupts, handles RX watermark completions, logs parity/clash/DP errors, masks slave status interrupts, and schedules work. The work reads and clears slave interrupt status, converts hardware bits to `sdw_slave_status[]`, handles device0 enumeration races by rechecking PING status, calls `sdw_handle_slave_status()`, and unmasks slave interrupts. Clock-stop masks slave interrupts, optionally blocks wake, prepares slaves, broadcasts clock stop, and waits for `CLK_STOP`; restart clears clock-stop, restores command accept, optionally exits slave clock stop, and can leave bus reset recovery to callers.

## State and Persistence Behavior
Persistent state in `struct sdw_cdns` includes register base, `sdw_bus`, IP offset, response buffer, transfer completion, PDI arrays, port count, link state, interrupt-enabled flag, message FIFO watermark cache, work items, status-update lock, DAI runtime array, and debugfs loopback selections. `msg_count` avoids redundant FIFOLEVEL writes. `response_buf` is reused across command transfers and filled by IRQ or polling response drain. BPT helpers are stateless except for rolling frame counters encoded in prepared buffers.

## Dependencies and Integration Points
The library depends on SoundWire core APIs, SoundWire register definitions, CRC8, PM runtime, ASoC DAI helpers, debugfs, and platform-specific users that allocate/fill `struct sdw_cdns` and call these exports. It installs `cdns_port_ops` into the bus so the SoundWire stream framework can program Cadence DPN registers. BPT support integrates with generic `sdw_bpt_msg` and with external DMA engines that consume/produce the prepared PDI buffers.

## Risks
Interrupt and transfer ordering is delicate: RX watermark must be cleared before completing to avoid races with the next transfer. `response_buf` capacity intentionally allows two entries beyond FIFO capacity; wrong FIFOLEVEL or deferred length corrupts response decoding. Clock-stop/restart interacts with interrupt masking and can lose status changes if not sequenced with platform PM. Debugfs parity injection deliberately taints the kernel and manipulates bus state. Loopback debugfs copies source port registers into target port programming, which can mask normal stream parameters. BPT/BRA helpers use packed byte/word layouts, CRC8, rolling counters, and size calculations where off-by-one errors lead to DMA buffer overruns or protocol failures.

## Test Signals
Important signals include command read/write success, NACK, ignored, timeout, paged register access, deferred transfer completion, IRQ handling for RX watermark and slave status, multi-peripheral device0 enumeration races, clock stop/restart with and without bus reset, Cadence initialization/config-update timeouts, PDI allocation/configuration for input/output/bidirectional streams, DPN bank0/bank1 port programming, debugfs register dump and parity injection, BPT bandwidth/buffer sizing, write/read DMA buffer preparation, response CRC/counter validation, and suspend/resume under active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/cadence_master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/cadence_master.h -->
# sources/distributed-fs/ceph-client/drivers/soundwire/cadence_master.h

## Purpose
Defines the shared Cadence SoundWire master data structures and exported function contract used by platform drivers. It describes PDI/stream metadata, the main `struct sdw_cdns` context, helper macros, and prototypes for initialization, IRQ, PM, port/stream, debugfs, transfer, and BPT/BRA functions.

## Important APIs, Types, and Functions
Key types are `struct sdw_cdns_pdi`, `struct sdw_cdns_streams`, `struct sdw_cdns_stream_config`, `struct sdw_cdns_dai_runtime`, and `struct sdw_cdns`. The `bus_to_cdns()` macro converts `struct sdw_bus *` to the containing Cadence context. Prototypes cover `sdw_cdns_probe()`, IRQ handlers, reset/init/PDI/clock helpers, debugfs initialization, PDI allocation/configuration, message transfer callbacks, bus config, ASoC stream setup, config update, and BPT/BRA buffer helpers.

## Control Flow
The header has no standalone execution. Platform drivers allocate and initialize `struct sdw_cdns`, call `sdw_cdns_probe()` and `sdw_cdns_init()`, install the Cadence transfer callbacks in their `sdw_bus`, and use the PDI/DAI helpers during ASoC stream setup. The stream framework calls Cadence port ops installed by `sdw_cdns_probe()`.

## State and Persistence Behavior
`struct sdw_cdns` persists for the master lifetime and owns the embedded `sdw_bus`, response buffer, completion, port/PDI data, stream runtime pointers, work items, link/interrupt flags, and status lock. `struct sdw_cdns_dai_runtime` persists per active DAI stream and is allocated/freed by `cdns_set_sdw_stream()`.

## Dependencies and Integration Points
Includes `<sound/soc.h>` and the private `bus.h`, making it a bridge between SoundWire core, Cadence hardware, and ASoC platform glue. Exported prototypes are implemented in `cadence_master.c` and consumed by Intel or other Cadence-IP platform drivers.

## Risks
The header exposes many internals of `struct sdw_cdns`; platform drivers can depend on layout details and make refactors risky. PDI arrays and DAI runtime arrays must be sized consistently by the platform glue. `ip_offset` selects between register layouts, so callers must initialize it correctly before using register helpers. BPT helpers require caller-provided DMA buffers sized from the matching calculator.

## Test Signals
Compile platform drivers against this header, probe Cadence-backed masters, verify PDI counts and DAI runtime allocation, run IRQ and PM paths, exercise both normal register transfers and BPT helpers, and check debugfs availability under `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/cadence_master.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/debugfs.c

## Purpose
Implements SoundWire debugfs support for bus and slave devices. It creates a global `soundwire` debugfs root, per-master directories, per-slave register dumps, and an unsafe command interface for arbitrary column-0 or BPT/BRA reads and writes.

## Important APIs, Types, and Functions
Exported functions are `sdw_bus_debugfs_init()`, `sdw_bus_debugfs_exit()`, `sdw_slave_debugfs_init()`, `sdw_slave_debugfs_exit()`, `sdw_debugfs_init()`, and `sdw_debugfs_exit()`. Register dump helpers include `sdw_sprintf()` and `sdw_slave_reg_show()`. Command controls are backed by `set_command()`, `set_command_type()`, `set_start_address()`, `set_num_bytes()`, `cmd_go()`, `do_bpt_sequence()`, and `read_buffer_show()`.

## Control Flow
Subsystem init creates `/sys/kernel/debug/soundwire` and a writable `firmware_file` string. Each bus creates `master-controller-link`; each slave creates a directory with `registers`, command-control files, `go`, `read_buffer`, and optional `firmware_file`. Reading `registers` resumes the slave, reads DP0, SCP, SDCA, banked, and DP1-14 registers through no-PM SoundWire reads, prints `XX` for failed reads, and releases runtime PM. For commands, users set command direction, command type, start address, byte count, and firmware file for writes, then write `1` to `go`. `cmd_go()` resumes the device, optionally loads firmware data, performs column-0 nread/nwrite or synchronous BPT, stores reads in a global buffer, logs timing, and drops the PM reference.

## State and Persistence Behavior
Global debugfs state includes `sdw_debugfs_root`, `cmd`, `cmd_type`, `start_addr`, `num_bytes`, a 1 MiB `read_buffer`, and `firmware_file`. These globals are shared by all slaves and masters, so concurrent debugfs users affect each other. Per-bus and per-slave debugfs dentries are stored in `bus->debugfs` and `slave->debugfs` and removed recursively on exit. Command operations taint the kernel with `TAINT_USER` because they mutate hardware behind normal driver state.

## Dependencies and Integration Points
Depends on `CONFIG_DEBUG_FS`, firmware loading, PM runtime, SoundWire core read/write/BPT APIs, SoundWire register definitions, and debugfs file helpers. The stubs in `bus.h` remove these hooks when debugfs is disabled. It integrates with bus/slave lifecycle through `sdw_bus_master_add/delete()` and slave add/delete paths.

## Risks
The command interface is intentionally unsafe: it can alter device registers outside driver synchronization and shares global command state across all slaves. `firmware_file` is a global string pointer exposed in each slave directory, so one user changes it for everyone. The read buffer is a large static allocation and can expose stale data if a read fails after partial completion. BPT sequence allocates a section but relies on cleanup-free style only for local pointer lifetime. Register dumps perform many bus transactions and may perturb runtime PM or timing-sensitive devices.

## Test Signals
Tests should cover debugfs root/master/slave creation and removal, register dumps on attached and inaccessible slaves, command validation for invalid direction/type/size/address, firmware write path, column-0 read/write path, BPT read/write path, read_buffer formatting, concurrent command users on two slaves, runtime PM failures, and disabled-debugfs builds using stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/dmi-quirks.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/dmi-quirks.c

## Purpose
Provides DMI-based SoundWire `_ADR` remapping quirks for systems whose firmware reports incorrect SoundWire peripheral addresses. It lets discovery code replace bad ACPI addresses with hardware-accurate addresses on known Intel/Realtek laptop and NUC designs.

## Important APIs, Types, and Functions
The local type is `struct adr_remap`, containing original and remapped 64-bit SoundWire addresses. Quirk tables include `intel_tgl_bios`, `dell_sku_0A3E`, `hp_omen_16`, and `intel_rooks_county`. `adr_remap_quirk_table` matches DMI vendor/product/board/SKU strings. The exported function is `sdw_dmi_override_adr(struct sdw_bus *bus, u64 addr)`.

## Control Flow
`sdw_dmi_override_adr()` calls `dmi_first_match()` on the quirk table. If a system match is found, it scans that match's `adr_remap` table until the sentinel and replaces `addr` when an exact match is found, logging the remap with `dev_dbg()`. If no system or address match exists, it returns the original address unchanged.

## State and Persistence Behavior
All quirk data is static const. The function has no mutable state and no persistence beyond the returned address used by discovery. The remap affects runtime enumeration identity for the current boot only.

## Dependencies and Integration Points
Depends on Linux DMI matching and SoundWire bus logging. The declaration is in `bus.h`, and Intel SoundWire discovery includes this object through the Intel module build. It integrates with ACPI/MIPI DisCo parsing before slave IDs are extracted from `_ADR`.

## Risks
DMI string matches can overmatch product families and apply remaps to later firmware revisions where the addresses are fixed. Exact 64-bit address constants must encode link, unique ID, manufacturer, part, version, and class correctly. Because this file is linked into the Intel driver aggregate, non-Intel SoundWire discovery does not necessarily get these quirks. Remapping can make firmware-described devices appear as different hardware, affecting driver binding.

## Test Signals
Test DMI matches for listed HP Spectre, HP board 8709, Intel LAPBC/LAPRC variants, Avell B.ON, Dell SKU 0A3E, and HP Omen 16. Validate no remap on unmatched systems, correct remap for each bad address, unchanged return for unknown addresses on matched systems, and downstream slave modalias/driver binding after remap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/dmi-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/generic_bandwidth_allocation.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/generic_bandwidth_allocation.c

## Purpose
Implements the generic SoundWire bandwidth allocation algorithm used by master drivers. It chooses bus clock/frame parameters, optionally assigns nonzero lanes, groups streams by sample rate and lane, and computes master/slave transport and port parameters for audio and BPT streams.

## Important APIs, Types, and Functions
Exported functions are `sdw_compute_params()` and `sdw_compute_slave_ports()`. Local types are `struct sdw_group_params` for per-rate/lane bandwidth and hwidth, and `struct sdw_group` for dynamically collected rate/lane groups. Important helpers include `sdw_compute_dp0_port_params()`, `sdw_compute_master_ports()`, `sdw_compute_group_params()`, `sdw_get_group_count()`, `sdw_compute_port_params()`, `sdw_select_row_col()`, `is_clock_scaling_supported()`, `is_lane_connected_to_all_peripherals()`, `get_manager_lane()`, and `sdw_compute_bus_params()`.

## Control Flow
`sdw_compute_params()` first calls `sdw_compute_bus_params()` to find current data rate and frame shape. The bus computation selects clock gear/frequency lists from master properties, limits dynamic scaling if any attached slave lacks support, checks whether lane0 has enough bandwidth at a given rate, and otherwise tries to move the latest runtime to a nonzero manager lane connected to all participating peripherals. It then derives default column from data rate, frame rate, and row, and validates row/column through `sdw_select_row_col()`. For BPT streams, DP0 master/slave port parameters use most of the frame except column 0. For audio streams, `sdw_get_group_count()` builds unique sample-rate/lane groups, `sdw_compute_group_params()` computes payload bandwidth and horizontal width per group, and `_sdw_compute_port_params()` lays groups from the end of the frame toward column 1 while calling `sdw_compute_master_ports()` and `sdw_compute_slave_ports()`.

## State and Persistence Behavior
The function mutates `bus->params.curr_dr_freq`, `row`, `col`, and per-lane used bandwidth during bus computation. It also mutates each `sdw_port_runtime` transport and port parameter structure and may set master and peripheral lane fields. Temporary grouping arrays are allocated and freed per computation. No external persistence is performed, but computed state remains in stream runtimes until recomputed or streams are removed.

## Dependencies and Integration Points
Depends on SoundWire stream runtime lists, master/slave properties, frame row/column tables, bit operations, and the inline fillers in `bus.h`. AMD, Intel, and other master drivers can install this function as `bus->compute_params`, or call `sdw_compute_slave_ports()` from custom algorithms. Later stream code consumes the computed parameters through master port ops and slave register programming.

## Risks
The algorithm assumes valid stream rates, bit depths, channel masks, default rows/columns, and frame-rate properties; divide-by-zero or invalid frame shapes are guarded only in some paths. Lane accounting uses `bus->lane_used_bandwidth` and may be stale if not reset by callers before recomputation. Multilane selection only checks the first slave runtime to find a candidate manager lane, then verifies connectivity for all peripherals. Group allocation grows arrays one element at a time and must keep rates/lanes arrays consistent on allocation failure. Column 0 reservation applies only lane0; nonzero-lane capacity checks differ.

## Test Signals
Tests should cover single-rate and mixed-rate streams, playback/capture mirror mode, BPT DP0 streams, insufficient bandwidth failures, default row/column validation, clock gear and explicit clock frequency selection, slaves with and without dynamic scaling support, multilane routing with connected and disconnected lane maps, lane bandwidth reset across repeated computations, paused/disabled streams included in bandwidth, and computed hstart/hstop/offset/sample interval values applied by master and slave port ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/generic_bandwidth_allocation.c -->
