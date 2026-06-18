# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.c

## Purpose
`bfad_im.c` implements the SCSI initiator-mode shim. It registers SCSI host templates, creates SCSI hosts for physical/vport ports, maps FCS initiator-target nexus callbacks into FC remote ports, queues SCSI commands to BFA IO objects, handles SCSI error recovery, manages queue depth, and posts vendor AEN events.

## Important APIs, Types, and Functions
Exported callbacks include `bfa_cb_ioim_done`, `bfa_cb_ioim_good_comp`, `bfa_cb_ioim_abort`, and `bfa_cb_tskim_done` for firmware/BFA completions. SCSI EH functions include `bfad_im_abort_handler`, `bfad_im_reset_lun_handler`, and `bfad_im_reset_target_handler`. FCS callbacks `bfa_fcb_itnim_alloc/free/online/offline` manage `bfad_itnim_s` lifecycle. Port/host lifecycle functions include `bfad_im_probe`, `bfad_im_probe_undo`, `bfad_im_port_new/delete/clean`, `bfad_im_scsi_host_alloc/free`, `bfad_scsi_host_alloc/free`, `bfad_thread_workq`, and `bfad_destroy_workq`. The file defines `bfad_im_scsi_host_template` and `bfad_im_vport_template`.

## Control Flow
Module init attaches physical and vport FC transport templates. Probe allocates `bfad_im_s`, creates an ordered reclaim workqueue, and initializes AEN work. Port creation allocates `bfad_im_port_s`; SCSI host allocation reserves an IDR ID, allocates a `Scsi_Host`, sets target/LUN/queue limits and transport template, and calls `scsi_add_host_with_dma`.

When FCS reports an ITNIM online/offline/free transition, the callback sets state and queues `bfad_im_itnim_work_handler`. The work handler adds FC remote ports on online, stores `fc_rport->dd_data`, appends to `itnim_mapped_list`, deletes remote ports on offline/free, unlinks mappings, and frees the ITNIM on final free. `bfad_im_queuecommand_lck` checks rport readiness and EEH state, maps SCSI DMA, verifies HAL started, allocates a BFA IO with the target nexus, stores it in `host_scribble`, and starts it. Completion callbacks set SCSI result, copy sense/residue, unmap DMA, adjust queue depth, and call `scsi_done`.

## State and Persistence
State is in-memory: `bfad_im_port_s` host and target lists, `bfad_itnim_s` state/channel/target ID/queue-depth timestamps, `Scsi_Host` transport attributes, command private status/waitqueue bits, AEN queues, and BFA IO/task objects. Queue-depth ramping persists only during runtime through `last_ramp_up_time` and `last_queue_full_time`.

## Dependencies and Integration Points
The file depends on Linux SCSI mid-layer, FC transport, IDR, workqueues, BFA IO/task/FCS APIs, LUN masking helpers, module parameters from `bfad_drv.h`, and sysfs/transport templates from `bfad_attr.c`. It feeds BSG by providing `bfad_get_im_port` data and host templates.

## Risks
Several paths assume `rport->dd_data`, `itnim_data->itnim`, and `itnim->bfa_itnim` are valid; disconnect races are partly handled but remain high risk. Abort waits poll `host_scribble` with exponential sleeps and then calls `scsi_done`, so double-completion and timeout interactions need scrutiny. Workqueue transitions drop and reacquire `bfad_lock` around FC transport calls, making state changes during the unlocked interval important. LUN masking special-cases LUN 0 and alters scan flags.

## Test Signals
Exercise probe/remove, physical and vport host creation, target discovery/loss/relogin, queuecommand under link-down and EEH states, IO completion status mapping, queue-full ramp down/up, LUN and target reset success/failure, LUN masking visibility, and AEN vendor event posting.
