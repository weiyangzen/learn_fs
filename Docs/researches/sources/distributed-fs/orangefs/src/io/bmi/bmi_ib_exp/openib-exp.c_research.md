# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/openib-exp.c

## Purpose
Implements the OpenIB/libibverbs provider backend for the experimental BMI InfiniBand method. It opens an active verbs device, creates shared PD/CQ/completion-channel resources, brings up per-connection RC queue pairs, registers eager and RDMA buffers, posts SEND/RECV/RDMA_WRITE work requests, converts work completions into the generic `bmi_ib_wc` format, and handles async/CQ event fds for blocking progress.

## Important APIs, Types, And Functions
Provider-private state is held in `struct openib_device_priv` and `struct openib_connection_priv`. Major functions include `openib_ib_initialize`, `openib_ib_finalize`, `openib_new_connection`, `exchange_data`, `init_connection_modify_qp`, `openib_drain_qp`, `openib_close_connection`, `openib_post_sr`, `openib_post_rr`, `openib_post_sr_rdmaw`, `openib_check_cq`, `openib_prepare_cq_block`, `openib_ack_cq_completion_event`, `openib_wc_status_string`, `openib_wc_status_to_bmi`, `openib_mem_register`, `openib_mem_deregister`, `return_active_nic_handle`, `parse_bmi_opts_get_ib_port`, and `openib_check_async_events`.

## Control Flow
Initialization chooses an IB port from the BMI options string or the default, locates an active HCA/port, detects whether the link layer is InfiniBand or Ethernet/RoCE, queries device capabilities, allocates a protection domain, creates a completion channel and CQ, marks async and CQ fds nonblocking, and installs provider callbacks into `ib_device->func`.

`openib_new_connection` registers per-connection eager send/receive regions, creates an RC QP with bounded WR and SGE caps, exchanges LID or GID plus QP number over the TCP control socket, transitions the QP through INIT, RTR, and RTS, posts all eager receive buffers, and performs a final TCP synchronization. `openib_post_sr` sends eager/protocol messages. `openib_post_rr` reposts eager receive buffers. `openib_post_sr_rdmaw` decodes CTS remote buffer descriptors and emits one or more RDMA writes that gather from the sender buflist and walk the receiver buflist, signaling only the final WR so generic code can deregister memory and send RTS_DONE.

## State And Persistence
Device state persists for the BMI method lifetime: verbs context, CQ, PD, completion channel, selected port/id, SGE scratch array, device caps, and unsignaled-send counters. Per connection, the backend keeps a QP, eager memory regions, remote LID/GID, and remote QP number. Registered user-memory handles are stored in `memcache_entry_t.memkeys.mrh/lkey/rkey` and released through `openib_mem_deregister`.

## Dependencies And Integration Points
The file depends on libibverbs (`infiniband/verbs.h`), BMI byte swapping, shared helpers in `ib-exp.h`/`util-exp.c`, and memory-cache callbacks in `mem-exp.c`. It is selected by `BUILD_OPENIB` and called only through the callback table set during `openib_ib_initialize`.

## Risks And Test Signals
There are clear stale-code risks in conditional branches: one `HAVE_IBV_GET_DEVICES` path references fields/symbols such as `hca_port` and `od->nic_lid` that do not match the current `openib_device_priv` shape. Disabled `MEMCACHE_BOUNCEBUF` and `!MEMCACHE_EARLY_REG` branches call `memcache_register` with an outdated extra argument. Runtime risks include single-HCA selection, fixed GID index 0 for RoCE, exact QP capability assumptions across connections, manual SGE splitting, and non-fatal provider-post error handling. Test signals include building both modern and legacy verbs discovery paths, IB and RoCE connection setup, malformed `ib_port` options, inactive-port fallback, CQ polling/event blocking, async event logging, registration ENOMEM flush retry, scattered large RDMA transfers, and provider teardown after cancellation/finalize.
