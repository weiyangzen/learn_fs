## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/reset.h

### Purpose
`reset.h` exposes the Hisilicon reset-controller init/exit API with stubs when reset-controller support is disabled.

### Important APIs, Types, And Functions
It forward declares `struct hisi_reset_controller` and declares `hisi_reset_init()`/`hisi_reset_exit()` under `CONFIG_RESET_CONTROLLER`. Stub builds return `0` and perform no cleanup.

### Control Flow
There is no runtime flow in the header; compile-time configuration selects real functions or inline stubs.

### State, Persistence, And Dependencies
No state is stored here. Users rely on `struct platform_device` being declared by other includes.

### Integration Points
CRG drivers include this header and can compile regardless of reset-controller configuration.

### Risks
The stub `hisi_reset_init()` returns `0`, which CRG probes treat as failure and return `-ENOMEM`; this effectively makes these CRG drivers fail to probe if built without reset-controller support. The returned zero is typed as a pointer, not an `ERR_PTR`.

### Test Signals
Build with and without `CONFIG_RESET_CONTROLLER`, inspect CRG probe behavior in the disabled case, and run W=1/sparse for missing forward declarations.
