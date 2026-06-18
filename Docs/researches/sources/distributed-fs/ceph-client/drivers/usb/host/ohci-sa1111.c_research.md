# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sa1111.c

## Purpose

`ohci-sa1111.c` is SA-1111 companion-chip bus glue for OHCI. It powers and resets the SA-1111 USB block, sets up local memory to work around SA-1111 DMA addressing errata, and binds the core OHCI callbacks to the SA-1111 bus.

## Important APIs, Types, and Functions

Important functions are `ohci_sa1111_reset()`, `ohci_sa1111_start()`, `sa1111_start_hc()`, `sa1111_stop_hc()`, `ohci_hcd_sa1111_probe()`, `ohci_hcd_sa1111_remove()`, and `ohci_hcd_sa1111_shutdown()`. The file defines SA-1111 USB reset/status bit masks and `ohci_sa1111_hc_driver`.

## Control Flow

Probe creates the HCD, gets the SA-1111 USB IRQ, configures a 64 KiB local-memory bounce pool to avoid DMA erratum constraints, reserves the register region, uses the already-mapped SA-1111 base as HCD registers, starts hardware, and adds the HCD. Starting hardware programs power sense/control polarity for Assabet, asserts interface/HC reset, enables the SA-1111 device clock, delays, and releases reset. Remove unregisters the HCD, stops hardware, releases the region, and drops the HCD. Shutdown calls the HCD shutdown callback and stops hardware if still accessible.

## State and Persistence Behavior

State is HCD local memory pool, SA-1111 device clock/reset state, memory region reservation, and OHCI core runtime state. Reset and clock state live in SA-1111 registers and are not persisted beyond hardware state.

## Dependencies and Integration Points

It depends on SA-1111 bus APIs, SA-1111 register mapping, machine detection for Assabet, USB local-memory support, and generic OHCI internals because it is included by `ohci-hcd.c` when configured.

## Risks and Test Signals

Risks include local-memory sizing assumptions, SA-1111 DMA erratum constraints, edge-triggered IRQ behavior, polarity assumptions for Assabet, and no explicit PM callbacks beyond shutdown. Test signals include probe on SA-1111 systems, bounce-buffer use under DMA debug, enumeration with memory above the erratum boundary, shutdown path with hardware accessible, and remove/reprobe without region leaks.
