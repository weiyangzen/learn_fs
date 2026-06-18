# sources/cloud-native/nydus/service/src/block_nbd.rs

## Purpose
`block_nbd.rs` exports a RAFSv6 `BlockDevice` through the Linux Network Block Device driver. It configures an `/dev/nbd*` device, handles kernel NBD requests over Unix socket pairs, and implements the `NydusDaemon` lifecycle wrapper for running the service under the daemon state machine.

## Important APIs, Types, And Functions
`nbd_ioctl()` wraps Linux NBD ioctl request generation. `NbdService::new()` configures block size/count/timeout/read-only/multi-conn flags; `create_worker()` establishes a socket pair and attaches one end to the kernel; `run()` invokes `NBD_DO_IT`; `stop()` clears active state and socket. `NbdWorker::run()` processes request headers asynchronously. `handle_request()` parses NBD requests and sends replies. `NbdDaemon` implements `DaemonStateMachineSubscriber` and `NydusDaemon`. `create_nbd_daemon()` constructs, starts, and transitions the daemon.

## Control Flow
Daemon creation builds a `BlobCacheMgr`, adds the bootstrap entry, creates a `BlockDevice`, initializes `NbdService`, starts the daemon state machine, then sends `Mount` and `Start`. Starting the daemon creates `nbd_threads` workers, each with a socket registered through `NBD_SET_SOCK`, and starts a control thread blocked in `NBD_DO_IT`. Workers read fixed 28-byte headers, validate magic/alignment, call `BlockDevice::async_read()` for read commands, return EINVAL/EIO on invalid or failed reads, stop on disconnect, and send a 16-byte reply plus data for successful reads.

## State, Persistence, And Dependencies
State includes an `active` atomic, scoped blob id, shared cache manager, open NBD device file, broadcast sender, daemon state atomics, service/control thread handles, and state-machine channels. There is no save/restore implementation; `save()` and `restore()` are unimplemented in `NbdDaemon`. Persistence is through the kernel NBD device and underlying blob cache population. Dependencies include Linux NBD ioctls, `bytes` parsing/building, `tokio_uring::net::UnixStream`, `mio::Waker`, and daemon FSM types.

## Integration Points
The module is compiled through the `block-nbd` feature and depends on `BlockDevice` for all storage semantics. It integrates with the general `NydusDaemon` trait so supervisors can start, stop, wait, and query state/cache manager.

## Risks
Only read and disconnect commands are handled; unknown command types return success with no data unless validation fails, which may be too permissive. `NbdDaemon::wait_service()` joins worker threads but not the `nbd_control_thread`, so lifecycle cleanup depends on control-loop exit elsewhere. Kernel NBD tests require privileged devices and are ignored. `save()`/`restore()` panic if called.

## Test Signals
The only in-file test, `test_nbd_device`, is ignored and requires `/dev/nbd15`. It exercises creating two workers and stopping after a short delay, but normal CI receives little active coverage for protocol parsing, ioctl setup, or daemon shutdown.
