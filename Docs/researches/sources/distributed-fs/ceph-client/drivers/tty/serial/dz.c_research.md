# sources/distributed-fs/ceph-client/drivers/tty/serial/dz.c

Purpose: DECstation DZ chipset serial driver. It exposes four muxed `ttyS` lines behind one shared DZ device and IRQ, supports optional console output, and integrates with MIPS DECstation machine resources.

Important APIs/types/functions: `struct dz_port` embeds `uart_port`, cached `cflag`, and parent mux pointer; `struct dz_mux` owns four ports plus atomic guards for shared MMIO and IRQ ownership. `dz_ops` provides serial callbacks. Key functions are `dz_receive_chars()`, `dz_transmit_chars()`, `dz_interrupt()`, `dz_startup()`, `dz_shutdown()`, `dz_set_termios()`, `dz_request_port()`, `dz_release_port()`, `dz_config_port()`, `dz_reset()`, and console helpers.

Control flow: init exits on IOASIC machines, initializes port descriptors from DECstation machine type, registers the UART driver, and adds four ports. Request-port uses `map_guard` to acquire shared MMIO once. Startup uses `irq_guard` to request shared IRQ once and enable DZ RX/TX interrupts. IRQ reads CSR, drains receive data for any line, and transmits one character for the line selected by `DZ_TLINE`. Shutdown disables per-line TX and frees shared IRQ when final user closes.

State/persistence: global `dz_mux` is the persistent runtime state; per-line `cflag` caches line parameters; atomic guards track shared resource users; hardware registers hold line settings. No disk persistence.

Dependencies/integration: DECstation MIPS headers/resources, PROM/console support, serial core, SysRq, TTY flip buffers, and `dz.h`. It is architecture/platform-specific, not DT-driven.

Risks: RX/TX are multiplexed through shared registers. Some modem status handling is marked FIXME. BREAK is inferred from NUL plus framing error. Console polling masks TX interrupts and can time out. Guard imbalance would leak or prematurely release shared resources.

Test signals: all four lines, shared IRQ open/close behavior, MMIO request/release balance, console boot on non-IOASIC DECstations, termios baud fallback, inferred breaks, modem line 2 behavior, and multi-line TX scanner interaction.
