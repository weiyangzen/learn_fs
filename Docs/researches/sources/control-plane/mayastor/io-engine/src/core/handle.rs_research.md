# sources/control-plane/mayastor/io-engine/src/core/handle.rs

## Purpose
Wraps an SPDK bdev descriptor and I/O channel into an async Rust handle for internal reads, writes, resets, write-zeroes, snapshots, and NVMe admin commands.

## Important APIs, Types, and Functions
- `BdevHandle<T: BdevOps>` owns an `IoChannelGuard` and shared `DescriptorGuard`.
- `open`, `open_with_bdev`, `close`, `get_bdev`, `io_tuple`, and `dma_malloc` provide setup helpers.
- `write_at`, `read_at`, `reset`, `write_zeroes_at`, `create_snapshot`, `nvme_identify_ctrlr`, `nvme_admin_custom`, and `nvme_admin` submit SPDK operations and await oneshots.
- `io_completion_cb` frees SPDK I/O and sends `NvmeStatus`.

## Control Flow and State
Opening obtains a descriptor, optionally claims the bdev, and allocates an I/O channel on the current core. Each async operation creates a oneshot, submits an SPDK bdev command with `cb_arg(sender)`, maps immediate errno into dispatch `CoreError`, and maps completion status into success or a specific `CoreError`. Drop order is important: channel is declared before descriptor so it is dropped first.

State is the live SPDK descriptor/channel. No persistent state is written except device effects from I/O/admin commands.

## Dependencies and Integration Points
Depends on `spdk_rs`, `Bdev`, `DescriptorGuard`, `DmaBuf`, `CoreError`, `SnapshotParams`, and `subsys::set_snapshot_time`. Used by replica wiping, bdev LVS helpers, and test/admin paths.

## Risks and Test Signals
All operations are reactor/thread-affine through the channel. The completion callback expects sender delivery to succeed and panics otherwise. `create_snapshot` only sends an NVMe admin command and ignores the provided params in this wrapper. Tests should cover dispatch errno mapping, completion status mapping, unallocated-block read behavior, channel allocation failure, and NVMe admin buffer sizing.
