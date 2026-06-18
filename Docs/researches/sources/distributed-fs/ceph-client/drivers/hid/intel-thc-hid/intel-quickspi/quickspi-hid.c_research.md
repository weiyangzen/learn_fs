# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.c

## Purpose
`quickspi-hid.c` connects QuickSPI HIDSPI protocol handling to the HID core. It registers a `hid_device`, parses the cached HIDSPI report descriptor, forwards HID raw GET/SET requests to QuickSPI protocol functions, and injects input reports received from the hardware path.

## Important APIs, types, and functions
The low-level HID callbacks are `quickspi_hid_parse()`, `quickspi_hid_start()`, `quickspi_hid_stop()`, `quickspi_hid_open()`, `quickspi_hid_close()`, `quickspi_hid_raw_request()`, and `quickspi_hid_power()`. Public functions are `quickspi_hid_probe()`, `quickspi_hid_remove()`, and `quickspi_hid_send_report()`.

## Control flow and integration points
Probe allocates a HID device, assigns the low-level driver, sets PCI bus/parent/driver_data, fills version/vendor/product/name/phys from the HIDSPI device descriptor, and calls `hid_add_device()`. Raw requests resume runtime PM, dispatch GET/SET through `quickspi_get_report()`/`quickspi_set_report()`, then autosuspend. RX data parsed by `quickspi_handle_input_data()` is sent into HID core by `hid_input_report()`.

## State and persistence behavior
The HID device pointer is stored in `qsdev->hid_dev` until removal. This file does not persist data. Runtime PM references are scoped to raw requests.

## Dependencies
It depends on Linux HID/input, PM runtime, `quickspi_device`, and QuickSPI protocol declarations.

## Risks and edge cases
Open/close/power callbacks are stubs, so they do not control hardware data flow. Unsupported raw request types log once but return zero, which may mask caller misuse. `quickspi_get_report()` returns the cached `qsdev->report_len`, so HID callers rely on protocol parsing to keep that length valid. `quickspi_hid_send_report()` assumes a registered HID device.

## Test signals
HID descriptor parse, HID add/remove, GET/SET report raw requests, unsupported request type behavior, runtime PM failures, RX input injection, and removal while reports are pending are useful signals.
