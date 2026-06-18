## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_37xx_reg.h

### Purpose
`ivpu_hw_37xx_reg.h` is the register and bit-mask map for ivpu 37xx IP blocks used by the hardware IP implementation.

### Important APIs, Types, And Functions
It defines host subsystem clock/reset, NoC QREQ/QACCEPT/QDENY, firewall IRQ enable, ICB status/clear/enable, IPC FIFO, AON power/isolation/idle/DPU-active registers, firmware loading address, workpoint mirror, TCU/TBU MMU/snoop override registers, CPU debug/timer/watchdog registers, performance counter, and doorbell registers with masks.

### Control Flow
There is no code flow. `ivpu_hw_ip.c` uses these macros through `REGV_*` and `REG_*` helpers for 37xx-specific power, boot, IRQ, watchdog, IPC, and doorbell sequences.

### State, Persistence, And Dependencies
Persistent state is hardware register state. The header depends on Linux bit macros and on register offsets matching BAR0 RegV layout for 37xx devices.

### Integration Points
It integrates with 37xx host SS bring-up, firmware boot entry, NPU IRQ dispatch, MMU TBU setup, IPC FIFO access, and doorbell ringing.

### Risks
Register maps are low-level hardware ABI. Wrong offsets/masks can power the wrong island, fail to clear interrupts, corrupt TBU snoop settings, or ring the wrong doorbell. Similar names across 37xx/40xx require generation-correct selection.

### Test Signals
Validate register read/write traces during 37xx probe/boot, IRQ status decoding, watchdog disable, IPC FIFO drain, doorbell stride, power-island status polling, and TBU MMU valid bits.
