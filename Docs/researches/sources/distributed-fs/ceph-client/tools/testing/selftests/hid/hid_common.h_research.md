# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_common.h

## Purpose
`hid_common.h` is the shared C harness for HID kselftests in this directory. It provides the synthetic HID report descriptor, UHID device creation/destruction, asynchronous UHID event processing, hidraw node discovery/opening, and common synchronization objects used by both `hidraw.c` and `hid_bpf.c`.

## Important APIs, types, and functions
`struct uhid_device` records the random physical id, UHID fd, kernel HID id, bus/vendor/product ids, and reader thread id. The global `rdesc` describes a vendor-defined HID device with two report IDs, input reports, output reports, and feature reports; `feature_data` supplies canned GET_REPORT replies. `setup_uhid()` creates `/dev/uhid`, emits `UHID_CREATE`, resolves the kernel HID id, and starts the listener. `uhid_send_event()` emits `UHID_INPUT2`. `open_hidraw()`, `get_hidraw()`, `get_hid_id()`, and `match_sysfs_device()` connect the synthetic device to sysfs and `/dev/hidrawN`.

## Control flow
UHID events are consumed by `uhid_read_events_thread()`, which polls the UHID fd until `UHID_STOP`. `uhid_event()` handles lifecycle notifications, captures output reports into `output_report`, replies to GET_REPORT using `feature_data`, and acknowledges SET_REPORT. `uhid_start_listener()` waits on `uhid_started` before tests proceed, ensuring the kernel has accepted the device.

## State and persistence
The file has process-global mutexes/condition variables for start and output synchronization, a process-global `output_report[10]`, and a `uhid_stopped` flag. These are test-process state only, but because they are global, fixtures rely on serialized harness behavior and careful teardown.

## Dependencies and integration points
It includes Linux `uhid.h`, `hidraw.h`, pthreads, poll, sysfs, and kselftest harness headers. It is the contract layer beneath all C HID tests in the subset and exposes shared descriptor data used by ioctl assertions.

## Risks and test signals
Key risks are sysfs race windows, random `dev_id` collisions, short retry loops under heavy load, and condition-variable misuse if UHID events are delayed. Positive signals include successful UHID start, stable HID id discovery, output report notification, and correct GET/SET report replies.
