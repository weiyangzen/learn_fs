<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/descriptor.rs -->
## sources/control-plane/mayastor/io-engine/src/core/descriptor.rs

### Purpose
`descriptor.rs` provides `DescriptorGuard`, an RAII wrapper around `spdk_rs::BdevDesc`. It centralizes descriptor close behavior, nexus-module claim/unclaim operations, and conversion from descriptor to I/O handle.

### Important APIs, Types, And Functions
`DescriptorGuard<T>` stores a `BdevDesc<T>` and the owning SPDK `Thread`. `UntypedDescriptorGuard` is `DescriptorGuard<()>`. Methods include `new`, `claim`, `unclaim`, `bdev`, and `into_handle`. It implements `Deref`, `Drop`, `Debug`, and an unsafe `Sync` implementation.

### Control Flow
`new` captures the current SPDK thread. `claim` finds the nexus bdev module and calls `claim_bdev`; `unclaim` releases the bdev through the same module. `bdev` returns a `Bdev<T>` wrapper around the descriptor's bdev. `into_handle` consumes the guard and delegates to `BdevHandle::try_from`. On drop, the descriptor is closed on the captured thread when available, directly on the primary thread when already there, or by sending a close message to the primary thread otherwise.

### State, Persistence, And Dependencies
The guard owns an open SPDK descriptor and optionally records its thread affinity. It changes SPDK bdev claim state through the nexus module and closes descriptors asynchronously across threads. Dependencies include `spdk_rs::{BdevDesc, BdevModule, Thread}`, `NEXUS_MODULE_NAME`, `Bdev`, `BdevHandle`, and `CoreError`.

### Risks And Test Signals
Correct close-thread routing is critical; closing on the wrong reactor thread can violate SPDK assumptions. `Sync` safety relies on only shared read access except `Drop`. Claim/unclaim logs errors and returns bool/void rather than rich errors. Tests should cover drop on owning, primary, and non-primary threads; claim failure; unclaim failure; debug formatting; and handle conversion preserving descriptor ownership.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/descriptor.rs -->
