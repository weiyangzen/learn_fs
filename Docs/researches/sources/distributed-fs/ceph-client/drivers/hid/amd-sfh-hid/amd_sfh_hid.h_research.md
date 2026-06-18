# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_hid.h

## Purpose

`amd_sfh_hid.h` defines the shared HID-client data structures and function prototypes used by the AMD SFH client and HID low-level driver.

## Important APIs, Types, and Functions

`MAX_HID_DEVICES` caps the sensor HID array at seven. `AMD_SFH_HID_VENDOR` and `AMD_SFH_HID_PRODUCT` identify synthetic HID devices. `struct request_list` represents a queued report request. `struct amd_input_data` stores DMA-visible sensor buffers and generated input report buffers. `struct amdtp_cl_data` is the central HID client state with descriptor/report arrays, HID devices, sensor status, request state, delayed work, and the request list. `struct amdtp_hid_data` is per-HID-device private data. Prototypes expose `amdtp_hid_probe()`, `amdtp_hid_remove()`, `amd_sfh_get_report()`, `amd_sfh_set_report()`, and `amdtp_hid_wakeup()`.

## Control Flow

The header establishes a two-way API: the client calls HID probe/remove and wakeup helpers, while the HID low-level driver calls client report handlers.

## State and Persistence Behavior

Arrays in `amdtp_cl_data` persist for the PCI device lifetime and are indexed by client enumeration order, not always by raw sensor ID. Request flags and `cur_hid_dev` are mutable synchronization state used by HID wait paths.

## Dependencies and Integration Points

It depends on HID device types, workqueues, waitqueues, and local MP2 code that embeds `amd_input_data` inside `amd_mp2_dev`.

## Risks and Test Signals

The fixed `MAX_HID_DEVICES` must cover all enumerated sensors; sensor additions can overflow expectations if discovery changes. Tests should cover all supported sensor combinations, request queue processing, and sensor-index/current-index mapping.
