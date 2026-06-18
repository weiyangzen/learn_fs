## sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.h

### Purpose
`sync_debug.h` defines the private types shared by the software sync timeline implementation, debugfs reporting, and tracepoints. It is not a public userspace ABI header; it binds `sw_sync.c`, `sync_debug.c`, and `sync_trace.h` together.

### Important APIs, Types, And Functions
The key types are `struct sync_timeline`, which owns the kref, name, context, current value, active fence rbtree/list, lock, and debug list node, and `struct sync_pt`, which embeds `struct dma_fence` plus timeline list/tree nodes and deadline storage. `dma_fence_parent()` recovers the timeline from the fence external lock. The header declares `sw_sync_debugfs_fops`, `sync_timeline_debug_add()`, and `sync_timeline_debug_remove()`.

### Control Flow, State, And Persistence
Objects persist through kref ownership in `sync_timeline` and `dma_fence` references in `sync_pt`. The timeline's lock protects active-point ordering and the timeline counter. The debug list node lets `sync_debug.c` enumerate live timelines while the fence parent relationship is inferred from the external spinlock passed to `dma_fence_init()`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are kernel list/rbtree/spinlock/kref concepts, `linux/dma-fence.h`, `linux/sync_file.h`, and `uapi/linux/sync_file.h`. Risks are structural: changing the fence lock parent assumption or list/tree invariants would break release, debug printing, and signaling. Test signals are mostly compile-time and behavioral through `sw_sync.c`: fence parent names, active list ordering, debug list membership, and deadline query correctness.
