# sources/distributed-fs/ceph-client/drivers/tty/serial/ucc_uart.c

## Purpose

`ucc_uart.c` is the Freescale QUICC Engine UCC slow UART driver. It exposes QE UCC UARTs as `ttyQE0` through `ttyQE3`, manages QE buffer descriptors and coherent DMA buffers, programs UCC parameter RAM, supports optional Soft-UART microcode on PPC32, and binds device-tree UCC UART nodes. The file was read as a complete 1531-line source file.

## Important APIs, Types, and Functions

`struct ucc_uart_pram` models the UCC UART parameter RAM, including standard and Soft-UART-only fields. `struct uart_qe_port` wraps `struct uart_port` with UCC register pointers, `ucc_slow_info`, UCC private state, OF node, descriptor rings, coherent buffer addresses, FIFO sizing, and shutdown delay. The serial-core table `qe_uart_pops` implements TX/RX control, startup/shutdown, termios, resource request/release, and validation. Important functions include `cpu2qe_addr()`, `qe2cpu_addr()`, `qe_uart_tx_pump()`, `qe_uart_int_rx()`, `qe_uart_int()`, `qe_uart_initbd()`, `qe_uart_init_ucc()`, `qe_uart_request_port()`, `qe_uart_set_termios()`, `soft_uart_init()`, `uart_firmware_cont()`, `ucc_uart_probe()`, and `ucc_uart_remove()`.

## Control Flow

Module init registers the fixed-major UART driver and OF platform driver. Probe optionally initializes Soft-UART, allocates `uart_qe_port`, reads MMIO resource, UCC number, RX/TX BRG clock names, port number, IRQ, and QE `brg-frequency`, then initializes serial-core fields and UCC slow-info fields before `uart_add_one_port()`. During serial-core config, `qe_uart_request_port()` calls `ucc_slow_init()`, captures UCC register/PRAM/BD pointers, and allocates coherent RX/TX character buffers. Startup refuses Soft-UART if firmware is not loaded, initializes RX/TX BDs, programs UCC registers/PRAM, requests the shared IRQ, enables RX interrupt events, and starts RX/TX in UCC slow mode. The IRQ handler clears UCCE events, dispatches break handling, drains RX BDs into tty buffers, and pumps queued TX data into free BDs. Shutdown waits for TX BDs to drain, optionally waits `UCC_WAIT_CLOSING`, disables UCC, gracefully stops TX, reinitializes BDs, and frees the IRQ.

## State and Persistence Behavior

Per-port persistent state includes descriptor ring positions `rx_cur`/`tx_cur`, coherent buffer mappings, UCC parameter RAM, UCC slow-private state, OF node reference, serial-core masks, and FIFO sizing. Global `soft_uart` and `firmware_loaded` apply process-wide to all ports. Hardware state is programmed into UCC GUMR, UCCM/UCCE, UPSMR/SUPSMR, BRGs, and PRAM fields on startup and termios changes. There is no disk persistence; firmware loading is asynchronous and stored only in the global flag.

## Dependencies and Integration Points

The driver depends on serial core, tty flip buffers, OF address/IRQ parsing, DMA coherent allocation, QUICC Engine UCC slow APIs, CPM/QE firmware APIs, Linux firmware loading, and PPC32 CPU revision probing for Soft-UART filenames. It binds OF nodes with `.type = "serial", compatible = "ucc_uart"` and `fsl,t1040-ucc-uart`, uses `qe_setbrg()` for BRG clocks, and presents major 204 minor 46-49 to match Freescale CPM-style devices.

## Risks and Edge Cases

The DMA address translation helpers call `BUG()` if a BD buffer points outside the coherent allocation, turning corruption into a kernel crash. `qe_uart_request_port()` does not call `ucc_slow_free()` if coherent allocation fails after `ucc_slow_init()`. The Soft-UART globals mean one port requiring Soft-UART affects all instances, and asynchronous firmware loading can make early opens fail until `firmware_loaded` is set. Termios bit clearing is suspicious: `upsmr &= UCC_UART_UPSMR_CL_MASK` and `supsmr &= UCC_UART_SUPSMR_CL_MASK` retain only character-length bits before ORing new values, which may discard other mode bits. `CREAD` handling modifies `read_status_mask` instead of `ignore_status_mask`, so receive suppression deserves careful hardware testing. The probe path holds a QE node reference in `qe_port->np`; error paths release it only after the QE node is found.

## Test Signals

Useful tests include OF probe validation for required properties, multiple port-number bounds, BRG clock-name validation, coherent DMA allocation failure injection, `ucc_slow_init()`/free leak checks, Soft-UART firmware present/missing/asynchronous scenarios, RX/TX descriptor wrap tests, break/parity/frame/overrun injection, termios matrix coverage for CS5-CS8/parity/stop/CREAD, shutdown drain timeout behavior, and serial-console or user-space loopback traffic across all four supported ports.
