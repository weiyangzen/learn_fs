## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/channel.rs

### Purpose
`nvmx/channel.rs` implements per-core NVMe I/O channel state for the Rust-native NVMe-oF block-device path. It owns I/O qpairs, SPDK poll groups, polling, channel reset/shutdown semantics, and per-channel I/O statistics.

### Important APIs, Types, And Functions
`NvmeIoChannel` is the SPDK channel context wrapper. `NvmeIoChannelInner` owns the optional `QPair`, `PollGroup`, `Poller`, stats controller, block device, controller reference, pending-I/O count, and shutdown flag. `IoStatsController` accumulates per-channel stats. `NvmeControllerIoChannel::create()` and `destroy()` are SPDK I/O channel callbacks. `nvme_poll()` processes poll-group completions and handles disconnected qpairs.

### Control Flow
Channel creation looks up the controller by ID, ensures it is `Running`, copies controller handle and namespace block size while holding the lock, releases the lock before qpair operations, looks up the block device, creates a qpair and poll group, adds the qpair, starts a poller, and stores a boxed `NvmeIoChannelInner` in the SPDK channel context. Reset drops the qpair and leaves the channel unusable until `reinitialize()` recreates and reconnects it. Shutdown performs reset, marks the channel one-way shutdown, and drops the controller reference. Destroy stops the poller, removes any qpair from the poll group, and frees the boxed inner state.

### State, Persistence, And Dependencies
State is runtime-only and bound to SPDK I/O channel lifetime. `num_pending_ios` is used by the submission layer for accounting and logging; byte counters are stored in block units until read out. Dependencies include `NVME_CONTROLLERS`, `QPair`, `PollGroup`, `BlockDevice`, `device_lookup`, SPDK poll group APIs, and configured poll intervals.

### Integration Points
Handles in `nvmx/handle.rs` obtain these channels via `spdk_get_io_channel`. Controller reset and shutdown traverse channels and call `reset()`, `reinitialize()`, or `shutdown()`. I/O stats aggregation in `controller.rs` reads each channel's `IoStatsController`.

### Risks
The code relies heavily on raw channel-context pointer arithmetic and boxed raw pointers. Qpair disconnect handling aborts queued requests but leaves shutdown commented out, so recovery depends on higher-level reset/failure detection. A failed `poll_group.add_qpair()` or qpair connect during reinitialize can leave resources partially created. Stats only account successful operations and ignore flush bytes.

### Test Signals
Exercise channel creation with missing, non-running, and running controllers; qpair/poll-group allocation failures; reset followed by reinitialize; reset racing shutdown; destroy with and without qpair; poll completion return values; disconnected qpair abort behavior; pending-I/O underflow warning; and stats aggregation by block size.
