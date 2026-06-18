<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid-client.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid-client.c

## Purpose
`ishtp-hid-client.c` implements the ISHTP client driver for HID-over-ISH. It connects to the ISH HID firmware GUID, enumerates firmware-published HID devices, fetches HID and report descriptors, registers each with hid-core, sends feature/input requests, and routes published reports back to the right HID device.

## Important APIs, Types, and Functions
The driver binds `hid_ishtp_id_table` and uses ring sizes 32 RX / 16 TX. RX parsing is centralized in `process_recv`, with diagnostics in `report_bad_packet`. HID request helpers exported to `ishtp-hid.c` are `hid_ishtp_set_feature`, `hid_ishtp_get_report`, and `ishtp_hid_link_ready_wait`. Initialization helpers are `ishtp_enum_enum_devices`, `ishtp_get_hid_descriptor`, `ishtp_get_report_descriptor`, and `hid_ishtp_cl_init`. Lifecycle functions include probe, remove, reset, suspend, resume, and workqueue handlers.

## Control Flow
Probe allocates client state and ISHTP client, links them through driver data, initializes waitqueues/work, obtains the trace callback, and calls `hid_ishtp_cl_init`. Init establishes an ISHTP connection to the HID GUID, registers RX callback, sends ENUM_DEVICES with retries, then for each enumerated device requests HID descriptor and report descriptor. On first initialization it calls `ishtp_hid_probe` to allocate and register hid-core devices; on reset it refreshes transport/descriptors without re-adding HID devices.

RX processing accepts one or more hostif messages in a buffer. Enumeration and descriptor responses are only accepted before init completes. GET report responses either copy into a raw request buffer or call `hid_input_report`, then wake waiters. SET feature responses wake waiters. Published input reports are routed directly to matching `hid_sensor_hubs`; aggregated report lists iterate embedded reports. Malformed packets increment `bad_recv_cnt`, log details, and trigger `ish_hw_reset`.

## State and Persistence Behavior
`struct ishtp_cl_data` persists per ISHTP HID client and stores descriptor arrays, device info, hid_device pointers, init flags, suspend state, counters, waitqueues, and work. Descriptors are devm-managed against the ISHTP client device. `suspended` blocks HID requests through `ishtp_hid_link_ready_wait` until resume work clears it. Reset work destroys/re-establishes the connection and retries init up to three times.

## Dependencies and Integration Points
The file depends on ISHTP client APIs, the hostif protocol structs in `ishtp-hid.h`, hid-core registration through `ishtp_hid_probe`, ISH hardware reset, and the ISHTP bus workqueue. It is the main bridge between firmware sensor hub protocol and Linux HID devices.

## Risks and Edge Cases
Packet parsing is defensive but complex; aggregated report pointer arithmetic (`report += sizeof(*report) + payload_len`) relies on compiler pointer scaling and is suspicious because `report` is a `struct report *`, not a byte pointer. `MAX_HID_DEVICES` bounds static arrays, but enumeration count from firmware is assigned directly and allocation uses firmware count; counts above 32 risk array overrun in later descriptor/HID arrays. Reset on malformed packet is disruptive but intended for recovery. Raw request state assumes one outstanding request per HID device.

## Test Signals
Test firmware enumeration, descriptor fetch timeouts, multiple HID devices, raw GET/SET feature reports, asynchronous input reports, aggregated report lists, suspend/resume request blocking, reset recovery, bad packet injection, and bounds behavior for zero or excessive device counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid-client.c -->
