<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c

### Purpose
Provides common Compaq iPAQ H3100/H3600 board support for flash, UART power/wake, EGPIO, keys, microcontroller ASIC, PCMCIA GPIO lookup, I/O mapping, and base pin/suspend setup.

### Important APIs, Types, And Functions
Important helpers are `h3xxx_set_vpp()`, `h3xxx_flash_init()`, `h3xxx_flash_exit()`, `h3xxx_uart_pm()`, `h3xxx_uart_set_wake()`, `h3xxx_mach_init()`, and `h3xxx_map_io()`. It exports `h3xxx_micro_asic` as a platform device.

### Control Flow
`h3xxx_mach_init()` installs PCMCIA and UART GPIO lookups, registers SA1100 UART PM/wake callbacks, registers flash, and adds EGPIO, key, and micro ASIC devices. `h3xxx_map_io()` maps SA1100 common I/O and H3600 bank/EGPIO regions, registers UART3 as the common serial port, and initializes PPC/GPIO sleep defaults.

### State, Persistence, And Dependencies
State includes flash partition/platform data, EGPIO platform data, key platform data, micro ASIC resources, GPIO lookup tables, and static map descriptors. Dependencies include SA1100 generic helpers, HTC EGPIO, GPIO keys, MTD CFI, SA11x0 serial, PCMCIA, and H3xxx machine constants.

### Integration Points
Used by `h3600.c` and other H3xxx machine variants as common board support.

### Risks
UART wake modifies global `PWER` bits for GPIO23/GPIO25. Flash Vpp relies on EGPIO availability. Broad GPIO reset in map setup may conflict with bootloader-provided states if assumptions change.

### Test Signals
H3600/H3xxx boot, flash writes with Vpp, serial power management/wake, EGPIO registration, keys, micro ASIC resources, PCMCIA detection, and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c -->
