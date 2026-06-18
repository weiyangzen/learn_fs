<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.c

## Purpose
`ishtp-hid.c` is the hid-core low-level driver glue for HID devices exposed through the ISHTP HID client. It parses firmware-provided report descriptors, translates hid-core GET/SET report calls into ISH hostif messages, waits for responses, and allocates/removes `hid_device` instances.

## Important APIs, Types, and Functions
The `ishtp_hid_ll_driver` implements parse, start, stop, open, close, request, wait, and raw_request callbacks. `ishtp_hid_parse` calls `hid_parse_report` on the descriptor stored by the client. `ishtp_raw_request` handles userspace-style raw GET/SET reports. `ishtp_hid_request` handles hid-core report requests. `ishtp_wait_for_response` waits for completion. `ishtp_hid_probe`, `ishtp_hid_remove`, and `ishtp_hid_wakeup` are called by `ishtp-hid-client.c`.

## Control Flow
Client initialization calls `ishtp_hid_probe` for each enumerated firmware HID device. Probe allocates a hid device and `ishtp_hid_data`, initializes a waitqueue, stores the device in the client array, fills bus/vendor/product/name fields, assigns the low-level driver, and calls `hid_add_device`. Parse occurs during HID addition and consumes the matching report descriptor.

For GET requests, raw or structured callbacks set request state, optionally provide a raw receive buffer, call `hid_ishtp_get_report`, and rely on `hid_hw_wait`/`.wait` to block until `ishtp_hid_wakeup` marks completion. SET requests allocate a hostif-header-prefixed buffer, encode the HID output report when needed, call `hid_ishtp_set_feature`, and free the temporary buffer.

## State and Persistence Behavior
Per-HID state in `struct ishtp_hid_data` stores enumeration index, request completion flag, client backpointer, waitqueue, and raw request buffer metadata. It persists until `ishtp_hid_remove`, which destroys each HID device and frees its private data. Request completion is a boolean synchronized by waitqueues, so callers assume one active request per HID device.

## Dependencies and Integration Points
The file depends on hid-core, `intel-ish-client-if.h`, hostif definitions in `ishtp-hid.h`, and request send/wakeup helpers from `ishtp-hid-client.c`. It exposes devices on `BUS_INTEL_ISHTP`.

## Risks and Edge Cases
`ishtp_raw_request` returns `len` after `hid_hw_wait` even if the wait path times out internally, so error propagation for raw requests is limited. SET report send is asynchronous and the temporary buffer is freed immediately after `hid_ishtp_set_feature` returns; this relies on lower layers copying the buffer synchronously. The trace macro uses a `client_data` token in this file without a local variable in some functions, which depends on macro behavior and should be build-checked carefully.

## Test Signals
Exercise HID descriptor parsing, hidraw GET/SET feature paths, normal HID request/wait paths, timeout behavior when firmware does not respond, multiple registered HID devices, removal cleanup, and build warnings around trace macro use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.c -->
