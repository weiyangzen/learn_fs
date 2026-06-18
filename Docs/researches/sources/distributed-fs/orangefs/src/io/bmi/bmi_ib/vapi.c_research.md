# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/vapi.c

## Purpose
`vapi.c` implements the legacy Mellanox VAPI/EVAPI backend for the BMI InfiniBand method. It provides the same provider vtable as `openib.c`, but through VAPI types and calls, including HCA discovery, PD/CQ/QP setup, memory registration, CQ event bridging, async-event reporting, and RDMA write posting.

## Important APIs, Types, and Functions
Provider state is stored in `struct vapi_device_priv` and `struct vapi_connection_priv`. The device struct holds HCA handle, CQ, PD, local LID, temporary SGE array, max outstanding WRs, async and completion event handler handles, and pipes used to expose events to `poll`. The connection struct holds QP handle/number, eager MRs and lkeys, unsignaled WR counter, remote LID, and remote QP number.

Key functions are `vapi_ib_initialize`, `vapi_ib_finalize`, `vapi_new_connection`, `verify_prop_caps`, `init_connection_modify_qp`, `vapi_drain_qp`, `vapi_close_connection`, `vapi_post_sr`, `vapi_post_rr`, `vapi_post_sr_rdmaw`, `vapi_check_cq`, `vapi_prepare_cq_block`, `vapi_ack_cq_completion_event`, `vapi_wc_status_to_bmi`, `vapi_mem_register`, `vapi_mem_deregister`, `reinit_mosal`, `async_event_handler`, and `cq_event_handler`.

## Control Flow
Initialization first calls `reinit_mosal` to work around old MOSAL library state after daemon forks. It lists HCAs, selects the first, allocates provider-private state, installs the vtable, obtains an HCA handle, registers async handlers, validates the port is active, allocates a PD, queries HCA capacity, creates a CQ, creates pipes for completion and async events, registers a completion event handler, and initializes SGE limits.

New connections register eager buffers, create an RC QP, verify returned QP capabilities, exchange local LID/QP number over the TCP bootstrap socket, transition the QP through INIT, RTR, and RTS, post all eager receive buffers, and perform a final synchronization exchange. SEND and receive posting functions translate common `buf_head` values into VAPI descriptors. RDMA writes are segmented using CTS remote buffer metadata exactly like OpenIB, with the final RDMA write signaled so `ib.c` can observe completion.

VAPI completion and async callbacks run in provider-created threads and write small records into pipes; common blocking code polls the read side through `vapi_prepare_cq_block`.

## State and Persistence Behavior
All state is runtime-only. Event pipes queue readiness notifications in process memory/kernel pipe buffers. Device resources are released in `vapi_ib_finalize`, while connection resources are released in `vapi_close_connection`. Registered memory handles are stored in `memcache_entry_t.memkeys`.

## Dependencies and Integration Points
This file depends on VAPI/EVAPI headers, optional `wrap_common.h`, `libmosal.so` dynamic symbols, BMI byte swapping, BMI method support, and the common BMI IB header. It is compiled when `BUILD_IB` defines `VAPI`; `ib.c` falls back to `vapi_ib_initialize` if OpenIB initialization is unavailable or fails.

## Risks and Edge Cases
VAPI support is legacy and contains hard exits through `error_verrno`, unlike the nonfatal `error()` helper. `reinit_mosal` uses `dlopen`/`dlsym` and internal MOSAL symbols when available, which is fragile across library versions. VAPI port selection is fixed at `VAPI_PORT` rather than using the OpenIB-style `ib_port` option. Event handlers write to pipes and log errors from callback context; pipe backpressure or closed descriptors during shutdown would be sensitive. RDMA segmentation and registration lifetimes must match the shared RTS/CTS state machine. Some retry/count constants differ from OpenIB, so provider behavior can diverge under loss or RNR pressure.

## Test Signals
Provider tests should cover HCA discovery failure, inactive port detection, MOSAL reinitialization paths, QP capability verification across multiple connections, eager and large RDMA transfers, completion pipe wakeups, async event pipe reads, VAPI status-to-BMI conversion, and finalize cleanup of handlers, pipes, CQ, PD, HCA handle, and memory registrations.
