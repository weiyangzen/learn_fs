# sources/distributed-fs/ceph-client/include/linux/serial_sci.h

## Purpose

`serial_sci.h` defines platform data for SuperH and Renesas SCI, SCIF, SCIFA, SCIFB, HSCIF, and related serial controllers. It supplies common control-register bits and a compact platform contract for drivers that bind these UART variants to the serial core.

## Important APIs, Types, And Functions

The header defines `SCSCR_*` bits for transmit interrupt, receive interrupt, transmit enable, receive enable, receive-error interrupt, timeout interrupt, and clock enable bits. The anonymous enum lists register layout identifiers such as `SCIx_SCI_REGTYPE`, `SCIx_SCIFA_REGTYPE`, `SCIx_SH4_SCIF_REGTYPE`, `SCIx_HSCIF_REGTYPE`, `SCIx_RZ_SCIFA_REGTYPE`, and `SCIx_RZV2H_SCIF_REGTYPE`.

`struct plat_sci_port_ops` contains an optional `init_pins()` hook. `struct plat_sci_port` carries the SCI type, `UPF_*` serial flags, sampling rate, initial SCSCR value, optional register type override, and optional platform operations.

## Control Flow

There is no code body. During platform setup and driver probe, the SCI driver consumes `plat_sci_port` to select a register map, initialize control register defaults, configure pins through `init_pins()`, and expose the port as a `uart_port`. Runtime control flow in the driver then uses the `SCSCR_*` bits to enable TX, RX, and interrupt sources.

## State And Persistence

Persistent state is external: platform data may be static, and hardware control state lives in SCI registers. The `scscr` field seeds initial receive/transmit and interrupt enable state for each port.

## Dependencies And Integration Points

Dependencies are `linux/bitops.h`, `linux/serial_core.h`, and `linux/sh_dma.h`. Integration points include Renesas/SuperH platform device setup, pin muxing, serial core `UPF_*` flags, and DMA-capable SCI variants.

## Risks And Test Signals

Risks are selecting the wrong register type for a SoC, enabling interrupts before pins or clocks are ready, and using a sampling rate inconsistent with baud calculations. Test signals include probe on each listed register type, TX/RX interrupt enable behavior, pin initialization, DMA-backed transfers, and boot-console operation on SCI/SCIF variants.
