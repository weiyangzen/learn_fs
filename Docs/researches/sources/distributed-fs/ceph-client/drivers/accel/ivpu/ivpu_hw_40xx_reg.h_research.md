## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_40xx_reg.h

### Purpose
`ivpu_hw_40xx_reg.h` maps ivpu 40xx and later host/IP registers used by generic 40xx/50xx/60xx hardware code.

### Important APIs, Types, And Functions
It defines host SS clock/reset enables, NoC handshakes, firewall IRQ enable, ICB status/clear/enable, IPC FIFO/status, AON power/isolation/idle registers, 50xx power-island delay/fabric override registers, firmware verification address, workpoint mirror, TCU/TBU overrides, CPU NoC handshakes, watchdog/timer/perf counter, and doorbell offsets/masks.

### Control Flow
No executable logic is present. `ivpu_hw_ip.c` selects this map for hardware IP 40xx and above for host SS, power island, top NoC, snoop/TBU, CPU boot, IRQ, IPC, and doorbell operations.

### State, Persistence, And Dependencies
State lives in hardware registers. The header depends on Linux bit macros and BAR0 RegV layout for 40xx+ devices, including 50xx-only delay registers.

### Integration Points
It underpins power/boot/IRQ handling for LNL/PTL/WCL/NVL-class devices and shares many helper flows with the 37xx map through generation-specific wrappers.

### Risks
Some masks differ subtly from 37xx, such as hostif L2 cache bit positions and CSS/MSS naming. 50xx delay/fabric registers must not be used on older IP generations.

### Test Signals
Test boot/power sequencing on 40xx, 50xx, and 60xx devices, register traces for NoC and CPU handshakes, 50xx power delay programming, IRQ decode/clear, IPC FIFO fill-level reads, and doorbell writes.
