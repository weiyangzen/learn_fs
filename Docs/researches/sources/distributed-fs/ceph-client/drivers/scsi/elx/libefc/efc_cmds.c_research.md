# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.c

## Purpose
`efc_cmds.c` translates libefc domain, nport, and remote-node lifecycle requests into SLI-4 resources and mailbox commands. It owns VFI/VPI/RPI allocation, registration, unregistration, DMA service-parameter staging, and callback-to-event conversion.

## Important APIs, Types, And Functions
Public entry points are `efc_cmd_nport_alloc`, `efc_cmd_nport_attach`, `efc_cmd_nport_free`, `efc_cmd_domain_alloc`, `efc_cmd_domain_attach`, `efc_cmd_domain_free`, `efc_cmd_node_alloc`, `efc_cmd_node_attach`, `efc_cmd_node_detach`, and `efc_node_free_resources`. Internal helpers validate mailbox status, allocate/read service parameters (`READ_SPARM64`), initialize VPI/VFI, register/unregister VPI/VFI/RPI, and call `efc_nport_cb`, `efc_domain_cb`, or `efc_remote_node_cb` with the corresponding libefc events.

## Control Flow And State
Nport allocation reserves a VPI, optionally reads hardware WWPN/WWNN into DMA, then issues `INIT_VPI`. Attach sets `fc_id`, sends `REG_VPI`, marks `attaching`, and on callback posts attach ok/fail. Free either unregisters an attached VPI, defers via `free_req_pending` while attach is outstanding, or posts `NPORT_FREE_OK`. Domain allocation allocates service-parameter DMA, reserves a VFI, runs `INIT_VFI`, then `READ_SPARM64`; domain attach sends `REG_VFI`; domain free sends `UNREG_VFI`. Node allocation reserves an RPI and stores `fc_id`/nport; attach sends `REG_RPI`; detach sends `UNREG_RPI`, treating `RPI_NOT_REG` as acceptable when appropriate.

## Dependencies And Integration Points
This file depends on `sli_resource_alloc/free`, `sli_cmd_*` builders, `efc->tt.issue_mbox_rqst`, Linux DMA APIs, and libefc state-machine callbacks. It is the hardware-facing half of the higher-level domain/nport/node state machines.

## Risks And Test Signals
Risks include leaked SLI resources on mailbox-format or issue failures, event callbacks after partially freed DMA, duplicate `return -EIO` and comment artifacts indicating lightly curated code, and deferred nport free racing attach completion. Test signals should cover mailbox success/failure for every VFI/VPI/RPI command, DMA allocation failure, attach-then-immediate-free, RPI-not-registered detach, and correct posting of alloc/attach/free events.
