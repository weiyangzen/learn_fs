# subset-b-005275 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ips.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ips.h

## Purpose

`ips.h` is the shared hardware, firmware, command, status, ioctl, and in-memory object contract for the Adaptec/IBM ServeRAID `ips` SCSI RAID controller driver. It does not implement request execution itself; instead it defines the constants, packet layouts, host-adapter state, queue structures, and function-pointer table consumed by the corresponding driver implementation. The file covers several controller families, including Copperhead/Trombone/Clarinet, Morpheus, and Marco, with macros that decide whether the implementation should use I2O delivery, memory-mapped I/O, or enhanced scatter-gather lists.

## Important APIs, Types, and Functions

The primary access macros are `IPS_HA()`, `IPS_COMMAND_ID()`, `IPS_IS_TROMBONE()`, `IPS_IS_CLARINET()`, `IPS_IS_MORPHEUS()`, `IPS_IS_MARCO()`, `IPS_USE_I2O_DELIVER()`, `IPS_USE_MEMIO()`, `IPS_HAS_ENH_SGLIST()`, `IPS_USE_ENH_SGLIST()`, and `IPS_SGLIST_SIZE()`. Hardware definitions include register offsets such as `IPS_REG_HISR`, `IPS_REG_CCSAR`, `IPS_REG_CCCR`, status queue registers, flash registers, I2O queue registers, and i960 message registers, plus bit definitions for interrupts, queue state, reset, bus mastering, and command start.

Command opcodes include logical-drive information, subsystem reads, configuration reads, NVRAM access, logical read/write, scatter-gather read/write, DCDB passthrough, flush, error table, firmware/BIOS download, version query, FFDC, and channel reset. Packet formats are represented by `IPS_IO_CMD`, `IPS_LD_CMD`, `IPS_IOCTL_CMD`, `IPS_DCDB_CMD`, `IPS_CS_CMD`, `IPS_US_CMD`, `IPS_FC_CMD`, `IPS_STATUS_CMD`, `IPS_NVRAM_CMD`, `IPS_VERSION_INFO`, `IPS_FFDC_CMD`, `IPS_FLASHFW_CMD`, `IPS_FLASHBIOS_CMD`, and the `IPS_HOST_COMMAND` union. Runtime structures include `IPS_ADAPTER` for the status queue, `IPS_LD_INFO`, `IPS_ENQ`, `IPS_CONF`, `IPS_NVRAM_P5`, `IPS_VERSION_DATA`, SCSI inquiry/capacity/sense/mode-page structures, `IPS_STD_SG_LIST`, `IPS_ENH_SG_LIST`, `ips_scb_t`, `ips_scb_pt_t`, and `ips_passthru_t`.

The central software state object is `ips_ha_t`. It owns adapter identity, queue limits, DMA/coherent buffers, SCB freelist/waitlist/activelist, pending passthrough queue, inquiry/config/NVRAM/subsystem buffers, ioctl and flash buffers, MMIO pointers, hardware function table, PCI device pointer, reset/active/wait flags, version data, and compatibility state. `ips_hw_func_t` abstracts controller-specific operations such as reset, issue, init, interrupt detection, interrupt handling, status update, BIOS erase/program/verify, and interrupt enable.

## Control Flow

The header encodes how the implementation is expected to branch during probe and I/O setup. PCI vendor/device/revision and optional module flags drive the chosen register interface and command delivery path. Older adapters use standard 32-bit scatter-gather entries, while Morpheus/Marco or hosts with `IPS_HA_ENH_SG` use enhanced entries with high and low address words. Command construction chooses the packet variant by firmware operation: logical-drive I/O uses `IPS_IO_CMD`; non-disk SCSI passthrough uses `IPS_DCDB_CMD` plus `IPS_DCDB_TABLE`; flash and version paths use their dedicated command structures.

Status flow is built around `IPS_STATUS` entries in an `IPS_ADAPTER` status queue. The implementation can derive command IDs, basic status, and extended status from each status word, then map the command ID back into `ips_ha_t.scbs`. Higher-level SCSI emulation uses the inquiry, read-capacity, request-sense, and mode-page layouts in this header to synthesize or parse target-visible responses.

## State and Persistence Behavior

All driver-owned state is transient kernel memory. Persistent controller state is represented indirectly through NVRAM page 5 (`IPS_NVRAM_P5`), subsystem parameters, firmware/BIOS version records, logical-drive configuration, and flash command packets. The header defines compatibility strings and the `IPS_DEFINE_COMPAT_TABLE()` macro so the implementation can compare adapter type and BIOS/firmware compatibility IDs. `ips_ha_t` tracks reset count, last FFDC timestamp, BIOS version, and `requires_esl`, but those fields are runtime reflections of hardware or policy rather than filesystem persistence.

## Dependencies and Integration Points

The header depends on Linux SCSI, gendisk geometry, DMA address, PCI, MMIO, uaccess, and NMI watchdog support. It is the ABI boundary for user passthrough ioctls such as `IPS_COPPUSRCMD`, `IPS_COPPIOCCMD`, `IPS_NUMCTRLS`, and `IPS_CTRLINFO`; these expose controller commands and adapter information to management utilities. It also integrates with firmware through fixed packet layouts, status codes, version/compatibility IDs, flash image directions, NVRAM signatures, and ServeRAID-specific logical-drive metadata.

## Risks and Edge Cases

Many structures are hardware ABI layouts; field order, width, and alignment are critical. The header mixes 32-bit bus-address fields with `dma_addr_t` fields, so 64-bit DMA paths must consistently select enhanced SGLs and avoid truncation. Several packet structures use fixed 12-byte CDBs while tape/extended variants carry 16-byte CDBs, which is a common source of passthrough errors. `IPS_MAX_*` constants constrain queue depth, logical drives, targets, chunks, and transfer length; implementation code must reject or split requests that exceed them. The compatibility/version block is intentionally generated by build tooling, so manual edits can desynchronize reported driver versions from firmware compatibility checks.

## Test Signals

Useful validation signals include compiling the `ips` driver with no structure-size or prototype drift, probe paths selecting expected IO/MMIO/I2O/enhanced-SG modes for each adapter family, passthrough utilities receiving correctly shaped `ips_passthru_t` data, management queries returning version and compatibility IDs, logical-drive inquiry/capacity/mode-page responses matching the header layouts, and stress I/O over both standard and enhanced scatter-gather paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/Makefile

## Purpose

This Makefile declares the Intel C600/Xeon E3 SAS controller low-level driver object composition. It builds the `isci` module when `CONFIG_SCSI_ISCI` is enabled and lists every translation unit linked into the composite `isci.o` object.

## Important APIs, Types, and Functions

The key build declarations are `obj-$(CONFIG_SCSI_ISCI) += isci.o` and `isci-objs := ...`. The object list includes `init.o`, `phy.o`, `request.o`, `remote_device.o`, `port.o`, `host.o`, `task.o`, `probe_roms.o`, `remote_node_context.o`, `remote_node_table.o`, `unsolicited_frame_control.o`, and `port_config.o`.

## Control Flow

There is no runtime control flow in the file, but the object order defines what source files participate in the module link. `init.o` supplies module and PCI entry points; `host.o` supplies controller lifecycle, interrupts, DMA setup, and request posting; `phy.o` supplies phy state handling; the remaining files supply ports, devices, requests, task management, firmware/OEM parameter parsing, remote-node allocation, unsolicited-frame handling, and port configuration.

## State and Persistence Behavior

The Makefile stores no runtime state. Its persistent effect is build-system state: enabling or disabling `CONFIG_SCSI_ISCI` determines whether the driver is present in the kernel or module build.

## Dependencies and Integration Points

It integrates with kbuild's composite-object convention. The file assumes all listed objects are in the same directory and that `CONFIG_SCSI_ISCI` is provided by the SCSI Kconfig tree. The module source set also implicitly depends on libsas, PCI, DMA, firmware loading, and SCSI transport support through the linked source files.

## Risks and Edge Cases

Dropping an object from `isci-objs` can compile successfully only if no symbols from that object are referenced, but it may silently remove subsystem behavior such as ROM parsing or frame control. Adding new source files requires updating this list. The trailing backslash style means accidental whitespace or deletion at line ends can alter the object list.

## Test Signals

The primary signal is a successful kernel build with `CONFIG_SCSI_ISCI=m` or `y`, producing an `isci` module/object with all expected symbols. Runtime smoke tests should show the `isci` PCI driver registering, firmware name advertised, and libsas callbacks wired from the linked units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/host.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/host.c

## Purpose

`host.c` implements the core controller side of the Intel C600 SAS (`isci`) driver. It owns the controller state machine, interrupt and completion processing, DMA memory setup, hardware initialization/reset, phy startup scheduling, power-control throttling, remote-node and task-context allocation, IO/task posting, controller stop/deinit, and SGPIO writes. It is the bridge between libsas/SCSI-visible operations and SCU/SMU hardware registers.

## Important APIs, Types, and Functions

Generic state-machine helpers are `sci_init_sm()` and `sci_change_state()`. Interrupt handling is split across `isci_msix_isr()`, `isci_intx_isr()`, `isci_error_isr()`, `sci_controller_isr()`, `sci_controller_error_isr()`, `sci_controller_completion_handler()`, and `isci_host_completion_routine()`. Completion dispatch goes through `sci_controller_process_completions()`, which routes task completions, SDMA completions, unsolicited frames, events, and notify entries to request, phy, port, or remote-device handlers.

Lifecycle APIs include `isci_host_init()`, `isci_host_start()`, `isci_host_scan_finished()`, `isci_host_deinit()`, `sci_controller_start()`, `sci_controller_stop()`, `sci_controller_reset()`, and `sci_controller_transition_to_ready()`. Hardware setup is handled by `sci_controller_construct()`, `sci_controller_initialize()`, `sci_controller_dma_alloc()`, `sci_controller_mem_init()`, `sci_controller_afe_initialization()`, `sci_controller_initialize_completion_queue()`, and `sci_controller_initialize_unsolicited_frame_queue()`.

Request and resource APIs include `sci_controller_post_request()`, `sci_request_by_tag()`, `isci_alloc_tag()`, `isci_free_tag()`, `isci_tci_free()`, `sci_controller_start_io()`, `sci_controller_continue_io()`, `sci_controller_complete_io()`, `sci_controller_terminate_request()`, `sci_controller_start_task()`, `sci_controller_allocate_remote_node_context()`, and `sci_controller_free_remote_node_context()`. Link and device coordination uses `sci_controller_link_up()`, `sci_controller_link_down()`, `sci_controller_has_remote_devices_stopping()`, and `sci_controller_remote_device_stopped()`.

## Control Flow

Initialization starts with `isci_host_init()`. It constructs the controller state machine, ports, dummy port, phys, and timers, resets hardware, performs controller initialization, allocates coherent queues/context/request memory, writes DMA base registers, constructs unsolicited-frame control, and enables SGPIO output selection. `sci_controller_initialize()` programs AFE analog settings, releases reset, waits for context RAM initialization, reads hardware capacity, configures protocol engines and DMA relaxed ordering, initializes phys, assigns port register windows, and initializes the port-configuration agent.

Starting begins in `isci_host_start()`, which marks `IHOST_START_PENDING`, calls `sci_controller_start()`, and enables interrupts. `sci_controller_start()` rebuilds the task-context free pool and remote-node table, disables interrupts while programming queues, starts ports, starts phys sequentially through `sci_controller_start_next_phy()`, arms a controller timeout, and transitions to `SCIC_STARTING`. Phy startup is paced by `phy_startup_timeout()` and by link-up callbacks. When all required phys and port-agent masks are ready, `sci_controller_transition_to_ready()` enters `SCIC_READY` and wakes SCSI scanning.

Interrupt flow first checks whether completion queue entries are present. MSI-X completion interrupts schedule the host tasklet; INTx also handles error interrupts inline. The tasklet drains the completion queue under `scic_lock`, dispatches completions by type, writes the SMU get pointer, clears completion interrupts, unmasks interrupts, and updates interrupt coalescing based on active task contexts. Unsolicited frames are routed either to phy frame handling during link bring-up or to remote devices after an RNC exists.

Stop/deinit flow marks `IHOST_STOP_PENDING`, starts `SCIC_STOPPING`, stops devices and ports, waits until remote devices finish stopping, then stops phys, disables SGPIO, resets hardware, and synchronously deletes controller, port-agent, power-control, port, and phy timers. Request posting requires `SCIC_READY`: start/continue task contexts set `IREQ_ACTIVE` and write post-context commands; completion clears active state after the remote-device layer accepts completion; termination posts a TC abort when appropriate.

## State and Persistence Behavior

Runtime state is held in `struct isci_host`: state-machine state, flags, timers, user/OEM parameters, port-agent masks, device table, remote-node table, power-control queue, task-context sequence numbers, coherent task/RNC/completion/UFI buffers, register pointers, TCI circular pool, phys, ports, libsas host, request objects, and remote-device objects. No filesystem persistence is performed. Hardware-facing persistent inputs are OEM/firmware parameters supplied by probe-time code and copied into `ihost->oem_parameters`; runtime state is rebuilt on resume.

Power control is a controller-local scheduler. It allows only `max_spin_up()` phys to consume power per interval, tracks waiting phys by phy index, grants all phys attached to the same SAS address together for wide SAS links, and uses a timer to reset the grant window. IO tags combine a sequence nibble and task-context index, and sequence numbers are advanced on free to reject stale completions.

## Dependencies and Integration Points

The file depends on Linux interrupt, tasklet, timer, spinlock, DMA coherent allocation, PCI MMIO, circ_buf, libsas, SCSI host scanning, and register accessor APIs. Internal dependencies include `port.h`, `remote_device.h`, `request.h`, `scu_completion_codes.h`, `scu_event_codes.h`, `registers.h`, `scu_remote_node_context.h`, `scu_task_context.h`, unsolicited-frame control, remote-node table, and port configuration. It integrates with libsas through host start/scan completion, task completion callbacks, phy/port/device notifications in sibling files, and GPIO writes.

## Risks and Edge Cases

Completion queue cycle-bit handling is central; an off-by-one or stale get pointer can lose interrupts or reprocess entries. `isci_host_completion_routine()` subtracts `SCI_MAX_PORTS` from active TCI count and feeds `ilog2(active)`, so zero/underflow behavior is a sensitive area. The timer cancellation model relies on `sci_timer.cancel` because some timers are deleted while `scic_lock` is held; callbacks must honor the flag consistently. Stop completion waits on remote-device state, so a device that never leaves `SCI_DEV_STOPPING` can block deinit until the controller timeout path marks failure. AFE programming is revision- and cable-selection-specific; incorrect OEM values or override bits can degrade link reliability. Several SDMA/error paths log TODOs rather than completing failed IO/device state, making hardware fault injection important.

## Test Signals

Signals include successful probe and `scsi_scan_host()` after `IHOST_START_PENDING` clears, link-up/link-down messages matching port-agent configuration, completion queue progress under I/O load, stale-tag rejection after abort/reuse, hotplug handling through unsolicited frames, remote-node allocation/free under expander-attached SATA and SSP devices, suspend/resume rebuilding hardware state, stop/remove completing without hung wait queues, SGPIO writes returning expected counts, and fault-injection tests for queue suspend, fatal events, TC abort, and controller start timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/host.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/host.h

## Purpose

`host.h` declares the controller object model and public controller-side APIs for the `isci` driver. It ties together libsas host state, SCU/SMU register windows, DMA context tables, phy/port/device arrays, power control, port configuration, wait queues, tasklets, and the common SCI state machine.

## Important APIs, Types, and Functions

`struct isci_host` is the primary type. It contains `sci_base_state_machine sm`, user and OEM parameters, `sci_port_configuration_agent`, `device_table`, `sci_remote_node_table`, `sci_power_control`, IO sequence numbers, task/RNC/completion/UFI DMA memory, unsolicited-frame control, phy-start timers, interrupt coalescing fields, MMIO register pointers, TCI circular pool, controller ID, `phys[]`, `ports[]`, `sas_ports[]`, `sas_ha`, PCI device, flags, event waitqueue, completion tasklet, lock, request table, and remote-device storage.

`struct sci_power_control` tracks SATA/SAS spin-up throttling with a timer, `phys_waiting`, `phys_granted_power`, and per-phy requester slots. `struct sci_port_configuration_agent` tracks configured and ready phy masks, valid port ranges, a timer, and link-up/link-down handler callbacks. `enum sci_controller_states` defines controller lifecycle states from initial/reset/initializing/initialized through starting/ready/resetting/stopping/failed.

Inline helpers include `to_pci_info()`, `to_shost()`, `for_each_isci_host`, wait helpers for host/device start and stop, `dev_to_ihost()`, `idev_to_ihost()`, tag construction/extraction macros `ISCI_TAG`, `ISCI_TAG_SEQ`, `ISCI_TAG_TCI`, revision helpers `is_a2()` through `is_c1()`, cable override helpers, and `isci_gpio_count()`. External declarations expose controller posting, frame release/copy, RNC allocation/free, request lookup, power-control queue operations, link notifications, IO/task lifecycle, host init/deinit/start/completion, port-configuration agent operations, and GPIO writes.

## Control Flow

The header defines the state transitions that `host.c` implements. Probe allocates `struct isci_host`, initializes ports/phys/devices, and calls `isci_host_init()`. Scanning invokes `isci_host_start()`, and `isci_host_scan_finished()` blocks SCSI scan completion until the start flag clears. IO paths allocate tags, start requests or tasks, complete or terminate them, and free tags through the declared controller APIs. Link notifications from `phy.c` enter `sci_controller_link_up()` or `sci_controller_link_down()`, which dispatch to the port-configuration agent. Remove/suspend paths call `isci_host_deinit()` and wait helpers.

## State and Persistence Behavior

`host.h` defines all controller runtime state but no persistent storage. Flags `IHOST_START_PENDING`, `IHOST_STOP_PENDING`, and `IHOST_IRQ_ENABLED` coordinate async lifecycle and interrupt masking. The device table maps hardware remote-node indexes to `isci_remote_device` objects, while the TCI pool and IO sequence array protect request reuse. OEM/user parameters are stored per host after module/platform/firmware parsing, and cable selections may be overridden globally through the module parameter declared elsewhere.

## Dependencies and Integration Points

The header includes libsas/SATA integration (`scsi/sas_ata.h`), remote device, phy, remote-node table, registers, unsolicited frame control, and probe ROM parameter definitions. It is included by most `isci` source files to share controller state and exported controller operations. It also binds to PCI through `struct pci_dev`, to SCSI through `Scsi_Host`, and to libsas through `sas_ha_struct`, `asd_sas_port`, and `asd_sas_phy`.

## Risks and Edge Cases

Because `struct isci_host` embeds arrays sized by hardware constants, changing `SCI_MAX_*` constants affects DMA table sizing, pool masks, tag encoding, and object lifetimes across the driver. `ISCI_TAG_SEQ()` and `ISCI_TAG_TCI()` assume power-of-two sequence and request counts, enforced in `isci.h`; mismatches would make stale completion checks unsafe. The wait helpers rely on flags being cleared on every failure and timeout path. `ports[SCI_MAX_PORTS + 1]` includes a dummy port, so callers must avoid treating every entry as a real libsas port.

## Test Signals

Compile-time signals include all users agreeing on `struct isci_host` field names and exported prototypes. Runtime signals include waiters waking on host/device start/stop, correct tag reuse behavior after many request cycles, link-up/down routing through the configured port mode, and remove/suspend paths deleting timers without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/init.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/init.c

## Purpose

`init.c` is the module, PCI, libsas, and SCSI-host registration layer for the Intel C600 SAS `isci` driver. It defines supported PCI IDs, module parameters, SCSI host template, libsas domain callbacks, PCI probe/remove, suspend/resume, host allocation, OEM parameter loading, and module init/exit.

## Important APIs, Types, and Functions

Module registration uses `isci_init()` and `isci_exit()`, a `pci_driver` named `isci`, and firmware declaration `MODULE_FIRMWARE(ISCI_FW_NAME)`. Supported devices are listed in `isci_id_table`. Module parameters include `no_outbound_task_to`, `ssp_max_occ_to`, `stp_max_occ_to`, `ssp_inactive_to`, `stp_inactive_to`, `phy_gen`, `max_concurr_spinup`, and `cable_selection_override`.

The SCSI surface is `isci_sht`, built from `LIBSAS_SHT_BASE`, with `scan_finished = isci_host_scan_finished`, `scan_start = isci_host_start`, queue depth, SG size, abort handler, host attributes, ATA sdev attributes, and DIF/DIX support enabled during host allocation. The libsas callback table `isci_transport_ops` wires port formed/deformed, device found/gone, execute task, task management, ATA readiness, nexus clear, phy control, and GPIO write callbacks to sibling driver files.

PCI and allocation helpers include `isci_register_sas_ha()`, `isci_unregister()`, `isci_pci_init()`, `num_controllers()`, `isci_setup_interrupts()`, `isci_user_parameters_get()`, `sci_user_parameters_set()`, `sci_oem_defaults()`, `isci_host_alloc()`, `isci_pci_probe()`, `isci_pci_remove()`, `isci_suspend()`, and `isci_resume()`.

## Control Flow

Module init attaches a SAS transport template using `isci_transport_ops` and registers the PCI driver. Probe allocates `isci_pci_info`, tries OEM parameter sources in priority order (EFI variable, option ROM, then request_firmware), validates any discovered per-controller parameters, initializes PCI BARs and DMA masks, allocates one or two `isci_host` objects based on BAR size, sets up MSI-X or shared INTx interrupts, and starts SCSI scanning for each host.

`isci_host_alloc()` initializes locks, waitqueues, tasklet, libsas host pointers, default/user/OEM parameters, ports, phys, and remote-device list heads. It allocates a `Scsi_Host`, calls `isci_host_init()` to initialize hardware/private state, attaches the SAS transport, sets host addressing and command limits, enables DIF/DIX guard support, adds the SCSI host, and registers the libsas HA. On failures it removes or drops the partially allocated SCSI host.

Interrupt setup first requests the exact MSI-X vector count, two vectors per controller, with even vectors for completions and odd vectors for errors. If MSI-X allocation or IRQ request fails, it frees any partial MSI-X setup and falls back to shared INTx, registering one handler per host on vector zero. Remove waits for host start, unregisters the SAS HA/SCSI host, and deinitializes hardware. Suspend unregisters active hardware state after `sas_suspend_ha()`; resume prepares libsas, reinitializes hardware, restarts the host, waits for start, and resumes libsas.

## State and Persistence Behavior

Persistent driver configuration is via module parameters and optional platform/firmware OEM data. Runtime state is allocated with devm-managed memory under the PCI device and normal SCSI host references. `pci_info->orom` stores the selected OEM parameter block for host allocation. The sysfs `isci_id` attribute exposes the per-controller ID. No on-disk state is written by this file.

## Dependencies and Integration Points

The file depends on Linux module, PCI, firmware, EFI runtime variable support, DMA mask APIs, SCSI host registration, libsas transport registration, SAS ATA attributes, tasklet setup, and power-management hooks. Internal integration points include `host.h`, `task.h`, `probe_roms.h`, port/device/task/phy functions declared in sibling headers, and the firmware file name from `probe_roms.h`.

## Risks and Edge Cases

OEM parameter source fallback is subtle: invalid option ROM entries discard the whole ROM path and fall back to firmware/defaults. `isci_host_alloc()` checks `id > orom->hdr.num_elements`, which should be reviewed with the ROM element count semantics because off-by-one validation could read an invalid controller slot. MSI-X setup requests an exact vector count; systems unable to provide it immediately fall back to INTx. Probe calls `scsi_scan_host()` after interrupts are registered, so host start and scan completion depend on `IHOST_START_PENDING` clearing even on start timeout. Resume assumes `isci_host_init()` and `isci_host_start()` restore enough hardware state before `sas_resume_ha()`.

## Test Signals

Validation signals include module load printing version `1.2.0`, PCI probe for all listed Intel device IDs, correct one-versus-two controller detection by BAR size, OEM parameter source messages, fallback to default SAS addresses when firmware is absent, MSI-X and INTx interrupt paths both working, `isci_id` sysfs values per host, SCSI scan delayed until controller start completes, libsas device discovery, and suspend/resume preserving the SAS domain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/isci.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/isci.h

## Purpose

`isci.h` is the common constants, status-code, timer, and base state-machine header for the Intel C600 SAS driver. It defines global hardware limits, BAR layout, queue sizes, completion-frame limits, transfer limits, SCI status enumerations, endian conversion helper, IRQ prototypes, and the minimal state-machine abstraction used by host, phy, port, device, and request code.

## Important APIs, Types, and Functions

Important constants include `DRV_NAME`, BAR indexes and sizes, MSI-X vector counts, `ISCI_CAN_QUEUE_VAL`, controller stop timeout, invalid IO tag value, and all `SCI_MAX_*` limits for phys, ports, SMP phys, remote devices, IO requests, sequence numbers, controllers, domains, scatter-gather elements, and completion queue sizing. The SCU queue definitions combine critical notifications, events, unsolicited frames, IO requests, and scratch entries into `SCU_MAX_COMPLETION_QUEUE_ENTRIES`.

`check_sizes()` provides compile-time assertions that event, unsolicited-frame, completion-queue, IO-request, and sequence limits remain power-of-two where required. `enum sci_status` defines generic controller/device/request statuses; `enum sci_io_status` and `enum sci_task_status` map IO and task-specific names onto those generic values. `sci_swab32_cpy()` converts dword-swapped SCU frame data to standard memory layout. `struct sci_timer` wraps `timer_list` with a cancel flag and helpers `sci_init_timer()`, `sci_mod_timer()`, and `sci_del_timer()`. `struct sci_base_state_machine` and `struct sci_base_state` define the enter/exit callback table model, with `sci_init_sm()` and `sci_change_state()` implemented in `host.c`.

## Control Flow

The header does not own runtime flow, but its types shape all driver state machines. Callers initialize a `sci_base_state_machine` with a state table and initial ID, then transition through `sci_change_state()`, which calls exit and enter hooks. Timer users call `sci_mod_timer()` to arm and `sci_del_timer()` to set `cancel` before deleting; callbacks check `cancel` under the relevant lock. Status values returned from controller, phy, port, device, IO, and task functions determine whether callers continue posting hardware commands, wait for async completion, retry, or fail upward to libsas/SCSI.

## State and Persistence Behavior

`isci.h` defines no persistent storage. Its constants are compile-time state shaping DMA allocations, queue masks, tag encoding, and firmware-visible limits. `struct sci_timer.cancel` is transient synchronization state that prevents callbacks deleted under `scic_lock` from acting on stale timers.

## Dependencies and Integration Points

The header includes Linux interrupt and type definitions. It integrates with the rest of the driver through shared constants and status values, with hardware register code through SCU limits, with libsas and SCSI through queue depths and protocol status mapping, and with IRQ setup through the `isci_msix_isr()`, `isci_intx_isr()`, and `isci_error_isr()` prototypes.

## Risks and Edge Cases

Changing any `SCI_MAX_*` value can break power-of-two assumptions, tag bit packing, completion queue masks, DMA table sizes, or hardware capacity comparisons. `SCU_MAX_COMPLETION_QUEUE_SHIFT` uses `ilog2()` on the computed entry count and expects the compile-time checks to keep that count a power of two. `sci_timer` deletion is not equivalent to `timer_delete_sync()` in all paths; users must honor the cancellation convention. Status enums are shared across layers, so adding or reordering values can affect IO/task aliases.

## Test Signals

Build-time `BUILD_BUG_ON*` checks are the first signal. Runtime signals include stable tag sequence masking, completion queue wraparound behavior, timers not firing after cancellation, and consistent status propagation from low-level SCI functions to libsas task completion and error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/isci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.c

## Purpose

`phy.c` implements Intel SCU phy initialization, link training, event and frame handling, hard/link reset control, libsas phy-control callbacks, and the phy state machine for the `isci` driver. It translates hardware OSSP/link events and unsolicited frames into libsas-visible link-up/link-down, SAS identify-frame, SATA signature-FIS, broadcast-change, and phy counter behavior.

## Important APIs, Types, and Functions

Public/exported functions include `sci_phy_linkrate()`, `phy_get_non_dummy_port()`, `sci_phy_set_port()`, `sci_phy_initialize()`, `sci_phy_setup_transport()`, `sci_phy_resume()`, `sci_phy_get_sas_address()`, `sci_phy_get_attached_sas_address()`, `sci_phy_get_protocols()`, `sci_phy_start()`, `sci_phy_stop()`, `sci_phy_reset()`, `sci_phy_consume_power_handler()`, `sci_phy_event_handler()`, `sci_phy_frame_handler()`, `sci_phy_construct()`, `isci_phy_init()`, and `isci_phy_control()`.

Hardware setup is split into `sci_phy_transport_layer_initialization()` and `sci_phy_link_layer_initialization()`. Internal helpers include `phy_to_host()`, `sciphy_to_dev()`, `phy_sata_timeout()`, `sci_phy_suspend()`, `sci_phy_start_sas_link_training()`, `sci_phy_start_sata_link_training()`, `sci_phy_complete_link_training()`, `phy_event_name()`, `scu_link_layer_set_txcomsas_timeout()`, `scu_link_layer_stop_protocol_engine()`, `scu_link_layer_start_oob()`, and `scu_link_layer_tx_hard_reset()`.

## Control Flow

Initialization writes transport-layer defaults, invalidates the STP remote-node index, enables STP write-data prefetch, programs identify data, source SAS address, phy ID, OOB reset, phy capabilities and parity, spin-up insertion controls, ALIGN insertion frequencies, revision-specific lookup/timeouts, max link rate, rate-change timeout, arbitration timer for A2 hardware, and disables link-layer hang detection. The phy then enters `SCI_PHY_STOPPED`.

Starting requires `SCI_PHY_STOPPED` and transitions into `SCI_PHY_STARTING`. The starting entry stops/suspends the protocol engine, starts OOB, clears protocol/broadcast state, notifies link down if restarting from ready, and enters the starting substate chain. Events then drive protocol selection and speed negotiation: SAS detected moves to SAS speed wait; SATA spin-up hold moves to SATA power wait; SAS/SATA speed events record negotiated link rate; identify timeouts extend TX COMSAS timeout and restart; link failures reset to starting. SAS identify frames are consumed in `SCI_PHY_SUB_AWAIT_IAF_UF`; SATA signature FIS frames are consumed in `SCI_PHY_SUB_AWAIT_SIG_FIS_UF`.

Power gating is coordinated with `host.c`: SAS or SATA power substates enqueue the phy with controller power control. `sci_phy_consume_power_handler()` either enables notify-enable-spinup for SAS or releases SATA spin-up hold and restarts OOB. Successful final substates enter `SCI_PHY_READY`, which calls `sci_controller_link_up()`. Exiting ready suspends the phy and clears STP RNI. Stopped entry deletes SATA timers, stops the protocol engine, and notifies link down for non-initial transitions.

The libsas `isci_phy_control()` callback implements disable, link reset, hard reset, and event counter retrieval. Link reset stops and restarts OOB under `scic_lock`; hard reset delegates to port reset logic; counter retrieval reads link-layer error counters into `struct sas_phy`.

## State and Persistence Behavior

Per-phy runtime state lives in `struct isci_phy`: base state machine, owning port, negotiated speed, protocol, phy index, delayed broadcast-change flag, link-training flag, SATA timer, transport/link register pointers, libsas phy object, SAS address, and last received identify frame or signature FIS. No persistent storage is written. The frame data is protected by `sas_phy.frame_rcvd_lock` when copied from unsolicited frames.

## Dependencies and Integration Points

The file depends on SCU event codes, register bit macros, OEM/user parameters from probe ROM structures, host power-control and link notification APIs, port activation/broadcast APIs, unsolicited-frame control, libsas phy objects, ATA FIS definitions, and PCI revision helpers. It is called from `host.c` during controller initialization, completion/event dispatch, controller start, deinit, and libsas phy management.

## Risks and Edge Cases

The start substate machine has many restart paths for mixed SAS/SATA indications, repeated hardware events, identify timeouts, and link failures. Incorrect state acceptance can strand a phy in link training or report a false link. SATA signature FIS timeout is long, and cancellation relies on the `sci_timer.cancel` convention. `sci_phy_get_attached_sas_address()` copies directly from the received identify frame and is only valid after SAS frame handling. Broadcast changes arriving before port assignment are deferred through `bcn_received_while_port_unassigned`; missed replay would hide topology changes. The hard reset path differs for SSP and non-SSP protocols, so SATA and SAS reset tests must be separate.

## Test Signals

Useful signals include link training at 1.5/3/6 Gbps for SAS and SATA devices, expander identify-frame handling, SATA signature FIS capture, spin-up throttling with multiple direct-attached disks, broadcast-change delivery before and after port assignment, link reset and hard reset through sysfs/libsas, phy counter reads, hotplug link-failure recovery, and suspend/resume reinitializing register pointers and timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.h

## Purpose

`phy.h` declares the `isci` phy object, phy-specific hardware frame/property structures, phy counter IDs, phy state IDs, and exported phy operations. It is the shared contract between host, port, completion, and libsas phy-control code.

## Important APIs, Types, and Functions

`struct isci_phy` contains the SCI state machine, owning port pointer, negotiated link rate, attached protocol, phy index, deferred broadcast flag, link-training flag, SATA timer, transport and link-layer MMIO register pointers, embedded `asd_sas_phy`, SAS address, and a union for the last received SAS identify frame or SATA device-to-host FIS.

`struct sci_phy_cap` models link-layer PHY capabilities with start, SSC, generation support, requested link rate, and parity bits. `struct sci_phy_proto` models SAS/STP/SMP/SSP initiator and target protocol bits. `struct sci_phy_properties`, `struct sci_sas_phy_properties`, and `struct sci_sata_phy_properties` describe runtime properties for generic, SAS, and SATA phys. `enum sci_phy_counter_id` lists optional counter IDs for frames, dwords, sync loss, disparity, CRC, timeout primitives, credit blocking, short frames, exhausted credit, after-DONE frames, and speed-negotiation sync errors.

`enum sci_phy_states` defines the base and starting-substate machine: initial, stopped, starting, await OSSP, await SAS speed, await IAF, await SAS power, await SATA power, await SATA phy, await SATA speed, await signature FIS, final, ready, resetting, and final. Exported functions cover construction, port assignment, initialization, start/stop/reset/resume, transport setup, event/frame handling, power consumption, address/protocol getters, link-rate getter, libsas initialization, and libsas phy control.

## Control Flow

The header-level state model is implemented in `phy.c`. Host initialization constructs each phy on the dummy port, initializes register windows, and transitions to stopped. Controller start invokes `sci_phy_start()`, event completions call `sci_phy_event_handler()`, unsolicited frames call `sci_phy_frame_handler()`, and final link-training success enters ready and notifies the controller. Port code can reassign phys with `sci_phy_set_port()`, and libsas management calls `isci_phy_control()`.

## State and Persistence Behavior

All state is in memory and hardware registers. The SAS address is copied from OEM parameters during `isci_phy_init()` and exposed through the embedded libsas phy. The received-frame union is the last link-discovery frame state used by libsas and device discovery; it is not persisted.

## Dependencies and Integration Points

The header includes SAS/libsas definitions, common `isci.h`, and `sas.h`, and forward-declares `struct isci_host`. It depends on register type declarations from included driver headers through users of the function prototypes. Integration points include host startup, port configuration, unsolicited-frame control, libsas phy management, and ATA signature FIS handling.

## Risks and Edge Cases

The `PHY_STATES` macro is used both for string names and enum values; edits must keep ordering stable with the state table in `phy.c`. `to_iphy()` relies on `asd_sas_phy` being embedded in `struct isci_phy`. The received-frame union overlays SAS and SATA frame formats, so consumers must check protocol/state before interpreting it. Timer, port, and register pointers are initialized in different phases, so callers must not invoke runtime handlers before `sci_phy_initialize()`.

## Test Signals

Compile signals include state enum/table alignment and prototype agreement. Runtime signals include correct libsas phy attributes, accurate link rate from `sci_phy_linkrate()`, valid SAS address reporting, frame data visible after discovery, successful phy enable/disable/reset operations, and correct event counter propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.h -->
