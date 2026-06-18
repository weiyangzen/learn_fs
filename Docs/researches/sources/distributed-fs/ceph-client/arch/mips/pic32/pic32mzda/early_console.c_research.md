## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_console.c

### Purpose
This file implements PIC32MZDA early UART setup and `prom_putchar()` support for early printk. It parses `earlyprintk=ttyS...` command-line parameters, configures PPS pins, programs UART baud/mode/status registers, and writes characters before normal serial drivers bind.

### Important APIs, Types, And Functions
State includes `uart_base` and `console_port`. `configure_uart_pins()` supports ports 1 and 5 with hard-coded PPS mappings. `configure_uart()` programs mode, baud generator, and TX/RX enable bits using PBCLK2. `pic32_getcmdline()`, `get_port_from_cmdline()`, and `get_baud_from_cmdline()` parse early command-line data. `fw_init_early_console()` maps UART space and initializes the selected/default console. `prom_putchar()` busy-waits for TX space and writes a byte.

### Control Flow
During `plat_mem_setup()` under `CONFIG_EARLY_PRINTK`, `fw_init_early_console()` maps UART registers, extracts port and baud or defaults to port 1 at 115200, configures PPS and UART. Later early printk calls `prom_putchar()`, which only emits when `console_port >= 0`.

### State, Persistence, And Dependencies
The UART mapping and console port persist through early boot. Dependencies include early clock helpers, PPS helpers from `early_pin.c`, firmware command-line helpers, and PIC32 UART base constants.

### Integration Points
This runs before full pinctrl and serial drivers. It uses built-in or firmware command lines depending on `CONFIG_CMDLINE_OVERRIDE`.

### Risks
Only ports 1 and 5 are supported. Command parsing is simple and assumes `ttyS<digit>,<baud>`. The UART mapping is intentionally not released. Bad PBCLK calculation causes baud mismatch.

### Test Signals
Boot with default earlyprintk, with `earlyprintk=ttyS5,57600`, and with unsupported ports; confirm early characters, pin muxing, and baud accuracy.
