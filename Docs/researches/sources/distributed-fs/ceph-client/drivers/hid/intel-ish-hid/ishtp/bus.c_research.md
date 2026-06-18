<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.c

## Purpose
`ishtp/bus.c` implements the Linux bus layer for ISHTP firmware clients. It dispatches received ISHTP messages, sends ISHTP frames through hardware ops, creates `ishtp` bus devices for firmware-advertised clients, registers/unregisters client drivers, schedules RX callbacks, handles reset removal/rebind, and exposes helper APIs to client drivers.

## Important APIs, Types, and Functions
Message functions include `ishtp_recv`, `ishtp_send_msg`, and `ishtp_write_message`. Firmware lookup helpers include `ishtp_fw_cl_by_uuid`, `ishtp_fw_cl_get_client`, `ishtp_get_fw_client_id`, and `ishtp_fw_cl_by_id`. Bus callbacks are `ishtp_cl_device_probe`, match, remove, suspend, resume, reset, uevent, and modalias. Device helpers include `ishtp_bus_add_device`, `ishtp_bus_new_client`, `ishtp_cl_device_bind`, `ishtp_bus_remove_all_clients`, `ishtp_register_event_cb`, get/put drvdata, `ishtp_device`, `ishtp_get_pci_device`, `ishtp_get_workqueue`, `ishtp_trace_callback`, and `ish_hw_reset`.

## Control Flow
`ishtp_recv` reads the ISHTP header from hardware, rate-syncs firmware clock, validates fragment length against MTU, then dispatches HBM, fixed-client, or normal client messages. Sending wraps an ISHTP header and payload with an IPC doorbell header produced by hardware ops and queues it to the IPC layer.

When HBM discovers a new firmware client, `ishtp_bus_new_client` builds a GUID-based name and calls `ishtp_bus_add_device`. Existing names are treated as reset/rebind cases: the firmware client pointer is refreshed and the client driver reset callback is invoked. New devices are registered on the `ishtp` bus and matched against driver GUID tables. RX events queue work on the ISHTP unbound workqueue and invoke the registered event callback. Reset handling marks the device resetting, clears bottom-half queues, removes or disconnects clients, frees DMA/client arrays, and reset completion restarts HBM discovery.

## State and Persistence Behavior
`ishtp_device_ready` gates late client-driver registration until the bus has at least one device. Each `ishtp_cl_device` stores parent device, firmware client pointer, list link, event work, driver data, manual reference count, and callback. Device lists and client lists are protected by spinlocks. Firmware client arrays are freed and rebuilt across reset.

## Dependencies and Integration Points
The file depends on the Linux driver model, module/bus APIs, ISHTP device/client internals, HBM helpers, and hardware ops from IPC. HID and firmware-loader clients register through `ishtp_cl_driver_register` and receive probe/reset/remove callbacks from this bus.

## Risks and Edge Cases
The manual `reference_count` is not a kref and is manipulated without locking in helpers, so reset/remove races need care. `ishtp_cl_driver_register` returns `-ENODEV` until `ishtp_device_ready`, which can affect module load ordering. Warm reset preserves referenced devices but clears firmware pointers, so client reset code must re-establish connections. Device naming by GUID assumes uniqueness.

## Test Signals
Validate HBM enumeration, uevent/modalias generation, driver autoload/probe, RX event callback scheduling, reset rebind of existing devices, client removal on cold remove, suspend/resume callback propagation, DMA module parameter behavior, and no use-after-free under reset storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.c -->
