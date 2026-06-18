## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.h

### Purpose
`pwc-dec1.h` defines the private state and initializer declaration for legacy codec1 decompression.

### Important APIs, Types, And Functions
It forward declares `struct pwc_device`, defines `struct pwc_dec1_private { int version; }`, and declares `pwc_dec1_init()`.

### Control Flow
The header has no runtime control flow. It lets `struct pwc_device` embed codec1 state and lets `pwc-ctrl.c` call the initializer.

### State, Persistence, And Dependencies
The only state is the stored device release version. No persistent storage exists.

### Integration Points
Included by `pwc.h`, `pwc-ctrl.c`, `pwc-if.c`, and `pwc-uncompress.c` for compile-time type and function visibility.

### Risks
The minimal private state reflects the missing decompressor implementation. Future codec1 support would likely need a larger state structure and corresponding updates to `struct pwc_device`.

### Test Signals
Build coverage should catch signature mismatches. Runtime coverage is tied to codec1 mode initialization and the unsupported YUV decompression path.
