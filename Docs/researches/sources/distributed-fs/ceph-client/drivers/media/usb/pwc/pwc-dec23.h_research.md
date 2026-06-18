## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.h

### Purpose
`pwc-dec23.h` defines private state and public entry points for Timon/Kiara codec2/codec3 decompression.

### Important APIs, Types, And Functions
`struct pwc_dec23_private` contains the decoder mutex, command cache, bit depth/scaling values, bit reservoir, stream pointer, temporary 4x4 block colors, pass tables, subblock table, bit-mask table, and DC/scaling tables. It declares `pwc_dec23_init()` and `pwc_dec23_decompress()`.

### Control Flow
The header has no runtime flow, but its fields are filled during mode initialization and consumed during frame decompression.

### State, Persistence, And Dependencies
State is embedded in `struct pwc_device` through a union in `pwc.h`, so one active codec-private state exists per device. There is no persistent storage.

### Integration Points
Included by the PWC core, mode control, decompression frontend, and codec implementation. It defines the shared contract between `pwc-ctrl.c`, `pwc-uncompress.c`, and `pwc-dec23.c`.

### Risks
The structure contains large lookup tables and is embedded in every `pwc_device`, so size changes affect per-device memory. Direct field access across files would make future decoder refactors harder, though current mutation is localized mostly to `pwc-dec23.c`.

### Test Signals
Build tests should cover all include combinations. Runtime tests should validate decoder state reinitialization when mode command bytes change.
