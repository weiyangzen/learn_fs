# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-dev.h

## Purpose
`quickspi-dev.h` defines QuickSPI PCI IDs, ACPI DSM function numbers, packet-size defaults, runtime-PM defaults, state enum, platform data, and the main `struct quickspi_device` used by the PCI, protocol, and HID layers.

## Important APIs, types, and functions
Constants enumerate MTL/LNL/PTL/WCL/ARL/NVL SPI port IDs, HIDSPI DSM functions for report addresses/opcodes/IO mode, QuickSPI DSM functions for speed/packet/performance limits, platform DSM LTR functions, IO mode/performance bitfields, and packet-size limits. `enum quickspi_dev_state` describes lifecycle states. `struct quickspi_driver_data` supplies per-platform max packet size. `struct quickspi_device` stores device pointers, THC context, descriptor, SPI addresses/opcodes/modes, packet/performance parameters, LTR values, buffers, report length, and waitqueue completion flags.

## Control flow and integration points
The header has no executable control flow. `pci-quickspi.c` fills ACPI and hardware fields, `quickspi-protocol.c` consumes descriptor/buffer/waitqueue state, and `quickspi-hid.c` registers and uses `hid_dev`.

## State and persistence behavior
It defines volatile per-device runtime state. Completion flags represent one outstanding reset, non-DMA interrupt, report descriptor, GET report, or SET report operation. No persistent storage is defined.

## Dependencies
It includes Linux bit helpers, HID-over-SPI definitions, sizes/waitqueue APIs, and `quickspi-protocol.h`. It forward-declares PCI, ACPI, THC, HID, and generic device types.

## Risks and edge cases
The header includes `quickspi-protocol.h`, which also forward-declares this device type; include ordering should remain acyclic. Single boolean completion flags can be lost if multiple same-type operations overlap. PCI ID constants must stay aligned with the match table. Buffer sizes depend on descriptor fields provided by the device.

## Test signals
Build coverage, platform data selection by PCI ID, ACPI field population, waitqueue/completion behavior under repeated raw requests, and PM tests using stored LTR/SPI config are the main signals.
