# sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.h

## Purpose
`mite.h` declares the NI MITE helper state, public helper prototypes, and register/bit definitions needed to map and program the MITE PCI bridge for NI GPIB boards.

## Important APIs, types, and functions
Primary types are `struct mite_dma_chain` and `struct mite_struct`. The header exposes `mite_devices`, inline helpers `mite_irq()` and `mite_device_id()`, and functions `mite_init()`, `mite_cleanup()`, `mite_setup()`, `mite_unsetup()`, and `mite_list_devices()`. It defines MITE DMA channel register offsets and bitfields such as `MITE_CHOR`, `MITE_CHCR`, `MITE_TCR`, `MITE_IODWBSR`, `WENAB`, and many DMA mode/control bits.

## Control flow
The header has no independent control flow. `tnt4882_gpib.c` calls the declared helpers to discover and activate PCI devices, then uses `mite_irq()` and `mite_device_id()` during board matching/IRQ setup.

## State and persistence behavior
`struct mite_struct` represents runtime PCI bridge state: linked-list membership, used flag, PCI device reference, BAR physical addresses, mapped MITE/DAQ I/O addresses, a near-end flag, and an in-memory DMA ring. There is no durable persistence.

## Dependencies and integration points
The header depends on Linux PCI types and bit macros. It is part of the TNT4882 driver module and bridges `mite.c` with `tnt4882_gpib.c`. The register constants mirror MITE hardware documentation and are suitable for later DMA support even though current GPIB code primarily uses window setup and IRQ/device ID helpers.

## Risks and edge cases
The header declares `mite_list_devices()` but `mite.c` in this subset does not define it, so any future caller would fail to link unless another translation unit supplies it. Many register bitfields are hardware ABI constants; incorrect values would misprogram DMA or address windows. `extern inline` helper style can be sensitive to compiler/kernel inline semantics.

## Test signals
Compile/link coverage for the declared helpers, PCI attach paths using `mite_irq()` and `mite_device_id()`, and any future DMA-channel programming tests using the register constants are the main signals.
