# sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.h

Purpose: shared header for the CPM SCC/SMC UART driver. It defines constants, feature flags, FIFO sizes, modem GPIO indexes, `struct uart_cpm_port`, and address translation helpers between CPU virtual buffer addresses and CPM/DMA addresses.

Important APIs/types/functions: `struct uart_cpm_port` embeds `uart_port` and tracks SMC/SCC register pointers, parameter RAM, RX/TX descriptor bases/cursors, TX/RX buffers, flags, clock/BRG command metadata, allocation bookkeeping, close wait, and optional GPIO descriptors. Macros include `SERIAL_CPM_MAJOR`, `SERIAL_CPM_MINOR`, `UART_NR`, FIFO sizes, `FLAG_SMC`, `FLAG_CONSOLE`, `IS_SMC()`, and GPIO indexes. `cpu2cpm_addr()` and `cpm2cpu_addr()` validate and translate offsets inside the allocated buffer span.

Control flow: allocation fills `mem_addr`, `dma_addr`, and `mem_size`; descriptor initialization calls `cpu2cpm_addr()`; RX/TX paths call `cpm2cpu_addr()`. The header itself has no runtime entry point.

State/persistence: `uart_cpm_port` is the in-memory lifetime state for a CPM UART. It stores both hardware-facing and serial-core-facing state. No disk persistence.

Dependencies/integration: conditionally includes `asm/cpm1.h` or `asm/cpm2.h`, exposes `DPRAM_BASE`, forward-declares `gpio_desc`, and is tightly coupled to `cpm_uart.c`.

Risks: helpers cast addresses to `u32`, suitable for the legacy CPM environment but not a generic 64-bit abstraction. Invalid addresses cause `BUG()`. Small fixed descriptor/buffer counts shape latency and throughput.

Test signals: address round-trips, SMC/SCC flag paths, console flag paths, GPIO index ordering, CPM1/CPM2 compilation, and all callers that mutate allocation fields.
