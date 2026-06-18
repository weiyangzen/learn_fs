# Research: subset-b-001070

Grouped research for the source-tree-aligned files in `subset-b-001070`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/init.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/init.c

## Purpose

`init.c` is the MHI host bus and controller lifecycle implementation. It registers the `mhi` bus, allocates controller-private runtime structures, parses controller channel/event configuration, sets up IRQs and DMA-backed MHI contexts, creates the root controller `mhi_device`, and manages MHI client device probe/remove and driver registration. It also owns sysfs attributes for controller-visible metadata and control actions such as serial number, OEM PK hash, SoC reset, and optional EDL trigger.

## Important APIs, Types, And Functions

- Exported controller APIs: `mhi_register_controller()`, `mhi_unregister_controller()`, `mhi_alloc_controller()`, `mhi_free_controller()`, `mhi_prepare_for_power_up()`, and `mhi_unprepare_after_power_down()`.
- Device/client APIs: `mhi_alloc_device()`, `__mhi_driver_register()`, `mhi_driver_unregister()`, and the `mhi_bus_type` bus object.
- Context setup: `mhi_init_dev_ctxt()`, `mhi_deinit_dev_ctxt()`, `mhi_init_mmio()`, `mhi_init_chan_ctxt()`, and `mhi_deinit_chan_ctxt()`.
- Config parsing: `parse_ch_cfg()`, `parse_ev_cfg()`, and `parse_config()` translate `struct mhi_controller_config` into allocated `struct mhi_chan` and `struct mhi_event` arrays.
- String tables for execution environment, device transition, channel state type, and PM state are generated from macros shared with `internal.h` and `trace.h`.

## Control Flow

Controller drivers call `mhi_register_controller()` after filling MMIO, IRQ, register access, runtime PM, and callback fields. Registration validates required callbacks and hardware resources, parses the supplied config, allocates command rings, initializes locks/workqueues/tasklets, selects DMA mapping strategy, allocates a controller id, requests IRQs, creates the root `mhi_device`, adds optional EDL sysfs support, and creates debugfs. Power preparation is separate: `mhi_prepare_for_power_up()` allocates the device context, discovers BHI/BHIe offsets, clears RDDM state if needed, and prepares an RDDM download table when configured.

`mhi_init_mmio()` programs context base addresses, MHI control/data address limits, event-ring counts, hardware event-ring counts, channel doorbell addresses, event doorbell addresses, wake doorbell address, and command doorbell address. Per-channel context creation is delayed until a client opens a channel through transfer preparation.

The bus probe path calls `mhi_device_get_sync()` to wake the device, validates that required callbacks exist for UL/DL/offload/client-managed rings, installs transfer callbacks on the channel structures, and then calls the client driver's `probe()`. Remove resets both directions, wakes waiters, marks channels suspended/disabled, invokes the client `remove()`, deinitializes channel contexts that had been enabled, and balances outstanding `mhi_device_get_sync()` references.

## State And Persistence Behavior

Most persistent state lives in `struct mhi_controller`: allocated channel/event/cmd arrays, `mhi_ctxt`, DMA ring memory, workqueue, PM locks, wake counters, tasklets, IRQs, root `mhi_dev`, and optional firmware/RDDM image tables. Channel state is mirrored in host-side `mhi_chan->ch_state` and device-visible channel context bits. Ring memory is coherent DMA with alignment enforced by `mhi_alloc_aligned_ring()`. Device objects hold references back to channel structures; `mhi_release_device()` clears `mhi_chan->mhi_dev` so suspend/resume or EE changes can recreate devices.

## Dependencies And Integration Points

This file depends on public MHI definitions in `<linux/mhi.h>`, common protocol definitions in `../common.h` through `internal.h`, Linux driver core bus/device APIs, DMA coherent allocation, IRQ APIs, debugfs hooks, sysfs, and the PM functions implemented in `pm.c`. It is used by transport drivers such as `pci_generic.c`, which provide register accessors, IRQ lists, runtime PM callbacks, and controller configs.

## Risks

The cleanup paths are tightly ordered; failures during config parsing, IRQ setup, or root device creation must free only the pieces already initialized. Doorbell offset bounds checks in `mhi_init_mmio()` are critical because invalid MMIO offsets would corrupt unrelated registers. The code mutates controller config-derived event data when shared MSI is used by PCI glue, so configs declared `static const` versus mutable matter. Client probe error paths call `mhi_unprepare_from_transfer()` even if transfer preparation was not performed by the framework here, so channel state assumptions must stay aligned with client driver behavior. Sysfs EDL trigger directly invokes controller reset paths and must only exist when the controller provides `edl_trigger`.

## Test Signals

Useful signals include successful `mhi` bus registration at postcore init, successful controller registration and power preparation for PCI devices, sysfs attributes under the root MHI device, correct creation/removal of channel devices across EE transitions, IRQ request/free balance under `CONFIG_DEBUG_SHIRQ`, DMA allocation failure injection, invalid channel/event config rejection, and suspend/resume paths that destroy and recreate channel devices without stale `mhi_chan->mhi_dev` pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/internal.h -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/internal.h

## Purpose

`internal.h` is the private contract for the MHI host implementation. It centralizes protocol-derived constants, internal PM bit states, execution-environment helpers, ring/channel/event/cmd data structures, doorbell configuration, function prototypes, debugfs stubs, and inline helpers shared by `init.c`, `main.c`, `pm.c`, firmware-loading code, debugfs code, and transport glue.

## Important APIs, Types, And Functions

- Core structures: `struct mhi_ctxt`, `struct mhi_ring`, `struct mhi_cmd`, `struct mhi_buf_info`, `struct mhi_event`, `struct mhi_chan`, `struct db_cfg`, `struct state_transition`, and `struct mhi_pm_transitions`.
- State enumerations: `enum mhi_fw_load_type`, `enum mhi_ch_state_type`, `enum dev_st_transition`, `enum mhi_pm_state`, and `enum mhi_er_type`.
- State string lists: `MHI_EE_LIST`, `MHI_CH_STATE_TYPE_LIST`, `DEV_ST_TRANSITION_LIST`, and `MHI_PM_STATE_LIST`, which feed both runtime string tables and trace symbolic output.
- Access predicates: `MHI_REG_ACCESS_VALID()`, `MHI_PM_IN_ERROR_STATE()`, `MHI_PM_IN_FATAL_STATE()`, `MHI_DB_ACCESS_VALID()`, wake-doorbell validity checks, event-access checks, suspend-state checks, and fatal-error checks.
- Private prototypes expose MHI register access, event processing, channel preparation, power transitions, firmware loading, IRQ handlers, DMA mapping helpers, and device creation/destruction.

## Control Flow

The header does not execute logic directly beyond small helpers, but it defines the state model used by the rest of the host stack. PM state is represented as a single-bit mask rather than a dense enum value at runtime; transition functions use that bitmask and convert it to strings through `to_mhi_pm_state_str()`. The inline `mhi_is_active()` tests public MHI device state, while `mhi_trigger_resume()` raises a wakeup event and cycles transport runtime PM callbacks to force resume.

## State And Persistence Behavior

`struct mhi_ring` stores both coherent DMA addresses and host virtual pointers for ring base, read pointer, write pointer, doorbell address, and the device context write pointer. `struct mhi_chan` combines two rings, channel identity, direction, execution-environment mask, state, completion object, client callbacks, and locks. `struct mhi_event` owns event-ring state, tasklet dispatch, IRQ index, hardware/client/offload flags, and the function pointer that parses events. These structures persist for the lifetime of a registered controller, while per-channel ring memory is allocated when channels are prepared.

## Dependencies And Integration Points

`internal.h` includes `../common.h`, which supplies protocol register offsets, TRE encoders/decoders, public state lists, and MMIO field masks. It integrates with the Linux device model through the exported `mhi_bus_type`, with optional `CONFIG_MHI_BUS_DEBUG` implementations, and with tracepoints through common macro lists consumed by `trace.h`.

## Risks

The PM predicates assume `pm_state` remains a valid single-bit mask; any accidental multi-bit assignment can break string conversion, transition validation, and register access checks. Ring pointer fields are `void *` arithmetic in C extensions and must remain aligned to `struct mhi_ring_element`. Function pointer contracts are broad: missing controller callbacks are checked in `init.c`, but incorrect callbacks can invalidate all higher-level logic. Offload and hardware event flags change ownership of rings, so callers must honor them before allocation, IRQ request, processing, or teardown.

## Test Signals

Build coverage with tracepoints enabled and disabled, `CONFIG_MHI_BUS_DEBUG` enabled and disabled, and compilers that warn on enum/bitmask misuse is valuable. Runtime signals include valid symbolic trace output for PM, EE, channel command, and device transition states; no invalid PM strings during normal operation; and correct behavior for M2 doorbell policies configured through `db_access`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/main.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/main.c

## Purpose

`main.c` implements the MHI host runtime hot path: register access wrappers, doorbell writes, DMA buffer mapping, ring pointer management, virtual device creation/destruction for channels, IRQ handlers, event-ring parsers, transfer queueing, command ring submission, channel start/stop/reset sequencing, and public buffer queue APIs for MHI client drivers.

## Important APIs, Types, And Functions

- Register helpers: `mhi_read_reg()`, `mhi_read_reg_field()`, `mhi_poll_reg_field()`, `mhi_write_reg()`, `mhi_write_reg_field()`, `mhi_write_db()`.
- Doorbell helpers: `mhi_db_brstmode()`, `mhi_db_brstmode_disable()`, `mhi_ring_er_db()`, `mhi_ring_cmd_db()`, and `mhi_ring_chan_db()`.
- Queue APIs: `mhi_queue_skb()`, `mhi_queue_buf()`, `mhi_queue_is_full()`, `mhi_get_free_desc_count()`, and `mhi_gen_tre()`.
- Event/IRQ paths: `mhi_irq_handler()`, `mhi_intvec_handler()`, `mhi_intvec_threaded_handler()`, `mhi_process_ctrl_ev_ring()`, `mhi_process_data_event_ring()`, `mhi_ev_task()`, and `mhi_ctrl_ev_task()`.
- Channel lifecycle: `mhi_send_cmd()`, `mhi_prepare_for_transfer()`, `mhi_unprepare_from_transfer()`, `mhi_reset_chan()`, and private helpers for channel command state.

## Control Flow

Client queueing enters through `mhi_queue_buf()` or `mhi_queue_skb()`, builds a `mhi_buf_info`, checks PM error state and ring fullness, generates a TRE under the channel write lock, maps or bounce-buffers the payload, takes runtime PM and wake references, rings the channel doorbell if PM permits, and balances the runtime PM reference immediately for device-to-host buffers or at completion for host-to-device buffers.

Event IRQs schedule tasklets unless the event ring is client-managed, in which case the owning MHI device receives `MHI_CB_PENDING_DATA`. Event parsers validate device read pointers, translate DMA pointers into host ring pointers, dispatch control events, state changes, command completions, EE changes, TX completions, and RSC completions, then recycle event-ring entries and ring the event doorbell. Command completions update `mhi_chan->ccs` and complete the waiting channel command.

Channel preparation checks EE masks, allocates non-offload channel contexts, sends a START command, and waits for completion. Unprepare sends RESET when appropriate, marks events for the channel as stale, completes pending buffers with `-ENOTCONN`, unmaps DMA, and deinitializes context memory.

## State And Persistence Behavior

The file maintains ring `rp`/`wp` in host memory and mirrors write pointers into device contexts before ringing doorbells. `mhi_buf_info` entries persist in the channel buffer ring until completion or reset. `pending_pkts` tracks outstanding host-to-device transfers and participates in low-power decisions. Channel state changes are protected by per-channel mutexes and rwlocks, while event rings use spinlocks/tasklets and controller PM uses `pm_lock`.

## Dependencies And Integration Points

`main.c` depends on `internal.h` and `trace.h`, DMA mapping APIs, tasklets, IRQ APIs, runtime PM callbacks supplied by the controller, and client callbacks installed during bus probe in `init.c`. It calls PM functions in `pm.c` for M0/M1/M3/SYS_ERR transitions and EE transition scheduling.

## Risks

Ring pointer validation is a major safety boundary; invalid device-provided pointers are logged and processing stops. The code unlocks channel read locks around client callbacks, so callback reentrancy and channel teardown must remain synchronized. Runtime PM reference balance differs by transfer direction and must stay paired with completion/reset paths. RSC event handling intentionally advances local descriptors based on ordered device caching, which relies on device protocol correctness. Command submission returns success even for an unsupported command after logging because the default case does not set an error before queuing; callers currently pass known command types.

## Test Signals

Tracepoints for generated TREs, data/control events, and channel command start/end should line up with successful transfers. Tests should cover ring-full behavior, DMA mapping failure, chained TRE completion, overflow completion, stale events during channel reset, client-managed event notification, invalid event pointer handling, SYS_ERR detection through both intvec and control events, and runtime PM reference balance under heavy UL and DL traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pci_generic.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pci_generic.c

## Purpose

`pci_generic.c` is the generic MHI-over-PCI controller driver for Qualcomm-style modems and related PCIe devices. It maps PCI device IDs to MHI controller configurations, claims PCI resources, wires MHI controller callbacks, registers and powers up the controller, handles EDL triggering, runtime/system PM, health-check recovery, PCI reset, AER recovery, and SR-IOV configuration.

## Important APIs, Types, And Functions

- Device description: `struct mhi_pci_dev_info` records controller config, optional VF config, firmware names, EDL image/trigger support, BAR, DMA width, MRU, sideband wake, M3 support, and reset-on-remove policy.
- Configuration macros build `struct mhi_channel_config` and `struct mhi_event_config` entries for UL, DL, SBL, FP, software data, control, and hardware event rings.
- PCI glue: `mhi_pci_claim()`, `mhi_pci_get_irqs()`, `mhi_pci_read_reg()`, `mhi_pci_write_reg()`, `mhi_pci_runtime_get()`, and `mhi_pci_runtime_put()`.
- Lifecycle: `mhi_pci_probe()`, `mhi_pci_remove()`, `mhi_pci_shutdown()`, `mhi_pci_reset_prepare()`, `mhi_pci_reset_done()`.
- Recovery and PM: `mhi_pci_recovery_work()`, `health_check()`, runtime suspend/resume, system suspend/resume, freeze/restore, and PCI error handlers.

## Control Flow

Probe selects the correct controller config for PF/VF, allocates `struct mhi_pci_device`, initializes recovery work and PF health timer, fills the embedded `struct mhi_controller`, claims PCI BAR and DMA mask, allocates MSI/MSI-X vectors, saves PCI state for recovery, registers the MHI controller, prepares MHI for power-up, and starts async MHI power-up. Runtime autosuspend is enabled only when PCI PME from D3hot and MHI M3 are supported.

When MSI vectors are scarce, `mhi_pci_get_irqs()` falls back to a shared MSI by rewriting each event config IRQ index to zero and setting `nr_irqs` to one. Health checks periodically read the physical function vendor ID; invalid reads queue recovery. Recovery powers down and unprepares MHI if it had started, restores PCI state, verifies liveness, prepares and synchronously powers up MHI, restarts the health timer, or attempts a PCI function reset on failure.

Runtime suspend stops the health timer and recovery work, transitions MHI to M3 if the device is started in AMSS, disables the PCI function, and enables D3 wake. Resume re-enables PCI, restores bus mastering and wake settings, exits M3, and restarts health checks. PCI AER and reset callbacks reuse the same MHI power-down/unprepare and recovery work patterns.

## State And Persistence Behavior

The embedded `mhi_controller` persists for the PCI device lifetime. `mhi_pci_device.status` holds `MHI_PCI_DEV_STARTED` and `MHI_PCI_DEV_SUSPENDED` bits. A saved PCI config snapshot is kept outside the PCI core's transient saved state for sudden error recovery. Timers and workqueues persist until remove/shutdown. Device tables are static, but some event config arrays are intentionally mutable because shared-MSI fallback patches IRQ fields.

## Dependencies And Integration Points

This driver integrates Linux PCI, PM runtime, timers, workqueues, MHI core APIs from `init.c`/`pm.c`, firmware names consumed by the MHI firmware loader, and child MHI client drivers for channels such as MBIM, QMI, DIAG, SAHARA, FIREHOSE, IP_SW, and IP_HW. It registers as `mhi-pci-generic` with a large `pci_device_id` table for Qualcomm, Quectel, Foxconn, Thales/Cinterion, Sierra, Telit, NetPrisma, and HP variants.

## Risks

Shared-MSI fallback mutates `event_cfg` through a `const struct mhi_controller_config *`, so configs backed by read-only memory would be unsafe; the current mutable event arrays are important. Runtime PM error recovery deliberately returns success after queuing async recovery to avoid destabilizing PCI state, which can hide failures except in logs. Health checks only run for physical functions. EDL trigger writes a magic cookie to channel doorbell 91 and resets the SoC; incorrect device matching or offset handling would be disruptive. Remove ordering must cancel timers/work before unregistering MHI to avoid use-after-free.

## Test Signals

Probe logs with the expected device name, successful BAR mapping, DMA mask setup, MSI allocation, MHI controller registration, channel device creation, and mission-mode uevents are primary signals. Exercise shared-MSI systems, PF/VF configs, runtime autosuspend/resume, D3hot wake, firmware crash callbacks, health-check-triggered recovery, AER reset, hibernation freeze/restore, EDL trigger sysfs, and reset-on-remove devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pci_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pm.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pm.c

## Purpose

`pm.c` implements the MHI host power-management and device-state machine. It validates PM state transitions, drives READY/M0/M2/M3/SYS_ERR/disable transitions, manages device wake doorbells, schedules execution-environment transition work, handles mission-mode entry, powers controllers up and down, exports suspend/resume APIs, and sends execution-environment uevents.

## Important APIs, Types, And Functions

- Transition validation: `dev_state_transitions[]` and `mhi_tryset_pm_state()`.
- Device state writes: `mhi_set_mhi_state()`.
- MHI transitions: `mhi_ready_state_transition()`, `mhi_pm_m0_transition()`, `mhi_pm_m1_transition()`, `mhi_pm_m3_transition()`, `mhi_pm_mission_mode_transition()`, `mhi_pm_disable_transition()`, and `mhi_pm_sys_error_transition()`.
- Work scheduling: `mhi_queue_state_transition()`, `mhi_pm_st_worker()`, and `mhi_pm_sys_err_handler()`.
- Exported PM APIs: `mhi_pm_suspend()`, `mhi_pm_resume()`, `mhi_pm_resume_force()`, `mhi_async_power_up()`, `mhi_sync_power_up()`, `mhi_power_down()`, `mhi_power_down_keep_dev()`, `mhi_force_rddm_mode()`, `mhi_device_get_sync()`, and `mhi_device_put()`.

## Control Flow

`mhi_async_power_up()` supplies default wake callbacks if needed, initializes PM to POR, validates the current execution environment, recovers from initial SYS_ERR if possible, enables IRQs, and queues either PBL firmware loading or READY processing. READY processing waits for reset clear and READY set, transitions to POR, initializes MMIO, primes software event rings, and asks the device to enter M0.

M0 transition updates host state, asserts wake, rings event/cmd/channel doorbells as needed, handles doorbell-mode reset requests, then releases wake and wakes waiters. M1 events move to M2 and either notify idle or immediately wake the device if resources are pending. Suspend moves from M0/M1 to M3_ENTER, writes M3, waits for M3 completion, and notifies LPM-capable clients. Resume moves from M3 to M3_EXIT, writes M0, waits for M0/M2, and notifies clients of LPM exit.

Mission-mode transition verifies the device EE, destroys devices from the previous EE, notifies controller and userspace, forces M0, primes hardware event rings, creates channel devices, and drops wake. SYS_ERR transition notifies the controller, moves to SYS_ERR_PROCESS, optionally resets hardware, kills tasklets, destroys channel devices, resets event/cmd contexts, and queues PBL or READY recovery. Disable transition optionally destroys devices, resets hardware unless in RDDM, kills IRQ/tasklets, resets rings, and moves to DISABLE.

## State And Persistence Behavior

`mhi_cntrl->pm_state` is a single-bit internal PM state protected by `pm_lock` and `pm_mutex` depending on scope. `dev_state`, `ee`, transition-list entries, wake counters, `pending_pkts`, M0/M2/M3 counters, and `state_event` waitqueue coordinate asynchronous hardware and software transitions. Device wake is reference counted in `dev_wake`; the wake doorbell is only written when PM-state predicates allow it.

## Dependencies And Integration Points

`pm.c` depends on register/ring helpers in `main.c`, context/MMIO setup in `init.c`, firmware loader functions, public MHI states from `common.h`, controller callbacks such as `status_cb`, `runtime_get`, `runtime_put`, and optional `wake_get`/`wake_put`, plus tracepoints in `trace.h`. PCI glue calls these APIs for power-up, runtime PM, recovery, reset, and removal.

## Risks

Transition correctness depends on `mhi_tryset_pm_state()` receiving valid bitmask states under the right lock. Error and shutdown paths drop `pm_mutex` while destroying devices and waking waiters, which is necessary but creates interleaving sensitivity. Wake reference imbalance is guarded by warnings in disable/SYS_ERR paths but can still cause suspend failures. RDDM support intentionally skips normal SYS_ERR handling, so controller configuration changes can alter crash recovery behavior. Suspend rejects pending packets and wake refs, making runtime PM sensitive to client drivers that hold wake references too long.

## Test Signals

Trace `mhi_tryset_pm_state` and `mhi_pm_st_transition` through full power-up, firmware download, mission-mode, runtime suspend/resume, SYS_ERR recovery, RDDM entry, graceful power-down, and non-graceful link-down. Check uevents for `EXEC_ENV`, controller callbacks for idle, mission mode, SYS_ERROR, fatal error, and RDDM, and warnings for nonzero wake or pending packet counts during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/trace.h -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/trace.h

## Purpose

`trace.h` defines the ftrace tracepoint interface for the MHI host stack. It turns shared MHI state macro lists into trace enums and records transfer ring elements, interrupt-vector state snapshots, PM state changes, event-ring entries, channel command transitions, and queued device-state transitions.

## Important APIs, Types, And Functions

- Trace enum definitions for MHI device states, internal PM states, execution environments, channel command state types, and device transition work states.
- `TRACE_EVENT(mhi_gen_tre)` records generated transfer ring element pointer and dwords.
- `TRACE_EVENT(mhi_intvec_states)` records local EE/state and device EE/state observed in the BHI interrupt-vector handler.
- `TRACE_EVENT(mhi_tryset_pm_state)` records requested PM state transitions.
- `DECLARE_EVENT_CLASS(mhi_process_event_ring)` with `mhi_data_event` and `mhi_ctrl_event` records event ring entries.
- `DECLARE_EVENT_CLASS(mhi_update_channel_state)` with command start/end events records channel command transitions.
- `TRACE_EVENT(mhi_pm_st_transition)` records worker-handled device transition states.

## Control Flow

This header is included normally by MHI source files for tracepoint declarations and included once with `CREATE_TRACE_POINTS` by `init.c` to instantiate tracepoints. The final `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` settings point the trace generator back to the host trace header.

## State And Persistence Behavior

Tracepoints do not alter MHI state. They sample fields from `struct mhi_controller`, `struct mhi_chan`, and `struct mhi_ring_element` at call sites. `tracepoint_string()` through `TPS()` is used for stable reason strings in channel command traces.

## Dependencies And Integration Points

The file depends on Linux tracepoint infrastructure, byte-order helpers, `../common.h`, and `internal.h`. It is called from `main.c` for TRE/event/channel-command tracing and from `pm.c` for PM and device-transition tracing.

## Risks

Trace field extraction assumes pointers passed by call sites remain valid for the trace fast assignment. Symbolic rendering relies on macro lists staying consistent with enum values. Because `mhi_tryset_pm_state` converts bitmask state with `__fls()`, invalid zero or multi-bit PM values would produce misleading trace output.

## Test Signals

With ftrace enabled, expected events should appear under the `mhi_host` trace system during queueing, event completion, channel start/reset, MHI intvec handling, and PM transitions. Build tests should cover tracepoints enabled and disabled, including header multi-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mips_cdmm.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mips_cdmm.c

## Purpose

`mips_cdmm.c` implements the MIPS Common Device Memory Map bus. CDMM exposes per-CPU in-core devices through a common MMIO region. This driver registers the `cdmm` bus, discovers CDMM device register blocks on each CPU, creates `struct mips_cdmm_device` instances, routes driver callbacks to the CPU owning each device, supports early probing for boot-time users, and coordinates CPU hotplug notifications.

## Important APIs, Types, And Functions

- Bus registration: exported `mips_cdmm_bustype`, `mips_cdmm_driver_register()`, and `mips_cdmm_driver_unregister()`.
- Early access: exported `mips_cdmm_early_probe()`.
- Per-CPU setup/discovery: `mips_cdmm_get_bus()`, `mips_cdmm_cur_base()`, weak `mips_cdmm_phys_base()`, `mips_cdmm_setup()`, `mips_cdmm_bus_discover()`, `mips_cdmm_cpu_online()`, and `mips_cdmm_cpu_down_prep()`.
- Callback routing: `BUILD_PERCPU_HELPER()` wraps probe/remove/shutdown through `work_on_cpu()`, and `BUILD_PERDEV_HELPER()` calls driver `cpu_up`/`cpu_down` callbacks for devices on a CPU.
- Data state: `struct mips_cdmm_bus` records physical base, mapped regs, DRB count, reserved block count, discovery status, and offline flag.

## Control Flow

At `subsys_initcall`, the driver registers the bus and a dynamic CPU hotplug state. On CPU online, it gets or allocates that CPU's bus record, configures the CDMM base if needed, marks it online, and either discovers devices or notifies existing drivers via `cpu_up`. Discovery scans device register blocks, decodes ACSR type/size/revision fields, creates one device per nonzero type, assigns a CPU device parent, resource range, bus, unique id, and name, then registers it with the driver core.

Driver probe/remove/shutdown callbacks must execute on the CPU that owns the CDMM device, so driver-core callbacks are wrappers that call `work_on_cpu(cdev->cpu, ...)`. CPU down first calls interested drivers' `cpu_down` callbacks through `bus_for_each_dev()`, then marks the per-CPU bus offline so future users revalidate or reconfigure CDMM.

`mips_cdmm_early_probe()` can be called before normal discovery, provided migration is prevented. It sets up the current CPU's CDMM region and scans for a requested device type, returning an MMIO pointer or an IOMEM error pointer.

## State And Persistence Behavior

CPU0 uses static `mips_cdmm_boot_bus`; other CPUs lazily allocate per-CPU `struct mips_cdmm_bus` pointers. `mips_cdmm_default_base` caches the first successful physical base for other CPUs. Device ids come from an atomic counter. CDMM enablement is stored in CP0 `cdmmbase`; `mips_cdmm_setup()` may inherit bootloader state, use DT/platform override, or copy the cached default.

## Dependencies And Integration Points

The driver depends on MIPS-specific CP0 register helpers, hazards, `cpu_has_cdmm`, `asm/cdmm.h`, device tree address parsing for `mti,mips-cdmm`, Linux CPU hotplug, per-CPU storage, work-on-CPU, and driver core bus APIs. Client CDMM drivers provide `struct mips_cdmm_driver` id tables and optional CPU hotplug callbacks.

## Risks

Callers of setup/early probe must prevent CPU migration; otherwise the per-CPU bus state and CP0 register state can mismatch. A missing physical base is memoized as sentinel `1` after logging once, so later setup returns `-ENOMEM`. Device discovery assumes ACSR size fields advance correctly; malformed hardware can affect scan progress. Probe/remove wrappers rely on `work_on_cpu()` availability during hotplug-sensitive windows.

## Test Signals

Signals include `cdmm%u discovery` logs, sysfs attributes for cpu/type/revision/modalias/resource, modalias `mipscdmm:tXX`, driver probe callbacks running on the owning CPU, CPU online/offline callbacks firing, early probe returning valid MMIO for known devices, and graceful behavior when no CDMM base is provided.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mips_cdmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/moxtet.c -->
# sources/distributed-fs/ceph-client/drivers/bus/moxtet.c

## Purpose

`moxtet.c` implements the Turris MOX module configuration bus over SPI. It discovers the physical module topology, registers a `moxtet` bus and child devices for modules, exposes module identity through sysfs, exports read/write helpers for client drivers, optionally exposes debugfs raw input/output views, and maps module interrupt bits into a nested IRQ domain.

## Important APIs, Types, And Functions

- Bus/driver integration: `moxtet_bus_type`, `__moxtet_register_driver()`, `moxtet_match()`, `moxtet_add_device()`, and child unregister helper.
- Topology/device creation: `moxtet_find_topology()`, `moxtet_set_irq()`, `of_register_moxtet_devices()`, `of_register_moxtet_device()`, and `moxtet_register_devices_from_topology()`.
- Exported device IO: `moxtet_device_read()`, `moxtet_device_write()`, and `moxtet_device_written()`.
- Debugfs: `input_read()`, `output_read()`, `output_write()`, `moxtet_register_debugfs()`, and `moxtet_unregister_debugfs()`.
- IRQ support: `moxtet_irq_domain_map()`, `moxtet_irq_domain_xlate()`, mask/unmask/print callbacks, `moxtet_irq_read()`, `moxtet_irq_thread_fn()`, `moxtet_irq_setup()`, and `moxtet_irq_free()`.
- SPI lifecycle: `moxtet_probe()`, `moxtet_remove()`, `moxtet_init()`, and `moxtet_exit()`.

## Control Flow

Module init registers the `moxtet` bus and the SPI driver. Probe sets up SPI, allocates `struct moxtet`, initializes the mutex, obtains the parent IRQ from device tree, reads topology bytes from SPI, validates the CPU module byte, records downstream module ids until `0xff`, logs known modules, and builds IRQ bit positions for modules with interrupt lines. If interrupts exist, it creates an IRQ domain, maps existing hardware IRQs, initializes all as masked, and requests a shared oneshot threaded parent IRQ.

Child device creation happens from device tree children first and then from discovered topology. DT children use their `reg` index and the discovered module id at that index; topology-created devices fill gaps without DT nodes. Duplicate detection is protected by a static mutex and compares bus instance, module id, and index. Remove frees the parent IRQ, tears down IRQ mappings/domain, removes debugfs, unregisters child devices, and destroys the mutex.

The exported IO helpers lock the bus mutex around SPI operations. Reads return the upper nibble of the module's topology/status byte. Writes store an output value into `tx[count - idx]` and write the whole chain, reflecting shift-register ordering. `moxtet_device_written()` reports the cached output byte for a module.

## State And Persistence Behavior

`struct moxtet` stores discovered module ids, module count, transmit shadow buffer, mutex, parent IRQ, IRQ-domain data, and debugfs root. Each `struct moxtet_device` holds bus pointer, module id, index, and optional OF node. Module metadata is static in `mox_module_table` and order-sensitive because IDs index directly into it. IRQ existence, mask, and hardware positions persist in `moxtet->irq`.

## Dependencies And Integration Points

The driver depends on `dt-bindings/bus/moxtet.h`, `<linux/moxtet.h>`, SPI core, OF device matching, OF IRQ lookup, generic IRQ domains, nested IRQ handling, debugfs, and Linux driver core. Client module drivers bind by OF compatible string or Moxtet module id table and use the exported read/write helpers.

## Risks

`moxtet_remove()` unconditionally calls `free_irq()` and `moxtet_irq_free()` even when no child IRQs existed; probe requires a valid parent IRQ, but `moxtet_irq.domain` may be null if no module advertised IRQ bits. The module table order must never drift from hardware IDs. The SPI output index reversal is easy to break when changing topology handling. IRQ handling repeatedly reads until no unmasked pending bits remain; a stuck asserted module IRQ can keep the threaded handler busy. DT child registration must clear `OF_POPULATED` and drop node refs on all failure/remove paths.

## Test Signals

Expected signals include topology logs for MOX A and downstream modules, child devices named `moxtet-<module>.<idx>`, sysfs module id/name/description, successful binding by OF and id table, debugfs hex input/output matching SPI state, nested IRQs delivered for PCI/Topaz/Peridot/USB3 modules, mask/unmask behavior, duplicate child rejection, and clean remove without OF node leaks or IRQ-domain mappings left behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/moxtet.c -->
