# sources/distributed-fs/ceph-client/drivers/most/most_cdev.c

## Purpose
This file implements the MOST character-device component. It creates `/dev` nodes for linked MOST channels and exposes blocking/nonblocking read, write, poll, open, and close operations backed by MOST buffer objects.

## Important APIs, types, and functions
- `struct cdev_component comp` stores the allocated character-device region, minor ID allocator, major number, and embedded `struct most_component` callbacks.
- `struct comp_channel` represents one cdev-linked MOST channel, including wait queue, unlink spinlock, cdev/device, I/O mutex, MOST interface/config pointers, channel id, MBO offset, FIFO of MBO pointers, access flag, and global list node.
- File operations are `comp_open()`, `comp_close()`, `comp_read()`, `comp_write()`, and `comp_poll()`.
- MOST component callbacks are `comp_probe()`, `comp_disconnect_channel()`, `comp_rx_completion()`, and `comp_tx_completion()`.
- Module init/exit registers the cdev class, chrdev region, MOST component, and configfs subsystem.

## Control flow
When configfs links a cdev component to a MOST channel, MOST core calls `comp_probe()`. It allocates a minor, creates `comp_channel`, initializes the cdev and FIFO sized to `cfg->num_buffers`, adds the channel to `channel_list`, creates the device node using the link name, and emits a uevent.

Opening the node checks access mode against channel direction (`O_RDONLY` for RX, `O_WRONLY` for TX), rejects concurrent opens with `access_ref`, starts the MOST channel through `most_start_channel()`, and records the open. Closing clears `access_ref`, stops the channel if still connected, and destroys the channel object if it was disconnected while open.

For TX, `comp_write()` waits for an available MBO from the core, copies user data into the current MBO at `mbo_offs`, and submits the MBO when full or when the datatype is control/async. For RX, `comp_rx_completion()` receives completed MBOs from core, enqueues them into the per-cdev FIFO, and wakes readers. `comp_read()` waits for FIFO data, copies from the current MBO to userspace, and returns the MBO to core when fully consumed. `comp_poll()` reports readability or writability based on FIFO/core-buffer state and disconnect status.

## State and persistence
All state is volatile. The global `channel_list` tracks live cdev channel objects. `comp.minor_id` and the allocated chrdev region manage device numbers. Per-open state is only `filp->private_data` and per-channel `access_ref`/`mbo_offs`. There is no disk persistence beyond device nodes managed by devtmpfs/udev.

## Dependencies and integration points
The component depends on cdev, device class, IDA, kfifo, wait queues, user-copy helpers, poll, and MOST core exported APIs. It registers with MOST core as component name `"cdev"` and with configfs through `most_register_configfs_subsys()`.

## Risks and edge cases
- Only one opener is allowed per channel; clients must handle `-EBUSY`.
- Disconnect while open is handled by setting `c->dev = NULL`, waking waiters, stopping the channel, and deferring object free until close; races rely on `io_mutex` plus `unlink` spinlock.
- `comp_write()` may return a partial count after a partial user copy and only submits the MBO once the configured boundary is reached.
- `kfifo_alloc()` uses `cfg->num_buffers`; invalid or zero configuration from configfs can affect behavior.
- Exit iterates remaining channels after deregistering component/configfs, so active users must be quiesced by disconnect handling.

## Test signals
Test cdev link creation and node naming, open access-mode enforcement, single-open behavior, blocking and nonblocking reads/writes, partial read/write offsets, poll readiness, RX completion wakeups, TX completion wakeups, disconnect during blocked I/O, module unload with open and closed channels, and configfs create/destroy link cycles.
