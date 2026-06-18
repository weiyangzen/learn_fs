# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_client.c

## Purpose

`amd_sfh_client.c` is the legacy AMD SFH HID client layer. It discovers MP2 sensors, allocates coherent sensor buffers and HID report buffers, starts sensors through `amd_mp2_ops`, creates synthetic HID devices, services HID get/set report requests, polls sensor input, and tears everything down on remove or suspend.

## Important APIs, Types, and Functions

`amd_sfh_hid_client_init()` is the main initialization path. `amd_sfh_hid_client_deinit()` stops sensors, cancels delayed work, and removes HID devices. `amd_sfh_get_report()` queues report requests in `amdtp_cl_data.req_list`; `amd_sfh_work()` fulfills the last queued feature/input request by calling descriptor callbacks and `hid_input_report()`. `amd_sfh_work_buffer()` periodically pushes input reports for enabled sensors. Static helpers include `amd_sfh_wait_for_response()`, `get_sensor_name()`, `amd_sfh_suspend()`, and `amd_sfh_resume()`.

## Control Flow

Initialization installs descriptor ops with `amd_sfh_set_desc_ops()`, assigns suspend/resume callbacks, asks `amd_mp2_get_sensor_num()` for active sensor IDs, allocates DMA and report buffers, starts each sensor, waits for status, and then probes a HID device for each enabled non-operating-mode sensor. Periodic delayed work reads input reports every `AMD_SFH_IDLE_LOOP` milliseconds. HID core report requests enter through `amd_sfh_get_report()` and are processed asynchronously by `amd_sfh_work()`.

## State and Persistence Behavior

Persistent per-device state lives in `amdtp_cl_data` and `amd_mp2_dev`: sensor IDs, DMA addresses, report descriptors, feature/input buffers, sensor status, request completion flags, and delayed work items. Request nodes are transient heap objects. The MP2 mutex guards report queue and buffer access. Device-managed allocations are freed by devres; explicit cleanup frees selected buffers on init failure and removes HID devices.

## Dependencies and Integration Points

This file depends on Linux DMA mapping, HID core, workqueues, lists, and the MP2 operation table from `amd_sfh_common.h`. It integrates with `amd_sfh_hid.c` for HID low-level device creation and wakeups, `amd_sfh_pcie.c` for start/stop/response callbacks, and `hid_descriptor/amd_sfh_hid_desc.c` for descriptors and report materialization.

## Risks and Test Signals

Risks include request-list assumptions (`list_last_entry()` requires a nonempty list), report-size zero paths, periodic work racing with suspend/remove if cancellation order changes, and sensor status handling that treats unsupported discovery as `-EOPNOTSUPP`. Test signals include successful sensor enumeration, HID sensor reports in userspace, suspend/resume without stale work, init failure cleanup with fault injection, and lockdep coverage around `mp2->lock`.
