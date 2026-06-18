<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c

### Purpose
Implements the Sharp Zaurus Collie SA1100 board machine with LoCoMo, Scoop, PCMCIA, power/battery GPIOs, UART modem control, flash, LCD, MCP, and machine setup.

### Important APIs, Types, And Functions
Defines exported platform devices `colliescoop_device` and `collie_locomo_device`. Key helpers include `collie_uart_set_mctrl()`, `collie_uart_get_mctrl()`, `collie_uart_probe()`, `collie_uart_init()`, `collie_flash_init()`, `collie_set_vpp()`, `collie_flash_exit()`, `collie_init()`, and `collie_map_io()`.

### Control Flow
`collie_uart_init()` registers a LoCoMo driver at device init. Machine map installs common SA1100 and flash mappings, registers UART functions if LoCoMo is enabled, and maps UART ports. Machine init configures CPU GPIO/PPC/sleep registers, initializes MCP pin routing, adds GPIO lookup tables, registers platform devices, LCD, flash, MCP, and saves SharpSL parameters.

### State, Persistence, And Dependencies
State is board platform data for Scoop, LoCoMo, UCB1x00, MCP, battery/power, keys, flash partitions, and LCD timings. Dependencies include SA1100 generic helpers, LoCoMo, Scoop, SharpSL, GPIO descriptors, MTD, framebuffer, MCP, and machine descriptors.

### Integration Points
`MACHINE_START(COLLIE, ...)` connects Collie-specific map/init to SA1100 IRQ/timer/late PM/restart.

### Risks
LoCoMo modem-control callbacks depend on the driver being probed. GPIO and PPC register initialization is broad and can affect many pins. Flash Vpp and LCD power are board-specific.

### Test Signals
Collie boot, LoCoMo probe, serial modem controls, LCD, flash partitions, power/battery GPIO lookup, PCMCIA/Scoop, and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c -->
