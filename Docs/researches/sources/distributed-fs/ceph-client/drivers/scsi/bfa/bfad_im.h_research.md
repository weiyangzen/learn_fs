# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_im.h

## Purpose
`bfad_im.h` declares the initiator-mode interface shared between BFAD core, SCSI/FC transport, BSG, and IM implementation files. It defines per-command, per-port, per-target-nexus, binding, and module state for the initiator path.

## Important APIs, Types, and Functions
The header declares IM lifecycle APIs (`bfad_im_module_init/exit`, `bfad_im_probe/undo`, `bfad_im_port_new/delete/clean`, `bfad_im_scsi_host_alloc/free`), transport helpers (`bfad_fc_host_init`, `bfad_scsi_host_alloc/free`, `bfad_get_itnim`), queue-depth functions, and BSG entry points. `struct bfad_cmd_priv` stores task-management completion status and waitqueue pointer in SCSI command private space. `struct bfad_im_port_s` links a BFAD port to its SCSI host, vport, binding list, and mapped ITNIM list. `enum bfad_itnim_state` models target nexus lifecycle. `struct bfad_itnim_s` stores FCS/BFA nexus pointers, FC rport pointer, SCSI target/channel IDs, work item, and queue-depth timing. `bfad_im_post_vendor_event` fills AEN entries and queues vendor event work.

## Control Flow
The header supports flow implemented in `bfad_im.c`: command private status is set by task completion callbacks; IM ports are allocated during port creation; ITNIM states drive workqueue processing; `bfad_get_aen_entry` moves entries from free to active queue; `bfad_im_post_vendor_event` timestamps and schedules notification only after FC4 probe completion.

## State and Persistence
All structures are runtime state. `bfad_im_port_s` stores host-visible mappings. `bfad_itnim_s` stores target nexus state and queue-depth timing. AEN entries carry wall-clock timestamps, instance numbers, sequence numbers, category, and event type until posted.

## Dependencies and Integration Points
It includes `bfa_fcs.h` and references SCSI, FC transport, workqueue, and BFA types through included driver headers. It exports templates and transport pointers consumed by `bfad_attr.c` and `bfad_im.c`.

## Risks
The command private `status` bit packing combines `IO_DONE_BIT` with shifted `bfi_tskim_status`; changes to task status width or bit usage could break waits. `bfad_get_im_port` assumes `shost_priv(host)` contains a valid pointer wrapper. AEN macros manipulate queues under a dedicated spinlock but queue work into IM workqueue, so teardown ordering matters.

## Test Signals
Compile tests should validate structure visibility and SCSI `cmd_size` assumptions. Runtime tests should cover task-management wait completion, AEN queue posting during probe and teardown, target online/offline/free transitions, and BSG access through declared hooks.
