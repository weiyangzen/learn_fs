# subset-b-005468 Research

Grouped source research for VT ioctl handling and UFS core support files under `sources/distributed-fs/ceph-client`. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/vt_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/vt_ioctl.c

## Purpose

`vt_ioctl.c` implements Linux virtual terminal and keyboard/display ioctl handling for console ttys. It bridges user ABI commands such as `KD*`, `VT_*`, palette/screen-map/unimap controls, font operations, process-controlled VT switching, compatibility ioctl conversion, and suspend/resume VT switching into the console, keyboard, tty, and selection subsystems.

## Important APIs, Types, and Functions

Exported or externally used functions include `vt_ioctl()`, `vt_compat_ioctl()`, `vt_waitactive()`, `vt_event_post()`, `reset_vc()`, `vc_SAK()`, `change_console()`, `vt_move_to_console()`, and exported `pm_set_vt_switch()`. `struct vt_event_wait` is the local wait-list node for `VT_WAITEVENT` and legacy active-console waits. `vt_k_ioctl()` handles keyboard/display `KD*` commands, `vt_io_ioctl()` handles palette and Unicode map operations, `vt_reldisp()` completes process-mode handshakes, and `complete_change_console()` performs the locked backend switch.

## Control Flow

`vt_ioctl()` first determines permission from controlling tty ownership or `CAP_SYS_TTY_CONFIG`, dispatches keyboard/display ioctls, then display-map ioctls, then the VT-specific switch. VT activation allocates the requested console under `console_lock` and calls `set_console()`. In `VT_PROCESS` mode, `change_console()` signals the current foreground VT owner and records `vt_newvt`; userspace later calls `VT_RELDISP` to allow or reject the switch. `complete_change_console()` switches screens, blanks/unblanks around graphics/text transitions, signals acquire events, resets dead process-controlled VTs, and posts `VT_EVENT_SWITCH`.

## State and Persistence Behavior

State is in `vc_data` fields (`vc_mode`, `vt_mode`, `vt_pid`, `vt_newvt`, geometry, font mask), global `fg_console`, `last_console`, `vt_dont_switch`, `disable_vt_switch`, `vt_events`, and keyboard state managed by helpers. No on-disk persistence exists; effects are live console mode, keymaps, fonts, palettes, Unicode maps, tty line discipline flushing, I/O permissions on x86, and process signals.

## Dependencies and Integration Points

The file depends on tty core, console locking, keyboard helpers, console font/map helpers, selection state, SAK handling, x86 `ioperm`, PM suspend helpers, pid/signal APIs, `uaccess`, and nospec array bounds hardening. It is the user ABI entry point for virtual terminal control and the kernel-internal path used by suspend code to move consoles.

## Risks and Test Signals

Risks include incorrect permission checks for mutating ioctls, process-mode switch races around `vt_newvt` and signals, missed `console_lock` protection when reading/deallocating `vc_data`, geometry resize rollback gaps, compatibility pointer conversion mistakes, event wait interruption handling, and stale graphics mode after owner death. Test signals include `KDSETMODE` blanking behavior, `VT_SETMODE` plus `VT_RELDISP` handshakes, `VT_WAITACTIVE` interruption, `VT_DISALLOCATE` busy rejection, `VT_WAITEVENT` payload conversion to 1-based VTs, compat `KDFONTOP`/unimap calls, suspend `vt_move_to_console()`, and permission denial for non-owner callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/vt_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ufs/Kconfig

## Purpose

This Kconfig file defines the top-level UFS host controller menu entry. It enables the generic `ufshcd` core and conditionally includes core and host-controller submenus.

## Important APIs, Types, and Functions

The key symbol is `SCSI_UFSHCD`, a tristate menuconfig named "Universal Flash Storage Controller". It depends on `SCSI`, `SCSI_DMA`, and a compatible `RPMB` setting, and selects `PM_DEVFREQ`, `DEVFREQ_GOV_SIMPLE_ONDEMAND`, and `NLS`.

## Control Flow

When `SCSI_UFSHCD` is enabled, the Kconfig parser sources `drivers/ufs/core/Kconfig` and `drivers/ufs/host/Kconfig`. Disabled top-level UFS support hides all subordinate UFS core and host options.

## State and Persistence Behavior

The file persists build-time configuration only through generated kernel config. It does not create runtime state, but choosing `m` or `y` affects whether UFS storage is available early enough for root filesystems.

## Dependencies and Integration Points

It integrates the UFS subsystem into the SCSI driver tree and ensures devfreq/simple-ondemand and NLS support are selected for the core driver.

## Risks and Test Signals

Risks are dependency mismatches, especially root-on-UFS systems built as modules, and unintended changes to selected dependencies. Test signals are `allyesconfig`, `allmodconfig`, rootfs boot configs, and visibility of core/host options only under enabled `SCSI_UFSHCD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ufs/Makefile

## Purpose

This Makefile wires the top-level UFS directory into the kernel build.

## Important APIs, Types, and Functions

The single build rule adds `core/` and `host/` to `obj-$(CONFIG_SCSI_UFSHCD)`.

## Control Flow

If `CONFIG_SCSI_UFSHCD` is enabled, kbuild descends into the UFS core and host subdirectories. The comment notes link order is important: the generic core must initialize before vendor host drivers.

## State and Persistence Behavior

No runtime state exists. Build artifacts and module linkage are affected by the selected configuration.

## Dependencies and Integration Points

This file integrates UFS with kbuild and enforces core-before-host ordering that host glue drivers rely on.

## Risks and Test Signals

Risks are link-order regressions and missing subdirectory traversal. Test signals include built-in and modular builds verifying `ufshcd-core` symbols are available to host drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/Kconfig

## Purpose

`core/Kconfig` defines optional features for the generic UFS host controller core.

## Important APIs, Types, and Functions

Symbols are `SCSI_UFS_BSG`, `SCSI_UFS_CRYPTO`, `SCSI_UFS_FAULT_INJECTION`, and `SCSI_UFS_HWMON`. BSG selects `BLK_DEV_BSGLIB`; crypto depends on `BLK_INLINE_ENCRYPTION`; fault injection depends on `FAULT_INJECTION`; hwmon depends on compatible `HWMON` linkage.

## Control Flow

The options are only visible after the top-level `SCSI_UFSHCD` menu is enabled. Each option controls whether its corresponding core object and public stubs compile into `ufshcd-core`.

## State and Persistence Behavior

The file affects compile-time feature presence: BSG device nodes, inline encryption keyslot support, fault injection attributes, and hwmon temperature device creation. It has no runtime state itself.

## Dependencies and Integration Points

It integrates UFS with block BSG, blk-crypto, kernel fault-injection/debugfs, and hwmon subsystems.

## Risks and Test Signals

Risks include enabling user ABI surfaces without their subsystem dependencies and mismatched built-in/module constraints. Test signals are config matrix builds and runtime checks that disabled options compile to inert inline stubs while enabled options create the expected sysfs/debugfs/device nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/Makefile

## Purpose

This Makefile builds the generic UFS core module or built-in object.

## Important APIs, Types, and Functions

`ufshcd-core.o` always includes `ufshcd.o`, `ufs-sysfs.o`, `ufs-mcq.o`, and `ufs-txeq.o`. Optional objects are `ufs-rpmb.o`, `ufs-debugfs.o`, `ufs_bsg.o`, `ufshcd-crypto.o`, `ufs-fault-injection.o`, and `ufs-hwmon.o` based on their config symbols.

## Control Flow

kbuild aggregates the listed objects into `ufshcd-core.o` when `CONFIG_SCSI_UFSHCD` is enabled.

## State and Persistence Behavior

No runtime state is stored here. The file determines which runtime features and ABI entry points exist in the built driver.

## Dependencies and Integration Points

It connects Kconfig choices to actual object inclusion and keeps core UFS support centralized for host glue drivers.

## Risks and Test Signals

Risks are missing optional objects after Kconfig enablement, unconditional references to disabled features, and object-order surprises. Test signals include build coverage for each optional symbol and module load with all combinations supported by dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.c

## Purpose

`ufs-debugfs.c` exposes diagnostic and control files under debugfs for UFS host instances: event counters, saved error injection into the error handler, exception-event mask throttling, and TX equalization inspection/retraining controls.

## Important APIs, Types, and Functions

Public functions are `ufs_debugfs_init()`, `ufs_debugfs_exit()`, `ufs_debugfs_hba_init()`, `ufs_debugfs_hba_exit()`, and `ufs_debugfs_exception_event()`. `struct ufs_debugfs_attr` describes file names, modes, and fops. Important handlers include `ufs_debugfs_stats_show()`, `ee_usr_mask_set()`, `ufs_saved_err_write()`, `ufs_tx_eq_params_show()`, `ufs_tx_eqtr_record_show()`, and `ufs_tx_eq_ctrl_write()`.

## Control Flow

Global init creates `/sys/kernel/debug/ufshcd`. Per-HBA init creates a child directory, registers common files, exception event controls, and per-HS-gear TXEQ directories when `UFSHCD_CAP_TX_EQUALIZATION` is set. User writes to `saved_err`/`saved_uic_err` update HBA error fields under `host_lock` and schedule error handling. Exception events may temporarily mask user-enabled exception bits and queue delayed restoration. Writing `retrain` to `tx_eq_ctrl` gates access, resumes runtime PM, and invokes `ufshcd_retrain_tx_eq()`.

## State and Persistence Behavior

State lives in `hba->debugfs_root`, `debugfs_ee_rate_limit_ms`, delayed work, error fields, exception masks, and TXEQ records in `hba->tx_eq_params`. Debugfs state is runtime-only and disappears on driver unload.

## Dependencies and Integration Points

It depends on debugfs, seq_file, runtime PM helpers, UFS error handling, exception event control, and TXEQ helpers in `ufs-txeq.c`. It uses `host_sem` and `ufshcd_is_user_access_allowed()` before device-affecting operations.

## Risks and Test Signals

Risks include debugfs-only writes causing error-handler storms, exception mask restoration races across runtime suspend, file-name-based dispatch mistakes, and TXEQ retraining while the device is not operational. Test signals include debugfs tree creation/removal, stats counter output, saved error writes scheduling EH, exception rate-limit masking/restoration, TXEQ record rendering for invalid/valid gears, and `retrain` denial when access is busy or unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.h

## Purpose

This header declares the UFS debugfs integration points and provides no-op stubs when debugfs is disabled.

## Important APIs, Types, and Functions

It forward-declares `struct ufs_hba` and declares `ufs_debugfs_init()`, `ufs_debugfs_exit()`, `ufs_debugfs_hba_init()`, `ufs_debugfs_hba_exit()`, and `ufs_debugfs_exception_event()`.

## Control Flow

There is no runtime control flow in the header. Compile-time `CONFIG_DEBUG_FS` selects real declarations or inline empty stubs.

## State and Persistence Behavior

The header owns no state. It controls whether callers need conditional compilation around debugfs hooks.

## Dependencies and Integration Points

It integrates `ufshcd.c` and other core code with `ufs-debugfs.c` while preserving clean builds without debugfs.

## Risks and Test Signals

Risks are signature drift between stubs and implementation and callers assuming side effects when debugfs is disabled. Test signals are builds with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.c

## Purpose

`ufs-fault-injection.c` adds fault-injection knobs for testing UFS error and timeout paths.

## Important APIs, Types, and Functions

Public functions are `ufs_fault_inject_hba_init()`, `ufs_trigger_eh()`, and `ufs_fail_completion()`. Module parameters `trigger_eh` and `timeout` use `ufs_fault_ops`, `setup_fault_attr()`, and per-HBA `fault_attr` copies.

## Control Flow

Module parameter writes parse standard fault-injection tuples into static template attributes and preserve the input string for reads. HBA init copies templates into `hba->trigger_eh_attr` and `hba->timeout_attr`, and optionally creates debugfs attributes. Runtime callers ask `should_fail()` to decide whether to trigger error handling or fail completion.

## State and Persistence Behavior

State is runtime kernel module parameter strings plus per-HBA fault attributes. It is not persisted beyond module lifetime.

## Dependencies and Integration Points

It depends on `FAULT_INJECTION`, optional fault-injection debugfs, module parameters, and `struct ufs_hba` fields consumed by core error paths.

## Risks and Test Signals

Risks include malformed parameter strings, global templates being copied only at HBA init time, and accidentally enabling aggressive failures on production systems. Test signals include parameter read/write parsing, debugfs attribute creation, deterministic `should_fail()` behavior for interval/probability/times settings, and disabled-config stubs returning false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.h

## Purpose

This header defines the compile-time contract for UFS fault injection.

## Important APIs, Types, and Functions

It declares `ufs_fault_inject_hba_init()`, `ufs_trigger_eh()`, and `ufs_fail_completion()` when enabled, and inline no-op/false stubs otherwise.

## Control Flow

No runtime control flow is present. `CONFIG_SCSI_UFS_FAULT_INJECTION` selects real hooks.

## State and Persistence Behavior

The header owns no state and lets core code call fault-injection hooks unconditionally.

## Dependencies and Integration Points

It depends on `linux/kconfig.h`, `linux/types.h`, and a forward declaration of `struct ufs_hba`.

## Risks and Test Signals

Risks are mismatched stub semantics and accidental build dependencies on fault-injection internals. Test signals are compile coverage for enabled and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-hwmon.c

## Purpose

`ufs-hwmon.c` exposes UFS temperature monitoring through the Linux hwmon subsystem and forwards UFS exception events as hwmon alarms.

## Important APIs, Types, and Functions

`struct ufs_hwmon_data` stores the `ufs_hba` pointer and enabled exception mask. Public functions are `ufs_hwmon_probe()`, `ufs_hwmon_remove()`, and `ufs_hwmon_notify_event()`. Core callbacks are `ufs_hwmon_read()`, `ufs_hwmon_write()`, and `ufs_hwmon_is_visible()`.

## Control Flow

Probe allocates per-device data and registers a hwmon chip named `ufs` with one temp channel exposing enable, input, critical, and low-critical values. Reads lock `host_sem`, reject access while shutting down, resume runtime PM, then query UFS temperature and boundary attributes. Writes only accept `temp_enable` values 0 or 1 and update the user exception-event mask for urgent temperature notifications.

## State and Persistence Behavior

Runtime state is `hba->hwmon_device`, allocated `ufs_hwmon_data`, and UFS device exception-event masks. Temperature values come from device attributes and are converted from UFS encoded Celsius offset to millidegrees Celsius.

## Dependencies and Integration Points

It depends on hwmon, UFS query attributes, runtime PM, `host_sem`, and exception-event mask helpers. It integrates UFS thermal alerts with standard userspace monitoring.

## Risks and Test Signals

Risks include query failures returning transient sysfs errors, incorrect enable reporting when masks are partially supported, temperature value zero mapping to `-ENODATA`, and alarm notification mismatch. Test signals include hwmon device creation/removal, reading all attributes, toggling enable, runtime-suspended access, and high/low temperature exception events producing hwmon notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-mcq.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-mcq.c

## Purpose

`ufs-mcq.c` implements UFSHCI multi-circular-queue support: queue count policy, queue memory allocation, MCQ register setup, completion polling, queue cleanup, and abort handling.

## Important APIs, Types, and Functions

Exports include `ufshcd_mcq_config_mac()`, `ufshcd_mcq_queue_cfg_addr()`, `ufshcd_mcq_read_cqis()`, `ufshcd_mcq_write_cqis()`, `ufshcd_mcq_poll_cqe_lock()`, `ufshcd_mcq_make_queues_operational()`, `ufshcd_mcq_enable()`, `ufshcd_mcq_enable_esi()`, and `ufshcd_mcq_config_esi()`. Internal/public core functions include `ufshcd_mcq_init()`, `ufshcd_mcq_memory_alloc()`, `ufshcd_mcq_sq_cleanup()`, and `ufshcd_mcq_abort()`. Module parameters configure read/write, read-only, and poll queue counts.

## Control Flow

Init validates requested queue counts against controller capacity, asks variant ops to configure MCQ resources and operational runtime mappings, allocates `ufs_hw_queue` state, and initializes locks. Memory allocation creates coherent SQE and CQE rings per queue. Operational setup programs base addresses, doorbell/status offsets, CQ/SQ attributes, interrupt enables, and queue-local cached register pointers. CQ polling updates tail, processes CQEs by deriving task tags, completes requests, clears CQEs, and advances head. Cleanup stops a SQ, writes cleanup task identity, waits for completion, and restarts the queue. Abort first searches/nullifies an unfetched SQE, then falls back to device task abort.

## State and Persistence Behavior

State is per-HBA queue arrays, DMA rings, queue head/tail slots, `mcq_enabled`, queue-count fields, and controller registers. It is runtime-only, rebuilt after reset or reinit.

## Dependencies and Integration Points

It depends on block-mq request mapping, SCSI commands, UFSHCI MCQ registers, DMA coherent allocation, variant ops for platform-specific resource layout, error handling, task abort helpers, and inline queue helpers in `ufshcd-priv.h`.

## Risks and Test Signals

Risks include invalid module queue counts, at least-one non-poll queue requirement, UFSHCI 4.0 indirect tag derivation, CQE double-completion avoidance during EH, broken RTC quirks causing cleanup/abort failure, and races around SQ stop/start with `sq_mutex`. Test signals include MCQ init on capacity boundaries, reset reinitialization, interrupt and polling completions, HCI 4.0 vs 4.1 tags, SQ cleanup return codes, abort of queued/fetched/completed commands, and vendor-op failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-mcq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-rpmb.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-rpmb.c

## Purpose

`ufs-rpmb.c` registers UFS RPMB regions as Linux RPMB devices for OP-TEE style consumers when advanced RPMB is not used.

## Important APIs, Types, and Functions

Public functions are `ufs_rpmb_probe()` and `ufs_rpmb_remove()`. `struct ufs_rpmb_dev` binds a region id, device, `rpmb_dev`, HBA pointer, and list node. `ufs_sec_submit()` sends SECURITY PROTOCOL IN/OUT SCSI commands. `ufs_rpmb_route_frames()` implements the rpmb framework route callback.

## Control Flow

Probe skips registration without an RPMB WLUN or when advanced RPMB is enabled. It requires a device id, initializes `hba->rpmbs`, then registers one device per nonzero RPMB region capacity. Each region gets a unique id derived from UFS device id plus region number and an `rpmb_descr`. Route-frame requests validate frame sizes by RPMB request type, send request frames via SECURITY PROTOCOL OUT, optionally send a result-read request, then read the response via SECURITY PROTOCOL IN. Remove unregisters every listed region device.

## State and Persistence Behavior

State is runtime device/list registration and RPMB framework handles. Persistent data is inside the UFS RPMB hardware, not this driver. Request effects include key programming, counter reads, authenticated writes, and reads.

## Dependencies and Integration Points

It depends on SCSI WLUN commands, the Linux RPMB framework, UFS device info, and `ufshcd-priv.h` probe/remove hooks. It integrates secure storage clients with UFS RPMB regions.

## Risks and Test Signals

Risks include wrong frame-size validation, result-read sequencing errors, device-id absence, multi-region cleanup after partial registration failure, and using the non-advanced path when firmware expects advanced RPMB. Test signals include region registration counts, all RPMB request types, failed SECURITY PROTOCOL commands, partial-probe unwind, and remove with empty/nonempty lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-rpmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.c

## Purpose

`ufs-sysfs.c` exposes the UFS controller, link, device descriptor, unit descriptor, query flag, query attribute, monitor, write booster, PM, and host-initiated defrag controls through sysfs.

## Important APIs, Types, and Functions

Public functions are `ufs_sysfs_add_nodes()`, `ufs_sysfs_remove_nodes()`, and exported `ufshcd_us_to_ahit()`. Important helpers include `ufs_sysfs_pm_lvl_store()`, `ufshcd_read_hci_reg()`, `ufs_sysfs_read_desc_param()`, `hid_query_attr()`, descriptor/flag/attribute macros, and visibility callbacks for HID and unit descriptors. It exports `ufs_sysfs_unit_descriptor_group` and `ufs_sysfs_lun_attributes_group` for SCSI device attachment.

## Control Flow

Host sysfs group creation installs default controls, capabilities, UFSHCI registers, monitor counters, power info, device/interconnect/geometry/health/power/string descriptors, flags, attributes, and HID controls. Device-affecting reads/writes generally take `host_sem`, check `ufshcd_is_user_access_allowed()`, resume runtime PM, issue UFS query or register access, then release PM and semaphore. PM level writes validate allowed levels and deep-sleep capability. Write booster and buffer flush writes validate feature/quirk support and update UFS flags or attributes. Descriptor macros read fixed-size big-endian fields; string descriptors first read the device descriptor to find string indexes. LUN groups convert SCSI LUNs to UPIU LUNs and hide unsupported WLUN attributes.

## State and Persistence Behavior

Sysfs writes mutate live HBA fields (`rpm_lvl`, `spm_lvl`, monitor state, RTC update period, PM QoS state, WB flush threshold, counters) and device attributes/flags. Some effects persist in the UFS device until reset or later query writes, but this file itself stores no on-disk state. Monitor counters live in `hba->monitor`; exception counters are atomic HBA fields.

## Dependencies and Integration Points

It depends on sysfs, SCSI device objects, runtime PM on the device WLUN, UFS query descriptor/flag/attribute helpers, UFSHCI registers, write booster helpers, PM QoS, clock scaling, HID attributes, and unit descriptor LUN validation in `ufshcd-priv.h`.

## Risks and Test Signals

Risks include ABI regressions, missing access gating around device queries, descriptor offset/size mismatches, endian conversion mistakes, runtime-PM failures, monitor reset races under `host_lock`, queue freeze ordering for max RTT writes, and visibility errors for WLUNs/HID support. Test signals include sysfs group create/remove, every descriptor family on real or emulated devices, WB enable/flush/resize controls, auto-hibern8 conversion round trips, PM level validation, HID enable/disable/progress reads, LUN descriptor visibility, and shutdown returning `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.h

## Purpose

This header declares host-level and LUN-level UFS sysfs group integration.

## Important APIs, Types, and Functions

It declares `ufs_sysfs_add_nodes()`, `ufs_sysfs_remove_nodes()`, and extern attribute groups `ufs_sysfs_unit_descriptor_group` and `ufs_sysfs_lun_attributes_group`.

## Control Flow

No runtime control flow exists in the header. Host code calls add/remove for controller groups, and SCSI device setup can attach exported LUN groups.

## State and Persistence Behavior

The header owns no state. It exposes sysfs ABI registration points.

## Dependencies and Integration Points

It depends on `linux/sysfs.h` and a forward declaration of `struct device`.

## Risks and Test Signals

Risks are declaration/definition drift and missing extern groups in configurations that build UFS core. Test signals are host sysfs and SCSI LUN sysfs group compilation and runtime registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-txeq.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-txeq.c

## Purpose

`ufs-txeq.c` implements adaptive UFS TX equalization training and application for high-speed gears, including UFSHCI v5.0 TX EQTR flows, M-PHY adaptation length selection, FOM evaluation, preset filtering, debug printing, and manual retraining.

## Important APIs, Types, and Functions

Module parameters are `use_adaptive_txeq`, `adaptive_txeq_gear`, `use_txeq_presets`, and `txeq_presets_selected`. Public functions include exported `ufshcd_apply_tx_eq_settings()`, `ufshcd_print_tx_eq_params()`, `ufshcd_config_tx_eq_settings()`, `ufshcd_apply_valid_tx_eq_settings()`, `ufshcd_is_txeq_presets_used()`, `ufshcd_is_txeq_preset_selected()`, and `ufshcd_retrain_tx_eq()`. Key internal helpers initialize iterators, compute adaptation lengths, apply TXEQ/TXEQTR settings, retrieve RX FOM, and update cached params/records.

## Control Flow

Configuration exits unless TXEQ is supported and adaptive mode is enabled. For eligible HS gears, it trains when cached parameters are invalid or forced. Training prepares the link by switching to HS-G1 with all lanes, sets initial adapt type, notifies variant ops, computes `PA_TXADAPTLENGTH_EQTR`, reads host/device TX equalization capabilities, iterates supported preshoot/deemphasis combinations, writes local and peer TXEQTR settings, triggers UIC TX EQTR, reads local and peer RX_FOM values, records FOM matrices, and chooses best per-lane settings. Applying settings writes local and peer `PA_TxEQGnSetting` and enables precoding for HS-G6 when FOM asks for it. Manual retrain pauses command processing, scales clocks up, negotiates target gear, forces training, and changes power mode.

## State and Persistence Behavior

State lives in module parameters and per-HBA TXEQ caches: capability bitmaps, per-gear `tx_eq_params`, `is_valid`, `is_applied`, FOM records, saved adapt length, and timestamps. Settings are programmed into UniPro/M-PHY attributes and may be lost across reset, so valid cached settings can be reapplied.

## Dependencies and Integration Points

It depends on UniPro DME get/set/peer operations, UFS power-mode changes, clock scaling, command pause/resume, variant ops for FOM and TXEQTR notifications, and debugfs readers in `ufs-debugfs.c`.

## Risks and Test Signals

Risks include long training latency, invalid gear/rate/lane assumptions, capability bitmap interpretation errors, FOM zero fallback hiding bad links, failure to restore old power mode after training errors, module parameter combinations that skip all presets, and variant-op mismatches. Test signals include disabled adaptive mode no-op, HS-G4/G5/G6 training, preset filtering, adaptation length bounds, FOM matrix recording, precoding enablement, reset reapply, manual retrain success/failure, and error paths restoring command processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-txeq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.c

## Purpose

`ufs_bsg.c` creates a block SCSI generic endpoint for raw UFS UPIU, UIC, task-management, query, NOP, and advanced RPMB requests.

## Important APIs, Types, and Functions

Public functions are `ufs_bsg_probe()` and `ufs_bsg_remove()`. Core handlers are `ufs_bsg_request()`, `ufs_bsg_alloc_desc_buffer()`, and `ufs_bsg_exec_advanced_rpmb_req()`.

## Control Flow

Probe initializes a child device named `ufs-bsgN` under the SCSI host and creates a bsg queue. Request handling resumes runtime PM, dispatches by `msgcode`, optionally allocates descriptor buffers for query descriptor reads/writes, calls raw UPIU or UIC helpers, handles advanced RPMB with DMA-mapped payloads and EHS validation, fills reply lengths, and completes successful jobs with `bsg_job_done()`. Remove tears down queue and device references.

## State and Persistence Behavior

Runtime state is `hba->bsg_dev` and `hba->bsg_queue`. Requests may mutate device state depending on raw UPIUs, query writes, UIC commands, or RPMB operations. No file-backed persistence is owned here.

## Dependencies and Integration Points

It depends on bsg-lib, DMA mapping, SCSI host device hierarchy, UFS raw command helpers, runtime PM, and advanced RPMB support in UFSHCI 4.0+ devices.

## Risks and Test Signals

Risks include user ABI exposure of low-level device commands, descriptor length validation mistakes, DMA map/unmap errors, completion only on success, advanced RPMB eligibility checks, and lifetime ordering for bsg device removal. Test signals include bsg node creation/removal, query read/write descriptor payloads, UIC command round trips, unsupported msgcodes, malformed advanced RPMB EHS/payloads, and runtime PM balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.h

## Purpose

This header declares the UFS BSG device setup/teardown interface and provides disabled stubs.

## Important APIs, Types, and Functions

It forward-declares `struct ufs_hba` and declares `ufs_bsg_probe()` and `ufs_bsg_remove()` under `CONFIG_SCSI_UFS_BSG`.

## Control Flow

There is no runtime control flow. Compile-time configuration selects real hooks or stubs that return success/do nothing.

## State and Persistence Behavior

No state is owned by the header.

## Dependencies and Integration Points

It lets core probe/remove code call BSG support unconditionally while keeping BSG optional.

## Risks and Test Signals

Risks are signature drift and callers assuming a bsg node exists when the config is disabled. Test signals are builds and probe/remove paths with BSG enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace.h

## Purpose

`ufs_trace.h` defines tracepoints for UFS core observability: clock gating/scaling, auto background operations, profiling, PM transitions, SCSI command lifecycle, UIC commands, UPIU payloads, and exception events.

## Important APIs, Types, and Functions

Trace events include `ufshcd_clk_gating`, `ufshcd_clk_scaling`, `ufshcd_auto_bkops_state`, profiling events, `ufshcd_system_suspend/resume`, runtime and WL PM events, `ufshcd_init`, `ufshcd_command`, `ufshcd_uic_command`, `ufshcd_upiu`, and `ufshcd_exception_event`. String mapping macros define symbolic output for link states, power modes, clock states, command phases, and TSF types.

## Control Flow

The header uses standard Linux tracepoint macros. When included with `CREATE_TRACE_POINTS` in `ufshcd.c`, it emits tracepoint definitions; other includes get declarations. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to this header.

## State and Persistence Behavior

Tracepoints do not persist state. They snapshot selected runtime fields into ring buffers when enabled.

## Dependencies and Integration Points

It depends on Linux tracing, UFS enums from `<ufs/ufs.h>`, and local trace enums from `ufs_trace_types.h`. It integrates UFS driver internals with ftrace/perf/tracefs tooling.

## Risks and Test Signals

Risks include trace ABI field changes, unsafe pointers in trace payloads, string mapping drift, and payload copying of UPIU headers/TSFs with wrong sizes. Test signals include enabling each tracepoint, decoding symbolic fields, command lifecycle correlation, PM profiling durations, and trace generation builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace_types.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace_types.h

## Purpose

This header defines small enums used by UFS tracepoints to classify command trace phases and transaction-specific field payloads.

## Important APIs, Types, and Functions

`enum ufs_trace_str_t` includes send/complete/error variants for SCSI commands, query requests, and task management. `enum ufs_trace_tsf_t` classifies UPIU TSF payloads as CDB, OSF, TM input, or TM output.

## Control Flow

No runtime control flow exists. The enums are consumed by `ufs_trace.h` and trace callers.

## State and Persistence Behavior

The header owns no state. Enum numeric values become part of trace event interpretation.

## Dependencies and Integration Points

It is included by `ufs_trace.h` and indirectly by UFS core trace call sites.

## Risks and Test Signals

Risks include reordering enum values without considering trace consumers and mismatches with string tables in `ufs_trace.h`. Test signals include trace decoding of every enum value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.c

## Purpose

`ufshcd-crypto.c` connects UFS inline encryption hardware to the block layer blk-crypto profile and programs UFS crypto keyslots.

## Important APIs, Types, and Functions

Public functions are `ufshcd_crypto_enable()`, `ufshcd_hba_init_crypto_capabilities()`, `ufshcd_init_crypto()`, and `ufshcd_crypto_register()`. Internal functions include `ufshcd_program_key()`, `ufshcd_crypto_keyslot_program()`, `ufshcd_crypto_keyslot_evict()`, and `ufshcd_find_blk_crypto_mode()`. The supported algorithm table maps blk AES-256-XTS to UFS AES-XTS 256.

## Control Flow

Capability init exits if custom crypto profiles are used, host/device capability bits are absent, or allocation/profile initialization fails. Otherwise it reads `REG_UFS_CCAP`, derives config-array base, allocates and caches crypto capability entries, initializes a blk crypto profile with slots, DUN size, raw key support, and supported modes. Keyslot programming chooses a matching UFS crypto capability by algorithm/key size/data-unit mask, fills a config entry, writes registers with CFGE cleared first and set last, then zeroizes the temporary config. Enable reprograms all blk-crypto keys after reset and returns whether standard `CRYPTO_GENERAL_ENABLE` should be set.

## State and Persistence Behavior

State lives in `hba->crypto_capabilities`, `crypto_cfg_register`, `crypto_cap_array`, and `crypto_profile`. Key material is written to hardware keyslots and explicitly zeroized from stack config buffers after programming. Keyslots are cleared during crypto init and eviction.

## Dependencies and Integration Points

It depends on blk-crypto, UFSHCI crypto registers, UFS host hold/release, devm allocation, and request queue registration. It is used by request preparation helpers in `ufshcd-crypto.h`.

## Risks and Test Signals

Risks include unsupported crypto modes, data-unit mask interpretation, broken hardware enable quirks, reset losing keys, key material lifetime in registers/PRDT, and capability count/register offset errors. Test signals include capability discovery, AES-256-XTS keyslot program/evict, reset reprogramming, queue registration, custom profile bypass, and builds without crypto support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.h

## Purpose

This header provides request-time inline encryption helpers and crypto lifecycle declarations for the UFS host controller.

## Important APIs, Types, and Functions

Inline helpers include `ufshcd_prepare_lrbp_crypto()`, `ufshcd_prepare_req_desc_hdr_crypto()`, `ufshcd_crypto_fill_prdt()`, and `ufshcd_crypto_clear_prdt()`. It declares lifecycle functions implemented in `ufshcd-crypto.c` and provides disabled stubs under non-crypto builds.

## Control Flow

For encrypted requests, the LRB records blk-crypto keyslot index and DUN. Request descriptor preparation sets crypto enable, CCI, and lower/upper DUN fields. Variant drivers may fill crypto PRDT entries. If keys are stored in PRDT due to a quirk, clear helper zeroizes PRDT entries after use.

## State and Persistence Behavior

The header mutates per-request LRB fields and request descriptor headers. It does not own persistent state, but it handles sensitive key/DUN metadata paths.

## Dependencies and Integration Points

It depends on SCSI command/request structures, blk-crypto fields, UFS descriptors, UFSHCI crypto layout, and variant `fill_crypto_prdt` operations.

## Risks and Test Signals

Risks include missing crypto clearing for key-in-PRDT hardware, wrong DUN width, stale keyslot indexes, and disabled-config stubs hiding missing feature tests. Test signals include encrypted and unencrypted request descriptor fields, PRDT fill/clear with quirks, and crypto-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-priv.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-priv.h

## Purpose

`ufshcd-priv.h` is the private contract between the UFS core implementation files. It declares core helpers, optional subsystem hooks, variant-operation wrappers, runtime PM helpers, exception-event mask helpers, LUN conversion, and MCQ queue inline operations.

## Important APIs, Types, and Functions

The header declares UFS query helpers, MCQ APIs, BSG/raw UPIU helpers, write booster helpers, TXEQ APIs, RPMB hooks, and error/command-control helpers. `enum ufs_descr_fmt` defines raw versus ASCII string descriptor reads. Important inline wrappers cover variant ops such as clock scaling, link startup, power changes, MCQ resource configuration, RX FOM, TXEQTR settings, suspend/resume, and debug register dumps. Runtime PM helpers operate on `hba->ufs_device_wlun->sdev_gendev`.

## Control Flow

Most logic is small dispatch: if a variant op exists, call it; otherwise return neutral success or `-EOPNOTSUPP` depending on whether the operation is optional or required. MCQ inline helpers update SQ/CQ head and tail slots and convert queue register byte offsets to slots. Exception-event mask helpers merge driver and user masks through `ufshcd_update_ee_control()`.

## State and Persistence Behavior

The header does not allocate state but reads/mutates HBA fields through inline helpers: write booster LUN index, runtime PM refs, MCQ queue slots, exception masks, and shutdown/user-access state. Effects are runtime-only and often reflect hardware register state.

## Dependencies and Integration Points

It depends on PM runtime, UFS public headers, SCSI/block-mq request tags, optional hwmon/RPMB configs, variant ops, and almost every UFS core `.c` file. It is the main coupling layer between `ufshcd.c`, sysfs, debugfs, MCQ, TXEQ, BSG, crypto, hwmon, and RPMB code.

## Risks and Test Signals

Risks include inline semantics changing many call sites, returning `-EOPNOTSUPP` where callers expect success, runtime PM helper use before WLUN exists, tag-to-command lookup warnings during races, MCQ slot math mismatches with hardware entry sizes, and LUN validation before `max_lu_supported` initialization. Test signals include build coverage across optional configs, variant-op absent/present behavior, runtime PM balancing, MCQ completion slot updates, exception mask merging, and valid/invalid unit descriptor LUNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-priv.h -->
