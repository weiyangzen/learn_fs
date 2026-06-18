# subset-b-005219 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_reqlist.h -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_reqlist.h

Purpose: provides the zfcp driver's in-memory hash table for tracking outstanding FSF requests by request ID. It is a small lock-protected helper used by the FCP/SCSI error and completion paths to find, remove, move, or iterate pending `struct zfcp_fsf_req` objects.

Important APIs/types/functions: `struct zfcp_reqlist` contains a spinlock and 128 list buckets. `zfcp_reqlist_alloc()` initializes the table, `zfcp_reqlist_free()` asserts the table is empty before freeing it, `_zfcp_reqlist_find()` does unlocked bucket lookup, and public helpers `zfcp_reqlist_find()`, `zfcp_reqlist_find_rm()`, `zfcp_reqlist_add()`, `zfcp_reqlist_move()`, and `zfcp_reqlist_apply_for_all()` wrap lookup, removal, insertion, bulk movement, and locked iteration.

Control flow: callers allocate one request list per adapter, add each FSF request after it receives a monotonically increasing `req_id`, look it up on completions or aborts, and remove it atomically when a completion owns the request. Bulk shutdown paths can splice all bucket contents into a plain list, while task-management code can apply a callback to every pending request under the request-list lock.

State and persistence: all state is volatile kernel memory: bucket membership through each request's `list` node plus the `req_id` hash. The helper does not reference hardware, sysfs, or persistent storage. Locking uses `spin_lock_irqsave()` because callers can run in interrupt-sensitive completion/error paths.

Dependencies and integration: depends on Linux list and spinlock primitives, zfcp's `struct zfcp_fsf_req`, and allocation helpers such as `kzalloc_obj()`. It is included by zfcp SCSI/FSF code and is particularly visible in abort and task-management cleanup paths.

Risks and test signals: `zfcp_reqlist_free()` uses `BUG_ON()` if any request remains, so teardown ordering must guarantee prior drain/removal. `zfcp_reqlist_apply_for_all()` explicitly is not safe against list mutation by the callback. The simple modulo hash relies on request IDs being distributed enough across 128 buckets. Test duplicate add/remove ordering, abort racing normal completion, adapter shutdown moving all requests, callback iteration that only mutates request payloads, and teardown after all FSF requests complete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_reqlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_scsi.c

Purpose: connects IBM zfcp FCP adapters to the Linux SCSI and Fibre Channel transport midlayers. It owns SCSI command submission, SCSI device initialization/destruction, error handling, host registration, FC rport lifecycle, transport statistics, protection capabilities, and FC host attribute updates.

Important APIs/types/functions: module parameters `queue_depth`, `dif`, `dix`, and `allow_lun_scan` tune device queueing, DIF/DIX, and NPIV LUN scanning. `zfcp_scsi_host_template` wires queuecommand, SCSI EH callbacks, device init/configure/destroy, host reset, and zfcp sysfs groups into the SCSI core. Core functions include `zfcp_scsi_queuecommand()`, `zfcp_scsi_sdev_init()`, `zfcp_scsi_eh_abort_handler()`, `zfcp_scsi_task_mgmt_function()`, `zfcp_scsi_adapter_register()`, `zfcp_scsi_adapter_unregister()`, `zfcp_scsi_get_fc_host_stats()`, rport scheduling/work helpers, `zfcp_scsi_set_prot()`, and host data update functions.

Control flow: normal I/O starts in `zfcp_scsi_queuecommand()`, which resets command bookkeeping, checks FC rport readiness, rejects LUN-specific failed/blocked states, and submits the command through `zfcp_fsf_fcp_cmnd()`. Device discovery calls `zfcp_scsi_sdev_init()`, which resolves the rport WWPN to a zfcp port, rejects removed ports or unauthorized LUNs unless NPIV LUN scan is allowed, initializes latency counters, marks the LUN running, and synchronously opens it through ERP. SCSI EH aborts find the old FSF request under `adapter->abort_lock`, clear its command pointer to prevent late completion side effects, issue an FSF abort, and wait for completion. LUN and target reset send FSF task-management functions, then null out matching pending SCSI command pointers in the request list. Host reset drives ERP reopen/reset paths and blocks until FC recovery completes.

State and persistence: persistent driver-visible state is in adapter, port, and `struct zfcp_scsi_dev` objects: atomic status bits, FC host fields, request-list entries, latency counters, cached statistics-reset data, and rport pointers. Hardware state is accessed through FSF exchange commands and ERP reopen/reset actions. No file-backed persistence exists; module parameters and sysfs writes affect runtime behavior.

Dependencies and integration: integrates SCSI midlayer, FC transport (`fc_remote_port_add/delete`, `fc_block_*`, FC host statistics), CCW device IDs, zfcp FSF command builders, ERP recovery, debug logging, QDIO limits, and optional DIF/DIX protection. It also consumes zfcp sysfs attribute groups from `zfcp_sysfs.c`.

Risks and test signals: abort/completion races are delicate because `host_scribble` stores the FSF request ID and `old_req->data` is cleared under a separate abort lock. `zfcp_scsi_sdev_init()` must balance port references on every rejection path. Target reset chooses the first SCSI device with the target ID, so target-wide behavior depends on shost device enumeration. Statistics reset subtracts cached port data only while adapter and port reset timers make sense. Test rport loss during queuecommand, blocked LUN retry behavior, LUN access denied with healthy port, abort while completion is in flight, TMF success/failure, host reset in NPIV and non-NPIV modes, host registration failure cleanup, DIF/DIX feature combinations, and FC stats reset/read after link reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_sysfs.c

Purpose: defines the zfcp device, port, LUN, SCSI-device, SCSI-host, and diagnostics sysfs attributes. The file exposes runtime state, recovery controls, port/unit management, measurement counters, latency counters, FC security information, and SFP/link diagnostics.

Important APIs/types/functions: macro families `ZFCP_DEV_ATTR`, `ZFCP_DEFINE_ATTR`, `ZFCP_DEFINE_A_ATTR`, `ZFCP_DEFINE_LATENCY_ATTR`, `ZFCP_DEFINE_SCSI_ATTR`, and `ZFCP_DEFINE_DIAG_SFP_ATTR` generate attribute show/store functions. Public attribute groups include `zfcp_sysfs_adapter_attr_groups`, `zfcp_port_attr_groups`, `zfcp_unit_attr_groups`, `zfcp_sysfs_sdev_attr_groups`, and `zfcp_sysfs_shost_attr_groups`. Key stores are `zfcp_sysfs_adapter_failed_store()`, `zfcp_sysfs_port_failed_store()`, `zfcp_sysfs_unit_failed_store()`, `zfcp_sysfs_port_rescan_store()`, `zfcp_sysfs_port_remove_store()`, `zfcp_sysfs_unit_add_store()`, and `zfcp_sysfs_unit_remove_store()`.

Control flow: read-only attributes fetch atomic status fields, FC identifiers, hardware/firmware versions, unit LUNs, queue statistics, and diagnostic buffers. Recovery write attributes accept only `0`, clear failed status, and trigger adapter/port/LUN ERP reopen or reset. `port_rescan` schedules and flushes a synchronous scan worker. Port removal validates the WWPN, checks the unit count and live SCSI devices under `zfcp_sysfs_port_units_mutex` and `host_lock`, marks the port removing by setting `port->units` to `-1`, deletes it from the adapter list, shuts it down, and unregisters the device. Unit add/remove parse a 64-bit FCP LUN and call the unit lifecycle helpers.

State and persistence: sysfs reflects and mutates volatile adapter/port/unit/SCSI state. `diag_max_age` persists only in `adapter->diagnostics->max_age` for the current adapter lifetime. Latency stores reset per-SCSI-device counters under the latency spinlock. Diagnostic reads refresh bounded cached buffers through zfcp diagnostic helpers before emitting values.

Dependencies and integration: depends on zfcp ERP, unit management, port lookup, diagnostic buffer code, SCSI host/device helpers, FC security FSF formatting, and Linux sysfs/device attribute infrastructure. It also coordinates with `zfcp_unit.c` via `zfcp_sysfs_port_units_mutex` to serialize unit creation/removal against port removal and SCSI device initialization.

Risks and test signals: port removal relies on `atomic_t units` carrying both a count and the sentinel `-1`, so all unit add/remove paths must obey the mutex. Several store paths trigger synchronous recovery and can block sysfs writes. `unit_failed_store()` rescans when the SCSI device is absent, while SCSI-device `zfcp_failed` assumes an existing `sdev`. Diagnostics return `unknown`, `unsupported`, `-ENOLINK`, or `-EOPNOTSUPP` depending on adapter state and capability. Test invalid numeric input, recovery writes while adapter/port is gone, concurrent `unit_add` versus `port_remove`, LUN latency reset under I/O, missing `scsi_host` during port rescan, FC security state transitions, and diagnostic reads before open, after ERP failure, and on adapters without SFP support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_unit.c -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_unit.c

Purpose: manages manually configured zfcp LUN objects and bridges them to the SCSI midlayer. It creates per-port unit devices, queues/manual scans matching FCP LUNs, looks up units and associated SCSI devices, and removes units cleanly.

Important APIs/types/functions: `zfcp_unit_scsi_scan()` converts a zfcp unit FCP LUN to a SCSI LUN and calls `scsi_scan_target()`. `zfcp_unit_queue_scsi_scan()` queues scan work for all units on a port. `zfcp_unit_find()` returns a referenced unit by FCP LUN. `zfcp_unit_add()` allocates/registers a unit device and scans it. `zfcp_unit_sdev()` and `zfcp_unit_sdev_status()` resolve the live `struct scsi_device`. `zfcp_unit_remove()` deletes the unit, removes any SCSI device, and unregisters the unit device.

Control flow: a new unit is added under `zfcp_sysfs_port_units_mutex`, first rejecting ports marked removing and duplicate LUNs. The unit is initialized with sysfs groups and scan work, registered as a child of the port device, counted in `port->units`, inserted under `unit_list_lock`, and then scanned outside the mutex to preserve the documented lock order. Removal takes the unit list write lock, finds and deletes the unit, removes the backing SCSI device if present, unregisters the unit device, and drops the lookup reference.

State and persistence: unit state is a kernel device object with FCP LUN, parent port pointer, list node, and delayed scan work. The unit count on the parent port is decremented in `zfcp_unit_release()`. No persistent storage is used; configured units exist for the lifetime of the zfcp port/device instance.

Dependencies and integration: depends on zfcp port lists, zfcp sysfs attribute groups, FC rport state, SCSI scan/remove APIs, and `zfcp_sysfs_port_units_mutex` from `zfcp_sysfs.c`. The workqueue path uses the adapter's SCSI host queue.

Risks and test signals: scan work holds a device reference and must always drop it when queueing fails or work completes. `zfcp_unit_add()` deliberately unlocks before scanning to avoid `scan_mutex` inversion, so tests should cover port/rport state changing immediately after insertion. Removal deletes the unit from the zfcp list before SCSI device removal, so concurrent lookup and sysfs status reads depend on device references. Test duplicate add, add while port is removing, scan with offline/missing rport, remove nonexistent LUN, remove while SCSI device exists, queue work failure, and reference count release after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_unit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/virtio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/s390/virtio/Makefile

Purpose: builds the s390 virtio-ccw transport driver when s390 guest support is enabled.

Important APIs/types/functions: the sole build rule is `obj-$(CONFIG_S390_GUEST) += virtio_ccw.o`, mapping the `CONFIG_S390_GUEST` Kconfig symbol to `virtio_ccw.c`.

Control flow: during kernel build, kbuild includes `virtio_ccw.o` only for configurations that enable s390 guest drivers. There is no runtime behavior in this file.

State and persistence: no state; this is build metadata.

Dependencies and integration: ties the driver under `drivers/s390/virtio` to the s390 guest configuration and the wider virtio/ccw subsystem.

Risks and test signals: incorrect gating would either omit virtio devices for s390 guests or compile the driver for unsupported configs. Test signals are build coverage for `CONFIG_S390_GUEST=y/m/n` and that `virtio_ccw.o` links with required virtio, CCW, and s390 channel I/O symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/virtio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/virtio/virtio_ccw.c -->
# sources/distributed-fs/ceph-client/drivers/s390/virtio/virtio_ccw.c

Purpose: implements the s390 CCW transport for virtio devices. It maps virtio config operations onto channel commands, manages virtqueues and indicator interrupts, negotiates transport revisions/features, auto-onlines CCW devices, and registers a `ccw_driver` for virtio device type `0x3832`.

Important APIs/types/functions: `struct virtio_ccw_device` is the per-device transport object with CCW device pointer, DMA area, serialized I/O state, queue list, interrupt locks, revision, and removal flags. Queue/feature/config structures include `vq_config_block`, legacy and modern `vq_info_block` variants, `virtio_feature_desc`, `virtio_thinint_area`, `virtio_rev_info`, and `virtio_ccw_vq_info`. Core functions are `ccw_io_helper()`, `virtio_ccw_setup_vq()`, `virtio_ccw_find_vqs()`, `virtio_ccw_del_vqs()`, `virtio_ccw_get_features()`, `virtio_ccw_finalize_features()`, config/status get/set/reset operations, `virtio_ccw_int_handler()`, adapter-interrupt helpers, `virtio_ccw_online()`, `virtio_ccw_offline()`, `virtio_ccw_remove()`, `virtio_ccw_set_transport_rev()`, and `no_auto_parse()`.

Control flow: probe installs the CCW interrupt handler and asynchronously sets devices online unless the `no_auto` module parameter excludes their bus IDs. Online allocation creates the virtio device, low-memory DMA command area, locks, queue list, and transport revision, then registers with the virtio core. Virtio core operations call into this driver to read/write feature words, configure queues with `CCW_CMD_SET_VQ`, register classic or adapter interrupt indicators, read/write config space, and write/read status. `ccw_io_helper()` serializes channel programs with `io_lock`, retries `-EBUSY`, marks `curr_io`, waits on `wait_q`, and returns the interrupt-completed error code. Interrupts clear command activity, translate IRB errors to `-EOPNOTSUPP` or `-EIO`, dispatch vring callbacks for set indicator bits, and notify config changes through the second indicator.

State and persistence: per-device state includes negotiated revision, local status byte, cached config bytes and readiness length, virtqueue list entries and DMA info blocks, DMA indicators, and removal/lost flags. Global state includes adapter-interrupt areas, summary indicators, `virtio_ccw_use_airq`, and parsed `devs_no_auto` bitmaps. No persistent storage exists; all state is runtime transport and kernel device state.

Dependencies and integration: depends on virtio core/config/ring APIs, s390 CCW device/channel I/O, adapter interrupts, KVM s390 notification hypercall, DMA helpers constrained below 2G for CCW payloads, async online support, and module/device initcall infrastructure. It exposes `virtio_config_ops` to virtio drivers and a `ccw_driver` to the s390 channel subsystem.

Risks and test signals: command serialization and interrupt completion are central; missing `curr_io` wakeups can hang virtio operations. Adapter interrupts share global bit vectors and must free bits on queue deletion/fallback. Revision negotiation must fall back to legacy revision 0 only when `SET_VIRTIO_REV` is unsupported, and revision >=1 requires `VIRTIO_F_VERSION_1`. Config writes call `virtio_ccw_get_config()` while holding no `io_lock` yet but later copy from the cached array under `vcdev->lock`; partial config reads must not corrupt unwritten fields. Remove/offline relies on `going_away` to prevent double unregister. Test legacy and modern revisions, missing `VIRTIO_F_VERSION_1`, classic interrupt fallback after adapter interrupt `-EOPNOTSUPP`, queue creation/deletion with sparse queue arrays, config change interrupt, status read on hot-unplug, `no_auto` range parsing, device-lost notification, online allocation failures, and callback synchronization under `CONFIG_VIRTIO_HARDEN_NOTIFICATION`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/virtio/virtio_ccw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/sbus/Makefile

Purpose: gates the SPARC SBUS miscellaneous character-driver subtree.

Important APIs/types/functions: `obj-$(CONFIG_SBUSCHAR) += char/` makes kbuild descend into `drivers/sbus/char` only when `CONFIG_SBUSCHAR` is enabled.

Control flow: build-time only; it has no runtime paths.

State and persistence: no runtime state.

Dependencies and integration: connects the top-level SBUS driver directory to the `char` subdirectory's Kconfig-selected objects.

Risks and test signals: the main signal is build matrix coverage that enabling `CONFIG_SBUSCHAR` reaches the child Makefile and disabling it excludes legacy SBUS char drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/Kconfig

Purpose: declares miscellaneous Linux/SPARC driver configuration symbols for PROM, flash, microcontroller, BBC I2C/environment control, envctrl, 7-segment display, and Oracle DAX devices.

Important APIs/types/functions: symbols are `SUN_OPENPROMIO`, `OBP_FLASH`, `TADPOLE_TS102_UCTRL`, `BBC_I2C`, `ENVCTRL`, `DISPLAY7SEG`, and `ORACLE_DAX`. Several depend on `SPARC64`, `PCI`, or both; `ORACLE_DAX` defaults to module.

Control flow: build configuration selects which source files in `drivers/sbus/char/Makefile` are built as built-ins, modules, or excluded. Help text documents the exposed device files and hardware families.

State and persistence: no runtime state, but chosen symbols affect kernel image/module composition and device ABI availability.

Dependencies and integration: integrates with SPARC platform support and the child Makefile. Config dependencies prevent some drivers from appearing on non-SPARC64 or non-PCI builds.

Risks and test signals: dependency mistakes can expose drivers on unsupported platforms or hide required legacy devices. Test `allyesconfig` and targeted SPARC64 configs, module builds for each tristate, and dependency visibility for non-PCI or non-SPARC64 combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/Makefile -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/Makefile

Purpose: maps SBUS character-driver Kconfig symbols to object files and combines the BBC I2C/environment-control pair into one module object.

Important APIs/types/functions: `bbc-objs := bbc_i2c.o bbc_envctrl.o` creates the composite `bbc.o`. Object rules build `envctrl.o`, `display7seg.o`, `flash.o`, `openprom.o`, `uctrl.o`, `bbc.o`, and `oradax.o` from their respective config symbols.

Control flow: build-time only; no runtime code.

State and persistence: no runtime state.

Dependencies and integration: ties Kconfig symbols to the source files in this directory and ensures `bbc_i2c.c` and `bbc_envctrl.c` are linked together for `CONFIG_BBC_I2C`.

Risks and test signals: composite BBC linkage matters because `bbc_i2c.c` calls `bbc_envctrl_init()` and cleanup. Test module and built-in builds for each symbol, especially `CONFIG_BBC_I2C=m`, and verify no unresolved exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_envctrl.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_envctrl.c

Purpose: implements environmental monitoring and fan control for UltraSPARC-III BBC I2C-attached temperature sensors and fan controllers. It programs MAX1617 temperature thresholds, periodically samples CPU/ambient temperatures, adjusts fan speeds, warns on unsafe temperatures, and initiates orderly poweroff before hardware cut-off limits are reached.

Important APIs/types/functions: state types come from `bbc_i2c.h`: `struct bbc_cpu_temperature`, `struct bbc_fan_control`, and `enum fan_action`. Local limit tables `cpu_temp_limits[]` and `amb_temp_limits[]` define warning, shutdown, and hardware power-off thresholds. Key functions are `set_fan_speeds()`, `get_current_temps()`, `analyze_ambient_temp()`, `analyze_cpu_temp()`, `prioritize_fan_action()`, `maybe_new_fan_speeds()`, `kenvctrld()`, `attach_one_temp()`, `attach_one_fan()`, `bbc_envctrl_init()`, and `bbc_envctrl_cleanup()`.

Control flow: `bbc_envctrl_init()` scans children provided by the BBC I2C bus, attaches `temperature` nodes as MAX1617 clients and `fan-control` nodes as DAC clients, initializes sensor conversion/limit registers and fan defaults, and starts `kenvctrld` only when both sensors and fans exist. The thread sleeps five seconds, samples all temperatures, computes moving averages, records per-sensor fan actions, combines those actions globally, and writes new fan DAC values. On shutdown or thread exit it forces all fans to full blast.

State and persistence: runtime state is held in global `all_temps`/`all_fans` lists and per-bus lists, current/previous/average temperatures, sample tick, fan speeds, power-supply fan state, and a global warning timestamp. Hardware state includes MAX1617 configuration, conversion rate, temperature limit registers, and fan controller DAC registers. There is no user-facing persistent storage.

Dependencies and integration: linked with `bbc_i2c.c` as the `bbc` module. It depends on custom BBC I2C byte operations, MAX1617 register constants, Open Firmware child node names, kernel threads, sleep/delay APIs, and `orderly_poweroff()`.

Risks and test signals: this code directly programs thermal shutdown thresholds and fan voltages; incorrect register writes can affect hardware safety. Global lists and `kenvctrld_task` are singleton-style even though cleanup is per bus, so multi-controller scenarios are fragile. `bbc_envctrl_cleanup()` stops the thread before deleting devices but does not clear `kenvctrld_task`. I2C read/write return values are mostly ignored. Test sensor/fan discovery combinations, MAX1617 register programming, fan speed clamp behavior, warnings at high/low thresholds, orderly poweroff threshold paths, cleanup during active polling, no-sensor/no-fan operation, and I2C failures while sampling or setting speeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_envctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.c

Purpose: provides a custom low-level I2C controller driver for UltraSPARC-III BBC devices and hosts the BBC environmental-control client code. It exposes blocking byte/buffer operations for child devices and probes OF children on each BBC I2C bus.

Important APIs/types/functions: exported client helpers are `bbc_i2c_getdev()`, `bbc_i2c_attach()`, `bbc_i2c_detach()`, `bbc_i2c_writeb()`, `bbc_i2c_readb()`, `bbc_i2c_write_buf()`, and `bbc_i2c_read_buf()`. Internal helpers include `wait_for_pin()`, `bbc_i2c_interrupt()`, `reset_one_i2c()`, `attach_one_i2c()`, and platform driver probe/remove. `struct bbc_i2c_bus` and `struct bbc_i2c_client` are declared in the header.

Control flow: probe maps the controller registers, optionally maps the bus-select register, requests a shared IRQ, records up to eight OF child platform devices, saves controller owner/clock bytes, resets the controller, and calls `bbc_envctrl_init()`. Client attach reads the child's `reg` property into bus/address and marks the child claimed. Reads and writes select a bus if needed, issue PCF-style START/STOP/control bytes, wait for the PIN interrupt/status transition, and transfer one register byte; buffer helpers loop bytewise.

State and persistence: each bus stores mapped MMIO pointers, original owner/clock settings, waitqueue state, child slots and claimed flags, and environmental-control lists. Hardware state is the I2C controller control/data registers plus optional bus selector. State is volatile and removed on driver detach.

Dependencies and integration: depends on OF platform devices, SPARC BBC/IO helpers, IRQs from `op->archdata.irqs`, exported symbols consumed by `bbc_envctrl.c`, and the platform compatible `SUNW,bbc-i2c`.

Risks and test signals: the driver explicitly does not use the Linux I2C core, so locking and transfer semantics are local. The bus `lock` is initialized but not used around transfers, which is risky if multiple clients issue I2C transactions concurrently. Probe failure and remove paths appear to swap resource indices in some `of_iounmap()` calls when both control and bus-select mappings exist. `wait_for_pin()` can spend many seconds retrying and returns a generic failure. Test probe with one/two resources, IRQ wakeup and timeout paths, concurrent client read/write access, child `reg` parsing, transfer NACK handling, cleanup after `bbc_envctrl_init()` failure, and module unload with active environment clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.h

Purpose: declares the private BBC I2C bus/client ABI shared between the low-level I2C controller and its environmental-control client implementation.

Important APIs/types/functions: `struct bbc_i2c_client` stores parent bus, platform child, bus number, and I2C address. `struct bbc_i2c_bus` stores controller mappings, waitqueue/IRQ wait state, child device slots, and per-bus temperature/fan lists. Environmental-control structs `bbc_cpu_temperature` and `bbc_fan_control` track sensor readings, fan actions, and fan output state. The header declares attach/detach, device lookup, byte/buffer read/write, and envctrl init/cleanup functions.

Control flow: `bbc_i2c.c` owns bus discovery and transfer primitives, while `bbc_envctrl.c` attaches clients to OF child platform devices and calls the blocking I2C operations.

State and persistence: this header defines volatile in-kernel state only. Sensor and fan list nodes exist simultaneously on per-bus and global lists managed by `bbc_envctrl.c`.

Dependencies and integration: depends on Linux OF and list APIs, platform devices via forward declarations/includes, and the composite `bbc` module linking both implementation files together.

Risks and test signals: the shared structures expose mutable fields directly, so both implementation files must preserve list and client lifetime invariants. `NUM_CHILDREN` limits discovery to eight children. Test ABI consistency by building `bbc_i2c.o` and `bbc_envctrl.o` together, attaching/detaching clients, and cleaning up list nodes for multiple sensors/fans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/display7seg.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/display7seg.c

Purpose: exposes the Sun CP1400/CP1500 seven-segment display and LED register as a misc character device named `d7s`. It supports ioctl reads/writes/toggle and optional Solaris compatibility behavior.

Important APIs/types/functions: `struct d7s` stores the mapped register and OBP default flipped state. `d7s_open()`, `d7s_release()`, and `d7s_ioctl()` implement the file interface for minor `D7S_MINOR`. `d7s_probe()` maps the one-byte register, registers the misc device, reads `/options/d7s-flipped?`, applies the default flip bit, and stores the singleton `d7s_device`. `d7s_remove()` deregisters and unmaps. The `sol_compat` module parameter controls flip handling.

Control flow: users open `/dev/d7s`, then use `D7SIOCWR` to write the register, `D7SIOCRD` to read it, or `D7SIOCTM` to toggle the flip bit. In non-Solaris mode, the last close restores the OBP flip default. Probe rejects a second device through the global singleton pointer.

State and persistence: state consists of the hardware register byte, global user count, singleton device pointer, module parameter, and stored default flip state. The register controls decimal point, alarm LED, flip bit, and display segment value. No persistent data is written beyond live hardware state.

Dependencies and integration: depends on SPARC OF platform probing for node name `display7seg`, miscdevice registration, `asm/display7seg.h` ioctl/minor definitions, and MMIO byte access.

Risks and test signals: ioctl does not return `-ENOTTY` for unknown commands; it silently returns success with no action. `d7s_remove()` appears to restore the OBP flip state only when `sol_compat` is true, while comments imply non-Solaris mode should honor the default. `of_find_node_by_path("/options")` failure is tolerated. Test singleton probe, register map failure, all three ioctls, unknown ioctl, Solaris and non-Solaris flip behavior on write/close/remove, open count races, and invalid minor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/display7seg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/envctrl.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/envctrl.c

Purpose: implements the older Sun `SUNW,envctrl` environmental monitoring misc device. It directly drives a PCF8584 I2C controller to read firmware-described ADC/GPIO child devices for temperatures, voltages, fan status, global address, and power-supply status, and starts a kernel thread that powers off on excessive CPU temperature.

Important APIs/types/functions: `struct i2c_child_t` stores child address, channel descriptors, translation tables, masks, and monitor types. Low-level I2C helpers include `envtrl_i2c_test_pin()`, `envctrl_i2c_test_bb()`, address/data read/write helpers, `envctrl_i2c_read_8591()`, and `envctrl_i2c_read_8574()`. User ABI functions are `envctrl_ioctl()` and `envctrl_read()` on misc minor `ENVCTRL_MINOR`. Initialization helpers parse OF properties in `envctrl_init_i2c_child()`, with monitor-specific setup for ADCs, fan status, global address, and voltage status. `kenvctrld()` monitors CPU temperature.

Control flow: probe maps the PCF8584 registers, walks OF children named `gpio` or `adc`, parses `reg`, `translation`, `tables`, `channels-in-use`, and `channels-description` properties, initializes the controller address/clock/interface, registers `/dev/envctrl`, and starts `kenvctrld`. Users first issue an ioctl selecting what subsequent `read()` should return; CPU reads can select a CPU number through the ioctl argument. Reads resolve the corresponding child, perform a direct I2C transaction, translate ADC data through firmware tables when needed, and copy a small result to userspace. The thread periodically reads all CPU temperature channels and calls `orderly_poweroff()` when the shutdown threshold is met.

State and persistence: global state includes the MMIO base, fixed-size child list, warning/shutdown temperatures, selected CPU for reads, and the kernel thread. Per-child state stores copied firmware table data and channel masks. Hardware state includes the PCF8584 controller and attached ADC/GPIO devices. No durable storage is modified.

Dependencies and integration: depends on SPARC OF properties and platform resources, `asm/envctrl.h` ioctl constants, miscdevice infrastructure, direct MMIO, delay loops, and kernel poweroff. It matches OF nodes with compatible `i2cpcf,8584`.

Risks and test signals: there is minimal validation for missing OF properties before `memcpy()`, fixed child array bounds are not checked against excessive children, and low-level I2C waits are polling loops with only log messages on timeout. `read_cpu` is global across file descriptors. `envctrl_init_i2c_child()` can leak allocated tables if a `tables` property is missing after allocation. `kenvctrld_task` is stopped unconditionally in remove. Test malformed/missing OF properties, more than eight children, all ioctl/read selectors, per-file CPU selection races, ADC translation types, GPIO fan/voltage/global masks, warning/shutdown thresholds, I2C timeout behavior, probe failure cleanup, and remove after thread start failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/envctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/flash.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/flash.c

Purpose: exposes UltraSPARC OpenBoot PROM flash memory through a misc device named `flash`, allowing read access and noncached mmap access for firmware update tools.

Important APIs/types/functions: global `flash` stores physical read/write bases, sizes, and a busy flag. File operations are `flash_open()`, `flash_release()`, `flash_llseek()`, `flash_read()`, and `flash_mmap()`. `flash_probe()` validates the parent bus node, records resource ranges, and registers misc minor `SBUS_FLASH_MINOR`.

Control flow: probe accepts flash nodes under `sbus`, `sbi`, or `ebus`, then sets separate read/write mappings if a second resource exists. Only one opener is allowed through a busy bit. Reads use `upa_readb()` from the read physical base. `mmap()` selects the read or write physical range depending on VMA flags when the ranges differ, rejects simultaneous read/write mappings in that case, marks the mapping noncached, and remaps PFNs into userspace.

State and persistence: the driver stores global physical ranges and busy state. The actual persistent state is OBP flash hardware, but this file performs no direct write operation; writing is expected through mapped flash-specific update sequences.

Dependencies and integration: depends on SPARC OF platform resources, miscdevice registration, UPA/MMIO helpers, Linux VM remapping, and `asm/upa.h`. The matching node name is `flashprom`.

Risks and test signals: `flash_mmap()` size calculation appears suspicious because it adjusts `size` to the requested mapping length when the request exceeds the resource, rather than clamping to remaining resource bytes. Read path does not guard negative/out-of-range `*ppos` beyond unsigned arithmetic effects. Busy state uses both mutex and spinlock on the same word. Test open exclusivity, resource combinations with shared/separate read/write bases, read at EOF and beyond EOF, mmap read-only/write-only/read-write cases, pgoff near range end, unsupported parent nodes, and misc registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/max1617.h -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/max1617.h

Purpose: defines register offsets for the MAX1617 temperature sensor used by the BBC environmental-control driver.

Important APIs/types/functions: constants cover ambient and CPU temperature reads, status, read/write aliases for config, conversion rate, high/low ambient limits, high/low CPU limits, and one-shot conversion.

Control flow: no executable control flow. `bbc_envctrl.c` uses these offsets to read current temperatures and program conversion rate and power-off thresholds through `bbc_i2c_writeb()`/`readb()`.

State and persistence: no driver state. The constants refer to MAX1617 hardware registers, some of which persist until the chip is reprogrammed or reset.

Dependencies and integration: included by `bbc_envctrl.c` and tied to the MAX1617-compatible devices exposed as BBC I2C `temperature` nodes.

Risks and test signals: incorrect offsets would misread temperatures or program unsafe thresholds. Test signals are hardware or emulated I2C traces confirming that ambient/CPU reads and limit writes target the expected addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/max1617.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/openprom.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/openprom.c

Purpose: implements the SPARC `/dev/openprom` misc device, providing SunOS/Solaris and NetBSD-compatible ioctls for reading, navigating, and modifying the Open Firmware device tree and PROM options.

Important APIs/types/functions: per-file `openprom_private_data` stores current and last nodes. User-copy helpers `copyin()`, `getstrings()`, `copyout()`, and `copyin_string()` validate and allocate ioctl buffers. SunOS handlers include `opromgetprop()`, `opromnxtprop()`, `opromsetopt()`, `opromnext()`, `oprompci2node()`, `oprompath2node()`, and `opromgetbootargs()`. NetBSD handlers include `opiocget()`, `opiocnextprop()`, `opiocset()`, and `opiocgetnext()`. `openprom_ioctl()` dispatches by command and file mode; `openprom_open()` initializes per-file node state.

Control flow: module init registers the misc device and resolves the `/options` node. On open, each descriptor starts at the root node. SunOS ioctls operate either on `/options`, the current node, or a node selected by phandle/path/PCI tuple. NetBSD ioctls copy an `opiocdesc`, resolve the node by phandle, and get/set properties or enumerate nodes/properties. A global mutex serializes all operations.

State and persistence: per-file state tracks current traversal nodes. Global state stores `options_node`. `of_set_property()` calls can mutate the live kernel OF tree/options representation and may affect firmware-like settings exposed to user programs, but the file itself has no independent persistent storage.

Dependencies and integration: depends on SPARC PROM/Open Firmware APIs, miscdevice minor `SUN_OPENPROM_MINOR`, openprom ioctl ABI headers, saved kernel command line, and optional PCI lookup for `OPROMPCI2NODE`.

Risks and test signals: node references from `of_find_node_by_*()` are stored without consistent `of_node_put()` balancing, matching older OF lifetime assumptions but worth auditing. `opiocnextprop()` appears to copy the next property's value rather than name, which is notable for a "next property" call. `oprompci2node()` calls `pci_device_to_OF_node()` before checking whether `pci_get_domain_bus_and_slot()` returned NULL. Property set operations accept user-provided names/values under write mode. Test SunOS and NetBSD ioctl compatibility, read/write mode permission checks, maximum buffer truncation, malformed user pointers, path/phandle traversal, PCI lookup absent/present, property set/get round trips, compat ioctl coverage, and module init when `/options` is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/openprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/oradax.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/oradax.c

Purpose: provides the character-device transport for Oracle Data Analytics Accelerator coprocessors on SPARC M7/M8 systems. User space submits DAX command control blocks through write, maps a completion area through mmap, reads submit/info/kill results, and relies on hypervisor calls for execution.

Important APIs/types/functions: hardware ABI structures include `dax_header`, `dax_control`, `dax_data_access`, `dax_ccb`, and `dax_cca`. `struct dax_ctx` is per-open state with kernel CCB buffer, completion area, pinned user pages, owner/client tasks, result union, and counters. File operations are `dax_open()`, `dax_close()`, `dax_write()`, `dax_read()`, and `dax_devmap()`. Hypervisor helpers include `dax_ccb_exec()`, `dax_preprocess_usr_ccbs()`, `dax_lock_pages()`, `dax_unlock_pages()`, `dax_ccb_wait()`, `dax_ccb_kill()`, `dax_ccb_info()`, and `dax_hv_errno()`. Module init `dax_attach()` discovers the MD virtual device, registers the DAX HV API, checks queue size, and creates the chardev.

Control flow: attach searches machine description `virtual-device` nodes for DAX1/DAX2 compatibility, chooses the HV major/minor and maximum CCB version, registers with the hypervisor, verifies `DAX_MAX_CCBS`, allocates a chardev number/class/device, and registers file operations. Open allocates a CCB buffer and completion-area page range, marks completions complete, and records the owning task. A CCB-array write copies user CCBs into kernel memory, validates version/opcode/address types, installs real completion addresses, pins user pages for VA streams, converts address types to VA alternate context, submits to `sun4v_ccb_submit()`, unlocks unaccepted pages, and returns the accepted byte count. Immediate-command writes perform kill, info, or dequeue by completion-area offset. Reads return the saved result only to the client task. Mmap maps the completion area read-only to the owner.

State and persistence: per-open state persists until close: CCB/CA buffers, pinned pages per completion slot and stream type, owner/client identity, completion statuses, and counters. Hardware/coproc state is in hypervisor queues and completion records. No on-disk persistence exists.

Dependencies and integration: depends on SPARC sun4v hypervisor DAX calls, machine description APIs, `asm/oradax.h` public ABI, Linux char-device/class APIs, user page pinning, physical address conversion, and user mmap/remap. It is selected by `CONFIG_ORACLE_DAX`.

Risks and test signals: user-page pinning currently uses `FOLL_WRITE` for all VA streams, including inputs, which is conservative but may reject read-only inputs. `dax_lock_pages()` indexes `ctx->ccb_buf[i]` while storing pages at `i + idx` and increments `i` for long CCBs; long CCB range accounting must match the user ABI. `ctx->client` gates the write/read protocol and can reject concurrent writes. Close waits and may kill unfinished CCBs before unpinning pages. Test DAX1 versus DAX2 discovery, unsupported MD compatibility, HV registration/query failures, open allocation cleanup, owner versus non-owner mmap/write/read, read-only mmap enforcement, valid and invalid opcodes/address types/CCB versions, long CCB arrays, partial HV acceptance, each HV error mapping, kill/info/dequeue commands, close with pending completions, and pinned-page dirtying for output streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/oradax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/uctrl.c -->
# sources/distributed-fs/ceph-client/drivers/sbus/char/uctrl.c

Purpose: implements a misc-device driver for the Tadpole TS102 microcontroller interface on Sparcbook 3 systems. It can query microcontroller event and external status and exposes a placeholder ioctl interface.

Important APIs/types/functions: register layouts `struct uctrl_regs` and `struct ts102_regs` describe mapped MMIO. `struct uctrl_txn` describes a microcontroller command transaction, and `struct uctrl_status` caches selected status fields. `enum uctrl_opcode` lists many supported microcontroller commands. Core functions are `uctrl_do_txn()`, `uctrl_get_event_status()`, `uctrl_get_external_status()`, `uctrl_open()`, `uctrl_probe()`, and `uctrl_remove()`. Macros `WRITEUCTLDATA` and `READUCTLDATA` poll FIFO status and access data registers.

Control flow: probe allocates global driver state, maps registers, requests the IRQ, registers `/dev/uctrl`, enables RX-not-empty interrupt bits, logs device info, and performs initial event/external status reads. Opening the device re-reads event and external status under a mutex. Transactions write the opcode and input bytes to the controller FIFO, read an ACK, then read requested output bytes. The interrupt handler currently just returns handled, and ioctl accepts no commands.

State and persistence: global singleton state includes mapped registers, IRQ number, a pending field, and cached status. Hardware state is the TS102 microcontroller FIFO/status/interrupt registers. No persistent storage is changed.

Dependencies and integration: depends on SPARC OF platform probing for node name `uctrl`, SBUS read/write helpers, misc minor `UCTRL_MINOR`, IRQ registration, and the Tadpole hardware protocol.

Risks and test signals: `global_driver` is dereferenced in open without checking probe success or removal races. The read macro's polling condition appears inverted for "receive not empty" and may read before data is ready or after timeout. Debug logging is compiled on unconditionally through `#define DEBUG 1`. The IRQ handler ignores device state, and ioctl is effectively unimplemented despite a large opcode list. Test probe failure cleanup, open after remove prevention, event/external status transaction timing, FIFO timeout behavior, IRQ delivery, misc registration failure, and safe behavior when userland issues unsupported ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/sbus/char/uctrl.c -->
