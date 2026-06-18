# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/openib.c

## Purpose
`openib.c` implements the `ib_device_func` provider backend for the Linux libibverbs/OpenIB stack. It opens an active HCA port, creates device-wide protection domain/completion queue/channel state, creates per-connection RC queue pairs, normalizes work completions for `ib.c`, and registers memory for eager and RDMA paths.

## Important APIs, Types, and Functions
Provider-private state is split between `struct openib_device_priv` and `struct openib_connection_priv`. The device struct holds `ibv_context`, `ibv_cq`, `ibv_pd`, port number, LID or GID, completion channel, hardware limits, temporary SGE array, unsignaled-send counters, and transport type (`IB` or `ROCE`). The connection struct holds an `ibv_qp`, eager send/recv MRs, remote LID/GID, and remote QP number.

Key functions are `openib_ib_initialize`, `openib_ib_finalize`, `openib_new_connection`, `init_connection_modify_qp`, `openib_post_sr`, `openib_post_rr`, `openib_post_sr_rdmaw`, `openib_check_cq`, `openib_prepare_cq_block`, `openib_ack_cq_completion_event`, `openib_mem_register`, `openib_mem_deregister`, `openib_check_async_events`, `return_active_nic_handle`, and `parse_bmi_opts_get_ib_port`.

## Control Flow
Initialization parses `ib_port`, selects an active device/port, determines whether the link layer is InfiniBand or Ethernet/RoCE, queries device limits, installs the provider vtable into `ib_device->func`, allocates a protection domain, creates a completion channel and CQ, and makes the async and completion fds nonblocking.

New connection setup registers the common eager buffers as MRs, creates a reliable-connected QP attached to the single CQ, records SGE and send-WR limits, exchanges local LID/GID and QP number over the TCP bootstrap socket, transitions the QP through INIT, RTR, and RTS, posts all eager receive buffers, then performs a final TCP sync so both sides have receives posted.

`openib_post_sr` posts eager/control SEND work requests. `openib_post_rr` reposts eager receive buffers. `openib_post_sr_rdmaw` consumes the sender buflist and the receiver CTS address/length/rkey array, creating as many RDMA write work requests as necessary; only the final segment is signaled with the `struct ib_work` id so common code can deregister memory and send RTS_DONE. `openib_check_cq` maps `ibv_wc` opcodes into the generic `bmi_ib_wc` consumed by `ib.c`.

## State and Persistence Behavior
All state is in memory. Device-wide resources live until `openib_ib_finalize`; per-connection QPs and eager MRs live until `openib_close_connection`. Registered user memory handles are stored in `memcache_entry_t.memkeys`. CQ and async events are edge notifications integrated with `ib_block_for_activity`.

## Dependencies and Integration Points
The file depends on `<infiniband/verbs.h>`, BMI byte swapping helpers, PVFS debug formatting, and common helpers from `ib.h`/`util.c`. It is selected by `module.mk.in` when `BUILD_OPENIB` defines `OPENIB`; `ib.c` calls `openib_ib_initialize` first when available.

## Risks and Edge Cases
The code contains compatibility branches for older `ibv_get_devices` APIs and newer device-list APIs; some identifiers in the older branch appear stale compared with the current struct names, so that path requires build coverage. The unsignaled-send counter in `openib_post_sr` is effectively unused because SENDs are always posted signaled. Many provider errors log and return without fully unwinding partially allocated connection resources. RDMA write segmentation must stay consistent with `ib.h` CTS layout and with memory registration refcounts. RoCE path assumes GID index zero. `return_active_nic_handle` returns early on some per-device failures without freeing the device list.

## Test Signals
Tests should cover active-port selection, `ib_port` option parsing, InfiniBand LID and RoCE GID handshakes, QP transition failures, eager send/receive, large list-buffer RDMA writes with more SGEs than a single WR can hold, CQ opcode/status translation, async event polling, registration failure with cache flush, and clean finalize after multiple connections.
