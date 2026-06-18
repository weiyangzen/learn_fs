# subset-b-005167 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3av.c -->
# sources/distributed-fs/ceph-client/drivers/ps3/ps3av.c Research

## Purpose
`ps3av.c` is the PS3 AV settings backend driver. It binds to the PS3 virtual UART AV settings device, initializes the AV backend, discovers hardware ports, chooses an initial video mode, and exports helper APIs used by PS3 framebuffer/audio code to set video mode, audio mode, mute state, and query mode geometry.

## Important APIs, Types, And Functions
The central private state is `struct ps3av`, a singleton containing the VUART device, mutex, asynchronous mode-setting work item, completion, detected region, hardware configuration, AV/optical/head port arrays, active mode, previous mode, and a 512-byte receive buffer. Public exports include `ps3av_do_pkt()`, `ps3av_set_video_mode()`, `ps3av_get_auto_mode()`, `ps3av_get_mode()`, `ps3av_video_mode2res()`, `ps3av_video_mute()`, `ps3av_audio_mute_analog()`, `ps3av_audio_mute()`, and `ps3av_set_audio_mode()`. The `video_mode_table` maps PS3 mode ids to command-level video IDs, color spaces, formats, aspect ratios, and resolution.

## Control Flow
Module init verifies PS3 LV1 firmware and registers `ps3av_driver` as a VUART port driver. Probe enforces a single device, allocates state, initializes work/completion/mutexes, derives region from OS area settings, calls `ps3av_cmd_init()`, fetches hardware config, honors `video=safe`, auto-selects a mode from monitor info, and stores it. Packet I/O runs through `ps3av_do_pkt()`, which validates the command table, serializes with `ps3av->mutex`, sets headers, sends through `ps3av_send_cmd_pkt()`, skips asynchronous event packets, validates the reply CID, and copies reply data back into the caller packet. Video mode changes wait for any previous work completion, update `ps3av_mode`, mute video, schedule `ps3avd`, then the worker disables signals, handles VESA and HDCP options, sends AVB parameter packets, waits for display settling, unmutes, and completes.

## State And Persistence
State is in memory only and is global to the singleton device. Persistent hardware-facing state is the AV backend's programmed mode, mute state, audio parameters, and port routing. `ps3av_mode_old` is used for HDCP mode transitions; completion `done` prevents overlapping asynchronous mode changes. The `safe_mode` module/global flag only affects auto-selection during probe.

## Dependencies And Integration Points
The driver depends on PS3 LV1 firmware, the PS3 VUART layer, `asm/ps3av.h` command layouts, PS3 OS area region values, `video_get_options()`, and `ps3_gpu_mutex` through the command helper path. It integrates with PS3 framebuffer/video users via exported symbols and with PS3 VUART bus matching through `PS3_MATCH_ID_AV_SETTINGS`.

## Risks
Packet reads trust reply `size` enough to read into the fixed receive buffer; correctness depends on firmware obeying `PS3AV_BUF_SIZE` protocol limits. Many helper loops return `-1` instead of preserving specific command errors. Probe logs init failure but continues into hardware config discovery. Mode changes are asynchronous, so callers get success before the display programming finishes. Monitor quirks and preferred-mode ordering can choose conservative or unexpected modes on unusual EDID data.

## Test Signals
Useful validation includes booting on PS3 LV1 firmware with HDMI, DVI, and AVMULTI outputs; exercising `video=safe`; switching all mode ids including VESA and HDCP-off flags; checking that concurrent mode requests serialize; verifying audio mute and mode programming on HDMI, AVMULTI, and SPDIF; and fault-injecting VUART timeouts, event packets, and malformed reply CIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3av_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/ps3/ps3av_cmd.c Research

## Purpose
`ps3av_cmd.c` builds PS3 AV command packets and translates high-level mode/audio requests into the firmware packet formats consumed by `ps3av_do_pkt()`. It is the protocol encoding companion to `ps3av.c`.

## Important APIs, Types, And Functions
The file exports command helpers such as `ps3av_cmd_init()`, `ps3av_cmd_fin()`, mute/TV/HDMI mode functions, `ps3av_cmd_set_av_video_cs()`, `ps3av_cmd_set_video_mode()`, `ps3av_cmd_video_format_black()`, `ps3av_cmd_set_audio_mode()`, `ps3av_cmd_set_av_audio_param()`, `ps3av_cmd_audio_mode()`, `ps3av_cmd_audio_mute()`, `ps3av_cmd_audio_active()`, `ps3av_cmd_avb_param()`, `ps3av_cmd_av_get_hw_conf()`, and `ps3av_cmd_video_get_monitor_info()`. Conversion tables map video color spaces and video IDs to AV backend constants. Audio helpers convert sample rate, word width, FIFO maps, channel layouts, IEC channel status, and HDMI audio info frames.

## Control Flow
Most helpers zero a packet struct, populate command-specific fields, call `ps3av_do_pkt()` with exact send and user-buffer sizes, then return `get_status()` from the reply. `ps3av_cmd_init()` initializes video, audio, then AV modules in order; `ps3av_cmd_fin()` shuts down AV. `ps3av_cmd_set_video_mode()` only formats an in-memory sub-packet for an AVB aggregate; the caller later submits it via `ps3av_cmd_avb_param()`. `ps3av_cmd_avb_param()` takes `ps3_gpu_mutex` around the packet transaction, coupling mode programming with GPU access.

## State And Persistence
The file has little private runtime state. `ps3av_mode_cs_info` is exported as default audio channel-status bytes and can be reused by other PS3 audio code. Hardware state changes persist in the AV backend after command submission: muting, video color space, HDMI mode, video timings, audio route and channel status, and active/inactive audio bits.

## Dependencies And Integration Points
It depends on packet definitions in `asm/ps3av.h`, PS3 firmware version checks via `ps3_compare_firmware_version()`, GPU locking via `ps3_gpu_mutex`, and the transport provided by `ps3av_do_pkt()` in `ps3av.c`. Callers are expected to provide valid AV port ids and video mode ids chosen by higher-level code.

## Risks
Several conversion fallbacks silently choose defaults, for example RGB8 or 480p, which can hide invalid inputs. `ps3av_cnv_ns()` appears to index the 44 kHz row for all valid sample rates rather than indexing by `fs - BASE`, so audio N values deserve regression attention. Aggregated AVB packet length is accumulated by callers and must remain within firmware packet limits. Many errors are logged but not escalated by higher layers.

## Test Signals
Test by comparing generated packet bytes for each supported video and audio mode against firmware documentation, validating status propagation for every command CID, exercising HDMI range options on firmware below and above 1.8.0, checking AVB length composition, and verifying audio sample-rate/channel combinations over HDMI and SPDIF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3av_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3stor_lib.c -->
# sources/distributed-fs/ceph-client/drivers/ps3/ps3stor_lib.c Research

## Purpose
`ps3stor_lib.c` provides common setup, teardown, and synchronous command helpers for PS3 storage devices. It abstracts hypervisor device open/close, event-port IRQ setup, DMA bounce mapping, accessible-region probing, and LV1 read/write or command completion waits.

## Important APIs, Types, And Functions
Public exports are `ps3stor_setup()`, `ps3stor_teardown()`, `ps3stor_read_write_sectors()`, and `ps3stor_send_command()`. The private `ps3_flash_workaround` tracks flash/disk open ordering to delay disk close while flash remains open. `ps3stor_probe_access()` probes all regions by reading one sector through the bounce LPAR and records accessible regions in `dev->accessible_regions`.

## Control Flow
Setup opens the HV device, creates an event receive port, requests the driver IRQ, validates bounce buffer alignment, creates a PS3 DMA region, maps the bounce buffer for bidirectional DMA, converts it to an LPAR address, then probes accessible regions. Failure paths unwind in reverse order. Teardown unmaps DMA, frees the DMA region, frees IRQ, destroys the receive port, and closes the HV device. Read/write and device-command helpers initialize `dev->done`, submit the LV1 call, wait for interrupt completion, then return either submission failure, stored LV1 status, or zero.

## State And Persistence
Device state is stored in the caller-owned `struct ps3_storage_device`: IRQ, DMA region, bounce DMA address, bounce LPAR, selected region index, completion, tag, and LV1 status. The library mutates `accessible_regions` and chooses the first accessible region. The flash workaround is process-global and persists across storage device setup/teardown calls.

## Dependencies And Integration Points
The file integrates with PS3 system-bus devices, LV1 storage calls, PS3 DMA region management, Linux DMA mapping, completions, IRQ handling, and concrete PS3 storage frontends that provide a bounce buffer and interrupt handler.

## Risks
The flash/disk close workaround is global and has no explicit locking, relying on probe/remove serialization. `ps3stor_probe_access()` performs real sector reads during setup and treats ROM as always accessible. Read/write helpers wait indefinitely for completion if the interrupt path never completes. Submission failures return `-1`, while completion failures return raw LV1 status, so callers must handle mixed error domains.

## Test Signals
Validation should cover flash, disk, and ROM devices; unformatted-disk flash workaround ordering; DMA alignment below 4K and 64K thresholds; failure-path unwinding for every setup step; inaccessible regions; interrupt completion with LV1 error status; and read/write sector calls across the chosen region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3stor_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/sys-manager-core.c -->
# sources/distributed-fs/ceph-client/drivers/ps3/sys-manager-core.c Research

## Purpose
`sys-manager-core.c` is the statically linked bridge between generic PS3 power-control entry points and the loadable PS3 system-manager driver. It lets the module register callbacks while preserving always-available poweroff/restart/halt symbols.

## Important APIs, Types, And Functions
`ps3_sys_manager_register_ops()` copies a supplied `struct ps3_sys_manager_ops` into a static global after `BUG_ON()` checks that both the ops pointer and `ops->dev` are present. `ps3_sys_manager_power_off()` and `ps3_sys_manager_restart()` call registered callbacks if present, then fall through to `ps3_sys_manager_halt()`. `ps3_sys_manager_halt()` logs an emergency halt message, disables local interrupts, and loops forever in `lv1_pause(1)`.

## Control Flow
The system-manager module registers or updates callbacks during its probe/remove lifecycle. Poweroff and restart paths dereference the last registered ops and pass the stored device pointer to the callback. If no callback is registered, or if the callback returns, the code enters the non-returning halt loop.

## State And Persistence
The only state is the static `ps3_sys_manager_ops` copy. There is no locking or reference counting around the registered module/device pointer. The final halt state is persistent by design because execution never returns.

## Dependencies And Integration Points
It depends on `asm/ps3.h` for `struct ps3_sys_manager_ops`, LV1 pause calls, exported GPL symbols, and platform power management code that invokes these functions as machine poweroff/restart handlers.

## Risks
Registration uses a raw struct copy with no lifetime protection, so remove paths must avoid leaving stale callback pointers. `BUG_ON()` makes invalid registration fatal. Callback failure is not reported because halt is unconditional afterward.

## Test Signals
Test signals are mostly platform integration checks: registered callbacks fire on poweroff and restart, missing callbacks still halt cleanly, invalid registration is caught in debug/fault tests, and no stale callback is reachable after system-manager module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/sys-manager-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/vuart.h -->
# sources/distributed-fs/ceph-client/drivers/ps3/vuart.h Research

## Purpose
`vuart.h` declares the PS3 virtual UART port-driver interface used by PS3 logical devices such as AV settings. It is a local contract between PS3 VUART bus support and port-specific drivers.

## Important APIs, Types, And Functions
`struct ps3_vuart_stats` records byte and interrupt counters. `struct ps3_vuart_work` wraps `work_struct`, a trigger bitmask, and the owning `ps3_system_bus_device`. `struct ps3_vuart_port_driver` embeds `struct ps3_system_bus_driver` and supplies `probe`, `remove`, `shutdown`, and `work` callbacks. Inline helpers convert a system-bus device to its VUART driver and a work item to its device. Function declarations cover driver registration, synchronous read/write, async read setup/cancel, RX byte clearing, trigger get/set, and enabling/disabling TX, RX, and disconnect interrupts.

## Control Flow
Port drivers register a `ps3_vuart_port_driver`. The VUART core matches devices, calls driver callbacks, schedules work using `ps3_vuart_work`, and exposes byte-oriented transport through `ps3_vuart_write()` and `ps3_vuart_read()`. Interrupt trigger helpers allow port drivers to tune or enable event notification.

## State And Persistence
This header does not own storage. It defines the shapes of per-port state managed by the VUART core and by drivers. Work items retain only a device pointer and trigger state until executed.

## Dependencies And Integration Points
It depends on PS3 system-bus definitions from `asm/ps3.h` and the Linux workqueue type. `ps3av.c` consumes this interface directly. Other PS3 VUART clients can share the same registration and I/O operations.

## Risks
The inline conversion helpers assume valid embedding and use `BUG_ON()` for missing bus drivers. Async read and interrupt semantics are only declared here, so users must coordinate lifetimes with the VUART implementation. Work items hold raw device pointers and require the core to prevent use-after-free during remove/shutdown.

## Test Signals
Useful tests include registering a mock port driver, matching by `match_id`, verifying work-to-device conversion, exercising sync and async reads, confirming trigger programming, and validating interrupt enable/disable paths during remove and disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/vuart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ptp/Kconfig Research

## Purpose
`drivers/ptp/Kconfig` defines build-time configuration for the Linux PTP hardware clock framework and a collection of PHC drivers. It controls whether the common character-device framework is built and which hardware, virtual, PHY, FPGA, and platform clocks can register with it.

## Important APIs, Types, And Functions
The primary symbol is `PTP_1588_CLOCK`, a tristate depending on `NET` and `POSIX_TIMERS`, selecting `PPS` and `NET_PTP_CLASSIFY`. `PTP_1588_CLOCK_OPTIONAL` lets drivers optionally compile against dummy helpers when PTP is off or modular. This group covers symbols for `PTP_1588_CLOCK_DTE`, `PTP_1588_CLOCK_IDT82P33`, `PTP_1588_CLOCK_IDTCM`, `PTP_1588_CLOCK_FC3W`, and `PTP_DFL_TOD`, plus the surrounding choices that show how the PTP menu is organized.

## Control Flow
Kconfig has no runtime flow. At configuration time, dependencies restrict visibility and selection. At build time, these symbols drive the PTP Makefile and determine which objects are included as built-ins or modules.

## State And Persistence
The selected symbols persist in the kernel `.config`. The runtime effect is whether `/dev/ptp*` support and hardware-specific PHC drivers are available.

## Dependencies And Integration Points
The framework requires networking and POSIX timers. Specific drivers add dependencies: DTE requires Broadcom-related architecture or compile-test plus MMIO; IDT/ClockMatrix/FemtoClock drivers require I2C through their MFD/regmap stack and PTP; DFL TOD requires FPGA DFL and PTP. Other entries integrate with PHYLIB, PCI, ACPI, MTD, common clock, and virtual-machine timing features.

## Risks
Incorrect dependencies can produce link failures, unusable built-in/module combinations, or hidden drivers. `PTP_1588_CLOCK_OPTIONAL` is particularly important for drivers that can compile with dummy PTP helpers. Defaults such as `default ETHERNET` and architecture-specific defaults affect kernel footprint.

## Test Signals
Validation includes `olddefconfig` and randconfig coverage, module/built-in combinations for optional PTP users, dependency checks for I2C/MFD-based drivers, and build tests for `COMPILE_TEST` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ptp/Makefile Research

## Purpose
The PTP Makefile maps Kconfig symbols to built objects for the PTP framework and its PHC drivers.

## Important APIs, Types, And Functions
`ptp-y` builds the common `ptp` module from `ptp_clock.o`, `ptp_chardev.o`, `ptp_sysfs.o`, and `ptp_vclock.o`. `ptp_kvm-*` selects architecture-specific KVM PTP pieces. Object assignments connect symbols to drivers including `ptp_dte.o`, `ptp_clockmatrix.o`, `ptp_fc3.o`, `ptp_idt82p33.o`, and `ptp_dfl_tod.o`.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` entries based on `.config`. If `PTP_1588_CLOCK=m`, `ptp-y` is linked into `ptp.ko`; if built in, it becomes part of vmlinux. Hardware driver objects follow their own tristate settings.

## State And Persistence
The Makefile has no runtime state. Its output persists as built modules or built-in objects in the kernel build tree.

## Dependencies And Integration Points
It is tightly coupled to `drivers/ptp/Kconfig` symbol names and source filenames. It also relies on Kbuild composite-object naming, especially for `ptp-y` and `ptp_kvm-*`.

## Risks
Missing an object from `ptp-y` can produce partially functional framework builds. A mismatch between Kconfig symbols and Makefile entries makes a selected driver silently not build. Adding a new PTP driver requires updating both files consistently.

## Test Signals
Build tests should cover `PTP_1588_CLOCK=y`, `m`, and disabled, plus module builds for each object in this subset. `make M=drivers/ptp` is a direct signal for missing object or symbol regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_chardev.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_chardev.c Research

## Purpose
`ptp_chardev.c` implements the userspace character-device interface for PTP clocks. It handles open/release, ioctls, pin configuration, event subscription masks, polling, and reading external timestamp events from per-file queues.

## Important APIs, Types, And Functions
Exports used by the PTP core include `ptp_disable_all_events()`, `ptp_set_pinfunc()`, `ptp_open()`, `ptp_release()`, `ptp_ioctl()`, `ptp_poll()`, and `ptp_read()`. Key helpers implement `PTP_CLOCK_GETCAPS`, EXTTS requests, PEROUT requests, PPS enable, precise and extended system offset sampling, pin get/set, and per-file event-mask commands.

## Control Flow
Open allocates a `timestamp_event_queue`, allocates its channel bitmap, enables all channels by default, links it into `ptp->tsevqs`, and creates debugfs mask visibility. Release removes debugfs, unlinks the queue, frees bitmap and memory. Ioctl dispatch validates ABI variants: V2 commands reject reserved fields and unsupported flags, V1 commands mask old valid flags. Writable operations require write-mode file access. EXTTS/PEROUT/PPS requests call the driver `enable()` callback under `pincfg_mux`. Read waits for queue events or defunct state, drains up to `PTP_BUF_TIMESTAMPS` events, and copies them to userspace.

## State And Persistence
Each open file has an independent queue and event-channel bitmap. Pin configuration lives in `ptp->info->pin_config` and persists across file descriptors until changed or disabled. Event queue data is transient. Debugfs directories expose per-open masks.

## Dependencies And Integration Points
This file depends on `ptp_private.h`, POSIX clock contexts, PTP UAPI structures, kernel timekeeping, PPS capability checks, waitqueues, bitmap helpers, debugfs, and driver-provided `struct ptp_clock_info` callbacks.

## Risks
The character ABI is strict; reserved field and flag validation must match userspace expectations. Pin function changes disable previous functions and can call into driver hardware while holding `pincfg_mux`. Per-open queue allocation returns `-EINVAL` on memory failure in a few places rather than `-ENOMEM`. Event masking uses channel numbers up to `PTP_MAX_CHANNELS`, so driver event indexes must stay in range.

## Test Signals
Use `testptp` or equivalent to exercise all ioctl versions, invalid reserved fields, permission failures for read-only descriptors, EXTTS/PEROUT boundary indexes, PPS capability checks, sys offset sampling counts, pin reassignments, poll/read behavior, mask clear/single-enable behavior, and unregister wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_chardev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_clock.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_clock.c Research

## Purpose
`ptp_clock.c` is the common PTP hardware clock framework core. It registers the `ptp` class and character-device region, creates POSIX clock devices, manages PPS sources, queues timestamp events to open file descriptors, and exposes registration helpers for hardware drivers.

## Important APIs, Types, And Functions
Public exports include `ptp_clock_register()`, `ptp_clock_unregister()`, `ptp_clock_event()`, `ptp_clock_index()`, `ptp_clock_index_by_of_node()`, `ptp_clock_index_by_dev()`, `ptp_find_pin()`, `ptp_find_pin_unlocked()`, `ptp_schedule_worker()`, and `ptp_cancel_worker_sync()`. It defines `ptp_clock_ops` for POSIX clock callbacks and uses an xarray to allocate stable clock indexes.

## Control Flow
`ptp_init()` registers the class and chrdev region at subsystem init. Hardware drivers call `ptp_clock_register()` with `ptp_clock_info`; the core validates required callbacks, allocates `struct ptp_clock`, allocates an index, creates the default event queue, initializes locks and waitqueue, fills missing cycle helpers, starts an auxiliary kthread worker if requested, handles virtual-clock metadata, populates pin sysfs groups, optionally registers a PPS source, initializes the device, and calls `posix_clock_register()`. Unregister marks the clock defunct, wakes readers, unregisters POSIX clock, disables events, stops worker, unregisters PPS, and drops the device reference. `ptp_clock_event()` fans EXTTS/EXTOFF events into subscribed queues and forwards PPS events to the PPS subsystem.

## State And Persistence
Persistent runtime state includes class devices `/dev/ptpN`, xarray index mapping, per-clock pin config, default and per-open timestamp queues, PPS source, virtual-clock bookkeeping, and dialed frequency. Event queues are bounded ring buffers that overwrite oldest events when full.

## Dependencies And Integration Points
The core depends on POSIX clocks, Linux device/class infrastructure, PPS, xarray, debugfs, sysfs helpers in other PTP files, and driver-provided `ptp_clock_info` operations. Network, PHY, FPGA, MFD, and virtual-machine drivers register through this layer.

## Risks
Registration has many unwind branches; resource ordering is important for queues, xarray entries, kworkers, PPS, and devices. `ptp_clock_adjtime()` enforces freerun checks and adjustment ranges, so bad driver `max_adj` or phase limits affect userspace. Event fanout holds `tsevqs_lock` while enqueueing into queues, requiring careful lock ordering. PPS events assume a registered PPS source when drivers emit PPS event types.

## Test Signals
Test signals include registering mock clocks with minimal callbacks, failed allocation unwind, PPS-capable registration, aux worker scheduling/cancel, clock set/get/adjtime UAPI behavior, unregister while readers block, event queue overflow, index lookup by device and OF node, and virtual-clock child unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_clockmatrix.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_clockmatrix.c Research

## Purpose
`ptp_clockmatrix.c` is the Renesas/IDT ClockMatrix PHC driver. It loads optional firmware, maps ToD channels to PLLs and outputs, exposes selected ToD channels as PTP clocks, supports external timestamp polling, and implements time, frequency, phase, and 1-PPS output operations through regmap.

## Important APIs, Types, And Functions
Important helpers include `idtcm_read()/idtcm_write()`, firmware parsing and mask handling (`idtcm_load_firmware()`, `check_and_set_masks()`), version detection (`idtcm_set_version_info()`), channel setup (`configure_channel_pll()`, `configure_channel_tod()`, `idtcm_enable_channel()`), PTP ops (`idtcm_gettime()`, `idtcm_settime()`, `idtcm_adjtime()`, `idtcm_adjphase()`, `idtcm_adjfine()`, `idtcm_enable()`), and delayed workers for phase pull-in and external timestamp polling. The driver supplies separate `ptp_clock_info` templates for older firmware and newer SCSR ToD write support.

## Control Flow
Probe obtains the parent RSMU regmap and mutex, initializes defaults, reads firmware/product version, loads firmware if available, waits for boot/APLL/DPLL readiness, then iterates ToD channels. Channels enabled by `tod_mask` are configured, initialized for DCO operating mode, started, and registered with `ptp_clock_register()`; disabled ToDs can still be configured as external timestamp channels. PTP gettime triggers an immediate primary ToD read. Settime and adjtime use firmware-version-specific paths: older firmware writes hardware DPLL ToD and syncs PPS outputs, while newer firmware uses SCSR ToD write commands for absolute or delta adjustments. Small adjustments may use firmware or software phase pull-in and an aux worker to restore frequency. EXTTS requests arm secondary ToD reads on selected reference pins and poll every 95 ms until events arrive.

## State And Persistence
`struct idtcm` stores firmware version, ToD mask, delayed EXTTS work, shared parent lock/regmap, event channel routing, overhead measurement, and per-channel state. Each channel stores register base addresses, PLL/mode/output mapping, current scaled frequency, DCO delay, phase-pull-in status, and PTP clock pointer. Hardware state includes loaded firmware registers, ToD enables, PLL operating modes, output squelch, and pending triggers.

## Dependencies And Integration Points
The driver integrates with the Renesas Synchronization Management Unit MFD (`rsmu_ddata`), regmap, firmware loader (`idtcm.bin` or module override), PTP core, delayed work, and IDT ClockMatrix register definitions. Userspace interacts through `/dev/ptpN` and PTP ioctls.

## Risks
The code supports multiple firmware register layouts, so `IDTCM_FW_REG()` choices are high-risk. Firmware parsing accepts partial configurations and skips read-only/page-offset holes; bad firmware can mis-map ToDs or outputs. EXTTS is polling-based, not interrupt-driven, and can miss semantics around single-shot masks. Remove unregisters clocks before canceling delayed work, while the work uses clock/channel pointers; ordering should be scrutinized. Phase pull-in blocks concurrent adjfine behavior by design.

## Test Signals
Validation needs firmware-present and firmware-missing probes, version paths below 4.8.7, 4.8.7+, and 5.2.0+, ToD mask/output mask parsing, all four ToD registrations, get/set/adjtime/adjfine/adjphase ioctls, 1-PPS perout enable restrictions, EXTTS pin assignment and polling, remove during active EXTTS, and regmap fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_clockmatrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_clockmatrix.h -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_clockmatrix.h Research

## Purpose
`ptp_clockmatrix.h` defines the private constants and state structures for the ClockMatrix PHC driver.

## Important APIs, Types, And Functions
The header defines firmware filename `idtcm.bin`, hardware limits (`MAX_TOD`, `MAX_PLL`, `MAX_REF_CLK`), write-phase limits, mask register addresses, default ToD-to-PLL/output mappings, firmware version enum, PTP PLL operating mode enum, and the `IDTCM_FW_REG()` compatibility macro. `struct idtcm_channel` captures one ToD/PTP channel's clock info, PTP clock, register bases, PLL mapping, mode transition callbacks, phase-pull-in state, current frequency, DCO delay, trigger reference, and output mask. `struct idtcm` captures device-wide state, regmap, lock, version, masks, delayed EXTTS work, event routing, and overhead timing. `struct idtcm_fwrc` describes packed firmware records.

## Control Flow
The header has no executable flow, but its callback fields drive runtime mode transitions: each channel stores functions for configuring write-frequency/write-phase mode and selecting firmware or software phase pull-in.

## State And Persistence
The structures declared here are the driver's durable in-memory state for each probed device and channel. Their values mirror persistent hardware state programmed into ClockMatrix registers.

## Dependencies And Integration Points
It depends on PTP clock types, regmap, `ktime`, and ClockMatrix register definitions from `linux/mfd/idt8a340_reg.h`. It is consumed only by `ptp_clockmatrix.c`.

## Risks
Constants in this header encode hardware register contracts. Wrong defaults can expose the wrong ToD as a PHC, align PPS to incorrect outputs, or use the wrong firmware-era register. The packed firmware record layout must match the firmware binary exactly.

## Test Signals
Tests should validate default masks, firmware-record parsing size/alignment, version-dependent register macro expansion, channel array bounds, and max phase/frequency limits used by PTP caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_clockmatrix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_dfl_tod.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_dfl_tod.c Research

## Purpose
`ptp_dfl_tod.c` exposes an Intel FPGA DFL Time-of-Day private feature as a PTP hardware clock. It maps the DFL MMIO feature, implements PHC time/frequency adjustment operations, and registers a PTP clock.

## Important APIs, Types, And Functions
`struct dfl_tod` holds PTP ops, device, PTP clock pointer, MMIO base, and spinlock. Helpers include `fine_adjust_tod_clock()`, `coarse_adjust_tod_clock()`, `dfl_tod_adjust_fine()`, `dfl_tod_adjust_time()`, `dfl_tod_get_timex()`, and `dfl_tod_set_time()`. `dfl_tod_clock_ops` advertises `adjfine`, `adjtime`, `gettimex64`, and `settime64` with `TOD_MAX_ADJ`.

## Control Flow
Probe allocates state, maps the DFL feature resource, initializes the spinlock, copies ops, and calls `ptp_clock_register()`. Fine frequency adjustment reads the clock frequency register, converts scaled ppm to period and drift-adjust values, and updates period/drift registers under lock. Time adjustment uses fine period adjustments when the delta fits hardware adjust-count limits, otherwise it performs a coarse read-modify-write of seconds/nanoseconds. Gettime reads nanoseconds first to trigger the hardware snapshot, then seconds low/high, while collecting system pre/post timestamps. Settime writes seconds high, seconds low, then nanoseconds, matching the hardware-required write order.

## State And Persistence
In-memory state is minimal. Hardware registers persist the ToD time, base period, drift adjustment, and in-progress adjust count. Spinlock protects register sequences.

## Dependencies And Integration Points
The driver depends on FPGA DFL bus support, MMIO accessors, PTP core, bitfield helpers, `readl_poll_timeout_atomic()`, and kernel time units. It binds to DFL feature id `0x22`.

## Risks
Adjustment math divides by `diff`; if the period is already at min/max, boundary handling must avoid zero divisors. Coarse negative adjustments convert through unsigned `now`, so large negative deltas need scrutiny. Polling is atomic under spinlock and can hold the lock for the adjustment timeout.

## Test Signals
Tests should cover DFL probe/remove, read snapshot ordering, set write ordering, positive/negative adjtime across fine and coarse thresholds, adjfine range checks, register polling timeout, and `PTP_SYS_OFFSET_EXTENDED` behavior using `gettimex64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_dfl_tod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_dte.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_dte.c Research

## Purpose
`ptp_dte.c` is a Broadcom Digital Timing Engine PTP clock driver. It maps a 44-bit NCO timer, exposes get/set/adjust/frequency operations, and preserves basic register state across suspend.

## Important APIs, Types, And Functions
`struct ptp_dte` stores MMIO base, PTP clock, clock caps, device, overflow tracking, spinlock, and saved registers. Helpers include `dte_write_nco()`, `dte_read_nco()`, `dte_write_nco_delta()`, `dte_read_nco_with_ovf()`, and PTP ops `ptp_dte_adjfine()`, `ptp_dte_adjtime()`, `ptp_dte_gettime()`, `ptp_dte_settime()`, and `ptp_dte_enable()`.

## Control Flow
Probe allocates state, maps the platform resource, initializes lock, copies static caps, registers with the PTP core, and stores driver data. Settime disables the increment register, writes the NCO registers, resets wrap tracking, then reenables default increment. Gettime reads the hardware NCO, detects wrap by comparing overflow bits, extends it with `ts_wrap_cnt`, and returns a timespec. Adjtime applies a signed delta while accounting for wrap/underflow. Adjfine converts scaled ppm to ppb, bounds it by `max_adj`, and writes an adjusted increment value. Suspend saves four registers and disables the NCO; resume restores them with special formatting for the overflow register.

## State And Persistence
Hardware stores low/time/overflow/increment registers. Software extends the 44-bit hardware clock using `ts_wrap_cnt` and `ts_ovf_last`, so long gaps without reads can lose wrap information. Suspend state is in `reg_val`.

## Dependencies And Integration Points
The driver depends on platform-device probing, OF compatible `brcm,ptp-dte`, MMIO accessors, PM sleep hooks, and PTP core registration.

## Risks
The 44-bit timer wraps in about 4.9 hours; wrap extension only updates on reads or adjustments. `ptp_dte_enable()` returns unsupported for all event requests. Negative adjustments around zero clamp if no wrap count exists. Frequency math assumes 125 MHz and the documented 3.29 register format.

## Test Signals
Validation should cover probe/remove, set/get monotonicity, wrap detection through simulated overflow, adjtime across wrap and underflow, adjfine max range, suspend/resume register restoration, and unsupported PEROUT/EXTTS/PPS ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_dte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.c Research

## Purpose
`ptp_fc3.c` is the Renesas/IDT FemtoClock3 Wireless PHC driver. It loads register firmware, calibrates timing hardware, maintains a software timecounter over a hardware sub-sync counter, supports frequency/phase adjustments, and reports external phase-offset measurements.

## Important APIs, Types, And Functions
Key helpers convert between nanoseconds and sub-sync counters, convert TDC measurements to offsets, configure LPF/TDC blocks, manage the TOD subcounter, and implement PTP ops: `idtfc3_gettime()`, `idtfc3_settime()`, `idtfc3_adjtime()`, `idtfc3_adjphase()`, `idtfc3_adjfine()`, `idtfc3_enable()`, and `idtfc3_aux_work()`. Probe uses `idtfc3_check_device_compatibility()`, `idtfc3_load_firmware()`, `idtfc3_configure_hw()`, and `idtfc3_enable_ptp()`.

## Control Flow
Probe obtains the parent RSMU regmap and lock, verifies device ID, loads firmware or defers if the firmware is missing, then enables the PTP clock. Firmware loading initializes default hardware parameters, parses firmware records, updates derived parameters for recognized addresses, writes valid register records, calibrates TDC/APLL, enables LPF, disables TDC, determines TDC sign, and reads clock parameters. Time reads update a software `ns` value from the current hardware subcounter. Settime programs a future subcounter load so the software time aligns at the next sync. Adjtime similarly computes a counter load from the delta. Adjfine and adjphase write LPF frequency/phase control words. EXTTS with `PTP_EXT_OFFSET` enables continuous TDC measurement; aux work periodically updates the timecounter and emits EXTOFF events from TDC FIFO measurements.

## State And Persistence
`struct idtfc3` stores parent regmap/lock, derived hardware parameters, TDC frequencies/sign, sub-sync counts, software timecounter fields, update periods, and measured write overhead. Hardware firmware and register settings persist in the chip until reset.

## Dependencies And Integration Points
The driver integrates with RSMU MFD data, regmap, firmware loader (`idtfc3.bin` or module override), PTP core, delayed aux worker scheduling, and FC3 register definitions from `idtRC38xxx_reg.h`.

## Risks
Timekeeping depends on periodic aux work; if it is delayed beyond counter wrap, software time can drift or jump. Firmware failure other than missing firmware is warned but probe can continue, so default configuration must be valid. EXTTS supports only external offset semantics, not ordinary edge timestamps. The static `tdc_get` in aux work is shared at function scope, which is safe for a single device but questionable for multiple instances.

## Test Signals
Test firmware defer and successful load, device ID rejection, derived parameter calculations, timecounter wrap, settime and adjtime around negative and large deltas, adjfine/adjphase control-word writes, EXTTS offset enable/disable, TDC FIFO overrun recovery, aux worker cadence, and remove while worker activity is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.h -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.h Research

## Purpose
`ptp_fc3.h` defines private constants and state for the FemtoClock3 PHC driver.

## Important APIs, Types, And Functions
It defines default firmware name `idtfc3.bin`, maximum frequency offset `MAX_FFO_PPB`, TDC polling period `TDC_GET_PERIOD`, and `struct idtfc3`. The state struct contains PTP caps and clock pointer, device and parent MFD/regmap references, shared lock, hardware parameter cache, TDC and time-reference frequencies, sub-sync timing, LPF mode, software timecounter fields, update/write timeouts, and measured TOD write overhead.

## Control Flow
There is no executable code. `ptp_fc3.c` fills the structure during probe and uses it across all PTP operations and aux worker runs.

## State And Persistence
The struct is the driver's in-memory representation of hardware configuration and current PHC time. `last_counter` and `ns` are especially important because they extend a hardware counter into PTP time.

## Dependencies And Integration Points
The header depends on PTP clock types, regmap, and `ktime`. It also assumes register-derived `struct idtfc3_hw_param` from the included FC3 MFD register header.

## Risks
If hardware parameters are stale or firmware parsing does not update them, all time conversions based on `ns_per_counter` and `ns_per_sync` are affected. The header's limits must match the chip's actual DCO/TDC capabilities.

## Test Signals
Validation should assert initialized fields after probe, sane derived periods, max adjustment consistency with PTP caps, and robust behavior if firmware leaves optional parameters at defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.c Research

## Purpose
`ptp_idt82p33.c` is the Renesas/IDT 82P33xxx PHC driver. It loads firmware, exposes selected PLLs as PTP clocks, implements time/frequency/phase adjustment, supports 1-PPS output enable, and polls for external timestamp events.

## Important APIs, Types, And Functions
Important helpers include regmap wrappers, ToD byte-array conversions, DPLL mode/trigger programming, external timestamp arm/check flows, `_idt82p33_gettime()`, `_idt82p33_settime()`, immediate and internally triggered adjtime paths, double-DCO small adjustment helpers, overhead measurement helpers, channel/caps initialization, firmware parsing, and `idt82p33_probe()/remove()`. PTP ops are `idt82p33_adjwritephase()`, `idt82p33_adjfine()`, `idt82p33_adjtime()`, `idt82p33_gettime()`, `idt82p33_settime()`, `idt82p33_enable()`, and `idt82p33_work_handler()`.

## Control Flow
Probe initializes defaults, cold-resets the chip, loads firmware if available, soft-resets, then enables each PLL selected by firmware/default `pll_mask`. Enabling a channel initializes register addresses, caps and pins, registers the PTP clock, puts the DPLL in DCO mode, measures ToD write overhead, zeroes the ToD, and enables ToD sync. Gettime temporarily disables EXTTS polling, triggers a ToD status read, reads the timestamp, and re-arms EXTTS as needed. Settime writes a triggered ToD configuration. Adjtime uses double-DCO for deltas below `phase_snap_threshold`; otherwise it prefers an internal 1-PPS-triggered write and may fall back to immediate write for larger positive deltas. EXTTS enable maps configured pins to hardware triggers and starts a 95 ms delayed polling loop.

## State And Persistence
Device state tracks PLL mask, output masks, delayed EXTTS work, event-channel routing, overhead timing, and one channel per possible PHC. Channel state includes PLL register addresses, current frequency, double-DCO state, output mask, trigger state, and delayed adjtime workaround work. Hardware state includes loaded firmware, DPLL modes, ToD counters, output squelch, and trigger selection.

## Dependencies And Integration Points
The driver depends on RSMU MFD parent data, regmap, firmware loader (`idt82p33xxx.bin` or module override), PTP core, delayed work, and IDT 82P33 register definitions. Userspace reaches it through `/dev/ptpN`, pin config, EXTTS, PEROUT, and clock adjustment ioctls.

## Risks
Firmware parsing drives PLL/output masks and skips some page offsets; malformed firmware can disable all PHCs or mis-map outputs. Polling-based EXTTS can miss events or race with gettime, which temporarily disables/re-arms triggers. The double-DCO worker suppresses adjfine while active and returns `-EBUSY` for adjtime. There is a suspicious loop in `idt82p33_measure_tod_write_9_byte_overhead()` that uses `i` instead of `j` for register offset/buffer index, worth targeted review.

## Test Signals
Test cold/soft reset and firmware load paths, default masks when firmware is missing, both PLL registrations, ToD overhead measurement, get/set/adjtime thresholds, double-DCO scheduling and restoration, adjphase range and register encoding, perout 1-PPS validation, EXTTS pin mapping/polling/single-shot behavior, and remove canceling delayed work before clock teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.h -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.h Research

## Purpose
`ptp_idt82p33.h` defines constants, limits, firmware record layout, and private state structures for the IDT 82P33xxx PHC driver.

## Important APIs, Types, And Functions
The header defines firmware name `idt82p33xxx.bin`, PHC/trigger/output limits, ToD byte count, DCO and adjustment thresholds, firmware mask addresses, default masks, write-phase limits and phase resolution. `struct idt82p33_channel` stores PTP caps, PTP clock, parent pointer, PLL mode, adjtime workaround work, current frequency, double-DCO flag, output mask, EXTTS trigger bookkeeping, and register addresses. `struct idt82p33` stores all channels, device, masks, delayed EXTTS work, event routing, shared lock/regmap/MFD, and overhead timing. `struct idt82p33_fwrc` is the packed firmware record.

## Control Flow
The header has no executable flow. Its work structures and fields are used by `ptp_idt82p33.c` to schedule delayed adjustment restoration and EXTTS polling.

## State And Persistence
These structures are the durable software state for each probed chip. Many fields mirror hardware state: PLL masks, output masks, trigger selections, DPLL register addresses, current frequency, and ToD overhead estimate.

## Dependencies And Integration Points
It depends on `linux/mfd/idt82p33_reg.h` for register definitions and on regmap/ktime/PTP clock types. It is private to the 82P33 driver.

## Risks
Hardware limits and default masks in the header shape runtime registration. Incorrect `MAX_*` values can cause out-of-bounds pin/event handling or prevent valid hardware features. Packed firmware record layout must match the binary firmware format exactly.

## Test Signals
Validation includes checking struct initialization for each PLL, firmware record parsing alignment, pin count and channel bounds, phase/frequency threshold behavior, and consistency between header limits and advertised PTP caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.h -->
