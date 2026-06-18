<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-platform.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-platform.c

### Purpose
`malta-platform.c` registers Malta legacy platform devices, primarily 8250 UART ports and the CBUS UART.

### Important APIs, Types, And Functions
`SMC_PORT()` describes SuperIO serial ports. `uart8250_data` contains COM1, COM2, and CBUS UART descriptors. `malta_add_devices()` registers `malta_uart8250_device` through `platform_add_devices()` at `device_initcall`.

### Control Flow
At device init, the serial8250 platform device is added with static port data. The CBUS UART uses MMIO, endian-dependent IO type, remapped memory, and a CPU IRQ.

### State, Persistence, And Dependencies
Persistent state is the platform device and its serial port descriptors. Dependencies include serial8250 platform support, platform device core, Malta IRQ numbering, and endian configuration.

### Integration Points
The serial driver probes these ports and exposes Malta console/serial devices. This complements early console setup in `malta-init.c`.

### Risks
The file intentionally avoids generic `8250_platform.c` ordering because it would make CBUS `ttyS0`. Wrong IRQ or IO type breaks serial. CBUS clock is double the usual rate and must stay accurate.

### Test Signals
Boot with serial8250, verify ttyS ordering, console on COM1, CBUS UART availability, and big-endian CBUS access mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-platform.c -->
