# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.c

## Purpose
`bfa_msgq.c` implements the host/firmware message queue transport used for larger firmware control messages. It owns a host-to-firmware command DMA ring, a firmware-to-host response DMA ring, mailbox doorbells for producer/consumer index updates, deferred command posting when the command ring is full, and message-class dispatch for response handlers.

## Important APIs, Types, and Functions
- `bfa_msgq_meminfo()` and `bfa_msgq_memclaim()` define and claim aligned DMA storage for command and response rings.
- `bfa_msgq_attach()` initializes command/response queue state, registers the MSGQ mailbox ISR, and registers IOC lifecycle notification.
- `bfa_msgq_regisr()` installs a response handler per BFI message class.
- `bfa_msgq_cmd_post()` copies a command into the command ring if space is available, otherwise queues it on `cmdq.pending_q`.
- `bfa_msgq_rsp_copy()` copies response payload bytes from the response ring without advancing the live queue consumer index.
- Internal FSMs `cmdq_sm_*` and `rspq_sm_*` manage stopped, init wait, ready, and doorbell-wait states.

## Control Flow and State
On `BFA_IOC_E_ENABLED`, `bfa_msgq_notify()` initializes a wait counter, starts both queue FSMs, and sends a MSGQ init mailbox containing command and response DMA addresses/depths. `bfa_msgq_init_rsp()` drives both queues from init-wait to ready. Posting a command uses `ntohs(cmd->msg_hdr->num_entries)` to test free entries, copies one or more 64-byte entries with `__cmd_copy()`, invokes the command callback with `BFA_STATUS_OK`, and sends `CMDQ_E_POST` to trigger a producer-index doorbell. If the ring lacks space, the command entry remains on `pending_q` until firmware sends a command-consumer-index update.

Firmware responses arrive first as mailbox events handled by `bfa_msgq_isr()`. Response producer-index doorbells call `bfa_msgq_rspq_pi_update()`, which walks response entries until consumer equals producer, dispatches each message to `rsphdlr[msg_class]`, advances by `num_entries`, and then sends a response consumer-index doorbell. Firmware can request a command-ring copy using `BFI_MSGQ_I2H_CMDQ_COPY_REQ`; the driver replies in 28-byte chunks through mailbox messages until `bytes_to_copy` reaches zero.

## State and Persistence Behavior
Queue state is in-memory plus DMA-visible rings: producer/consumer indices, ring depths, pending command list, doorbell mailbox commands, copy state (`token`, `offset`, `bytes_to_copy`), and response handlers. IOC disable or failure resets indices and flags and drains pending commands with `BFA_STATUS_FAILED`. The rings themselves are not persisted beyond device lifetime.

## Dependencies and Integration Points
This file depends on `bfi.h` for MSGQ wire formats, `bfa_msgq.h` for queue structures, and `bfa_ioc.h` for mailbox queueing and IOC lifecycle notifications. `bna_enet.c` attaches MSGQ, registers the ENET class handler, and posts ENET commands for port, pause, stats, queue config, MAC, VLAN, RSS, and RIT operations.

## Risks
- Command callbacks indicate that a command was copied into the MSGQ ring, not that firmware completed the requested operation; higher layers must wait for class-specific responses.
- Response dispatch stops if a message class is out of range or lacks a handler, leaving later responses unprocessed until the issue is resolved.
- Ring-depth arithmetic assumes power-of-two depths because indexes are wrapped with bit masks.
- The code trusts `num_entries` in response headers for advancement; corrupt firmware data could desynchronize the ring.
- Stopped/init-wait states record doorbell-update flags when posts occur, so callers must tolerate delayed notification.

## Test Signals
Signals include MSGQ init success after IOC enable, command queue full and pending-list drain behavior, correct producer/consumer doorbells, multi-entry command and response wrapping, class dispatch for ENET responses, copy-request chunk sequencing, pending-command failure callbacks on IOC failure, and no stuck `dbell_wait` state under mailbox backpressure.
