## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.h

### Purpose
`ivpu_hw_ip.h` declares the IP-side hardware operations used by common hardware, IPC, PM, MMU, and job paths.

### Important APIs, Types, And Functions
The API covers host SS configuration, idle generation, power-domain and NoC enabling, perf timer read, snoop/TBU setup, SOC CPU boot, watchdog disable, diagnostics, IPC FIFO count/address/TX, IRQ clear/enable/disable and generation-specific IRQ handlers, doorbell set, and 50xx fabric request override.

### Control Flow
There is no implementation in the header. Callers select these functions through common wrappers or direct calls during power-up, boot, interrupt handling, and IPC/job operations.

### State, Persistence, And Dependencies
State lives in hardware registers touched by the implementation. The header depends on `ivpu_drv.h` and a valid `struct ivpu_device`.

### Integration Points
It forms the boundary between generic driver logic and RegV IP-specific programming in `ivpu_hw_ip.c`.

### Risks
Functions assume RegV is mapped and hardware is in the correct power state. 50xx fabric override hooks should only be used on supporting generations.

### Test Signals
Build/link coverage for all prototypes and runtime coverage through hardware init/boot/IPC/IRQ/job paths on each IP generation.
