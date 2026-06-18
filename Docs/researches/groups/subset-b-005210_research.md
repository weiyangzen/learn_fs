# subset-b-005210 grouped research

Work item `subset-b-005210` covers the s390 common I/O channel subsystem, channel-path, CHSC, CRW, CMF, and CCW-device bus files under `sources/distributed-fs/ceph-client/drivers/s390/cio/`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chp.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/chp.c

## Purpose
This file manages registered s390 channel paths (`struct channel_path`) and their runtime/configuration state. It exposes channel-path sysfs attributes, registers channel paths discovered from SCLP/CRW/CHSC information, varies paths logically online/offline, and schedules SCLP configure/deconfigure operations.

## Important APIs, Types, and Functions
The main exported APIs are `chp_get_status()`, `chp_get_sch_opm()`, `chp_is_registered()`, `chp_update_desc()`, `chp_new()`, `chp_get_chp_desc()`, `chp_cfg_schedule()`, `chp_cfg_cancel_deconfigure()`, `chp_info_get_status()`, and `chp_ssd_get_mask()`. Internal state includes `chp_cfg_task[][]`, `cfg_lock`, `cfg_work`, `cfg_wait_queue`, cached `sclp_chp_info`, `info_lock`, and `chp_info_expires`. The sysfs surface includes `status`, `configure`, `type`, CMG/channel-measurement attributes, CHID/ESC/speed fields, and `util_string`.

## Control Flow
`chp_init()` registers the CRW handler for channel paths, initializes configure work, reads SCLP channel-path info, and registers initially configured or standby paths. `chp_new()` serializes on the CSS mutex, allocates a channel path, fetches CHSC descriptions/measurement characteristics, rejects invalid descriptors, registers the device, and attaches measurement attributes when channel measurement is enabled. Runtime `status` writes call `s390_vary_chpid()`, which updates logical state and calls `chsc_chp_vary()` to notify subchannels. `configure` writes enqueue `cfg_func()`, which issues `sclp_chp_configure()` or `sclp_chp_deconfigure()`, expires cached SCLP information, and propagates online/offline changes through CHSC helpers.

## State and Persistence
State is volatile kernel memory plus hardware/SCLP/CHSC channel-path state. `channel_subsystems[0]->chps[]` owns registered channel-path pointers. `chp_info` caches SCLP status for one jiffy and is refreshed on expiry or after configure changes. Pending configure tasks persist only in `chp_cfg_task[][]` until the work item consumes them. Measurement data comes from CSS CUB/ECUB memory and live CHSC descriptors, not from disk.

## Dependencies and Integration Points
This file depends on SCLP channel-path configuration APIs, CRW handlers, CHSC description/measurement helpers, the CSS device hierarchy, the CIO debug facility, and sysfs device attributes. It integrates with `chsc.c` for channel-path online/offline/vary propagation, with `css.c` for slow-path settling, and with subchannel drivers through CHSC/CSS callbacks.

## Risks and Test Signals
Risk areas include races among sysfs vary/configure, CRW path events, and slow-path subchannel evaluation; stale `chp_info` if SCLP refresh fails; incomplete rollback when sysfs measurement attributes fail after device registration; and path-mask mistakes in `chp_ssd_get_mask()` when full-link-address validity is partial. Test signals include channel-path CRW injection, `status` and `configure` sysfs transitions, SCLP configure failure handling, registration of standby paths at boot, measurement attribute creation/removal when `cm_enable` changes, and subchannel path masks after vary on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chp.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/chp.h

## Purpose
This header defines the channel-path data model and public helpers used by s390 CIO, CSS, and CHSC code to track channel-path identity, status, descriptions, measurement characteristics, and path links.

## Important APIs, Types, and Functions
It defines status constants (`CHP_STATUS_*`), event constants (`CHP_ONLINE`, `CHP_OFFLINE`, `CHP_VARY_ON`, `CHP_VARY_OFF`, `CHP_FCES_EVENT`), `struct chp_link`, and `struct channel_path`. `channel_path` embeds a Linux device, channel-path id, mutex-protected descriptors (`fmt0`, `fmt1`, `fmt3`), logical state, CMG capability flags, speed, and measurement-characteristic blocks. `chp_test_bit()` reads SCLP/CHSC bitmaps, and `chpid_to_chp()` maps a `chp_id` into the active CSS channel-path table.

## Control Flow
The header contains no standalone execution, but callers use it to move between hardware IDs and registered kernel objects. CHSC/CSS/device event code builds `struct chp_link` values, resolves them with `chp_ssd_get_mask()`, and calls channel-path APIs to update descriptors, schedule configuration, or compute operational path masks.

## State and Persistence
The header declares volatile in-kernel structures only. `chpid_to_chp()` assumes the singleton `css_by_id()` model and that `channel_subsystems[0]` is initialized. No persistent storage is defined.

## Dependencies and Integration Points
It depends on Linux device/mutex types, `asm/chpid.h`, `chsc.h`, and `css.h`. It is the contract shared by `chp.c`, `chsc.c`, `css.c`, `device.c`, and measurement code.

## Risks and Test Signals
Risk areas are singleton-CSS assumptions, direct array indexing by hardware ids, and declaration drift between channel-path structures and CHSC descriptor formats. Test signals are compile coverage of all includers, channel-path registration with valid and invalid CHPID values, and path-event propagation using full and partial FLA masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.c

## Purpose
This file implements the common in-kernel Channel Subsystem Call (CHSC) services. It issues CHSC requests for subchannel, QDIO, channel-path, measurement, SCM, PNSO, GIB, and control-unit information; processes Store Event Information notifications from CSS CRWs; and propagates channel-path/resource events to CSS and CCW devices.

## Important APIs, Types, and Functions
Exports include `chsc_notifier_register()`, `chsc_error_from_response()`, `chsc_get_ssd_info()`, `chsc_ssqd()`, `chsc_sadc()`, `chsc_chp_online()`, `chsc_chp_offline()`, `chsc_chp_vary()`, `__chsc_do_secm()`, `chsc_secm()`, channel-path descriptor helpers, `chsc_get_channel_measurement_chars()`, `chsc_init()`, `chsc_enable_facility()`, `chsc_determine_css_characteristics()`, `chsc_siosl()`, `chsc_scm_info()`, `chsc_pnso()`, `chsc_sgib()`, and `chsc_scud()`. Shared globals are serialized CHSC/SEI pages, `chsc_page_lock`, `chsc_notifiers`, and exported `css_general_characteristics`/`css_chsc_characteristics`.

## Control Flow
Synchronous helpers allocate or reuse a page-aligned request area, fill CHSC headers/opcodes, issue `chsc()`, translate condition/response codes, and copy result payloads to caller structures. `chsc_process_crw()` handles CSS CRWs by repeatedly issuing SEI requests, with an old-firmware fallback when notification type masks are unsupported. NT0 events fan out to link-incident logging, resource accessibility scans, channel-path availability/configuration processing, SCM updates, AP config notifiers, and FCES path events. Channel-path online/offline/vary helpers update descriptors, wait for existing slow-path work, iterate affected subchannels, and schedule reprobes.

## State and Persistence
All state is in kernel memory or hardware-managed CHSC/CSS structures. `sei_page` and `chsc_page` are allocated at init and freed on cleanup. CSS characteristics persist in exported globals after detection. Channel measurement enable state is stored in `channel_subsystem.cm_enabled` and CHSC-programmed CUB/ECUB addresses. No disk persistence exists.

## Dependencies and Integration Points
The file depends on low-level `chsc()`, CRW registration, CIO debug logs, SCLP/CHSC architecture structures, CSS iteration, channel-path registration, SCM bus hooks, zPCI event handlers, AP config notifier users, QDIO, and CMF/CSS measurement data. It is the main firmware boundary for `chp.c`, `css.c`, `device.c`, QDIO, SCM, PCI, and network subchannel code.

## Risks and Test Signals
Risk areas include one shared CHSC page requiring strict locking, firmware response-code mapping, unsupported-notification fallback behavior, event-overflow recovery, channel-path event races with slow-path scans, and copying variable-length CHSC response blocks. Test signals include CHSC response-code fault injection, CRW/SEI event injection for each content code, channel-path add/remove/vary tests, SECM enable/disable with sysfs attributes, QDIO SSQD/SADC callers, `css_general_characteristics` detection, SCM/zPCI/AP notification paths, and `chsc_scud()` validation of malformed response lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.h

## Purpose
This header declares CHSC request/response layouts, channel-measurement descriptor formats, CSS characteristic structures, SCM information structures, and the public CHSC helper API used throughout s390 common I/O.

## Important APIs, Types, and Functions
Important types include `struct cmg_chars`, `struct cmg_cmcb`, `struct cmg_entry`, `struct cmg_ext_entry`, `struct channel_path_desc_fmt1`, `struct channel_path_desc_fmt3`, `struct css_chsc_char`, `struct chsc_ssd_info`, `struct chsc_ssqd_area`, `struct chsc_scssc_area`, `struct chsc_scpd`, `struct chsc_sda_area`, `struct sale`, and `struct chsc_scm_info`. It declares CHSC helpers for SSD, CSS characteristics, facility enable, channel-path vary/descriptions, measurement characteristics, SSQD/SADC/SGIB/SIOSL/SCM/PNSO, SCUD, and CSSID/IID lookup.

## Control Flow
The header has no executable logic except SCM stubs compiled when `CONFIG_SCM_BUS` is absent. It defines the packed ABI blocks that implementation functions fill before issuing CHSC instructions, and the declarations that let device, CSS, CMF, QDIO, SCM, and PCI code call into `chsc.c`.

## State and Persistence
The header declares exported `css_chsc_characteristics` and the external CHSC state contracts, but it does not allocate state. CHSC request areas are transient and page-aligned by callers. No persistence is defined.

## Dependencies and Integration Points
It depends on Linux types/device declarations and architecture headers for CSS characteristics, CHPID, CHSC, SCHID, and QDIO layouts. Its packed structures are hardware ABI integration points, so alignment and bitfield layout are part of the contract.

## Risks and Test Signals
Risk areas include bitfield packing drift across compilers/architecture headers, ABI-sized structure changes, feature-bit misinterpretation, and missing stubs for optional SCM users. Test signals include compile-time size/alignment checks where available, boot-time CHSC characteristic detection, QDIO/SADC and SCM callers, and cross-file builds that include `chsc.h` without extra hidden dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.c

## Purpose
This module is the driver for CHSC subchannels and the `/dev/chsc` misc interface. It enables CHSC subchannels, starts asynchronous CHSC requests on available subchannels, exposes multiple CHSC ioctls to userspace tooling, and supports an optional CHSC command to run when the device file closes.

## Important APIs, Types, and Functions
Key state includes CHSC debug logs, `on_close_request`, `on_close_chsc_area`, `on_close_mutex`, `chsc_lock`, and `chsc_ready_for_use`. The CSS driver callbacks are `chsc_subchannel_probe()`, `chsc_subchannel_irq()`, `chsc_subchannel_remove()`, and `chsc_subchannel_shutdown()`. Request handling centers on `chsc_async()`, `chsc_examine_irb()`, `chsc_ioctl_start()`, `chsc_ioctl_start_sync()`, info ioctls for channel paths/control units/subchannels/configuration/component lists/DCAL, and on-close set/remove handling.

## Control Flow
Module init creates CHSC debug logs, registers the CHSC interruption subclass, registers a CSS driver for subchannel type `SUBCHANNEL_TYPE_CHSC`, and registers the misc device. Probe allocates `struct chsc_private`, stores it as driver data, and enables the subchannel. `chsc_async()` scans enabled, idle CHSC subchannels, sets the request key/SID, issues `chsc()`, and either completes synchronously, records an in-progress request for IRQ completion, or retries another subchannel. IRQ completion copies the IRB, updates SCHIB, completes the request, and drops the subchannel device reference. Ioctls allocate page request areas, copy user input, issue synchronous or asynchronous CHSC commands, then copy results back.

## State and Persistence
State is volatile. Only one `/dev/chsc` opener is allowed through `chsc_ready_for_use`. The on-close command persists only while the device file is open and is freed during release or remove. In-flight asynchronous requests are stored in each subchannel's `chsc_private`. Debug data is kept by the s390 debug feature.

## Dependencies and Integration Points
The module depends on CSS driver registration, low-level `chsc()`, CIO subchannel enable/disable/update helpers, CHSC architecture ioctl structures, `copy_from_user()`/`copy_to_user()`, miscdevice infrastructure, CHSC interruption subclass registration, and the s390 debug feature. It bridges privileged userspace CHSC tools to CHSC subchannel hardware.

## Risks and Test Signals
Risk areas include user-provided page-sized CHSC requests, async request lifetime across remove/release, single-open behavior, global on-close state, response-length copies into user structures, and condition-code/IRB interpretation. Test signals include probing/removing CHSC subchannels, concurrent `/dev/chsc` opens returning `-EBUSY`, each ioctl with valid and malformed payloads, async completion and no-request IRQ logs, on-close execution/removal, and teardown while a request is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.h

## Purpose
This private header defines the tiny request/private-state structures shared within the CHSC subchannel driver.

## Important APIs, Types, and Functions
`struct chsc_request` contains a completion and the IRB copied by the interrupt handler. `struct chsc_private` stores the currently active request pointer for a CHSC subchannel.

## Control Flow
There is no executable logic. `chsc_sch.c` initializes `chsc_request.completion`, assigns the request pointer before an asynchronous CHSC starts, and the IRQ handler clears the pointer and completes the request.

## State and Persistence
The structures hold only transient in-kernel request state. No persistent storage or exported API is defined.

## Dependencies and Integration Points
The header relies on includers having completion and IRB types available. It is local to the CHSC subchannel module and not a broad subsystem contract.

## Risks and Test Signals
Risk areas are request lifetime and header dependence on include order. Test signals are async CHSC ioctl completion, module remove while a request exists, and compile coverage of `chsc_sch.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/cio.c

## Purpose
This file implements the low-level s390 common I/O instruction wrappers and interrupt entry point for subchannels. It starts, resumes, halts, clears, cancels, configures, enables/disables, and interrogates subchannels, handles I/O interrupts, and supports early CCW console subchannels.

## Important APIs, Types, and Functions
Exports include debug identifiers, per-CPU `cio_irb`, `cio_set_options()`, `cio_start_key()`, `cio_start()`, `cio_resume()`, `cio_halt()`, `cio_clear()`, `cio_cancel()`, `cio_cancel_halt_clear()`, `cio_commit_config()`, `cio_update_schib()`, `cio_enable_subchannel()`, `cio_disable_subchannel()`, `init_cio_interrupts()`, console helpers when enabled, `cio_tm_start_key()`, and `cio_tm_intrg()`. It uses low-level I/O instructions from `ioasm.h`: `ssch`, `rsch`, `hsch`, `csch`, `xsch`, `stsch`, `msch`, and `tsch`.

## Control Flow
`cio_debug_init()` creates CIO message/trace/CRW debug areas early. Start paths build command-mode or transport-mode ORBs with interrupt parameters pointing back to the subchannel, issue `ssch`, and translate condition codes. Halt/clear/cancel/resume wrappers issue the corresponding instruction and update pending bits. `cio_cancel_halt_clear()` is a staged teardown sequence: cancel once if possible, halt up to three times, then clear up to 255 times, returning `-EBUSY` while asynchronous completion is expected. Configuration flows update a local SCHIB, call `msch`, verify the hardware accepted the target config, and retry status-pending/busy cases. `do_cio_interrupt()` reads the TPI info, `tsch()`s the IRB, updates SCSW, and dispatches to the bound CSS driver IRQ callback.

## State and Persistence
State is volatile per-subchannel SCHIB/config/ORB data and per-CPU IRBs. `cio_commit_config()` copies successful hardware state into `sch->schib`. Console support stores an early `console_sch` pointer and configures the console ISC. Hardware subchannel state persists until reconfigured by another instruction or reset, but the file itself has no disk persistence.

## Dependencies and Integration Points
It depends on architecture I/O instructions, interrupt setup, IRQ statistics, ftrace tracepoints, airq/ISC setup, CSS subchannel objects, IO-subchannel private ORBs, channel-path status, blacklist/console configuration, and CCW/transport-mode callers. It is the lowest common execution layer for `device.c`, `chsc_sch.c`, CMF, QDIO, and CCW drivers.

## Risks and Test Signals
Risk areas include condition-code translation, stale SCHIB state after failed `stsch`/`msch`, interrupt `intparm` validity, cancel/halt/clear retry exhaustion, concurrent config changes under subchannel locks, and console paths running before full bus registration. Test signals include instruction fault injection, start/halt/clear/cancel status-pending paths, enable retry without concurrent-sense after `-EIO`, transport-mode start/interrogate, no-intparm interrupts, IRQ handler dispatch with and without drivers, and early console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/cio.h

## Purpose
This header defines core s390 CIO hardware data structures and the internal subchannel API used by CSS, CCW-device, CHSC, CMF, and low-level I/O code.

## Important APIs, Types, and Functions
It defines packed `struct pmcw`, `struct schib_config`, `struct schib`, `enum sch_todo`, and `struct subchannel`. `struct subchannel` carries the hardware id, locks, subchannel type, path masks, current SCHIB, desired ISC, SSD info, Linux device, bound CSS driver, slow-path todo work, target config, and DMA mask. It declares low-level CIO operations for start/resume/halt/clear/cancel, config commit/update, subchannel enable/disable, transport-mode I/O, airq init, console probing, and per-CPU `cio_irb`.

## Control Flow
The header contributes no runtime logic except compile-time console stubs. Implementations use `struct subchannel.config` as the desired state and `schib` as the last observed hardware state, with `enum sch_todo` controlling CSS slow-path work priority.

## State and Persistence
All structures model volatile hardware/kernel state. No data is persisted. Packing/alignment are part of the hardware ABI and DMA-visible contract.

## Dependencies and Integration Points
It depends on architecture CIO, FCX, SCHID, TPI, CHPID, and Linux device/mod_devicetable types, plus `chsc.h` for SSD info. It is the central type contract for nearly every file in this subset.

## Risks and Test Signals
Risk areas include packed bitfield layout, mismatches between desired config and hardware SCHIB, subchannel lifetime/reference handling, and assuming console stubs are safe when `CONFIG_CCW_CONSOLE` is off. Test signals are full s390 CIO build coverage, subchannel registration/probe, MSCH config verification, transport-mode callers, and lockdep coverage around `subchannel.lock` and `reg_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debug.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debug.h

## Purpose
This header centralizes CIO debug-feature handles and logging macros for message, trace, and channel-report-word diagnostics, and declares the shared CIO debugfs directory.

## Important APIs, Types, and Functions
It declares `cio_debug_msg_id`, `cio_debug_trace_id`, `cio_debug_crw_id`, `cio_debugfs_dir`, and macros `CIO_TRACE_EVENT()`, `CIO_MSG_EVENT()`, `CIO_CRW_EVENT()`, plus inline `CIO_HEX_EVENT()`. These wrap the s390 `debug_*` APIs.

## Control Flow
The macros emit text, sprintf, or hex trace records to debug-feature buffers initialized in `cio.c`. There is no independent control flow in the header.

## State and Persistence
State lives in debug-feature buffers and the debugfs dentry created elsewhere. Logs are in-memory kernel debug data, not persistent storage.

## Dependencies and Integration Points
It depends on `<asm/debug.h>` and is included by most CIO/CHSC/CSS/channel-path files. `cio_debugfs_dir` is used by debugfs feature files such as CRW injection.

## Risks and Test Signals
Risk areas include logging before debug areas are initialized, null debug handles on init failure, and format-string mismatch in variadic macros. Test signals include boot-time debug area creation, trace visibility under `/sys/kernel/debug/s390`, CRW/event logging, and builds with debug feature support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debugfs.c

## Purpose
This small file creates the shared CIO debugfs directory used by optional CIO debugging interfaces.

## Important APIs, Types, and Functions
It defines global `struct dentry *cio_debugfs_dir` and `cio_debugfs_init()`, which calls `debugfs_create_dir("cio", arch_debugfs_dir)` during `subsys_initcall`.

## Control Flow
At subsystem init time, the file creates `/sys/kernel/debug/s390/cio` under the architecture debugfs directory and returns success. Other files can then create files below `cio_debugfs_dir`.

## State and Persistence
The only state is the debugfs dentry pointer. Debugfs entries are runtime-only and disappear at unmount/reboot.

## Dependencies and Integration Points
It depends on Linux debugfs and `cio_debug.h`. `cio_inject.c` uses this directory for `enable_inject` and `crw_inject`.

## Risks and Test Signals
Risk areas include debugfs being unavailable or `arch_debugfs_dir` not initialized as expected; the function does not check for an error dentry. Test signals are the presence of `/sys/kernel/debug/s390/cio`, successful creation of child debugfs files, and boot ordering relative to `cio_inject_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.c

## Purpose
This file implements a debugfs-based CIO test hook for injecting synthetic Channel Report Words. It lets developers trigger the CRW handling path without waiting for hardware machine checks.

## Important APIs, Types, and Functions
State includes `crw_inject_lock`, static key `cio_inject_enabled`, and one pending `crw_inject_data` pointer. Key functions are `crw_inject()`, `stcrw_get_injected()`, `crw_inject_write()`, `enable_inject_write()`, and `cio_inject_init()`. Debugfs files are `enable_inject` and `crw_inject`.

## Control Flow
Userspace first writes `1` to `enable_inject`, enabling the static branch. A write to `crw_inject` parses seven hex fields into a `struct crw`, stores a kmemdup copy if no injection is pending, and calls `crw_handle_channel_report()`. The CRW collector path calls `stcrw_get_injected()` instead of or alongside hardware retrieval when injection is enabled; this copies the synthetic CRW to the caller and frees the pending object.

## State and Persistence
Only one injected CRW can be pending. The pending object is protected by `crw_inject_lock` and is consumed once. The static key controls runtime overhead and state is not persistent.

## Dependencies and Integration Points
It depends on `CONFIG_CIO_INJECT`, debugfs, CRW handling, `cio_debugfs_dir`, static branches, and architecture CRW definitions. It integrates directly with `crw.c` through `stcrw_get_injected()` and `crw_handle_channel_report()`.

## Risks and Test Signals
Risk areas include malformed debugfs input, stale pending CRWs blocking new injections with `-EBUSY`, debugfs init ordering, and ensuring injection is compiled out or inert when disabled. Test signals include enabling/disabling the static key, invalid format handling, one-shot CRW consumption, overflow/chained CRW test injections, and CRW dispatcher callbacks seeing synthetic events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.h

## Purpose
This header declares the optional CRW injection interface used by the CRW retrieval path when CIO injection support is enabled.

## Important APIs, Types, and Functions
Under `CONFIG_CIO_INJECT`, it includes `asm/crw.h`, declares static key `cio_inject_enabled`, and declares `stcrw_get_injected(struct crw *crw)`.

## Control Flow
The header has no runtime flow. Compile-time configuration controls whether the declarations are visible to callers.

## State and Persistence
It declares volatile test state only; no persistent storage is involved.

## Dependencies and Integration Points
It integrates `cio_inject.c` with CRW collection code and depends on the architecture CRW type. Callers must guard uses with `CONFIG_CIO_INJECT` or include this header under matching configuration.

## Risks and Test Signals
Risk areas include configuration mismatches and missing stubs for disabled builds if callers are not conditionalized. Test signals are builds with and without `CONFIG_CIO_INJECT` and runtime CRW injection through debugfs when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cmf.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/cmf.c

## Purpose
This file implements the s390 Channel Measurement Facility for CCW devices. It allocates channel measurement blocks, enables/disables subchannel measurement, exposes per-device measurement sysfs attributes, reads accumulated timing/count data, and reactivates measurement after recovery or hibernation.

## Important APIs, Types, and Functions
Important types are `enum cmb_index`, `enum cmb_format`, `struct cmb_operations`, `struct cmb_data`, `struct cmb_area`, basic `struct cmb`, and extended `struct cmbe`. Public functions are `enable_cmf()`, `disable_cmf()`, `cmf_read()`, `cmf_readall()`, `cmf_reenable()`, `cmf_reactivate()`, `retry_set_schib()`, and `cmf_retry_copy_block()`. Module parameters select `format` and basic `maxchannels`. `cmbops_basic` and `cmbops_extended` abstract allocation, setup, read, read-all, reset, and sysfs attributes.

## Control Flow
`init_cmf()` autodetects basic versus extended measurement using CSS characteristics unless overridden. Enabling a device locks the device, allocates a measurement block, resets it, creates the `cmf` sysfs group, and calls the format-specific `set()` to update the subchannel SCHIB measurement mode. Basic mode allocates one global contiguous CMB array and uses indices; extended mode allocates per-device cache-aligned CMBEs and programs a block address. Reads either sample individual live fields or copy a stable block after waiting for in-progress I/O to quiesce through temporary `DEV_STATE_CMFCHANGE` or `DEV_STATE_CMFUPDATE` state-machine states.

## State and Persistence
State is volatile. Per-device `cdev->private->cmb` points to `struct cmb_data`, with hardware and last-copied blocks plus timestamps. Global `cmb_area` tracks all measured devices and the basic global CMB array; `cmbe_cache` owns extended blocks. Hardware accumulates counts/times until reset/disable. There is no disk persistence.

## Dependencies and Integration Points
It depends on CCW device private state and locks, CIO subchannel configuration, `cio_commit_config()`, TOD clock conversion, sysfs, module parameters, CSS characteristic detection, and the s390 `schm` instruction. `device.c` exposes `cmb_enable`, disables CMF on remove/shutdown, and calls retry helpers from the CCW state machine.

## Risks and Test Signals
Risk areas include global CMB array sizing, measurement block lifetime while hardware may update it, state-machine waits timing out or being interrupted, read atomicity during active I/O, basic versus extended format selection, sysfs cleanup on partial enable failure, and disabling after the device disappeared. Test signals include boot with `s390cmf` parameters, enabling/disabling `cmb_enable`, readout of all basic/extended attributes, active-I/O read waits, CMF reenable after disconnected recovery, hibernate resume reactivation, allocation exhaustion, and subchannel removal during measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/cmf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/crw.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/crw.c

## Purpose
This file implements Channel Report Word machine-check dispatch for s390 CIO. It registers per-reporting-source handlers, runs a kernel thread that drains CRWs, handles chained/overflow reports, and enables channel-report machine checks.

## Important APIs, Types, and Functions
Public APIs are `crw_register_handler()`, `crw_unregister_handler()`, `crw_handle_channel_report()`, and `crw_wait_for_channel_report()`. Internal state includes `crw_handler_mutex`, `crw_handlers[NR_RSCS]`, atomic request counter `crw_nr_req`, and wait queue `crw_handler_wait_q`. The collector thread is `crw_collect_info()`.

## Control Flow
Subsystem users register a handler for a CRW reporting source code. Machine-check notification calls `crw_handle_channel_report()`, incrementing `crw_nr_req` and waking `kmcheck`. The collector waits until work exists, repeatedly calls `stcrw()`, records up to two chained CRWs, calls all handlers on overflow, or dispatches the completed CRW/chained pair to the handler selected by `rsc`. When draining finishes, it decrements the request count and wakes waiters. Init starts `kmcheck` and sets the CR14 channel report submask bit.

## State and Persistence
All state is volatile. Handler registrations persist only while modules/subsystems remain loaded. CRWs are consumed from hardware or injection once read. There is no disk persistence.

## Dependencies and Integration Points
It depends on architecture control registers, `stcrw()`, kthreads, wait queues, and subsystem handlers registered by CSS/CHSC/channel-path code. When injection is enabled elsewhere, `stcrw()` retrieval may be substituted or augmented by synthetic CRW data.

## Risks and Test Signals
Risk areas include serialization under `crw_handler_mutex` while handlers run, only supporting two chained CRWs directly, overflow fanout to all handlers, signal handling in the collector, and handler registration races. Test signals include CRW injection for CSS/SCH/CPATH sources, overflow CRW handling, chained CRW pairs, unregister during idle, `crw_wait_for_channel_report()` draining, and boot verification that `kmcheck` starts and CR14 is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/crw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/css.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/css.c

## Purpose
This file implements the s390 Channel Subsystem bus (`css`), subchannel discovery/registration, CRW-driven slow-path evaluation, channel-subsystem sysfs attributes, a CSS-wide DMA pool, and CSS driver registration.

## Important APIs, Types, and Functions
Exports include `for_each_subchannel()`, `for_each_subchannel_staged()`, `css_alloc_subchannel()`, `css_register_subchannel()`, `css_sch_device_unregister()`, `get_subchannel_by_schid()`, `css_sch_is_valid()`, `css_sched_sch_todo()`, `css_schedule_eval()`, `css_schedule_eval_all()`, `css_schedule_eval_cond()`, `css_wait_for_slow_path()`, `css_schedule_reprobe()`, `css_complete_work()`, `sch_is_pseudo_sch()`, `css_driver_register()`, and `css_driver_unregister()`. It owns `css_init_done`, `max_ssid`, `channel_subsystems[]`, the `css_bus_type`, `slow_subchannel_set`, `cio_work_q`, and the CIO DMA gen_pool.

## Control Flow
`channel_subsystem_init()` initializes CHSC, detects CSS characteristics, enables multiple subchannel sets if possible, initializes slow-path state, registers CRW handlers and the CSS bus, creates the CSS device and pseudo subchannel, registers reboot cleanup, initializes DMA/airq/ISC state, registers the I/O subchannel driver, registers early console subchannels, and schedules full evaluation. Fast CRW handling calls `css_evaluate_subchannel(..., slow=0)`, which defers new/complex work with `-EAGAIN`. Slow-path work iterates staged known and unknown subchannels, probes new devices with `stsch()`/`css_probe_device()`, calls driver `sch_event()` for known subchannels, and tracks pending IDs in `slow_subchannel_set`. Sysfs `rescan` schedules and completes a full evaluation; `cm_enable` toggles CSS-wide channel measurement through CHSC.

## State and Persistence
State is in-memory bus/device state plus hardware subchannel status. Registered subchannels are Linux devices under the CSS bus. `slow_subchannel_set` records pending evaluations, `subchannel.todo` records per-subchannel work, and `channel_subsystem` stores channel paths, PGID, measurement buffers, and pseudo-subchannel. The DMA pool grows as needed and is freed only by explicit destroy paths. No disk persistence exists.

## Dependencies and Integration Points
It depends on CHSC initialization and characteristics, CRW source registration, low-level `stsch`, blacklist checks, CIO debug, idset helpers, Linux bus/device/workqueue APIs, reboot notifiers, DMA/genalloc, airq/ISC setup, and `device.c` for I/O subchannel handling. CSS drivers bind by subchannel type through `struct css_driver`.

## Risks and Test Signals
Risk areas include slow-path idset consistency, OOM fallback to brute-force scans, single-CSS assumptions, registration/unregistration races with workqueue references, subchannel validity rules for IO/MSG types, DMA pool growth and freeing, reboot-time CMF disable, and sysfs rescan blocking behavior. Test signals include full boot discovery, CRW-triggered add/remove/path-modification events, manual rescan, `cio_settle`, blacklisted device filtering, subchannel driver bind/unbind, pseudo-subchannel orphan movement, `cm_enable` toggling, DMA allocation/free users, and cleanup on init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/css.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/css.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/css.h

## Purpose
This header defines the CSS bus contract: path-grouping constants, PGID/path-state data, CSS driver callbacks, channel-subsystem state, slow-path scheduling APIs, and subchannel registration helpers.

## Important APIs, Types, and Functions
It defines path grouping constants (`SPID_*`, `SNID_*`), `enum css_eval_cond`, `struct path_state`, `struct extended_cssid`, `struct pgid`, `struct css_driver`, and `struct channel_subsystem`. Public declarations include CSS driver registration, subchannel allocation/registration/unregistration/lookup, staged and brute-force subchannel iteration, SSD refresh, slow-path scheduling/completion, pseudo-subchannel checks, `css_sch_is_valid()`, and the global `cio_work_q`.

## Control Flow
There is no standalone flow. CSS drivers provide `irq`, `chp_event`, `sch_event`, `probe`, `remove`, `shutdown`, and `settle` callbacks, which `css.c` invokes from interrupt and process contexts. Inline `css_by_id()` and `for_each_css()` currently map all lookups to the singleton CSS.

## State and Persistence
The header describes volatile CSS state: registered channel paths, global PGID, measurement buffers, pseudo-subchannel, and synchronization primitives. No persistence is defined.

## Dependencies and Integration Points
It depends on Linux device/workqueue/wait/mutex types and architecture CIO/CHPID/SCHID headers. It is included by channel-path, CHSC, CIO, device, and CMF code.

## Risks and Test Signals
Risk areas include singleton CSS helpers, callback context expectations, structure lifetime across bus unregister, and path-grouping bitfield layout. Test signals include compiling all CSS drivers, boot discovery, multi-subchannel-set enablement, slow-path scheduling, and future work involving multiple CSS instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/css.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/device.c

## Purpose
This file implements the CCW device bus and the CSS driver for I/O subchannels. It discovers CCW devices, drives recognition/online/offline state transitions, binds `ccw_driver`s, handles I/O subchannel interrupts/events/path changes, manages orphaned devices, exposes CCW/sysfs attributes, and coordinates recovery after lost paths or disconnected devices.

## Important APIs, Types, and Functions
Exports include `io_subchannel_init()`, `ccw_device_set_online()`, `ccw_device_set_offline()`, `get_ccwdev_by_dev_id()`, `get_ccwdev_by_busid()`, `ccw_driver_register()`, `ccw_driver_unregister()`, `ccw_purge_blacklisted()`, `ccw_device_set_disconnected()`, `ccw_device_set_notoper()`, `ccw_device_sched_todo()`, and `ccw_device_siosl()`. Key internal flows include `io_subchannel_probe()`, `io_subchannel_recog()`, `io_subchannel_register()`, `io_subchannel_sch_event()`, `io_subchannel_chp_event()`, `io_subchannel_quiesce()`, `sch_get_action()`, `ccw_device_move_to_sch()`, `ccw_device_move_to_orph()`, and recovery timer/work functions. Sysfs attributes include CCW ids/modalias/online/CMB enable/availability and subchannel logging/vpm.

## Control Flow
`io_subchannel_init()` registers the `ccw` bus and the `io_subchannel` CSS driver. Probe initializes path masks and config, commits SCHIB settings, creates subchannel sysfs attributes, allocates I/O private DMA state, and schedules subchannel evaluation. Evaluation either attaches a new `ccw_device`, moves an orphan back to a real subchannel, unregisters stale devices/subchannels, triggers recognition, or verifies paths. Recognition runs asynchronously through the device state machine and schedules registration work when the device reaches offline state. Online/offline sysfs and exported APIs synchronize with the device FSM, call driver `set_online`/`set_offline`, and roll back on failures. CHPID events adjust OPM/LPM/path masks, terminate I/O on affected paths, trigger verification, or forward FCES path events to drivers.

## State and Persistence
State is volatile in `struct ccw_device`, `ccw_device_private`, parent `struct subchannel`, work items, timers, and wait queues. Online devices hold an extra device reference. Orphaned devices are moved under the CSS pseudo-subchannel while waiting for a matching subchannel to return. Recovery uses `recovery_timer`, `recovery_work`, `recovery_phase`, and escalating delays. No disk persistence exists; hardware subchannel/device state is re-read through SCHIB and device-recognition I/O.

## Dependencies and Integration Points
The file depends on the CCW device state-machine functions declared in `device.h` and implemented in sibling files, low-level CIO instruction wrappers, CSS bus callbacks, CHSC SIOSL, channel-path masks, blacklist handling, CMF, DMA/gen_pool helpers, Linux driver core, sysfs, timers/workqueues, and optional CCW console support. External CCW drivers integrate through `struct ccw_driver` probe/remove/shutdown/set_online/set_offline/path_event callbacks.

## Risks and Test Signals
Risk areas include complex lock ordering between `sch->lock`, device locks, and registration mutexes; async work references during unregister/move; races among CRW events, online/offline sysfs writes, recognition, and driver binding; handling devices that vanish, change devno, or lose all paths; CMF cleanup on remove/shutdown; and forced online from boxed state. Test signals include boot-time CCW discovery, driver modalias/probe matching, online/offline success and rollback, no-path/disconnected recovery, orphan move/reprobe, blacklist purge, CHPID vary/offline/online/FCES events, console subchannel path, `logging` sysfs SIOSL, CMF enable during remove, and CRW injection for subchannel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/device.h

## Purpose
This header declares the CCW device finite-state-machine states/events and the internal helper APIs used by the CCW bus, I/O subchannel driver, recognition/path-verification code, request handling, timeout handling, machine-check recovery, and CMF integration.

## Important APIs, Types, and Functions
It defines `enum dev_state` with normal, recognition, online/offline, verification, boxed, quiesce, disconnected, CMF, and lock-stealing states; `enum dev_event` for not-operational, interrupt, timeout, and verify events; `fsm_func_t`; and external `dev_jumptable`. Inline `dev_fsm_event()` increments IRQ stats for interrupt events and dispatches the state-machine action. It declares helper APIs for subchannel init/recognition, online/offline, sense, internal request handling, path grouping/verification/disband, STLOCK, recovery, timers, not-operational/disconnected transitions, CMF retry/reactivation, and `dev_attr_cmb_enable`.

## Control Flow
The core inline flow is `dev_fsm_event()`: read the current private state, update interrupt accounting when needed, and call the state/event function from `dev_jumptable`. `dev_fsm_final_state()` identifies stable states that online/offline and recognition wait loops use.

## State and Persistence
The header defines symbolic state values but no storage. Runtime state lives in `ccw_device_private` owned by `asm/ccwdev.h`/implementation files. There is no persistence.

## Dependencies and Integration Points
It depends on CCW device definitions, timers, atomics, wait queues, notifiers, IRQ stats, and `io_sch.h`. It is the coordination contract between `device.c`, device FSM implementation files, path-grouping code, request code, and `cmf.c`.

## Risks and Test Signals
Risk areas include jumptable coverage for every state/event pair, interrupt accounting in special CMF states, wait loops relying on final-state classification, and state additions that require updates across multiple implementation files. Test signals include state-machine table compile coverage, interrupt/timeout/not-operational event injection, online/offline wait completion, CMF change/update retries, disconnected recovery, and path-verification/disband transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device.h -->
