## sources/control-plane/mayastor/io-engine/src/bdev/util/uring.rs

### Purpose
`bdev/util/uring.rs` checks whether the running kernel supports io_uring with the queue depth expected by SPDK uring bdevs.

### Important APIs, Types, And Functions
`kernel_support()` attempts to create `io_uring::IoUring` with queue depth 512 and returns a boolean.

### Control Flow
The function returns true on successful ring creation. On error it logs the error at debug level and returns false.

### State, Persistence, And Dependencies
No persistent state. The function briefly creates and drops an io_uring instance. Dependency is the `io_uring` crate and logging.

### Integration Points
Capability checks can use this before enabling or selecting the uring bdev path.

### Risks
Successful creation at depth 512 is a proxy for support, not a complete guarantee that every SPDK uring operation will work with a given file/device. Permission and resource limits can make support appear false.

### Test Signals
Cover success on supported kernels, expected false on blocked/unsupported environments, and debug logging on creation failure. Unit testing likely needs a wrapper or integration environment because it depends on kernel features.
