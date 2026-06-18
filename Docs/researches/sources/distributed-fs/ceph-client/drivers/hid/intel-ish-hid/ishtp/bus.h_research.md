<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.h

## Purpose
`ishtp/bus.h` declares the private/public ISHTP bus interfaces used by the transport core and ISHTP client drivers. It defines `struct ishtp_cl_device` and prototypes for message send, client enumeration, RX events, reset handling, and helper accessors.

## Important APIs, Types, and Functions
`struct ishtp_cl_device` embeds a Linux `device`, points to the owning `ishtp_device` and `ishtp_fw_client`, links into the device list, stores event work, driver data, manual reference count, and an event callback. Prototypes include `ishtp_bus_new_client`, `ishtp_cl_device_bind`, `ishtp_cl_bus_rx_event`, `ishtp_send_msg`, `ishtp_write_message`, `ishtp_use_dma_transfer`, `ishtp_bus_remove_all_clients`, `ishtp_recv`, `ishtp_reset_handler`, `ishtp_reset_compl_handler`, and `ishtp_fw_cl_by_uuid`.

## Control Flow
The header has no executable flow. HBM code calls `ishtp_bus_new_client` when firmware clients are discovered. Transport IRQ code calls `ishtp_recv`. Client code sends through `ishtp_send_msg`/`ishtp_write_message` indirectly or directly and uses RX event callbacks scheduled by `ishtp_cl_bus_rx_event`.

## State and Persistence Behavior
The structure defines device lifetime and callback state for bus clients. Event work and driver data persist until device removal or reset cleanup.

## Dependencies and Integration Points
It depends on Linux device/model headers and `intel-ish-client-if.h`. It is included by bus implementation, IPC glue, and ISHTP clients that need bus helper APIs.

## Risks and Edge Cases
The manual reference count field requires disciplined get/put usage and does not itself enforce lifetime safety. Event callbacks can be cleared during reset/remove, so users must tolerate missing callbacks. Header prototypes must remain synchronized with exported symbols in `bus.c`.

## Test Signals
Build all ISHTP clients, verify reset/remove callback paths, RX event delivery, message send prototypes, and correct parent/firmware-client pointers during client binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.h -->
