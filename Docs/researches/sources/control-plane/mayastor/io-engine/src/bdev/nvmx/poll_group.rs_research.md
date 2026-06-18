## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/poll_group.rs

### Purpose
`nvmx/poll_group.rs` wraps SPDK NVMe poll groups used by per-core I/O channels to process qpair completions.

### Important APIs, Types, And Functions
`PollGroup(NonNull<spdk_nvme_poll_group>)` exposes `create()`, `add_qpair()`, `remove_qpair()`, and `as_ptr()`. `Drop` destroys the poll group and logs destroy errors.

### Control Flow
`create()` calls `spdk_nvme_poll_group_create()` with a channel context pointer and returns `CoreError::GetIoChannel` on null. Channel creation adds a qpair to the group, channel reset/removal removes it, and polling happens in `channel.rs` through `as_ptr()`.

### State, Persistence, And Dependencies
State is a runtime SPDK poll-group pointer. Dependencies are SPDK poll-group FFI, `QPair`, and `CoreError`.

### Integration Points
`NvmeIoChannelInner` owns a `PollGroup` for each SPDK I/O channel. Qpair lifecycle in `channel.rs` and completion polling both rely on this wrapper.

### Risks
Destroy errors are logged but cannot be recovered during Drop. The wrapper assumes all qpairs are removed or otherwise safe before destruction. Raw pointer validity depends on SPDK channel lifetime.

### Test Signals
Cover poll group creation failure, add/remove return codes, destroy logging on error, and channel teardown ordering around qpair removal.
