# sources/distributed-fs/ceph-client/drivers/gpib/ines/ines_gpib.c

## Purpose

`ines_gpib.c` is the board driver for INES iGPIB 7210 hardware. It supports PCI, ISA, and optionally PCMCIA devices, registers accelerated and unaccelerated linux-gpib interfaces, and delegates the base GPIB controller behavior to the NEC7210 core while using INES FIFO/extended registers for faster transfers.

## Important APIs, Types, and Functions

- `ines_line_status()` maps INES bus-control monitor bits to linux-gpib `BUS_*` line status.
- `ines_accel_read()` and `ines_accel_write()` implement FIFO/counter-backed data movement.
- `pio_read()` and `ines_write_wait()` are accelerated transfer helpers around FIFO count and wait conditions.
- `ines_interrupt()` calls `nec7210_interrupt()`, reads INES ISR3/ISR4, pushes IFC events, logs FIFO errors, and wakes sleepers for transfer-count and watermark events.
- `ines_pci_interrupt()` adds Quancom interrupt clear/re-enable behavior before delegating to `ines_interrupt()`.
- `ines_common_pci_attach()`, `ines_pci_attach()`, and `ines_pci_accel_attach()` discover PCI boards, enable devices, request regions and IRQs, program PCI bridge interrupt/timing registers, reset the NEC7210, and call `ines_online()`.
- `ines_isa_attach()`/`ines_isa_detach()` handle configured ISA I/O/IRQ resources.
- Optional PCMCIA code registers a `pcmcia_driver`, configures sockets/windows, tracks `curr_dev`, and attaches via `ines_common_pcmcia_attach()`.
- Module init/exit registers/unregisters the PCI driver and multiple `struct gpib_interface` tables.

## Control Flow

The common attach path calls `ines_generic_attach()` to allocate private data, initialize `nec7210_priv`, set I/O accessors, mark the chip type `IGPIB7210`, and initialize the PCI chip type. PCI attach then searches a custom `pci_ids[]` list with optional bus/slot filters, enables the device, requests all PCI regions, selects GPIB I/O base and offset, stores bridge-specific bases, resets the NEC7210, requests a shared IRQ, and programs bridge-specific interrupt routing. PLX enables local and PCI interrupts, AMCC disables prefetch/write FIFO and sets wait states before enabling add-on interrupts, and Quancom writes its IRQ enable register.

`ines_online()` programs INES auxiliary mode, puts the controller into immediate RFD holdoff, clears extended/DMA state, sets FIFO watermarks and ISR masks for accelerated mode, disables IN/OUT FIFOs for unaccelerated mode, calls `nec7210_board_online()`, and in accelerated mode disables normal data-in/data-out NEC interrupts because FIFO interrupts drive transfer wakeups.

Accelerated read immediately holds off RFD, clears/enables the input FIFO, configures extended-mode last-byte handling for input, sets the transfer counter if more data is expected, enables counter mode, sets holdoff on END, releases holdoff, drains the FIFO until length, END, timeout, or device clear, disables counter mode, and reports END from `RECEIVED_END_BN`.

Accelerated write clears/enables output FIFO, configures output counter mode, optionally enables last-byte handling for EOI, fills FIFO chunks while `num_out_fifo_bytes()` stays under threshold, waits for the last byte to drain, disables counter mode, and reports bytes written as `length - num_out_fifo_bytes()`.

## State and Persistence Behavior

Private state is `struct ines_priv`: embedded NEC7210 state plus PCI device/resource metadata, IRQ number, bridge type, and `extend_mode_bits`. The driver maintains shadowed extended-mode bits to avoid losing unrelated flags. Transfer state is a combination of INES FIFO counts, transfer counter registers, ISR3/ISR4 bits, NEC7210 state bits, and `board->status`. PCMCIA support additionally uses global `curr_dev`.

## Dependencies and Integration Points

The file depends on Linux PCI, optional PCMCIA, I/O port, IRQ, DMA headers, `gpib_pci_ids.h`, INES register definitions, PCI bridge headers, and the NEC7210 core. It integrates with gpib-common by registering interface names `ines_pci`, `ines_pci_unaccel`, `ines_pci_accel`, `ines_isa`, and optional PCMCIA variants.

## Risks and Test Signals

Many attach error paths return `-1` or other errors after partial allocation/resource acquisition; cleanup relies on detach or leaves risk of leaked private data, PCI refs, regions, or IRQs. In `ines_pci_detach()`, the AMCC case checks `plx_iobase` before writing PLX INTCSR, which looks inconsistent with AMCC naming and may fail to disable AMCC interrupts. `ines_set_xfer_counter()` rejects counts above 0xffff but accelerated paths can receive larger lengths; tests should cover large transfers. Optional PCMCIA uses a single global `curr_dev`, limiting multi-card behavior. Test signals are module init unwind paths, PCI bridge variants, ISA attach/detach, accelerated/unaccelerated transfers, END/EOI handling, IFC event queueing, FIFO error logging, timeout/device-clear behavior, and PCMCIA insert/remove/resume if enabled.
