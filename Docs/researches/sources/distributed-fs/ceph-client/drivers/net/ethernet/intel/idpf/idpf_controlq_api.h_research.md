# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_api.h

## Purpose
This header is the public-ish internal API for IDPF control queue management. It defines queue types, queue register descriptions, generic control queue message format, queue creation parameters, live queue state, mailbox opcodes, and callable queue lifecycle/send/receive functions.

## Important APIs, Types, And Functions
`enum idpf_ctlq_type` defines mailbox, config, event, and RDMA queue categories. `struct idpf_ctlq_reg` stores head, tail, length, base address, and masks. `struct idpf_ctlq_msg` is the software message abstraction with source type, host id, opcode, payload length, function/status union, mailbox cookie, and direct or indirect context. `struct idpf_ctlq_create_info` describes a queue to create. `struct idpf_ctlq_info` stores live ring indices, DMA descriptor memory, RX/TX backing arrays, and registers. Public functions include `idpf_ctlq_init()`, `idpf_ctlq_add()`, `idpf_ctlq_remove()`, `idpf_ctlq_send()`, `idpf_ctlq_recv()`, `idpf_ctlq_clean_sq()`, `idpf_ctlq_post_rx_buffs()`, and `idpf_ctlq_deinit()`.

## Control Flow
Upper layers create queues from `idpf_ctlq_create_info`, send `idpf_ctlq_msg` arrays on TX queues, clean send completions to recover status and caller-owned messages, receive messages from RX queues, and repost consumed DMA buffers. The API separates direct 16-byte descriptors from indirect payload-backed messages.

## State And Persistence
Live control queue state is represented by `struct idpf_ctlq_info`. The API stores ring state, lock state, DMA memory, buffer arrays, queue type/id, and register offsets for the lifetime of a created queue. Message payload DMA buffers are owned by callers on TX and returned to callers on RX until reposted.

## Dependencies And Integration Points
The header includes `idpf_mem.h` for DMA memory definitions and forward-declares `struct idpf_hw`. It is consumed by the queue implementation, hardware header, and virtchnl mailbox layer. Mailbox opcodes `idpf_mbq_opc_send_msg_to_cp` and `idpf_mbq_opc_send_msg_to_peer_drv` connect this queue abstraction to the control plane.

## Risks
Ownership rules are easy to misuse: send will hold message pointers until clean, while receive transfers indirect payload buffers to the caller until repost. `data_len` determines direct versus indirect handling, so inconsistent payload metadata can lead to invalid DMA addresses or copied context. Queue type support in implementation is narrower than the enum, so callers must not assume every enum value can be created.

## Test Signals
API tests should verify create-info register propagation, direct and indirect send/receive, status propagation through clean, caller buffer ownership, host id masking, source VM/VF/PF decoding, and expected failures for unsupported queue creation.
