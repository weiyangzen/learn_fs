<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_nbd.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_nbd.rs

Purpose: wraps SPDK NBD export support for nexus or other bdevs. It finds free `/dev/nbd*` devices, starts SPDK NBD, waits for kernel readiness, and disconnects NBD devices during cleanup.

Important APIs/types/functions: `NbdError`, `wait_until_ready`, `find_unused`, `start_cb`, `start`, `NbdDisk`, `NbdDisk::create`, `destroy`, `get_path`, and `as_uri`.

Control flow: `find_unused` reads the kernel NBD module `nbds_max`, scans `/sys/class/block/nbd*/pid` to skip in-use devices, and also asks SPDK whether a path is already in use. `start` calls `spdk_nbd_start` and waits on a oneshot callback. `NbdDisk::create` finds a path, starts SPDK NBD, then polls from an unaffinitized helper thread until the block device reports nonzero size or the retry loop gives up. `destroy` sets kernel NBD size to zero and calls `nbd_disconnect` from a helper thread while the reactor polls.

State and persistence: `NbdDisk` owns a raw `spdk_nbd_disk` pointer. No persistent configuration is written. Temporary readiness and destroy completion are coordinated with atomics and helper threads. The exported URI is `file:///dev/nbdX`.

Dependencies/integration: depends on SPDK NBD FFI, Linux NBD ioctls, sysfs parsing, Mayastor reactors and `Mthread`, oneshot channels, `ffihelper` errno conversion, and Unix file descriptors. `NexusTarget::NbdDisk` stores this wrapper when a nexus is shared over NBD.

Risks: Linux-specific sysfs/ioctl behavior and NBD kernel module availability are assumed. Several paths unwrap file opens and ioctl results inside helper threads, so device disappearance can panic. Readiness polling passes a pointer to an immutable zero `size` variable to ioctl, relying on kernel writes through const-looking Rust binding. Destroy uses raw pointer cast through `usize` to cross threads. NBD is described as mostly for testing, so production hardening is limited.

Test signals: missing NBD module, all devices busy, SPDK already using a candidate path, successful start callback, readiness timeout path, destroy while device path disappears, ioctl failure behavior, URI formatting, and repeated create/destroy without stale `/sys/class/block/nbd*/pid` state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_nbd.rs -->
