# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_uart.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_uart.c

### Purpose
`sdio_uart.c` is an SDIO function driver that exposes SDIO UART/GPS functions as Linux TTY devices named `ttySDIO*`. It implements a sleeping, SDIO-access-safe serial driver for 16550A-like register sets that cannot use the regular 8250 infrastructure.

### Important APIs, Types, And Functions
The key type is `struct sdio_uart_port`, which embeds `struct tty_port`, points to `struct sdio_func`, protects function lifetime with `func_lock`, stores IRQ recursion state, register offset, TX FIFO, write lock, modem/control state, error counters, UART clock, IER/LCR, and status masks. Major flows are `sdio_uart_probe()`, `sdio_uart_remove()`, `sdio_uart_init()`, `sdio_uart_exit()`, `sdio_uart_activate()`, `sdio_uart_shutdown()`, `sdio_uart_irq()`, RX/TX helpers, TTY operations, and modem/termios helpers.

### Control Flow
Module init allocates/registers a dynamic TTY driver, then registers an SDIO driver for UART and GPS classes. Probe currently rejects generic UART class as unsupported, parses GPS tuple 0x91/SUBTPL_SIOREG for register offset and clock, initializes a tty port, assigns a free port index, and registers a TTY device. Opening a tty activates the port: resets TX FIFO, claims SDIO host, enables the function, claims SDIO IRQ, clears FIFOs/interrupt status, initializes LCR/IER/modem state, applies termios, raises RTS/DTR when baud is nonzero, checks CTS flow control, clears TTY I/O error, and kicks the IRQ handler. IRQ handling reads IIR/LSR, drains RX into tty flip buffers, handles modem deltas, and transmits queued bytes. Shutdown disables RX/IRQs, clears modem control, flushes FIFOs, disables the function, and releases the host. Remove unregisters the tty device, nulls `port->func`, hangs up users, releases IRQ, disables the function, and drops references.

### State, Persistence, And Dependencies
State is in the global `sdio_uart_table`, per-port kfifo, tty references, SDIO function driver data, UART registers accessed via CMD52, modem counters, and TTY device nodes. Dependencies include SDIO core APIs, TTY core, kfifo, serial register constants, SDIO IDs/classes, module infrastructure, and tuple data provided by `sdio_cis.c`.

### Integration Points
The driver binds through `sdio_bus.c`, uses `sdio_io.c` and `sdio_irq.c`, and exposes standard tty operations to userspace. It depends on the MMC/SDIO core to supply function devices, tuple lists, host locking, and IRQ dispatch.

### Risks
SDIO register access can sleep, so all TTY callbacks must avoid spinlock-only assumptions. Lifetime is delicate: `port->func` is nulled under `func_lock` during removal while tty users may still hold port references. IRQ recursion is explicitly guarded with `in_sdio_uart_irq` because direct IRQ kicks can re-enter through tty echo/flow control. TX uses a page-sized kfifo and short 16-byte bursts, so throughput depends on IRQ cadence. Generic SDIO UART class returns `-ENOSYS`, leaving only GPS tuple-described devices usable. Modem delta reads may consume bits before `sdio_uart_check_modem_status()`, as noted by a FIXME.

### Test Signals
Test GPS-class probe with valid/invalid tuple 0x91, tty open/close/hangup, termios baud/format/flow-control changes, RX parity/frame/break/overrun handling, TX wakeup and XON/XOFF, CTS/DCD modem changes, removal while tty is open, IRQ recursion, suspend/remove through SDIO core, and unsupported UART-class binding.
