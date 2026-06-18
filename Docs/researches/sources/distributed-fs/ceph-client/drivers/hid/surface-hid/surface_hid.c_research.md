# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid.c

Purpose: generic Surface Aggregator Module HID transport for HID target category devices on newer Surface systems.

Important APIs/types: `struct surface_hid_buffer_slice` defines chunked descriptor transfer payloads. SSAM command IDs cover output report, get/set feature report, and descriptor retrieval. Probe fills `struct surface_hid_device` ops and notifier before calling `surface_hid_device_add()`.

Control flow: descriptor reads loop over 128-byte SSAM payload slices until the device marks `end` or expected length is reached. Raw report operations translate HID output/feature operations into SSAM synchronous requests. Event notifier accepts command `0x00` and forwards event data to `hid_input_report()`.

State and persistence: per-device SSAM UID, controller, notifier, and ops are stored in the shared core object. No persistent storage beyond the HID device lifetime.

Dependencies and integration: depends on SSAM controller/device APIs and the shared Surface HID core. It registers as an `ssam_device_driver` for HID category devices and uses `surface_hid_pm_ops`.

Risks: descriptor slice parsing must reject bogus length/offset to avoid buffer misuse; report set mutates `buf[0]` to the report ID. Event filtering is command-id-only because SSAM registry matching carries the device identity.

Test signals: descriptor length/type validation in core, input event delivery from SSAM, output and feature report requests, async probe, hot remove, and PM suspend/resume.
