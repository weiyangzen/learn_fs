# sources/distributed-fs/ceph-client/drivers/gpib/ines/ines.h

## Purpose

`ines.h` declares board-private state and INES-specific register/bit definitions for iGPIB 7210 boards. It layers INES FIFO, extended-mode, PCI-bridge, and bus-monitor controls on top of the NEC7210 core.

## Important APIs, Types, and Constants

- `enum ines_pci_chip` identifies no PCI bridge, PLX9050, AMCC5920, Quancom, and QuickLogic5030 variants.
- `struct ines_priv` embeds `struct nec7210_priv`, stores PCI device pointer, PLX/AMCC base addresses, IRQ, PCI chip type, and shadowed `extend_mode_bits`.
- `ines_inb()` and `ines_outb()` access INES registers via the embedded NEC7210 I/O base and offset.
- Register enums define FIFO status, ISR3/ISR4, FIFO counts/watermarks, extended status/mode, transfer counters, XDMA control, and bus control monitor.
- Bit enums define FIFO/transfer/IFC/ATN events, FIFO readiness, extended mode behavior, extended status, INES FIFO enable bits in ADMR, DMA control bits, bus line monitor bits, and INES auxiliary commands/register bits.

## Control Flow and Integration

`ines_gpib.c` uses this header for accelerated read/write setup, interrupt decoding, bus line status, T1 delay programming, attach-time PCI bridge handling, and board online/reset flows.

## State and Persistence Behavior

`extend_mode_bits` is a software shadow of `EXTEND_MODE` and persists while attached. The embedded NEC7210 private state carries controller status, register shadows, and transfer state.

## Dependencies

It includes `nec7210.h`, `gpibP.h`, PLX/AMCC/Quancom PCI bridge headers, and `linux/interrupt.h`.

## Risks and Test Signals

The inline I/O helpers assume I/O-port access and correct offset; wrong PCI ID metadata corrupts register selection. FIFO counter width is limited, and `ines_gpib.c` guards transfer counter values above 0xffff. Test signals are accelerated read/write, FIFO watermark IRQs, bus line readback, T1-delay selection, and all supported PCI bridge variants.
