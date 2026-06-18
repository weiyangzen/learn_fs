<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_child.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_child.rs

Purpose: defines the `NexusChild` object and its lifecycle, health, sync, reservation, close/unplug, rebuild, and I/O-log behavior. It wraps a child URI, block device, descriptor, state atomics, event listener attachment, and rebuild metadata for one replica under a nexus.

Important APIs/types/functions: `ChildError`, `FaultReason`, `ChildState`, `ChildStateClient`, `ChildSyncState`, `ChildDestroyState`, `NexusChild`, `open`, `online`, `close`, `unplug`, `hot_removed`, `reservation_acquire`, `reservation_acquire_argkey`, `reservation_preempt_holder`, `resv_check_holder`, `get_io_handle`, `get_io_handle_nonblock`, `start_io_log`, `stop_io_log`, `io_log_channel`, `rebuild_job`, and `get_rebuild_progress`.

Control flow: `open` rejects destroying or permanently faulted children, validates parent size against child size, opens the block device for write access, stores a descriptor, sets state `Open`, and records sync state. `online` recreates the underlying block device for recoverable closed/faulted children, then opens it out-of-sync for rebuild. `close` transitions destroy state, unclaims the descriptor, destroys the device, waits for removal/unplug notification when needed, and clears destroy state. `unplug` responds to device removal by dropping device/descriptor only for intentional destroy, closing open state, reconfiguring the parent unless the child already faulted for I/O error, and notifying `close`.

State and persistence: child state, sync state, and destroy state are `AtomicCell`s; fault timestamp is mutex-protected. Persistent-store enabled mode requires child URI UUIDs and panics if missing. NVMe reservation behavior depends on environment and `NexusNvmeParams`; PTPL behavior uses the global environment. I/O logs are optional per child and converted into rebuild maps when stopped.

Dependencies/integration: depends on Mayastor block-device traits, device create/destroy/lookup, SNAFU/CoreError errno mapping, URL parsing for replica UUIDs, persistent store availability, rebuild job registry, SPDK NVMe reservation structures/actions, DMA buffers, eventing, and `nexus_lookup_mut` for unplug reconfiguration.

Risks: `Url::parse(uri).expect` in UUID extraction can panic on invalid child URI. Persistent-store UUID enforcement also panics. Reservation report parsing uses `align_to` and assumes returned buffer layout is compatible. Close waits on a bounded channel with retry sleeps; unusual event ordering can leave descriptors longer than intended. State transitions mix atomic stores and event generation without a single global lock.

Test signals: state/client-state transitions, recoverable vs permanent faults, open too-small child, device open failure, online recreation failure, close idempotency, hot remove vs intentional destroy, unplug descriptor dropping, UUID extraction and invalid URIs, NVMe reservation unsupported path, reservation holder/preempt cases, PTPL flag behavior, I/O log lifecycle, and rebuild progress lookup.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_child.rs -->
