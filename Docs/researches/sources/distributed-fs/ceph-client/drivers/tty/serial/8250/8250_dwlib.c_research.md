# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.c

## Purpose
Provides shared DesignWare 8250 helper logic for fractional divisors, termios integration, hardware RS485/addressing support, FIFO/capability discovery from Component Parameter Register, and fallback to emulated RS485.

## Important APIs, types, and functions
- Fractional divisor helpers: `dw8250_get_divisor()` and local `dw8250_set_divisor()`.
- Exported termios wrapper: `dw8250_do_set_termios()`.
- RS485/addressing helpers: `dw8250_wait_re_deassert()`, `dw8250_update_rar()`, `dw8250_rs485_set_addr()`, `dw8250_rs485_config()`, `dw8250_detect_rs485_hw()`, and `dw8250_rs485_supported`.
- Exported setup: `dw8250_setup_port()`.

## Control flow
`dw8250_setup_port()` first probes whether hardware RS485 exists by writing/reading `RE_EN`. If present, it installs hardware RS485 config, expands LSR save mask for address-detected status, and advertises address receive/destination features; otherwise it installs generic 8250 emulated RS485 callbacks. It then marks no-TEMT capability, probes the DLF register width by writing all ones and restoring the old value, and if present installs fractional divisor callbacks.

It reads UART version and CPR; if CPR is missing, it uses a platform-provided `cpr_value`. CPR FIFO mode makes the port fixed 16550A with computed FIFO size and FIFO capability. CPR bits add auto-flow-control and IrDA capabilities.

RS485 config programs TCR, DE/RE enable registers, DE/RE polarity, transfer mode, and optional 9-bit addressing. Receive address changes deassert RE, waits one frame time, writes RAR, and restores RE.

## State and persistence behavior
Mutates caller-owned `dw8250_port_data`, `uart_port`, and `uart_8250_port`: `dlf_size`, `hw_rs485_support`, rs485 callbacks/supported flags, FIFO size, capabilities, divisor callbacks, and LSR masks. Hardware registers hold RS485, address, DLF, and capability-related state.

## Dependencies and integration points
Depends on `8250_dwlib.h` extended register accessors, serial8250 divisor/termios/RS485 emulation helpers, device properties, and serial_core RS485 structures. Exported symbols are used by `8250_dw.c`.

## Risks and edge cases
- DLF probing writes `~0U` to hardware and must restore firmware value; broken DLF implementations could misreport width.
- Hardware RS485 detection writes `RE_EN`; side effects on active hardware would be risky if called outside setup.
- Address receive config must avoid changing RAR while receiving; the frame-time wait is a heuristic without BUSY signal.
- CPR fallback data must match the SoC, otherwise FIFO/capability detection is wrong.

## Test signals
Hardware RS485 detection present/absent, RS485 enable/disable and polarity/address modes, fractional divisor baud accuracy, CPR-derived FIFO/capability reporting, IrDA line discipline capability, and fallback to emulated RS485 when RE_EN is not writable.
