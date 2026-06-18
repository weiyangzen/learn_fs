<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_channel.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_channel.rs

Purpose: defines per-core nexus I/O channel state: child handles used as readers and writers, detached handles awaiting disconnection, partial-rebuild I/O log channels, read round-robin cursor, frozen I/O queue, and channel-level I/O mode.

Important APIs/types/functions: `NexusChannel`, `IoMode`, `DrEvent`, `new`, `destroy`, `for_each_writer`, `for_each_io_log`, `select_reader`, `detach_device`, `disconnect_detached_devices`, `reconnect_all`, `connect_children`, `reconnect_io_logs`, `fault_device`, `set_io_mode`, `is_frozen`, `resubmit_frozen`, `abort_frozen`, and `freeze_io_submission`.

Control flow: channel creation decides whether the current SPDK thread should host normal frontend I/O handles or act as an auxiliary channel, initializes I/O log channels, then connects healthy children. `connect_children` opens two handles for each healthy child, one writer and one reader, and adds rebuilding out-of-sync children as write-only if at least one reader exists. Dynamic reconfiguration clears/rebuilds handle vectors and refreshes I/O logs. Faulting a device delegates to nexus retire logic, then reconnects logs.

State and persistence: state is per-core and non-persistent. Detached handles remain alive until `disconnect_detached_devices` drops them, allowing two-phase retire. Frozen `NexusBio` objects are queued in memory while `IoMode::Freeze` is active and resubmitted or failed later. `previous_reader` is an `UnsafeCell<usize>` because reader selection mutates through `&self` in the I/O path.

Dependencies/integration: depends on `BlockDeviceHandle`, `NexusChild` state predicates, `Nexus::io_log_channels`, SPDK thread identity, runtime flags `ENABLE_IO_ALL_THRD_NX_CHAN` and `ENABLE_NEXUS_CHANNEL_DEBUG`, and `NexusBio` for frozen I/O resubmission.

Risks: reader/writer handles are duplicated by calling `get_io_handle` twice per healthy child; failure of either faults the child. If no readers exist, rebuilding children are not added as write-only. The read cursor uses unsafe interior mutability and must remain single-threaded per SPDK channel. Frozen I/Os consume memory until resume or abort. Detach/disconnect ordering is critical to avoid I/O races and dangling handles.

Test signals: channel creation on primary vs I/O threads, healthy child reader/writer connection, rebuilding child write-only behavior, read round-robin selection, detach then disconnect with predicates, reconnect after child state changes, freeze/resubmit/abort semantics, debug dump safety with missing device names, and fault path reconnecting I/O logs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_channel.rs -->
