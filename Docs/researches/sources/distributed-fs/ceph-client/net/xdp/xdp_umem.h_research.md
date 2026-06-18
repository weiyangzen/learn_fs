# sources/distributed-fs/ceph-client/net/xdp/xdp_umem.h

Purpose: declares the internal AF_XDP UMEM lifecycle API shared between socket and buffer-pool implementation files.

Important APIs/types: includes `<net/xdp_sock_drv.h>` for `struct xdp_umem` and declares `xdp_get_umem()`, `xdp_put_umem()`, and `xdp_umem_create()`.

Control flow: this header has no executable flow; callers use it to create a UMEM from `struct xdp_umem_reg`, hold references while sharing pools/sockets, and release references with optional deferred cleanup.

State and persistence: no state is owned here. The declared APIs manipulate `struct xdp_umem` state in `xdp_umem.c`.

Dependencies and integration: included by `xsk.c` and `xsk_buff_pool.c`, and indirectly ties internal code to driver-facing XDP socket structures.

Risks and test signals: risks are ABI/internal declaration drift with `xdp_umem.c` or `net/xdp_sock_drv.h`. Build tests should compile all AF_XDP configurations and verify no stale prototypes or missing includes.
