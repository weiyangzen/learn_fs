# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/serial.c

Purpose: LPC32xx standard/high-speed UART early setup and loopback erratum helper.

Important APIs/types/functions: Defines `lpc32xx_loopback_set()`, `lpc32xx_serial_init()`, `struct uartinit`, and UART init tables for UART3-6.

Control flow: Serial init enables UART clocks, disables autoclock by programming UART clock modes, sets pre-UART dividers, flushes RX FIFOs before and after clockmode programming, disables UART6 IrDA pulsing, and disables UART5 USB transparent routing. Loopback helper maps HS UART base to CLOOP bit and toggles it for an LPC3250 erratum workaround.

State and persistence: Hardware state includes UART clock registers, FIFO control/DLL accesses, UART control CLOOP/CTRL bits, IrDA bypass, and UART5 USB route. No persistent software state.

Dependencies and integration points: Depends on clock framework, static LPC32xx MMIO macros, serial core register definitions, and exported NXP misc users.

Risks: `clk_enable()` is called without prepare/error propagation or later disable. FIFO flush reads from UART registers and assumes clocks are live. Unknown high-speed UART bases trigger WARN.

Test signals: Boot with console on standard UARTs, test UART5/USB coexistence, UART6 IrDA bypass, and HS UART loopback erratum behavior.
