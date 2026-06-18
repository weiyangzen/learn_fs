# sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.c

Purpose: Freescale CPM1/CPM2 SCC/SMC UART driver for PowerPC CPM communication processors. It exposes `ttyCPM` ports backed by CPM parameter RAM, CPM buffer descriptors, coherent or DPRAM buffers, optional console/poll/udbg support, and optional GPIO modem lines.

Important APIs/types/functions: `struct uart_cpm_port cpm_uart_ports[UART_NR]`, `cpm_uart_pops`, `cpm_uart_startup()`, `cpm_uart_shutdown()`, `cpm_uart_set_termios()`, `cpm_uart_tx_pump()`, `cpm_uart_int_rx()`, `cpm_uart_int()`, `cpm_uart_allocbuf()`, `cpm_uart_initbd()`, `cpm_uart_init_smc()`, `cpm_uart_init_scc()`, `cpm_uart_map_pram()`, `cpm_uart_init_port()`, `cpm_uart_console_setup()`, and `cpm_uart_early_write()`.

Control flow: probe assigns a sequential port index, maps IRQ, initializes the CPM port from DT, and adds it to serial core. Initialization reads clock/BRG, command opcode, SMC/SCC resources, parameter RAM, GPIOs, and serial-core fields, then allocates descriptors and data buffers. Startup reinitializes non-console descriptors, requests IRQ, and enables RX/TX. IRQ acknowledges SMC/SCC events and dispatches break, RX, and TX. RX walks completed descriptors into the TTY flip buffer and returns descriptors to CPM ownership; TX fills descriptors from `x_char` or xmit FIFO.

State/persistence: state spans `uart_cpm_port`, CPM registers, parameter RAM, MURAM buffer descriptors, coherent/DPRAM buffers, clock/BRG metadata, optional GPIOs, and serial-core counters/masks. Descriptor ownership bits are the core runtime state. No disk persistence.

Dependencies/integration: CPM architecture headers, MURAM APIs, CPM commands, OF address/IRQ/platform, DMA mapping, clocks, GPIO descriptors, serial core, console, TTY flip buffers, SysRq, and PowerPC udbg. DT must provide compatible, registers, parameter RAM, `fsl,cpm-command`, and clock or `fsl,cpm-brg`.

Risks: descriptor ownership and CPU/CPM address translation are fragile; bad translations hit `BUG()`. Console allocation differs from normal DMA. `probe_index` assumes stable bounded probe order. RX can stop on flip-buffer pressure. Parameter RAM mapping has legacy fallback behavior. Shutdown may sleep waiting for TX.

Test signals: SMC and SCC variants, CPM1/CPM2 builds, console and non-console allocation, descriptor wraparound, low-baud/low-latency RX sizing, GPIO modem signals, poll/udbg, termios updates, break handling, and probe/remove failure unwinding.
