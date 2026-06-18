# sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.c

## Purpose
`mite.c` is a small helper for NI MITE PCI interface chips used by NI PCI GPIB boards. It discovers National Instruments PCI devices, stores them in a global list, enables selected devices, maps the MITE and DAQ BARs, programs the I/O device window, and tears mappings/devices down.

## Important APIs, types, and functions
The global list head is `struct mite_struct *mite_devices`. Public functions are `mite_init()`, `mite_setup()`, `mite_unsetup()`, and `mite_cleanup()`. `mite_setup()` enables the PCI device, sets bus mastering, requests regions, maps BAR0 as MITE registers and BAR1 as DAQ/GPIB registers, writes `MITE_IODWBSR`, and marks the entry used.

## Control flow
At TNT4882 module init, `mite_init()` walks all PCI devices with vendor `PCI_VENDOR_ID_NATINST`, allocates a `mite_struct` for each, takes a device reference, and pushes it onto `mite_devices`. `ni_pci_attach()` later selects an unused matching entry and calls `mite_setup()`. Detach calls `mite_unsetup()` to unmap BARs, release PCI regions, disable the device, and clear `used`. Module exit calls `mite_cleanup()` to drop PCI references and free list nodes.

## State and persistence behavior
Runtime state is the global linked list of `struct mite_struct`, each holding PCI identity, mapped register bases, physical BAR addresses, a used flag, and a preallocated DMA-chain array. No persistent state exists, and the DMA-chain array is not actively configured by this file.

## Dependencies and integration points
The file depends on PCI core, I/O remapping, region management, and MITE register constants from `mite.h`. It integrates only with `tnt4882_gpib.c`, which consumes the global list and mapped `daq_io_addr` for TNT4882 register access.

## Risks and edge cases
`mite_setup()` has partial-failure cleanup gaps: if requesting regions or the second `ioremap()` fails after earlier resources were acquired, the caller must be careful because this function does not unwind all prior steps before returning. `mite_init()` lists all NI vendor devices and leaves board-type filtering to `ni_pci_attach()`. The global list is not locked, so it assumes module-level attach/remove serialization through the GPIB path.

## Test signals
PCI enumeration with multiple NI devices, attach selection by bus/slot, setup/unsetup resource accounting, BAR mapping failure injection, repeated attach/detach, and module unload reference cleanup are the most relevant signals.
