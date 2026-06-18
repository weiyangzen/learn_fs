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
