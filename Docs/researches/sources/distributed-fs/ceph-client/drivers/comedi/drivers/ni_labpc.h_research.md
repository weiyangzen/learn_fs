# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.h

## Purpose
`ni_labpc.h` is the shared interface for ISA, PCI, PCMCIA, common, and ISA-DMA Lab-PC driver pieces. It defines board capabilities, private runtime state, transfer modes, and the common attach/detach entry points.

## Important APIs, Types, And Functions
`enum transfer_type` distinguishes FIFO-not-empty, FIFO-half-full, and ISA-DMA acquisition transfers. `struct labpc_boardinfo` describes board name, maximum AI speed in nanoseconds, scan-up support, AO presence, and Lab-PC-1200 register availability. `struct labpc_private` stores optional ISA DMA, an 8254 counter helper, remaining sample count, command-register shadows `cmd1` through `cmd6`, last status-register reads, current transfer mode, and function pointers for byte access. The exported declarations are `labpc_common_attach()` and `labpc_common_detach()`.

## Control Flow
Bus-specific files populate `dev->board_ptr` with a `struct labpc_boardinfo`, establish either `dev->iobase` or `dev->mmio`, and call `labpc_common_attach()`. Common code fills `struct labpc_private`, installs I/O or MMIO byte-access callbacks, creates subdevices, and uses the shared fields during commands, interrupts, calibration, and EEPROM operations.

## State And Persistence
The header defines the state contract but does not allocate state. The command-register shadows persist across operations to prevent unrelated bitfields from being lost during DIO/AO/AI changes. The read/write function pointers persist for the attachment lifetime and abstract ISA/PCMCIA port I/O from PCI MMIO.

## Dependencies And Integration Points
The types reference `struct comedi_isadma`, `struct comedi_8254`, and Comedi device/subdevice types. It is included by `ni_labpc.c`, `ni_labpc_common.c`, `ni_labpc_cs.c`, `ni_labpc_isadma.c`, and `ni_labpc_pci.c`.

## Risks
Because this header is the ABI between split compilation units, any field layout or semantic change must be coordinated across common and bus-specific drivers. The access function pointers must be initialized before any register helper is used. Command-register shadows can become inconsistent if a code path writes hardware directly without updating the corresponding shadow.

## Test Signals
Test signals are compile/link level: every bus wrapper should build against the declarations, Kconfig combinations with and without ISA DMA should compile, `labpc_private` fields should be initialized before use in common attach, and static analysis should verify no direct command-register writes bypass the intended shadows.
