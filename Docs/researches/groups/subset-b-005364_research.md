# subset-b-005364 Research

Grouped research report for the requested SLIMbus and SoC driver files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/qcom-ngd-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/slimbus/qcom-ngd-ctrl.c

## Purpose
This is the Qualcomm SLIMbus NGD controller driver. It bridges the generic SLIMbus core to Qualcomm Non-ported Generic Device hardware, using DMA message queues for SLIMbus packets, QMI to coordinate with the remote audio subsystem, runtime PM for power collapse, and SSR/PDR notifiers for remote processor restart handling.

## Important APIs, Types, And Functions
Important private state lives in `struct qcom_slim_ngd_ctrl`, which embeds `struct slim_controller`, a `struct slim_framer`, QMI state, DMA channels, descriptor rings, work items, runtime state, and restart locks. `struct qcom_slim_ngd` represents a child NGD platform device. The QMI request/response structs and `qmi_elem_info` tables encode select-instance and power messages.

Key functions include `qcom_slim_ngd_xfer_msg()`, `qcom_slim_ngd_xfer_msg_sync()`, `qcom_slim_ngd_enable_stream()`, `qcom_slim_ngd_get_laddr()`, `qcom_slim_ngd_power_up()`, `qcom_slim_ngd_runtime_resume()`, `qcom_slim_ngd_runtime_suspend()`, `qcom_slim_ngd_ssr_pdr_notify()`, and the parent/child probes `qcom_slim_ngd_ctrl_probe()` and `qcom_slim_ngd_probe()`.

## Control Flow
The parent controller probe maps NGD registers, requests the IRQ, registers SSR/PDR hooks, initializes SLIMbus controller callbacks, and creates a child platform device for the concrete NGD instance. The child probe enables runtime PM, starts QMI service lookup, and allocates the master worker queue.

When QMI service appears, `qcom_slim_ngd_up_worker()` enables the controller. Enable selects the SLIMbus hardware instance over QMI, resumes runtime PM, powers up the remote service, initializes DMA queues, enables RX/TX message queues, waits for capability exchange, then registers with the SLIMbus core. Transfers allocate a TX descriptor, optionally translate core connect/disconnect messages into Qualcomm user messages, write the packed message to the DMA buffer, submit TX DMA, and wait for completion. RX DMA callbacks parse replies and forward responses to `slim_msg_response()`.

## State, Persistence, And Dependencies
State is in memory and hardware registers only. DMA buffers are coherent allocations for RX and TX queues. TX ring indexes are protected by `tx_buf_lock`, serialized message submission uses `tx_lock`, and subsystem restart teardown uses `ssr_lock`. Runtime PM state transitions update `enum qcom_slim_ngd_state`. Dependencies include SLIMbus core, DMAengine, PM runtime, QMI, QRTR sockets, PDR, Qualcomm SSR notifier APIs, device tree, and platform IRQ/resources.

## Integration Points
The driver registers a `slim_controller` and supplies `xfer_msg`, `get_laddr`, `enable_stream`, and framer timing. It also consumes child DT nodes for SLIMbus devices, notifies `of_slim_get_device()` children after restart, maps two NGD compatibles, and exposes power state through runtime PM rather than userspace.

## Risks
Several paths mutate transaction fields or stream/channel state before final transfer success, so error unwinding can leave software state ahead of hardware. `qcom_slim_qmi_send_power_request()` does not check `qmi_txn_init()` before sending. DMA init failure after RX setup does not immediately unwind RX in `qcom_slim_ngd_init_dma()`. Error paths in TX allocation and user-message conversion can return without freeing an allocated descriptor or TID in all cases. SSR and runtime PM share controller state, making lock ordering and wakeup timing important.

## Test Signals
Useful signals include probe and QMI service discovery, runtime suspend/resume, SLIMbus device enumeration after SSR, DMA TX/RX completion, `slim_msg_response()` delivery for value and address replies, stream enable success on audio playback/capture, timeout logs for capability exchange or TX, and fault injection around missing DMA channels, QMI timeout, and remote processor restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/qcom-ngd-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/sched.c -->
# sources/distributed-fs/ceph-client/drivers/slimbus/sched.c

## Purpose
This file implements SLIMbus clock pause and wake handling for the core controller scheduler. The exported `slim_ctrl_clk_pause()` API lets a controller enter the SLIMbus low-power clock-pause sequence or wake from it.

## Important APIs, Types, And Functions
`slim_ctrl_clk_pause()` operates on `struct slim_controller` and its embedded `struct slim_sched`. It uses `DEFINE_SLIM_BCAST_TXN()`, `slim_do_transfer()`, `wait_for_completion_timeout()`, `txn_lock`, and the controller `wakeup` callback. It sends `SLIM_MSG_MC_BEGIN_RECONFIGURATION`, `SLIM_MSG_MC_NEXT_PAUSE_CLOCK`, and `SLIM_MSG_MC_RECONFIGURE_NOW`.

## Control Flow
For wakeup, it returns immediately if the bus is already active. Otherwise it waits up to 100 ms for any previous pause transition to complete, calls the controller `wakeup` hook when paused, and marks the scheduler active on success. For pause entry, it rejects invalid restart values, ignores requests when already paused, scans all transaction IDs under `txn_lock` to reject pause while responses are pending, marks the state as entering pause, sends the three-message reconfiguration sequence, and completes `pause_comp` when paused.

## State, Persistence, And Dependencies
The only persistent state is `sched->clk_state` and the `pause_comp` completion. `m_reconf` serializes reconfiguration. The function depends on SLIMbus message transfer, transaction ID tracking, and controller-specific wakeup support.

## Integration Points
Controller drivers call this API from runtime/system power paths. Message APIs use the scheduler state to avoid conflicting with clock pause. The controller must implement `wakeup` if hardware needs explicit framer wake.

## Risks
The function scans TID slots linearly under a spinlock, which is simple but makes `SLIM_MAX_TIDS` part of pause latency. The pause sequence updates clock state after transfer outcomes but has no rollback beyond marking active. Wakeup depends on `pause_comp`; a lost completion causes a timeout.

## Test Signals
Test with active pending transactions returning `-EBUSY`, invalid restart returning `-EINVAL`, successful pause completing `pause_comp`, wake from paused state calling the controller hook, and timeout behavior when pause never completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/slimbus.h -->
# sources/distributed-fs/ceph-client/drivers/slimbus/slimbus.h

## Purpose
This private SLIMbus core header defines message encodings, scheduler state, stream/channel/port state machines, controller internals, and internal core function prototypes shared by the SLIMbus core and controller drivers.

## Important APIs, Types, And Functions
It defines message constants for management, data-channel, reconfiguration, destination type, clock pause, and header extraction. Major types include `struct slim_framer`, `struct slim_msg_txn`, `struct slim_sched`, `struct slim_channel`, `struct slim_port`, `struct slim_stream_runtime`, and `struct slim_controller`. Transaction helper macros construct logical, broadcast, and enumeration destination messages. Inline helpers `slim_tid_txn()` and `slim_ec_txn()` classify messages needing transaction IDs or element codes.

## Control Flow
This file has no runtime flow, but it establishes the control contracts used elsewhere. Stream lifecycle moves channels from allocated to associated, defined, content-defined, active, removed, or disconnected. Port state moves disconnected, unconfigured, configured. The controller callback table defines how core transfer, address assignment, address lookup, stream enable/disable, and wakeup requests flow into hardware drivers.

## State, Persistence, And Dependencies
All defined state is in kernel memory owned by SLIMbus devices, controllers, and stream runtimes. There is no filesystem persistence. Dependencies include public `linux/slimbus.h`, driver model devices, IDA/IDR users from controller implementation, completions, mutexes, and list management.

## Integration Points
The header is consumed by SLIMbus core files and hardware drivers such as the Qualcomm NGD controller. Public exported functions such as `slim_register_controller()`, `slim_do_transfer()`, and stream helpers rely on these internal structures.

## Risks
This is a central ABI-like internal contract. Field layout and enum semantics must stay synchronized with the core, controller drivers, and stream code. Duplicate definition of `SLIM_CL_PER_SUPERFRAME` is harmless but noisy. Incorrect message length or destination encoding here propagates to all controllers.

## Test Signals
Signals are compile coverage for all SLIMbus users, controller registration, transaction ID allocation and response matching, stream lifecycle tests, and functional message transfer across supported controller drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/slimbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/stream.c -->
# sources/distributed-fs/ceph-client/drivers/slimbus/stream.c

## Purpose
This file implements the exported SLIMbus stream lifecycle used by audio clients: allocate, prepare, enable, disable, unprepare, and free. It maps audio stream configuration to SLIMbus port association and channel definition messages.

## Important APIs, Types, And Functions
Exports are `slim_stream_allocate()`, `slim_stream_prepare()`, `slim_stream_enable()`, `slim_stream_disable()`, `slim_stream_unprepare()`, and `slim_stream_free()`. Internal helpers include `slim_connect_port_channel()`, `slim_disconnect_port()`, `slim_define_channel()`, `slim_define_channel_content()`, `slim_activate_channel()`, `slim_deactivate_remove_channel()`, `slim_get_prate_code()`, and `slim_get_segdist_code()`.

## Control Flow
Allocation creates a runtime, names it, and links it to the SLIMbus device stream list. Prepare validates that ports are not already allocated, allocates per-port state, records rate/bps/direction, chooses PUSH/PULL/ISO protocol from sample rate relative to superframe rate, computes rate multiplier, initializes channel fields, and sends connect-source or connect-sink messages for each selected port. Enable either delegates to a controller-specific `enable_stream` callback or sends a reconfiguration sequence, defines each channel and content, activates channels, marks ports configured, and reconfigures now. Disable optionally calls controller `disable_stream`, then deactivates/removes channels inside a reconfiguration. Unprepare disconnects ports and frees port state. Free removes the stream from the device list.

## State, Persistence, And Dependencies
State is the runtime allocation, list membership, per-port state, channel state, protocol, rate, bps, and rate multiplier. It depends on SLIMbus core transfer, public stream config structures, and ALSA PCM direction constants.

## Integration Points
ASoC DPCM operations map naturally to these calls: startup, hw_params, trigger start, trigger pause/stop, and shutdown. Controller drivers may override stream enable/disable for hardware-specific aggregate commands.

## Risks
Several helper calls ignore return values in loops, so prepare and enable can report success after failed port or channel transfers. State fields are often advanced before transfer success. If `slim_get_prate_code()` fails after port allocation, `rt->ports` is leaked unless the caller unprepares. Segment distribution only accepts table values and returns `-EINVAL`, but callers do not check all helper errors.

## Test Signals
Exercise supported and unsupported sample rates, multiple-port masks, playback and capture direction mapping, controller-specific enable path, generic reconfiguration path, transfer-failure injection, repeated prepare rejection, and clean list removal on free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/slimbus/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/Kconfig

## Purpose
This is the top-level Kconfig menu for Linux SoC-specific drivers. It groups vendor SoC support under "SOC (System On Chip) specific Drivers" and sources each vendor subtree.

## Important APIs, Types, And Functions
The file has no C APIs. Its important entries are `source` statements for vendor Kconfig files, including Amlogic, Apple, Aspeed, Atmel, Broadcom, Qualcomm, Renesas, Rockchip, Tegra, TI, Xilinx, and others.

## Control Flow
During Kconfig parsing, selecting the `drivers/soc` menu loads each vendor configuration file in order. Those files define actual options and dependencies. This file only controls menu visibility and inclusion order.

## State, Persistence, And Dependencies
Configuration state is persisted in the kernel `.config` generated by Kconfig. This file depends on the existence and correctness of all sourced vendor Kconfig paths.

## Integration Points
It is integrated by the kernel build system when `drivers/soc` Kconfig is sourced from the broader driver menu. Vendor Makefiles then consume selected symbols.

## Risks
Broken or missing source paths break menu parsing for the whole SoC driver menu. Inclusion order can affect menu organization but not object linking directly. Adding a vendor here without a Makefile entry leaves options unbuilt.

## Test Signals
Run `make menuconfig` or `make olddefconfig` across representative architectures and confirm all sourced vendor menus parse without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/Makefile

## Purpose
This Makefile aggregates vendor SoC driver subdirectories into the kernel build.

## Important APIs, Types, And Functions
It has no runtime APIs. Its important build variables are `obj-y` and `obj-$(CONFIG_...)` entries that descend into vendor directories such as `apple/`, `aspeed/`, `atmel/`, `bcm/`, `amlogic/`, and `qcom/`.

## Control Flow
Kbuild evaluates the file after configuration. Unconditional `obj-y` directories are visited and their child Makefiles decide object selection. Conditional entries, such as `obj-$(CONFIG_ARCH_AT91) += atmel/`, only recurse when the symbol is enabled.

## State, Persistence, And Dependencies
Build state comes from `.config`. The file depends on matching vendor directories and per-vendor Makefiles.

## Integration Points
This is the build companion to `drivers/soc/Kconfig`. It bridges selected configuration symbols to compiled objects and modules.

## Risks
Mismatch between Kconfig sourcing and Makefile recursion can expose options that never build or build directories that have no relevant options. Unconditional vendor recursion is acceptable when child Makefiles are fully conditional.

## Test Signals
Build `drivers/soc/` for allmodconfig, allyesconfig, and architecture defconfigs covering conditional entries, and check for missing-directory or unused-symbol regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/amlogic/Kconfig

## Purpose
This file defines Amlogic Meson SoC driver configuration options for canvas, clock measurement, and SoC information drivers.

## Important APIs, Types, And Functions
Configuration symbols are `MESON_CANVAS`, `MESON_CLK_MEASURE`, `MESON_GX_SOCINFO`, and `MESON_MX_SOCINFO`. The clock measurement option selects `REGMAP_MMIO`, while the SoC information options select `SOC_BUS`.

## Control Flow
When the Amlogic menu is parsed, each option becomes available based on architecture and `COMPILE_TEST`. Defaults prefer enabling clock measurement and SoC info on `ARCH_MESON`, while canvas defaults to off.

## State, Persistence, And Dependencies
Chosen values are stored in `.config`. Build-time dependencies are `ARCH_MESON`, ARM/ARM64 for the appropriate SoC info driver, `COMPILE_TEST`, `REGMAP_MMIO`, and `SOC_BUS`.

## Integration Points
The corresponding Amlogic Makefile turns these symbols into `meson-canvas.o`, `meson-clk-measure.o`, `meson-gx-socinfo.o`, and `meson-mx-socinfo.o`.

## Risks
Incorrect dependency constraints can make platform-only code compile on unsupported architectures or hide useful compile-test coverage. Defaulting bool SoC info options on affects boot-time registration paths.

## Test Signals
Use ARM Meson, ARM64 Meson, and COMPILE_TEST configs to confirm symbols appear, select required dependencies, and produce expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/amlogic/Makefile

## Purpose
This Makefile maps Amlogic SoC Kconfig symbols to their driver object files.

## Important APIs, Types, And Functions
It defines object selection for `meson-canvas.o`, `meson-clk-measure.o`, `meson-gx-socinfo.o`, and `meson-mx-socinfo.o`.

## Control Flow
Kbuild includes each object when its matching `CONFIG_MESON_*` symbol is enabled. There is no runtime flow.

## State, Persistence, And Dependencies
Build state is fully determined by `.config` symbols from `drivers/soc/amlogic/Kconfig`.

## Integration Points
It is reached from `drivers/soc/Makefile` via `obj-y += amlogic/`.

## Risks
Any symbol/object name mismatch prevents configured drivers from building. Since all entries are direct one-object drivers, missing module aggregation is low risk.

## Test Signals
Compile with each `CONFIG_MESON_*` option as built-in and module where applicable and confirm expected `.o` or `.ko` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-canvas.c -->
# sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-canvas.c

## Purpose
This driver manages the Amlogic Meson canvas hardware lookup table, which maps small canvas IDs to physical buffer layout parameters used by display/video blocks.

## Important APIs, Types, And Functions
The core state is `struct meson_canvas`, containing MMIO base, spinlock, 256-entry allocation bitmap, and endianness support. Exported APIs are `meson_canvas_get()`, `meson_canvas_alloc()`, `meson_canvas_config()`, and `meson_canvas_free()`. `canvas_write()` and `canvas_read()` are local MMIO helpers.

## Control Flow
Consumers obtain a canvas provider through the `amlogic,canvas` phandle. Allocation scans `used[]` for a free ID under the lock. Configuration checks endianness support and allocation state, writes low and high layout registers, triggers a LUT write for the selected index, and reads back to flush writes. Free clears the allocation state.

## State, Persistence, And Dependencies
State is runtime-only in `used[]` and hardware LUT registers. The driver depends on platform resource mapping, device tree matching, MMIO, spinlocks, and the public Amlogic canvas header.

## Integration Points
Video, DRM, and media drivers call exported functions to allocate and configure canvas IDs. The provider is matched by compatibles including legacy Meson8 variants and generic `amlogic,canvas`.

## Risks
The API trusts `canvas_index` bounds because it is a `u8`, matching `NUM_CANVAS`. Address/stride/height fields are packed with rounding but not range-checked against bit widths. Consumers must free IDs or leaks persist until driver removal. `meson_canvas_get()` returns `-EINVAL` if provider drvdata is not set instead of deferring.

## Test Signals
Probe on each compatible, allocate all 256 IDs, verify exhaustion, configure an allocated ID, reject unallocated config/free, reject endianness on older SoCs, and validate downstream display/video behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-canvas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-clk-measure.c -->
# sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-clk-measure.c

## Purpose
This driver exposes Amlogic internal clock measurement hardware through debugfs. It supports multiple Meson SoC families by providing clock ID name tables and register layouts.

## Important APIs, Types, And Functions
Main types are `struct meson_msr_id`, `struct msr_reg_offset`, `struct meson_msr_data`, and `struct meson_msr`. Large static tables map measurement IDs to names for M8, GX, AXG, G12A, SM1, C3, and S4. `meson_measure_id()` performs one hardware measurement. `meson_measure_best_id()` retries with shorter gate durations if the counter saturates. `clk_msr_show()` and `clk_msr_summary_show()` implement debugfs files.

## Control Flow
Probe copies match-data tables into device-managed memory, maps the MMIO resource, initializes a regmap, copies the register offset description, creates `debugfs/meson-clk-msr`, a `measure_summary` file, and one file per named clock. Reading a file locks `measure_lock`, programs duration and clock source, enables measurement, polls until not busy, disables measurement, reads the value, computes Hz, and returns the result.

## State, Persistence, And Dependencies
State is per-device regmap, copied measurement table, and register-offset data. The debugfs tree is non-persistent. Dependencies include platform MMIO resources, regmap-mmio, debugfs, seq_file, field macros, and SoC-specific DT compatibles.

## Integration Points
The driver is diagnostics-only and does not register clocks. It is selected by `MESON_CLK_MEASURE` and binds to compatibles such as `amlogic,meson-gx-clk-measure`, `amlogic,c3-clk-measure`, and `amlogic,s4-clk-measure`.

## Risks
Debugfs entries are not explicitly removed by a remove callback, relying on device/module teardown behavior. Summary reads abort on the first failed clock measurement, so one bad source hides later results. Clock tables are hardware knowledge encoded in C arrays and can silently drift from vendor documentation.

## Test Signals
Probe each compatible, verify debugfs directory creation, read individual clock files, read summary, force saturation to exercise shorter durations, and validate measured rates against known parent clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-clk-measure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-gx-socinfo.c -->
# sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-gx-socinfo.c

## Purpose
This initcall decodes Amlogic Meson GX and newer SoC ID registers and registers a Linux `soc_device` with family, SoC/package ID, and revision strings.

## Important APIs, Types, And Functions
Static tables `soc_ids[]` and `soc_packages[]` map major/package fields to marketing names. Inline helpers extract major, minor, package, and misc fields from `socinfo`. `socinfo_to_soc_id()` and `socinfo_to_package_id()` perform table lookup. `meson_gx_socinfo_init()` does all registration.

## Control Flow
At device initcall time, the code finds the `amlogic,meson-gx-ao-secure` syscon node, verifies availability and `amlogic,has-chip-id`, obtains a regmap, reads `AO_SEC_SOCINFO_OFFSET`, allocates `soc_device_attribute`, formats revision and SoC ID strings, registers with `soc_device_register()`, and logs the detected chip.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated strings. Dependencies include OF, syscon/regmap, bitfield helpers, and `SOC_BUS`.

## Integration Points
Userspace sees the decoded information under sysfs soc device attributes. Other kernel paths may use soc_bus matching. The Kconfig option selects `SOC_BUS` and builds this bool driver on ARM64 Meson platforms.

## Risks
Unknown IDs fall back to `"Unknown"` rather than failing, which preserves boot but can reduce diagnostics. String allocation failures after `soc_dev_attr` allocation are not explicitly checked before registration. The table must be updated for new package IDs.

## Test Signals
Boot on known GX/G12/SM/C/S parts, inspect `/sys/devices/soc*`, verify unknown-ID fallback, and test missing/disabled/no-chip-id DT nodes returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-gx-socinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-mx-socinfo.c -->
# sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-mx-socinfo.c

## Purpose
This initcall decodes older Amlogic Meson MX-family SoC identity from assist, bootrom, and optional analog-top syscon registers and registers it with soc_bus.

## Important APIs, Types, And Functions
`meson_mx_socinfo_revision()` maps major, misc, and metal revision values to revision strings. `meson_mx_socinfo_soc_id()` maps major and metal revision to SoC ID strings. `meson_mx_socinfo_init()` performs syscon lookup, register reads, root model lookup, attribute allocation, and registration.

## Control Flow
The initcall obtains regmaps by compatibles for assist and bootrom. It optionally reads the analog-top metal revision if a matching node exists. Then it reads the hardware revision and misc version, allocates attributes, copies the root `model` property into `machine`, formats revision and SoC ID strings, registers the soc device, and logs the result.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated strings. Dependencies include syscon/regmap, OF, `SOC_BUS`, and ARM Meson platform configuration.

## Integration Points
It supplies userspace-visible SoC metadata for Meson6, Meson8, Meson8b, and Meson8m2 platforms. It complements the GX socinfo driver for newer ARM64 parts.

## Risks
String allocation failures are not checked before `soc_device_register()`. If analog-top exists but regmap/read fails, init aborts even though base identity could be available. Unknown revisions are normalized to generic or unknown strings.

## Test Signals
Boot on Meson6, Meson8, Meson8b, and Meson8m2 DTs, inspect soc_bus attributes, test missing syscon compatibles, and verify metal revision branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-mx-socinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/Kconfig

## Purpose
This file defines Apple SoC support options for mailbox IPC, RTKit protocol support, SART DMA filtering, and hardware tunables.

## Important APIs, Types, And Functions
Symbols are `APPLE_MAILBOX`, `APPLE_RTKIT`, `APPLE_SART`, and `APPLE_TUNABLE`. `APPLE_RTKIT` depends on `APPLE_MAILBOX`; `APPLE_MAILBOX` depends on PM and 64-bit compile-test support; SART and tunable depend on Apple architecture or compile-test.

## Control Flow
The whole Apple menu is gated by `ARCH_APPLE || COMPILE_TEST`. Selecting options controls whether the corresponding module objects are built by the Apple Makefile.

## State, Persistence, And Dependencies
Configuration is persisted in `.config`. Dependencies model RTKit's mailbox requirement and platform/compile-test availability.

## Integration Points
Apple NVMe, display, and coprocessor client drivers rely on these support libraries when enabled.

## Risks
If RTKit clients can be enabled without `APPLE_RTKIT`, link or probe failures occur elsewhere. Keeping `APPLE_TUNABLE` tristate but promptless means only dependent drivers should select it.

## Test Signals
Run Apple defconfig and COMPILE_TEST builds, confirm dependency propagation, and verify `APPLE_RTKIT=m` pulls in mailbox availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/Makefile

## Purpose
This Makefile builds Apple SoC support modules from one or more implementation files.

## Important APIs, Types, And Functions
It creates `apple-mailbox.o` from `mailbox.o`, `apple-rtkit.o` from `rtkit.o` and `rtkit-crashlog.o`, `apple-sart.o` from `sart.o`, and `apple-tunable.o` from `tunable.o`.

## Control Flow
Kbuild includes each composite object based on its `CONFIG_APPLE_*` symbol. Composite object variables collect implementation files for module or built-in linking.

## State, Persistence, And Dependencies
Build state is determined by Kconfig. There is no runtime state.

## Integration Points
This file is reached from `drivers/soc/Makefile` through unconditional Apple directory recursion.

## Risks
Composite object names must match module expectations and exported symbols. If `rtkit-crashlog.o` is omitted, RTKit crash handling would fail to link.

## Test Signals
Build all Apple options as modules and built-ins and confirm generated module names and symbol exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.c

## Purpose
This driver implements the low-level Apple mailbox FIFO used for 96-bit messages between the application processor and Apple coprocessors. It supports ASC, T8015 ASC, and M3 register layouts.

## Important APIs, Types, And Functions
`struct apple_mbox_hw` describes register offsets, status bits, and optional mailbox-level IRQ controls. Exported APIs are `apple_mbox_get()`, `apple_mbox_get_byname()`, `apple_mbox_start()`, `apple_mbox_stop()`, `apple_mbox_poll()`, and `apple_mbox_send()`. IRQ handlers are `apple_mbox_recv_irq()` and `apple_mbox_send_empty_irq()`.

## Control Flow
Probe maps registers, requests named `recv-not-empty` and `send-empty` IRQs with `IRQF_NO_AUTOEN`, enables runtime PM, and stores driver data. Consumers get a mailbox via DT phandle, set `rx` and `cookie`, and start it. Sending takes the TX lock, waits for A2I FIFO space either by atomic polling or send-empty completion, writes message words, and returns. Receive IRQs poll I2A messages under RX lock and invoke the consumer callback.

## State, Persistence, And Dependencies
State is `struct apple_mbox`: MMIO registers, active flag, IRQ numbers, locks, TX completion, and callback pointer. Dependencies include OF phandles, platform IRQs, runtime PM, spinlocks, iopoll, and MMIO read/write access.

## Integration Points
RTKit is the primary in-tree consumer. Device links bind consumer lifetime to the mailbox provider. Hardware match data selects register layout for Apple compatibles.

## Risks
The driver assumes callbacks are installed before start; a NULL `rx` would crash on incoming messages. The send path uses level-triggered IRQ behavior carefully, but incorrect ack order on new hardware could cause missed or repeated wakeups. Runtime PM is active only while started.

## Test Signals
Test blocking and atomic sends when FIFO is full, receive polling and IRQ paths, runtime PM transitions on start/stop, M3 IRQ-ack behavior, phandle deferral, and RTKit boot traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.h -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.h

## Purpose
This private Apple mailbox header declares the message format, mailbox state, and exported mailbox helper APIs used by Apple coprocessor protocol drivers.

## Important APIs, Types, And Functions
`struct apple_mbox_msg` encodes a 64-bit `msg0` and 32-bit `msg1`. `struct apple_mbox` stores device/MMIO/hardware data, active state, IRQs, RX/TX locks, TX completion, and the receive callback. Function declarations cover mailbox lookup, start/stop, polling, and sending.

## Control Flow
The header defines the callback control contract: users install `mbox->rx` and `mbox->cookie`, call `apple_mbox_start()`, then receive callbacks for incoming FIFO messages. Outgoing messages flow through `apple_mbox_send()`.

## State, Persistence, And Dependencies
State is runtime-only and owned by `mailbox.c`. The header depends on Linux device and type definitions.

## Integration Points
Included by Apple RTKit and mailbox implementation files. It is private to the Apple SoC driver folder rather than a public mailbox framework API.

## Risks
The exposed `struct apple_mbox` lets consumers mutate callbacks and state directly, so concurrent consumers are not supported. It does not encode ownership beyond DT device links.

## Test Signals
Compile coverage for RTKit and mailbox, plus runtime tests that install callbacks before start and validate send/receive message field preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-crashlog.c -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-crashlog.c

## Purpose
This file parses and dumps Apple RTKit crashlog buffers after a coprocessor crash.

## Important APIs, Types, And Functions
It defines crashlog fourcc constants, packed/on-wire structs for headers, mailbox history, and register dumps, and a single exported-to-folder function `apple_rtkit_crashlog_dump()`. Helpers dump string, version, time, mailbox, and register sections.

## Control Flow
`apple_rtkit_crashlog_dump()` copies and validates the crashlog header, clamps parsing to the declared size, then walks sections. Each section dispatches by fourcc to a decoder. A repeated header marks end-of-log. Unknown sections are logged and skipped by their section size.

## State, Persistence, And Dependencies
The function is stateless and operates on a shadow buffer supplied by `rtkit.c`. It depends on RTKit internal state for device logging and on ARM64 PSR mode constants, with fallback defines for compile-test on other architectures.

## Integration Points
`apple_rtkit_crashlog_rx()` copies crashlog shared memory into normal memory and calls this decoder before notifying client `crashed` callbacks.

## Risks
Parsing trusts section headers enough to add `section_size` to `offset`; malformed zero or undersized section sizes could cause poor progress or reading beyond section payload intent. Most strings are printed directly from firmware-provided buffers, relying on crashlog format to include termination. It logs sensitive register/message history to the kernel log.

## Test Signals
Feed valid crashlogs with every section type, unknown sections, truncated headers, oversized declared size, too-small regs section, footer present/missing, and malformed section sizes under KUnit or targeted fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-crashlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-internal.h -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-internal.h

## Purpose
This private header defines internal Apple RTKit state shared between the protocol implementation and crashlog parser.

## Important APIs, Types, And Functions
It defines endpoint constants and `struct apple_rtkit`, which stores client cookie/ops, device, mailbox, completions, boot result, protocol version, AP/IOP power states, crash flag, endpoint bitmap, shared memory buffers for ioreport/crashlog/oslog/syslog, syslog sizing, and workqueue. It declares `apple_rtkit_crashlog_dump()`.

## Control Flow
The struct fields are used by RTKit boot, endpoint discovery, mailbox RX work dispatch, shared-memory request handling, power-state transitions, and crash notification.

## State, Persistence, And Dependencies
All state is in memory and scoped to an RTKit instance. Dependencies include completions, bitmaps, DMA mapping, workqueues, the public RTKit header, and the Apple mailbox header.

## Integration Points
Only Apple RTKit implementation files should include this header. Client drivers use the public `linux/soc/apple/rtkit.h` APIs instead.

## Risks
This is the central synchronization state for RTKit. Missing locks around some state fields rely on ordered workqueue and lifecycle sequencing. Direct sharing between implementation files means structure changes must be coordinated carefully.

## Test Signals
Compile RTKit and crashlog together, exercise boot/reinit/free, and use concurrency tests around mailbox RX during reinit/shutdown to validate assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit.c -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit.c

## Purpose
This file implements the Apple RTKit IPC protocol library used by client drivers to communicate with Apple coprocessors over the Apple mailbox and shared memory buffers.

## Important APIs, Types, And Functions
Exports include `apple_rtkit_init()`, `devm_apple_rtkit_init()`, `apple_rtkit_free()`, `apple_rtkit_boot()`, `apple_rtkit_shutdown()`, `apple_rtkit_poweroff()`, `apple_rtkit_idle()`, `apple_rtkit_quiesce()`, `apple_rtkit_wake()`, `apple_rtkit_start_ep()`, `apple_rtkit_send_message()`, `apple_rtkit_poll()`, `apple_rtkit_is_running()`, and `apple_rtkit_is_crashed()`. Key internal handlers cover management hello/endpoint map/power acks, shared buffer requests, crashlog, ioreport, syslog, oslog, and RX work dispatch.

## Control Flow
Initialization obtains a mailbox, installs the RX callback, creates an ordered high-priority workqueue, and starts the mailbox. RX callback checks endpoint discovery, optionally lets clients handle app endpoints early, then queues work. Management hello negotiates protocol version. Endpoint-map messages set endpoint bits, start required system endpoints, and complete boot discovery. Boot waits for endpoint map and IOP power ACK, then sets AP power on. Send paths enforce crash/running checks for application endpoints and use DMA barriers before mailbox writes. Shutdown, idle, quiesce, poweroff, and wake are implemented as AP/IOP power-state message exchanges plus optional reinitialization.

## State, Persistence, And Dependencies
State includes endpoint bitmap, completions, version, boot result, AP/IOP power states, crash flag, shared-memory buffers, syslog buffer, and ordered workqueue. Dependencies include the Apple mailbox, DMA coherent memory or client `shmem_setup`/`shmem_destroy`, completions, bitfield macros, and public client ops.

## Integration Points
Client drivers provide `struct apple_rtkit_ops` callbacks for receiving messages, early handling, shared memory setup, and crash notification. RTKit manages system endpoints internally and passes application endpoints from `0x20` upward to clients.

## Risks
Shared state is largely protected by sequencing rather than locks; RX work during reinit is handled by stopping mailbox and flushing the workqueue. `apple_rtkit_common_rx_get_buffer()` trusts firmware-requested sizes and relies on DMA allocation or client validation. Syslog index check uses `idx > n_entries`, which may allow `idx == n_entries`. Failure to allocate RX work silently drops messages. Crash state blocks later sends.

## Test Signals
Test protocol version negotiation, endpoint map pagination, system endpoint startup, boot timeouts, AP/IOP power-state transitions, app endpoint send gating, shared memory request paths with and without client mapping, syslog log entries, crashlog copy and callback, reinit during traffic, and mailbox poll fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/sart.c -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/sart.c

## Purpose
This driver manages Apple SART DMA address filters. It lets client drivers add or remove physical memory ranges that coprocessors may access when a full IOMMU is not used.

## Important APIs, Types, And Functions
`struct apple_sart_ops` abstracts SART v0, v2, and v3 register encodings. `struct apple_sart` stores device, MMIO, ops, protected entries, and used entries. Exports are `devm_apple_sart_get()`, `apple_sart_add_allowed_region()`, and `apple_sart_remove_allowed_region()`. Version-specific helpers get/set entries.

## Control Flow
Probe maps registers, selects ops from DT match data, scans all 16 entries, and marks bootloader-populated entries as protected. Clients get the provider through the `apple,sart` phandle. Adding a region skips protected and used entries, atomically claims a free bit, validates alignment/size, writes allow flags/address/size, and returns. Removing scans non-protected entries for exact address and size, clears the hardware entry, and clears the used bit. Shutdown clears all non-protected entries.

## State, Persistence, And Dependencies
Persistent hardware state exists in SART registers; software mirrors protected and used entries in bitmaps. Dependencies include platform MMIO, OF phandles, device links, bit operations, and public SART header definitions.

## Integration Points
Apple NVMe and other coprocessor clients use SART to permit DMA buffers. Bootloader entries remain protected to avoid breaking firmware-reserved mappings.

## Risks
`sart_set_entry()` shifts `paddr` by `size_shift` and `size` by `paddr_shift`; current values match, but the naming is error-prone if future variants differ. There is no mutex around used-entry scanning beyond atomic bit operations; duplicate exact mappings are possible if clients request the same region. Device link return is not checked. Exact match is required for removal.

## Test Signals
Probe all SART compatibles, preserve bootloader entries, add aligned and reject unaligned regions, exhaust 16 entries, remove exact regions, ensure protected entries survive shutdown, and validate client DMA succeeds only with allowed ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/sart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/tunable.c -->
# sources/distributed-fs/ceph-client/drivers/soc/apple/tunable.c

## Purpose
This helper parses and applies Apple Silicon hardware tunables supplied by firmware or boot stages through device tree properties.

## Important APIs, Types, And Functions
Exports are `devm_apple_tunable_parse()` and `apple_tunable_apply()`. The public `struct apple_tunable` contains entries with MMIO offset, mask, and value.

## Control Flow
Parsing validates the MMIO resource is at least one word, finds the named DT property, requires property length to be triples of 32-bit values, allocates a flexible-array tunable, reads offset/mask/value triples, and rejects unaligned or out-of-resource offsets. Applying iterates entries, reads the current register value, clears masked bits, ORs the desired value, and writes only when changed.

## State, Persistence, And Dependencies
State is a device-managed parsed tunable object. Hardware persistence is whatever register effects the writes have. Dependencies include OF property helpers, overflow-safe `struct_size()`, MMIO read/write, and a public tunable header.

## Integration Points
Apple platform drivers can parse device-specific register adjustments and apply them after mapping hardware registers.

## Risks
The parser does not validate that `value` is contained within `mask`; it will set any bits present in value. Applying is not locked, so drivers must serialize against other register programming. Incorrect firmware properties can alter hardware behavior broadly despite offset range checks.

## Test Signals
Test missing property, malformed length, offset alignment, offset beyond resource, successful parse, idempotent apply, and value/mask interactions on a fake MMIO region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/apple/tunable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/aspeed/Kconfig

## Purpose
This file defines ASPEED SoC support options for LPC control, LPC snoop, UART routing, P2A bridge control, and SoC information.

## Important APIs, Types, And Functions
Symbols include `ASPEED_LPC_CTRL`, `ASPEED_LPC_SNOOP`, `ASPEED_UART_ROUTING`, `ASPEED_P2A_CTRL`, and `ASPEED_SOCINFO`. Most driver options select `REGMAP` and `MFD_SYSCON`; socinfo selects `SOC_BUS`.

## Control Flow
The menu is available for `ARCH_ASPEED` or `COMPILE_TEST`. Driver options default to `ARCH_ASPEED`, making common BMC features enabled on ASPEED builds.

## State, Persistence, And Dependencies
Configuration choices persist in `.config`. Dependencies reflect syscon/regmap use and soc_bus registration.

## Integration Points
The ASPEED Makefile maps these symbols to the corresponding driver objects.

## Risks
`ASPEED_SOCINFO` contains duplicate `default ARCH_ASPEED`, which is harmless but redundant. Broad defaults can increase built-in surface on ASPEED platforms.

## Test Signals
Run ASPEED defconfig and COMPILE_TEST builds, inspect selected dependencies, and confirm each option produces its expected object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/aspeed/Makefile

## Purpose
This Makefile maps ASPEED SoC configuration symbols to object files.

## Important APIs, Types, And Functions
Object entries are `aspeed-lpc-ctrl.o`, `aspeed-lpc-snoop.o`, `aspeed-uart-routing.o`, `aspeed-p2a-ctrl.o`, and `aspeed-socinfo.o`.

## Control Flow
Kbuild includes objects according to `CONFIG_ASPEED_*` values. There is no runtime flow.

## State, Persistence, And Dependencies
Build state is determined by `.config` symbols from the ASPEED Kconfig file.

## Integration Points
Reached from `drivers/soc/Makefile` via ASPEED directory recursion.

## Risks
Symbol/object mismatches would break selected driver builds. Direct single-object mappings are otherwise low complexity.

## Test Signals
Build each ASPEED option as module or built-in where supported and verify expected outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-ctrl.c

## Purpose
This miscdevice driver controls ASPEED LPC firmware/memory windows from host LPC space to BMC memory or flash and exposes an mmap interface for the reserved BMC memory buffer.

## Important APIs, Types, And Functions
`struct aspeed_lpc_ctrl` stores the miscdevice, LPC regmap, clock, reserved memory, PNOR flash info, AST2600 FWH2AHB state, and SCU regmap. File operations are `aspeed_lpc_ctrl_mmap()` and `aspeed_lpc_ctrl_ioctl()`. IOCTLs include `ASPEED_LPC_CTRL_IOCTL_GET_SIZE` and `ASPEED_LPC_CTRL_IOCTL_MAP`.

## Control Flow
Probe records optional flash resource and reserved-memory resource, validates reserved memory is power-of-two and naturally aligned, gets the parent LPC syscon regmap, handles AST2600 SCU setup, enables the clock, and registers `/dev/aspeed-lpc-ctrl`. GET_SIZE returns reserved memory size. MAP validates flags, window type, size/offset alignment, offset within flash or memory, programs HICR7/HICR8 mapping registers, optionally enables AST2600 FWH2AHB, and enables LPC firmware cycles.

## State, Persistence, And Dependencies
State lives in hardware registers and the miscdevice struct. Dependencies include parent LPC syscon, optional flash phandle, optional reserved memory, clocks, miscdevice, mmap, usercopy, and ASPEED LPC ioctl UAPI.

## Integration Points
Userspace controls host-visible LPC windows and maps BMC reserved memory. This binds as a child of the ASPEED LPC syscon node.

## Risks
The IOCTL copies the mapping struct before checking command, so unknown commands still require a readable user pointer. There is no explicit serialization around HICR register updates. Host exposure of BMC memory/flash is security-sensitive and relies on userspace permissions and DT region constraints. FWH2AHB programming is AST2600-specific.

## Test Signals
Probe with/without flash and reserved memory, reject invalid memory geometry, test GET_SIZE, MAP for flash and memory, mmap range checks, AST2600 FWH2AHB path, and host LPC read/write validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-snoop.c -->
# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-snoop.c

## Purpose
This driver captures host writes to configured LPC I/O ports, commonly BIOS port 0x80 progress codes, and exposes captured bytes through per-channel miscdevices.

## Important APIs, Types, And Functions
State is split across `struct aspeed_lpc_snoop`, `struct aspeed_lpc_snoop_channel`, and static channel configs. File operations provide blocking/nonblocking `read`, `poll`, and no seek. IRQ handling is in `aspeed_lpc_snoop_irq()`. Setup helpers include `aspeed_lpc_enable_snoop()` and `aspeed_lpc_disable_snoop()`.

## Control Flow
Probe validates the parent LPC compatible, obtains the syscon regmap and clock, requests the shared IRQ, reads `snoop-ports` DT entries, and enables one or two channels. Each enabled channel allocates a 2048-byte kfifo, registers a miscdevice, programs the snoop port, enables channel interrupts, and optionally sets HICRB enable bits on newer SoCs. IRQ reads pending status, acknowledges it, reads the snooped data byte, pushes it into the channel FIFO discarding oldest on overflow, and wakes readers.

## State, Persistence, And Dependencies
Runtime state includes channel enabled flags, kfifo contents, wait queues, and LPC hardware registers. Dependencies include regmap/syscon, clocks, IRQs, miscdevice, kfifo, poll, and DT `snoop-ports`.

## Integration Points
Userspace reads `/dev/aspeed-lpc-snoop0` and `/dev/aspeed-lpc-snoop1`. The driver binds as a child of ASPEED LPC syscon and uses model data to decide HICRB support.

## Risks
The remove path comments that concurrent reader safety could improve; misc deregistration and FIFO free can race with open readers. FIFO overflow discards old data by design. If no `snoop-ports` entries exist, probe returns `-ENODEV`. Shared IRQ handling returns `IRQ_NONE` when no snoop bit is set.

## Test Signals
Generate LPC writes to configured ports, read blocking and nonblocking devices, poll readiness, verify FIFO discard on overflow, test one-channel and two-channel DTs, remove with open files, and compare AST2400 versus AST2500/2600 HICRB behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-snoop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-p2a-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-p2a-ctrl.c

## Purpose
This miscdevice driver controls ASPEED P2A, a VGA MMIO-to-BMC bridge that lets the host access selected BMC memory regions.

## Important APIs, Types, And Functions
`struct aspeed_p2a_ctrl` tracks miscdevice, SCU regmap, model region config, a mutex-protected reader/readwriter reference model, and optional reserved memory for mmap. `struct aspeed_p2a_user` tracks per-open references. Key functions are `aspeed_p2a_ioctl()`, `aspeed_p2a_mmap()`, `aspeed_p2a_region_acquire()`, `aspeed_p2a_open()`, and `aspeed_p2a_release()`.

## Control Flow
Probe maps optional reserved memory, obtains parent syscon regmap, selects AST2400/AST2500 region model data, disables all P2A regions and bridge, then registers `/dev/aspeed-p2a-ctrl`. Open allocates per-file tracking. SET_WINDOW either increments read-only bridge usage or maps requested address ranges to read-write by clearing model-specific SCU2C bits for matching regions, then enables the bridge. GET_MEMORY_CONFIG returns mmap base/size. Release decrements per-file references, disables no-longer-used regions, and disables the bridge when no reader or open region remains.

## State, Persistence, And Dependencies
State is SCU bridge/region register bits plus kernel reference counters. Dependencies include miscdevice, mutex, usercopy, mmap, syscon/regmap, reserved memory, and ASPEED P2A ioctl UAPI.

## Integration Points
Userspace requests host access windows and may mmap the reserved BMC memory buffer. Region definitions encode AST2400 and AST2500 address maps.

## Risks
`map.addr + (map.length - 1)` can underflow when length is zero and overflow is not checked, potentially producing misleading region matching. Reference counters are `u32` and can wrap under repeated IOCTL calls. `remove()` deregisters the miscdevice but does not explicitly disable all regions. Exposing BMC memory to a host is security-sensitive.

## Test Signals
Test read-only and read-write window setup, zero-length and overflow requests, multi-open reference release, mmap bounds, bridge disable after final close, region coverage for AST2400/AST2500, and removal while mapped/open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-p2a-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-socinfo.c -->
# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-socinfo.c

## Purpose
This early initcall decodes ASPEED silicon ID and optional chip ID registers and registers a soc_bus device describing the BMC SoC.

## Important APIs, Types, And Functions
`rev_table[]` maps silicon IDs to SoC names. `siliconid_to_name()` masks package/revision bits to find the family name. `siliconid_to_rev()` maps generation/revision fields to A0/A1/A2/A3 strings. `aspeed_socinfo_init()` performs OF lookup, MMIO reads, attribute allocation, and registration.

## Control Flow
At early init, it finds the `aspeed,silicon-id` node, verifies availability, maps resource 0 to read silicon ID, optionally maps resource 1 to read the 64-bit chip ID, reads the root model property, allocates soc attributes, formats ID and serial strings, registers a `soc_device`, and logs the result.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated strings. Dependencies include OF, ioremap from DT resources, sys_soc, and early init ordering.

## Integration Points
Userspace gets machine, family, revision, soc_id, and optional serial number through soc_bus sysfs. Other drivers may use soc_device matching.

## Risks
The code calls `of_device_is_available(np)` without checking whether `np` is NULL, which relies on helper tolerance. Unknown IDs are reported as `"Unknown"` and `"??"`. Allocation failures return `-ENODEV` instead of `-ENOMEM`.

## Test Signals
Boot AST2400/2500/2600/2700 systems, inspect soc_bus attributes, test optional chipid absence, unknown silicon IDs, disabled node behavior, and early init ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-socinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-uart-routing.c -->
# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-uart-routing.c

## Purpose
This driver exposes ASPEED UART routing muxes through sysfs so users can select UART RX/TX path connections among UART controllers and I/O pins at runtime.

## Important APIs, Types, And Functions
`struct aspeed_uart_routing` stores the parent syscon regmap and selected attribute group. `struct aspeed_uart_routing_selector` binds a sysfs attribute to a register, mask, shift, and option string array. `aspeed_uart_routing_show()` displays current option with brackets. `aspeed_uart_routing_store()` validates and writes a selected option.

## Control Flow
Static selector tables describe AST2500 and AST2600 routing choices. Probe gets the parent regmap, selects an attribute group from match data, creates the sysfs group, and stores driver data. Reads decode the selector field and print all choices. Writes match the provided string against the options array and update the relevant register bits.

## State, Persistence, And Dependencies
State is the hardware routing registers and sysfs attributes. Dependencies include platform device, parent syscon/regmap, OF match data, and sysfs device attributes.

## Integration Points
Userspace configures routes through attributes named like `io1`, `uart1`, and `uart10`. The driver binds to ASPEED UART-routing child nodes for AST2400/2500/2600.

## Risks
`dev_set_drvdata()` is called after `sysfs_create_group()`, so a very early sysfs read could see NULL drvdata. Reserved options are exposed as selectable strings where present. There is no higher-level validation to prevent conflicting routes. Remove uses `platform_get_drvdata()` even though probe used `dev_set_drvdata()`, which is equivalent for platform devices but worth noting.

## Test Signals
Read every sysfs attribute, write all valid options, reject invalid strings, verify register fields, test AST2500 and AST2600 groups, and stress concurrent sysfs writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-uart-routing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/atmel/Kconfig

## Purpose
This file defines Atmel/Microchip AT91 SoC support options for soc_bus identification and Special Function Register support.

## Important APIs, Types, And Functions
Symbols are `AT91_SOC_ID` and `AT91_SOC_SFR`. `AT91_SOC_ID` is a bool defaulting to `ARCH_AT91`; `AT91_SOC_SFR` is a tristate driver for SAMA5Dx SFR access.

## Control Flow
Kconfig exposes these options when `ARCH_AT91` or `COMPILE_TEST` is enabled. Selections drive the Atmel Makefile object list.

## State, Persistence, And Dependencies
Configuration persists in `.config`. `AT91_SOC_ID` affects early/subsys init registration; `AT91_SOC_SFR` affects module or built-in SFR/NVMEM support.

## Integration Points
These symbols build `soc.o` and `sfr.o`.

## Risks
`AT91_SOC_SFR` help mentions the module name `sfr`, while Kbuild object naming under the Atmel folder determines the actual module path. Dependencies are broad for compile testing.

## Test Signals
Check AT91 defconfigs, allmodconfig module naming, and COMPILE_TEST builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/atmel/Makefile

## Purpose
This Makefile maps Atmel/Microchip AT91 SoC options to object files.

## Important APIs, Types, And Functions
`obj-$(CONFIG_AT91_SOC_ID) += soc.o` and `obj-$(CONFIG_AT91_SOC_SFR) += sfr.o`.

## Control Flow
Kbuild includes each object according to the selected config symbol.

## State, Persistence, And Dependencies
Build state comes from `.config`. There is no runtime state.

## Integration Points
Reached conditionally from `drivers/soc/Makefile` when `CONFIG_ARCH_AT91` is enabled.

## Risks
If `AT91_SOC_SFR` is enabled only through COMPILE_TEST but parent directory recursion is gated by `ARCH_AT91`, it may not build from the top-level Makefile unless another path recurses into atmel. That coupling should be kept in mind when changing recursion rules.

## Test Signals
Build AT91 defconfig and COMPILE_TEST configurations that enable each symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/sfr.c -->
# sources/distributed-fs/ceph-client/drivers/soc/atmel/sfr.c

## Purpose
This driver exposes Atmel SAMA5D2/SAMA5D4 Special Function Register serial-number words through NVMEM and feeds them into kernel randomness.

## Important APIs, Types, And Functions
`struct atmel_sfr_priv` holds the SFR regmap. `atmel_sfr_read()` reads from `SFR_SN0 + offset` with 32-bit stride. `atmel_sfr_nvmem_config` describes an 8-byte read-only NVMEM provider. `atmel_sfr_probe()` registers the provider and adds serial number bytes to randomness.

## Control Flow
Probe allocates private state, obtains a regmap from the node syscon, fills config `dev` and `priv`, registers NVMEM, reads the full serial number, and calls `add_device_randomness()` if the read succeeds.

## State, Persistence, And Dependencies
State is device-managed private data and the NVMEM registration. Hardware serial registers persist in SoC SFRs. Dependencies include syscon/regmap, NVMEM provider framework, OF/platform binding, and randomness API.

## Integration Points
Consumers can read the serial number through NVMEM. The driver binds to `atmel,sama5d2-sfr` and `atmel,sama5d4-sfr`.

## Risks
The global `atmel_sfr_nvmem_config` is mutated at probe time, which is not ideal for multiple instances. `atmel_sfr_read()` divides bytes by 4 and relies on NVMEM stride/word-size alignment. Returning the serial read result from probe can fail binding if randomness read fails after NVMEM registration.

## Test Signals
Probe both compatibles, read NVMEM bytes, verify regmap bulk read offsets, test error propagation from regmap and NVMEM registration, and check randomness path does not break probe unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/sfr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.c

## Purpose
This file identifies Atmel/Microchip AT91-family SoCs from CIDR/EXID registers and registers a soc_bus device.

## Important APIs, Types, And Functions
The `socs[]` table, built conditionally by SoC family config symbols, maps CIDR masks, version masks, EXID values, names, and families. `at91_get_cidr_exid_from_dbgu()` reads legacy DBGU ID registers. `at91_get_cidr_exid_from_chipid()` reads newer chipid nodes. `at91_soc_init()` performs matching and registration. `atmel_soc_device_init()` gates registration to allowed root compatibles.

## Control Flow
At subsys init, the root node is checked against allowed AT91/Microchip compatibles. The code first tries legacy DBGU, then chipid nodes. It scans `socs[]` for a CIDR mask match and, when CIDR indicates extended ID, an EXID match. On success it allocates attributes, formats revision from the configured version mask, registers the soc device, and logs family/name/revision.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated revision string. Dependencies include OF, MMIO mapping, conditional compile symbols for SoC families, and `SOC_BUS`.

## Integration Points
This provides userspace and kernel soc_bus identity for AT91RM9200, AT91SAM9, SAM9X60, SAM9X7, SAMA5, SAMV7, SAMA7D6, and SAMA7G5 variants.

## Risks
The table is large and conditionally compiled, so missing config coverage can make a supported SoC unidentifiable. Some SAM9X7 entries appear to pass EXID values as CIDR masks, which should be checked against intended matching semantics. Failure returns NULL rather than detailed errno from `at91_soc_init()`.

## Test Signals
Boot every supported family, verify soc_bus attributes and revision masks, test legacy DBGU and chipid paths, unknown CIDR/EXID fallback, and configuration combinations that include/exclude table blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.h -->
# sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.h

## Purpose
This header defines AT91 SoC identification table structures and constants used by `soc.c`.

## Important APIs, Types, And Functions
`struct at91_soc` contains CIDR match/mask, version mask, EXID match, name, and family. `AT91_SOC()` builds table entries. The header declares `at91_soc_init()` and defines CIDR/EXID constants for many AT91, SAMA5, SAMA7, SAM9X, SAME/SAMS/SAMV devices.

## Control Flow
There is no runtime flow in the header. Constants feed the table scan in `soc.c`, where CIDR and EXID values select a matching SoC descriptor.

## State, Persistence, And Dependencies
The header has no persistent state. It depends on `linux/sys_soc.h` for `struct soc_device`.

## Integration Points
Used by Atmel SoC identification code and potentially other AT91 code that wants the init declaration.

## Risks
Identity constants are hardware facts; typos can cause wrong soc_bus names. The macro positional arguments make mistakes easy, especially because masks and matches are both `u32`.

## Test Signals
Compile `soc.c`, verify every table entry maps to the intended CIDR/EXID, and compare constants with datasheets or known boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/Kconfig

## Purpose
This file defines the Broadcom SoC driver menu and the top-level `SOC_BRCMSTB` option for Broadcom set-top-box SoCs.

## Important APIs, Types, And Functions
The key symbol is `SOC_BRCMSTB`, which depends on `ARCH_BRCMSTB`, `BMIPS_GENERIC`, or `COMPILE_TEST` and selects `SOC_BUS`. The file also sources the `brcmstb/Kconfig` submenu.

## Control Flow
Kconfig presents the Broadcom menu, then loads brcmstb-specific options. Enabling `SOC_BRCMSTB` permits child options such as PM support.

## State, Persistence, And Dependencies
Configuration persists in `.config`. Dependencies model Broadcom STB architecture support and soc_bus registration.

## Integration Points
The Broadcom Makefile recurses into `brcmstb/` when `SOC_BRCMSTB` is enabled.

## Risks
The top-level option says it enables support code while individual drivers are selected separately, so user expectations depend on submenu clarity. If `SOC_BUS` behavior changes, this option affects all brcmstb support.

## Test Signals
Run BRCMSTB and BMIPS defconfigs and check menu visibility, selected `SOC_BUS`, and child menu availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/Makefile

## Purpose
This Makefile conditionally descends into the Broadcom STB SoC driver directory.

## Important APIs, Types, And Functions
It contains one object-directory rule: `obj-$(CONFIG_SOC_BRCMSTB) += brcmstb/`.

## Control Flow
Kbuild recurses into `brcmstb/` only when `SOC_BRCMSTB` is enabled.

## State, Persistence, And Dependencies
Build state is determined by `.config`. There is no runtime behavior.

## Integration Points
It is included from the top-level SoC Makefile and pairs with `drivers/soc/bcm/Kconfig`.

## Risks
If a brcmstb child option is selected without `SOC_BRCMSTB`, objects will not build. Current Kconfig gates child options under `SOC_BRCMSTB`.

## Test Signals
Build with `SOC_BRCMSTB=y` and `n`, and confirm brcmstb objects appear only when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Kconfig

## Purpose
This file defines Broadcom STB suspend/resume support configuration.

## Important APIs, Types, And Functions
The symbol is `BRCMSTB_PM`, a bool defaulting to yes when visible. It depends on `PM` and `BMIPS_GENERIC` and is enclosed by `if SOC_BRCMSTB`.

## Control Flow
When `SOC_BRCMSTB` is enabled, Kconfig exposes `BRCMSTB_PM` only on BMIPS systems with PM support. The brcmstb Makefile uses it to include the `pm/` directory.

## State, Persistence, And Dependencies
Configuration persists in `.config`. Dependencies ensure PM code is only built for supported BMIPS generic platforms.

## Integration Points
Controls Broadcom STB platform suspend/resume code under `drivers/soc/bcm/brcmstb/pm/`.

## Risks
Default-y platform PM support can change suspend/resume behavior broadly on eligible systems. ARM/ARM64 BRCMSTB builds do not see this option due to `BMIPS_GENERIC` dependency.

## Test Signals
Check BMIPS generic PM builds, suspend/resume smoke tests, and verify non-BMIPS BRCMSTB configs do not select this option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Makefile

## Purpose
This Makefile builds Broadcom STB common support and optional PM support.

## Important APIs, Types, And Functions
It unconditionally includes `common.o` and `biuctrl.o` when the brcmstb directory is built, and conditionally includes `pm/` for `CONFIG_BRCMSTB_PM`.

## Control Flow
Kbuild reaches this file only when `SOC_BRCMSTB` is enabled. It then builds common STB support and optional suspend/resume code.

## State, Persistence, And Dependencies
Build state comes from `SOC_BRCMSTB` and `BRCMSTB_PM`.

## Integration Points
Works with the Broadcom Kconfig hierarchy to compile shared brcmstb SoC code and PM support.

## Risks
Unconditional common object build means `common.o` and `biuctrl.o` must be valid for every `SOC_BRCMSTB` configuration. Missing PM directory coverage would break only when `BRCMSTB_PM` is enabled.

## Test Signals
Build with `SOC_BRCMSTB=y` and `BRCMSTB_PM` both enabled and disabled, and verify expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Makefile -->
