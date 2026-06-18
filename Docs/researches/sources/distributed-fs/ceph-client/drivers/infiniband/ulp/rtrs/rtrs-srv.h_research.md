# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.h

## Purpose
Defines private server-side RTRS state shared by server core, stats, sysfs, and trace code.

## Important APIs, Types, And Functions
Declares `enum rtrs_srv_state`, stats structures, `struct rtrs_srv_con`, `struct rtrs_srv_op`, `struct rtrs_srv_mr`, `struct rtrs_srv_path`, `struct rtrs_srv_sess`, `struct rtrs_srv_ctx`, and `struct rtrs_srv_ib_ctx`. Provides `to_srv_path()` and `rtrs_srv_update_rdma_stats()`. Declares `close_path()`, IB event handler, stats helpers, and sysfs create/destroy functions.

## Control Flow
The header defines the data model used by `rtrs-srv.c`: a server context owns sessions; sessions own paths and preallocated chunk pages; paths own RDMA connections, memory regions, operation IDs, stats, and kobjects. `rtrs_srv_op` is the handle passed to upper-layer callbacks and later returned to `rtrs_srv_resp_rdma()`.

## State And Persistence
All structures represent live kernel memory. `refcount_t` protects sessions, `percpu_ref` protects inflight operation IDs during path close, and kobjects expose parts of the state to sysfs.

## Dependencies And Integration Points
Includes device/refcount/percpu Linux APIs and `rtrs-pri.h`. It is consumed by server implementation, sysfs, stats, and tracepoint declarations.

## Risks
Changes to these structures affect lifetime management across multiple files. `rtrs_srv_op` contains embedded WR/SG objects reused for response posting, so concurrent reuse is controlled by queue depth and operation ID lifetime. Stats updates are per-CPU and intentionally low overhead.

## Test Signals
Build all server compilation units, run sysfs/stat operations, issue concurrent IO and close, verify operation completion/ref release, and enable tracepoints using `to_srv_path()`-based state extraction.
