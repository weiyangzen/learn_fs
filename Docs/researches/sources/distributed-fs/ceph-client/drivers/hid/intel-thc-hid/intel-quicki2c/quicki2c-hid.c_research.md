# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.c

## Purpose
`quicki2c-hid.c` adapts QuickI2C protocol operations to the HID core's low-level driver interface. It registers a `hid_device`, parses the cached report descriptor, handles HID raw GET/SET/output report requests, and forwards received input reports to HID core.

## Important APIs, types, and functions
The HID callbacks are `quicki2c_hid_parse()`, `quicki2c_hid_start()`, `quicki2c_hid_stop()`, `quicki2c_hid_open()`, `quicki2c_hid_close()`, `quicki2c_hid_raw_request()`, `quicki2c_hid_power()`, and `quicki2c_hid_output_report()`. Public functions are `quicki2c_hid_probe()`, `quicki2c_hid_remove()`, and `quicki2c_hid_send_report()`.

## Control flow and integration points
Probe allocates a HID device, assigns the low-level driver, sets bus to `BUS_PCI`, fills version/vendor/product from the HIDI2C descriptor, sets name/phys, and calls `hid_add_device()`. Raw requests resume runtime PM, dispatch GET/SET to `quicki2c_get_report()` or `quicki2c_set_report()`, then autosuspend. Output reports call `quicki2c_output_report()`. RX data from the PCI IRQ path enters HID core through `hid_input_report()`.

## State and persistence behavior
The HID device pointer is stored in `qcdev->hid_dev` until removal. The file owns no persistent storage beyond HID core registration. Runtime PM references are transient around raw requests.

## Dependencies
It depends on Linux HID/input, PM runtime, `quicki2c_device`, and protocol helpers in `quicki2c-protocol.c`.

## Risks and edge cases
Callbacks are mostly stubs, so open/close do not gate hardware activity. Unsupported raw request types log an error but return the initial zero `ret`, which can look like success. `quicki2c_hid_send_report()` assumes `hid_dev` is valid and registered. Descriptor parsing fails if the report descriptor was not fetched before HID probe.

## Test signals
HID registration/removal, report descriptor parse failure, GET/SET feature and input raw requests, output report writes, runtime PM error propagation, unsupported request type handling, and injected HID input reports from IRQ context are useful tests.
