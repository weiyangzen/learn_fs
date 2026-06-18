# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.h

## Purpose
`quickspi-hid.h` is the small declaration header for QuickSPI HID-core integration.

## Important APIs, types, and functions
It forward-declares `struct quickspi_device` and declares `quickspi_hid_send_report()`, `quickspi_hid_probe()`, and `quickspi_hid_remove()`.

## Control flow and integration points
There is no executable control flow. The PCI driver calls probe/remove, and protocol RX parsing calls `quickspi_hid_send_report()` for input data.

## State and persistence behavior
The header owns no state; implementation state is stored in `quickspi_device` and HID core objects.

## Dependencies
It intentionally depends only on the forward-declared QuickSPI device type.

## Risks and edge cases
Signature drift breaks PCI/protocol callers. The API does not encode report ownership or lifetime, so callers must pass valid buffers for the duration of `hid_input_report()`.

## Test signals
Build coverage and runtime HID probe/remove/input-report forwarding validate this header.
