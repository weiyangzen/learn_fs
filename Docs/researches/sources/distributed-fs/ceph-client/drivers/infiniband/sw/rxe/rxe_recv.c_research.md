# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_recv.c

## Purpose

`rxe_recv.c` validates received RoCE packets, checks address/key correctness, demultiplexes unicast and multicast traffic, and queues accepted packets to responder QP tasks.

## Important APIs, Types, and Functions

Important functions include `rxe_rcv()`, `hdr_check()`, `rxe_rcv_pkt()`, `rxe_rcv_mcast_pkt()`, `check_type_state()`, `check_keys()`, `check_addr()`, and `rxe_chk_dgid()`.

## Control Flow

Transport receive supplies packet metadata and calls `rxe_rcv()`. The code validates opcode/type/state, PKEY/QKEY, addressing, destination GID, and QP/multicast lookup. Unicast packets are queued to one QP via `rxe_resp_queue_pkt()`. Multicast packets are cloned for attached QPs.

## State and Persistence Behavior

Accepted skbs persist on `qp->req_pkts` until responder cleanup. QP/device references are held while queued. Bad PKEY/QKEY counters and receive-related counters are updated on violations.

## Dependencies and Integration Points

It depends on RXE header parsing, opcode tables, QP pools, multicast support, netdev/GID state, and the responder queue entry point. It is downstream of `rxe_net.c` and upstream of `rxe_resp.c`.

## Risks and Edge Cases

Malformed packets may carry bad opcodes, invalid QPNs, wrong DGIDs, bad keys, or inconsistent lengths. Multicast cloning must preserve references and free failures correctly. Queued packet references must be released by responder cleanup.

## Test Signals

Test valid RC/UC/UD/GSI receive, malformed packet rejection, bad PKEY/QKEY counters, wrong DGID, multicast fanout/detach, VLAN receive, and QP reset/error/destroy during receive.
