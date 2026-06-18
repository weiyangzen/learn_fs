# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_cmds.h

## Purpose
`efc_cmds.h` declares the libefc-to-SLI command API implemented by `efc_cmds.c`. It lets state machines request hardware allocation, attach, detach, and resource cleanup without knowing mailbox formats.

## Important APIs, Types, And Functions
`EFC_SPARAM_DMA_SZ` defines the DMA staging size used for service parameters. The exported functions cover nport/VPI allocation, attach, and free; domain/VFI allocation, attach, and free; remote-node/RPI allocation, attach, detach, and resource release.

## Control Flow And State
The declarations encode the lifecycle ordering expected by callers: allocate a domain or nport, attach it once an FC_ID is known, and later free it; allocate a remote node, attach it with service parameters, detach it when shutting down, then free resources. Some functions are asynchronous by design because mailbox completions post libefc events later.

## Dependencies And Integration Points
Callers pass `struct efc`, `struct efc_domain`, `struct efc_nport`, `struct efc_remote_node`, and `struct efc_dma` from `efclib.h`/`efc_common.h`. Implementations use SLI-4 mailbox helpers and base-driver `issue_mbox_rqst`.

## Risks And Test Signals
The header does not expose ownership annotations, so tests need to verify callers do not free objects before callbacks. Useful signals include state-machine unit/integration traces showing each command result mapped to the documented `EFC_EVT_*` event and resource leak checks over repeated link flap cycles.
