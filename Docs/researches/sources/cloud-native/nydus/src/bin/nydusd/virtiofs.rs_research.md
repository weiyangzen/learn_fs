# sources/cloud-native/nydus/src/bin/nydusd/virtiofs.rs

## Purpose
`virtiofs.rs` implements the feature-gated virtio-fs/vhost-user daemon mode for `nydusd`. It adapts a `fuse_backend_rs::Vfs` into a `vhost_user_backend` device backend and wraps it in the shared `NydusDaemon`/`FsService` abstractions.

## Important APIs, Types, And Functions
`VhostUserFsBackend` holds queue processing state: event-index flag, kill event pair, guest memory, FUSE server, and backend request fd. `process_queue` consumes descriptor chains and dispatches FUSE messages. `VhostUserFsBackendHandler` implements `VhostUserBackendMut` and declares queue count, queue size, feature bits, memory updates, backend request fd, exit events, and event handling. `VirtioFsService` implements `FsService`. `VirtiofsDaemon` implements `NydusDaemon` and `DaemonStateMachineSubscriber`. `create_virtiofs_daemon` constructs the vhost-user daemon, service, state machine, optional initial mount, and starts daemon state transitions.

## Control Flow
The backend handler receives queue events for high-priority and request queues. For each available descriptor chain, `process_queue` builds a `Reader` and `VirtioFsWriter`, invokes `Server::handle_message`, adds the descriptor to the used ring, and signals the guest depending on EVENT_IDX state. `handle_event` loops while notifications indicate more work when EVENT_IDX is enabled. `VirtiofsDaemon::start` opens the vhost-user listener socket and spawns a `vhost_user_listener` thread. `create_virtiofs_daemon` creates state-machine channels, kicks the state machine, mounts the optional backend, then sends Mount and Start events.

## State And Persistence
Runtime state includes guest memory, virtqueue state owned by the vhost-user backend, the listener socket path, daemon state atomics, service backend collection, optional supervisor/id, and state-machine channels. Persistent external effects are the vhost-user socket and any mounted RAFS/passthrough backend state. Save/restore and inflight-op export are unsupported for this mode.

## Dependencies And Integration Points
It depends on `fuse_backend_rs`, `vhost`, `vhost_user_backend`, `virtio_queue`, `vm_memory`, `vmm_sys_util`, shared `nydus` daemon traits, `UpgradeManager`, `FsBackendCollection`, and `BuildTimeInfo`. `nydusd/main.rs` calls `create_virtiofs_daemon` when the `virtiofs` feature and subcommand are enabled.

## Risks
The queue processor treats many failures as unrecoverable I/O errors to the caller. Missing guest memory fails requests. Several lock acquisitions use `unwrap`, so poisoned mutexes panic. `set_event_idx` ignores its argument and always enables EVENT_IDX. `exit_event` comments note missing backend support for a kill event. `start` spawns a listener thread and only logs listener errors. Save/restore are unsupported, limiting live upgrade semantics compared with FUSE mode.

## Test Signals
No tests are present in this file. Useful coverage requires feature-enabled integration tests with a vhost-user client: queue negotiation, normal FUSE requests, EVENT_IDX and non-EVENT_IDX notifications, startup/shutdown, optional initial mount, API mount operations through `VirtioFsService`, and unsupported save/restore behavior.
