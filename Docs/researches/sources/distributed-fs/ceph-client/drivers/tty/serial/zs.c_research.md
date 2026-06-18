# sources/distributed-fs/ceph-client/drivers/tty/serial/zs.c

## Purpose

`zs.c` is the DECstation IOASIC Zilog Z85C30 SCC serial driver. It initializes up to two SCC chips with two channels each, exposes them as `ttyS` ports through serial core, handles DECstation-specific modem-line wiring, supports serial console output, and directly programs the Z85C30 register set using the definitions in `zs.h`. The file was read as a complete 1308-line source file.

## Important APIs, Types, and Functions

The driver uses `struct zs_scc` and `struct zs_port` from `zs.h`, plus local `struct zs_parms` for discovered SCC resources. Important low-level helpers are `read_zsreg()`, `write_zsreg()`, `read_zsdata()`, `write_zsdata()`, `load_zsregs()`, `zs_receive_drain()`, `zs_transmit_drain()`, and `zs_line_drain()`. Serial-core operations are in `zs_ops`, including modem control, TX/RX start-stop, break, startup/shutdown, termios, PM, request/release/configure, and verify. Runtime paths include `zs_receive_chars()`, `zs_raw_transmit_chars()`, `zs_status_handle()`, and `zs_interrupt()`. Setup paths include `zs_probe_sccs()`, `zs_console_setup()`, `zs_init()`, and `zs_exit()`.

## Control Flow

`zs_probe_sccs()` discovers SCC0/SCC1 IRQ availability from DECstation platform arrays, initializes `zs_sccs[]`, fills each channel's `uart_port`, mapbase, IRQ, clock, and register shadow from `zs_init_regs`. Console init can map and reset a port before normal module init. Module init registers the `ttyS` UART driver and adds each discovered port. During config, `zs_request_port()` reserves and maps MMIO, then `zs_reset()` resets the chip once per SCC and loads the register shadow. Startup reference-counts the shared IRQ per SCC through `irq_guard`, clears receive and pending interrupts, enables RX/TX/ext interrupts, enables break detection, records modem and break state, and marks TX stopped. The shared interrupt handler reads RR3 from channel A, prioritizes RX for both channels, then external status and TX. Termios edits the register shadow for character size, parity, stop bits, clock mode, BRG constants, read/ignore masks, receive enable, and modem interrupts, then reloads hardware registers.

## State and Persistence Behavior

Persistent state is held in static `zs_sccs[]`; each `zs_port` contains a register shadow `regs[16]`, current modem state, break state, clock mode, and TX-stopped flag. Each `zs_scc` has a shared spinlock, IRQ reference guard, and one-time initialized flag. Hardware state persists in Z85C30 registers and is deliberately mirrored through the register shadow because many write registers are not readable. There is no file-backed persistence. Console paths temporarily alter TX enable and interrupt bits, then restore the saved shadow values.

## Dependencies and Integration Points

The driver depends on DECstation platform headers (`dec_interrupt`, IOASIC addresses, `dec_kn_slot_base`), serial core, tty flip buffers, sysrq, shared IRQs, MMIO, and the Z85C30 register definitions in `zs.h`. It exposes classic `ttyS` major/minor numbering, supports `CONFIG_SERIAL_ZS_CONSOLE`, and relies on DECstation channel wiring where channel A signals are used to represent some modem lines for channel B.

## Risks and Edge Cases

Register access requires recovery delays and high-byte IOASIC offsets; timing or offset mistakes can corrupt SCC programming. The driver has complex channel-A/channel-B modem-line coupling, so DTR/RTS/DSR/RI/DCD regressions are easy when changing modem code. `zs_status_handle()` increments `dsr` for `TIOCM_RNG` and `rng` for `TIOCM_DSR`, which appears swapped. `zs_shutdown()` disables RX but writes R5 without clearing `TxENAB`, relying on other paths for TX state. IRQ sharing is guarded per SCC, but startup failure after IRQ acquisition must keep `irq_guard` balanced. The code uses static maximum SCC counts and cannot dynamically scale beyond two chips.

## Test Signals

Signals include MIPS/DECstation build coverage, boot discovery with SCC0/SCC1 present and absent, console setup/write before and after normal registration, TX/RX loopback per channel, shared IRQ receive-priority behavior, modem-line delta tests for channel B wiring, break/sysrq handling, termios coverage for BRG and CS/parity/stop settings, startup/shutdown reference-count tests on both channels of one SCC, and static analysis of register-shadow updates versus hardware writes.
