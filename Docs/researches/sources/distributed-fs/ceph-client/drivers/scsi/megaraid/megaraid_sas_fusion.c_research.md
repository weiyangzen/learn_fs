# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.c

## Purpose

`megaraid_sas_fusion.c` is the Fusion-generation MegaRAID SAS controller implementation. It owns adapter initialization, DMA resource allocation, IOC init, interrupt and reply-queue handling, SCSI I/O request construction, management DCMD passthrough, RAID/JBOD map synchronization, SCSI task management, online controller reset, watchdog/fault handling, and crash-dump collection. It plugs these operations into `megasas_instance_template_fusion` so the common `megaraid_sas` driver core can call the Fusion-specific implementation.

The file bridges Linux SCSI/block-layer commands to the controller's MPI2-style request descriptor interface. It uses the fast-path geometry helpers from `megaraid_sas_fp.c` and the wire/data structures from `megaraid_sas_fusion.h`.

## Important APIs, Types, And Functions

Adapter reset and interrupt APIs include `megasas_adp_reset_wait_for_ready()`, `megasas_enable_intr_fusion()`, `megasas_disable_intr_fusion()`, `megasas_clear_intr_fusion()`, `megasas_read_fw_status_reg_fusion()`, and `megasas_adp_reset_fusion()`. These manipulate PCI registers through `instance->reg_set`, protect PCI config access during reset, and handle Fusion reset write sequences.

Command and DMA allocation APIs include `megasas_alloc_fusion_context()`, `megasas_free_fusion_context()`, `megasas_alloc_cmds_fusion()`, `megasas_free_cmds_fusion()`, `megasas_alloc_request_fusion()`, `megasas_alloc_reply_fusion()`, `megasas_alloc_rdpq_fusion()`, `megasas_create_sg_sense_fusion()`, and `megasas_allocate_raid_maps()`. They allocate the `fusion_context`, IO request frames, request descriptors, reply descriptor queues, RDPQ arrays, chain frames, sense buffers, command objects, firmware maps, and driver maps.

Initialization APIs include `megasas_fusion_update_can_queue()`, `megasas_configure_queue_sizes()`, `megasas_alloc_ioc_init_frame()`, `megasas_ioc_init_fusion()`, and `megasas_init_adapter_fusion()`. `megasas_ioc_init_fusion()` builds the IOC init payload, negotiates driver capabilities, posts the init frame, checks firmware status, and detects features like atomic descriptors.

Map synchronization APIs include `megasas_sync_pd_seq_num()` for JBOD/system-PD sequence maps, `megasas_get_ld_map_info()` for LD RAID maps, `megasas_get_map_info()` for validated fast-path map activation, and `megasas_sync_map_info()` for pended map-change notification.

I/O construction APIs include `megasas_build_and_issue_cmd_fusion()`, `megasas_build_io_fusion()`, `megasas_build_ldio_fusion()`, `megasas_build_ld_nonrw_fusion()`, `megasas_build_syspd_fusion()`, `megasas_make_sgl()`, `megasas_make_sgl_fusion()`, `megasas_make_prp_nvme()`, `megasas_set_pd_lba()`, `megasas_stream_detect()`, `megasas_set_raidflag_cpu_affinity()`, and `megasas_prepare_secondRaid1_IO()`. These functions prepare `MPI2_RAID_SCSI_IO_REQUEST` frames, RAID contexts, request descriptors, SGLs/PRPs, CDBs, MSI-X routing, and dual-command RAID1 writes.

Completion APIs include `complete_cmd_fusion()`, `megasas_complete_r1_command()`, `map_cmd_status()`, `megasas_blk_mq_poll()`, `megasas_irqpoll()`, `megasas_complete_cmd_dpc_fusion()`, and `megasas_isr_fusion()`. They drain reply descriptors, map firmware statuses to SCSI results, unmap DMA, return commands, update outstanding counters, and call `scsi_done()`.

Management and task-management APIs include `build_mpt_mfi_pass_thru()`, `build_mpt_cmd()`, `megasas_issue_dcmd_fusion()`, `megasas_issue_tm()`, `megasas_task_abort_fusion()`, `megasas_reset_target_fusion()`, and `megasas_check_mpio_paths()`. They tunnel MFI frames over Fusion passthrough and send MPI2 task management requests for abort and target reset.

Reset/fault APIs include `megasas_wait_for_outstanding_fusion()`, `megasas_reset_reply_desc()`, `megasas_refire_mgmt_cmd()`, `megasas_return_polled_cmds()`, `megasas_reset_fusion()`, `megasas_fusion_start_watchdog()`, `megasas_fusion_stop_watchdog()`, `megasas_fault_detect_work()`, `megasas_fusion_crash_dump()`, and `megasas_fusion_ocr_wq()`.

## Control Flow And Integration

Probe-time initialization enters through the instance template's `.init_adapter = megasas_init_adapter_fusion`. The function reads firmware queue-depth capabilities, calculates host and controller queue sizes, derives maximum chain frame sizes from scratchpad bits, allocates IOC init memory, MFI commands, Fusion commands, request/reply descriptors, sense and SG buffers, issues IOC init, reads controller info, allocates RAID maps, fetches and validates the LD map, and pends map synchronization if fast-path mapping succeeds.

Normal SCSI I/O enters `.build_and_issue_cmd = megasas_build_and_issue_cmd_fusion`. The function first enforces LDIO and firmware outstanding thresholds, gets the tag-indexed `megasas_cmd_fusion`, obtains a request descriptor, calls `megasas_build_io_fusion()`, assigns the SMID, optionally creates a peer command for RAID1 fast-path writes, increments per-device busy accounting, and posts one or two descriptors through `megasas_fire_cmd_fusion()`.

`megasas_build_io_fusion()` resets reusable frame fields, copies the SCSI CDB, sets initial CDB length, dispatches by `megasas_cmd_type()` to LD read/write, LD non-read/write, system-PD read/write, or system-PD non-read/write builders, constructs SGLs, stores the SGE count in the appropriate RAID context layout, sets SCSI read/write control flags, installs sense buffer address, and links the SCSI command to the Fusion command.

`megasas_build_ldio_fusion()` is the main LD hot path. It parses 6/10/12/16-byte read/write CDBs into LBA and transfer length, calls `MR_BuildRaidContext()` when a validated RAID map exists, chooses MSI-X index, applies Ventura RAID1 write and bandwidth-limiting rules, updates stream-detection and CPU-affinity hints, and then chooses fast-path physical I/O or LD firmware I/O. Fast path rewrites the CDB to PD LBA with `megasas_set_pd_lba()`, sets `MPI2_FUNCTION_SCSI_IO_REQUEST`, installs physical devhandle and LUN, may perform RAID1 read load balancing through `get_updated_dev_handle()`, and records alternate mirror handles for dual-command RAID1 writes. Non-fast-path LD I/O uses `MEGASAS_MPI2_FUNCTION_LD_IO_REQUEST` and target id as devhandle.

Completion is reply-descriptor driven. `megasas_isr_fusion()`, blk-mq polling, irq_poll, or the DPC all call `complete_cmd_fusion()`. It reads descriptors from `fusion->reply_frames_desc[MSIxIndex]` using `fusion->last_reply_idx`, looks up the command by SMID, switches on request `Function`, completes task management completions, maps SCSI status for fast-path and LD I/O, handles RAID1 peer completion aggregation, completes MFI passthrough commands, marks reply descriptors unused, updates the reply-post host index register, and restores queue depth as needed.

Online controller reset enters `megasas_reset_fusion()`. It serializes with `reset_mutex`, handles crash-dump forced-fault mode for I/O/DCMD timeout, disables interrupts and irq_poll, drains outstanding completions, returns or requeues pending SCSI commands on failure, attempts adapter reset and IOC init up to bounded retries, refires or completes management commands, reloads RAID/JBOD maps, resets stream-detection state, re-enables interrupts and irq_poll, refreshes target properties, restarts SR-IOV heartbeat, reconfigures crash-dump settings, and either returns the adapter to operational state or kills the HBA.

## State And Persistence Behavior

The dominant state container is `struct fusion_context`, allocated in `megasas_alloc_fusion_context()` and attached to `instance->ctrl_context`. It owns command arrays, DMA pools, request frames, reply descriptors, RDPQ tracking, map buffers, load-balance caches, span caches, IOC init memory, and feature flags. `struct megasas_instance` contributes global adapter state: queue depths, outstanding counters, map ids, reset flags, heartbeat state, crash-dump buffers, interrupt maps, and SCSI host configuration.

Most state is volatile and rebuilt at probe or OCR. The firmware remains the source of truth for controller configuration, LD maps, PD sequence maps, and capability bits. Driver persistence across reset consists of preserving software allocations where possible, refiring eligible management commands, returning SCSI commands to the mid-layer, and refreshing firmware-derived maps after IOC init.

Several double-buffering schemes are important:

- `fusion->ld_map[2]` and `fusion->ld_drv_map[2]` alternate by `instance->map_id & 1`.
- `fusion->pd_seq_sync[2]` alternates by `instance->pd_seq_map_id & 1`.
- RDPQ reply queues are split into chunks so groups of queue descriptors stay within required 4 GB DMA boundaries.

Outstanding counts are held in atomics such as `fw_outstanding`, `ldio_outstanding`, per-device balanced-mode busy counters, load-balance PD pending counters, and blk-mq poll busy flags. Reset flags `MEGASAS_FUSION_IN_RESET` and `MEGASAS_FUSION_OCR_NOT_POSSIBLE` gate ISR and reset behavior.

Crash dump state uses `instance->crash_dump_buf` as firmware DMA input and `instance->crash_buf[]` vmalloc buffers as host-side copies. `fw_crash_state`, `fw_crash_buffer_size`, `drv_buf_index`, and `drv_buf_alloc` track availability for user-space collection.

## Dependencies

This file depends on `megaraid_sas_fusion.h` for all Fusion wire formats and context structures, `megaraid_sas.h` for common driver state and MFI command definitions, and `megaraid_sas_fp.c` APIs for RAID map validation and LD-to-PD mapping. It integrates with Linux PCI, DMA pools/coherent DMA, SCSI mid-layer, blk-mq polling, irq_poll, delayed workqueues, timers, DMI, endian helpers, atomics, mutexes, and kernel logging.

External driver functions include `megasas_complete_cmd()`, `megasas_transition_to_ready()`, `megasas_get_ctrl_info()`, `megasas_get_target_prop()`, `megasas_set_dynamic_target_properties()`, `megasas_setup_jbod_map()`, `megasas_set_crash_dump_params()`, `megasas_get_snapdump_properties()`, `megaraid_sas_kill_hba()`, `megasas_check_and_restore_queue_depth()`, MFI command allocation/return/issue helpers, and SR-IOV heartbeat helpers.

## Risks And Edge Cases

Resource allocation has strict DMA boundary requirements. Sense buffers, request frames, reply queues, and RDPQ chunks must not cross 4 GB boundaries for supported controllers. The code retries with alignment pools or reduces queue depth in some cases, but allocation failure paths must avoid leaks and partially initialized pointer use.

The I/O hot path reuses preallocated frames by tag. Any field not reset in `megasas_build_io_fusion()` or `megasas_return_cmd_fusion()` can leak stale context into later commands. This is especially sensitive for `RaidContext`, `ChainOffset`, EEDP fields, peer SMIDs, `r1_alt_dev_handle`, SGL flags, and stream-detection bits.

Fast-path routing correctness depends on the RAID map validation and geometry code. Bugs in `MR_BuildRaidContext()`, CDB rewriting, or devhandle selection can misdirect physical I/O. The fallback path must disable fast path when maps are unavailable, PD handles are invalid, or read-ahead/stream policies require LD I/O.

RAID1 fast-path writes issue two commands for one SCSI command. Completion only finishes the SCSI command after both peer commands complete, and it chooses error status from the failing peer when needed. Peer SMID, alternate devhandle, outstanding counter, and command return ordering are all correctness-critical.

Completion and reset concurrency is delicate. Reply queues may be drained by ISR, irq_poll, blk-mq poll, DPC, reset, and synchronized IRQ paths. `access_irq_context()` and per-queue `busy_mq_poll` reduce concurrent consumers, but reset must disable interrupts, synchronize IRQs, drain completions, and return commands without double completion.

OCR is high risk because it mutates nearly every state domain: outstanding commands, firmware state, maps, management command ownership, queue depths, stream caches, heartbeat timers, target properties, and crash-dump settings. A failed reset kills the HBA. SR-IOV VF behavior has special heartbeat and settle-time paths that differ from PF reset.

NVMe PRP construction is another boundary-sensitive area. `megasas_make_prp_nvme()` splits scatterlist entries into PRP entries, inserts PRP list pointers at page boundaries, and relies on `max_chain_frame_sz` being large enough. Incorrect page-size assumptions or oversized SGLs can corrupt chain frames.

## Test Signals

Probe tests should show successful IOC init, correct queue-depth logging, successful controller info read, RAID map validation, and no DMA allocation boundary errors. I/O tests should cover LD fast path, LD firmware path, system PD path, non-read/write commands, NVMe fast path with PRPs, chained SGLs, T10 PI/EEDP read/write CDBs, RAID1 read load balancing, RAID1 dual fast-path writes, stream-detected read-ahead fallback, and multi-queue MSI-X routing.

Completion tests should verify residual counts and sense data for check-condition paths, `DID_IMM_RETRY` on config sequence mismatch, bad-target mapping for offline/missing devices, correct decrement of `fw_outstanding` and `ldio_outstanding`, no double completion during irq_poll/ISR races, and correct reply-post host index updates.

Reset tests should inject SCSI I/O timeout, MFI DCMD timeout, firmware fault, crash-dump available, failed IOC init, map fetch failure, SR-IOV heartbeat timeout, and management commands active during OCR. Passing signals are returned or requeued SCSI commands, no stuck outstanding counters, refreshed maps, re-enabled interrupts, restarted heartbeat where applicable, and adapter state restored to `MEGASAS_HBA_OPERATIONAL` or clean HBA kill on unrecoverable failure.
