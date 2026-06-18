# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wr.c

## Purpose
`wr.c` posts kernel UD/GSI send and receive work requests to MANA queues and records enough shadow state for later CQ polling.

## Important APIs, Types, And Functions
`mana_ib_post_recv()` iterates receive WRs and calls `mana_ib_post_recv_ud()` for UD/GSI. `mana_ib_post_send()` iterates send WRs and calls `mana_ib_post_send_ud()`. The helpers build GDMA SGE arrays, post work with `mana_gd_post_work_request()`, fill `ud_rq_shadow_wqe` or `ud_sq_shadow_wqe`, advance shadow producers, and ring the queue doorbell. Sends prepend the AH AV DMA buffer as an SGE and fill `struct rdma_send_oob`.

## Control Flow
Receive posting checks shadow queue capacity and max two SGEs, converts SGEs to GDMA format, posts the WQE, records `IB_WC_RECV`, `wr_id`, and posted WQE size, then rings. Send posting validates port/netdev, opcode `IB_WR_SEND`, shadow capacity, max two payload SGEs, prepends the address vector, sets OOB fields including fence/signaled/solicited flags, PSN, remote QPN, qkey, and MTU-derived client data unit, posts, increments SQ PSN, records `IB_WC_SEND`, and rings.

## State And Persistence
Posting advances GDMA queue producer state in hardware/core code and software shadow queue `prod_idx`. UD SQ PSN is stored in `qp->ud_qp.sq_psn`. Posted WQE size is used later to advance GDMA queue tails on completion. No state persists beyond QP lifetime.

## Dependencies And Integration Points
The file depends on GDMA work-request APIs, MANA AH objects from `ah.c`, QP queues and shadow queues from `mana_ib.h`, netdev MTU for send sizing, and CQ completion handling in `cq.c`.

## Risks
Only UD/GSI and `IB_WR_SEND` are supported; unsupported QP types or opcodes fail. The maximum SGE count is hard-coded to two payload SGEs. Send requires a valid AH and netdev. Shadow state is written only after hardware post succeeds, so a completion for an unshadowed WQE would be dropped by CQ handling. `err` in `mana_ib_post_send()` is not initialized before the loop but the loop always executes for non-NULL WR; callers should not pass NULL lists expecting a defined local value path beyond return.

## Test Signals
Test multi-WR lists with bad_wr handling, SGE count limits, shadow queue full, unsupported QP/opcode, IPv4/IPv6 AH send, GSI qkey override, PSN increment, doorbell ringing, post failure without shadow advance, and CQ poll conversion after send/recv completions.
