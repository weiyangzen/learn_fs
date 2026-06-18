# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_msgq.h

## Purpose
`bfa_msgq.h` declares the software-side MSGQ transport structures and public API used by BNA modules to send variable-size firmware commands and receive asynchronous responses through DMA rings plus mailbox doorbells.

## Important APIs, Types, and Functions
- `BFA_MSGQ_FREE_CNT()` computes available command entries using producer/consumer indices.
- `BFA_MSGQ_INDX_ADD()` wraps queue indices.
- `BFA_MSGQ_CMDQ_NUM_ENTRY`, `BFA_MSGQ_CMDQ_SIZE`, `BFA_MSGQ_RSPQ_NUM_ENTRY`, and `BFA_MSGQ_RSPQ_SIZE` size the two DMA rings at 128 entries each.
- `bfa_msgq_cmd_set()` initializes a `struct bfa_msgq_cmd_entry` with completion callback, callback argument, byte size, and BFI message header pointer.
- `struct bfa_msgq_cmd_entry` is the caller-owned command descriptor queued or posted by MSGQ.
- `struct bfa_msgq_cmdq` tracks command queue FSM, producer/consumer index, DMA address, mailbox doorbells, copy-request state, and `pending_q`.
- `struct bfa_msgq_rspq` tracks response queue FSM, producer/consumer index, DMA address, handlers indexed by `BFI_MC_MAX`, and doorbell state.
- `struct bfa_msgq` combines command/response queues with IOC notification and init mailbox state.
- Public functions: `bfa_msgq_meminfo()`, `bfa_msgq_memclaim()`, `bfa_msgq_attach()`, `bfa_msgq_regisr()`, `bfa_msgq_cmd_post()`, and `bfa_msgq_rsp_copy()`.

## Control Flow and State
Consumers allocate or reserve DMA memory according to `bfa_msgq_meminfo()`, claim it with `bfa_msgq_memclaim()`, attach MSGQ to an IOC with `bfa_msgq_attach()`, register message-class handlers, then construct commands by filling a BFI message structure and applying `bfa_msgq_cmd_set()`. The header intentionally exposes the command-entry structure so higher layers can embed one command descriptor in persistent objects such as ENET, port, stats, TX, or RX state machines.

## State and Persistence Behavior
The declared structures are runtime state only. They persist across command submissions while the driver is attached, but IOC disable/failure transitions reset active queue state in the implementation. The most important contract is ownership: the command message memory and `bfa_msgq_cmd_entry` must remain valid until MSGQ either copies/posts it or queues it and later invokes the callback.

## Dependencies and Integration Points
The header includes `bfa_defs.h`, `bfi.h`, `bfa_ioc.h`, and `bfa_cs.h`. It uses Linux `list_head`, BFA DMA descriptors, mailbox command structures, IOC notify structures, BFI message classes, and BFI MSGQ entry sizes. ENET and other firmware clients depend on these declarations for command submission and response registration.

## Risks
- Queue free-count and index macros require power-of-two depths; changing queue depths without preserving that invariant breaks wrapping.
- `bfa_msgq_cmd_set()` stores pointers rather than copying message headers; callers must not use stack-allocated message structures for asynchronous commands.
- The handler array is sized by `BFI_MC_MAX`; mismatched message class constants between firmware ABI and driver would cause drops or out-of-range handling.
- The typo-like API name `bfa_msgq_regisr` is part of the local interface and must be used consistently.

## Test Signals
Header-level validation is compile-time and integration-oriented: all call sites should build after structure changes, DMA memory sizing should match implementation expectations, command entries should survive deferred posting, and response class registration should dispatch ENET responses through `bna_msgq_rsp_handler()`.
