# sources/distributed-fs/ceph-client/include/linux/hid_bpf.h

## Purpose
`hid_bpf.h` defines the HID-BPF interface that lets BPF programs inspect or alter HID report descriptors, incoming device events, raw feature/input/output requests, and output reports. It also defines HID core internal dispatch hooks and per-device BPF state.

## Important APIs, Types, And Functions
`struct hid_bpf_ctx` is the user-facing BPF context with `hid`, `allocated_size`, and mutable `size`/`retval`. `struct hid_ops` exposes HID core callbacks to BPF internals. `struct hid_bpf_ops` is a BPF struct_ops callback table with `hid_device_event`, `hid_rdesc_fixup`, `hid_hw_request`, and `hid_hw_output_report`. `struct hid_bpf` stores device data, attached programs, locks, SRCU, descriptor fixup ops, and destruction state. Under `CONFIG_HID_BPF`, dispatch and lifecycle functions are declared; otherwise inline stubs return pass-through success or original data.

## Control Flow And State
When enabled, HID core initializes device BPF state, connects attached operations by HID ID, optionally replaces report descriptors through `hid_rdesc_fixup`, dispatches incoming reports through device-event programs, and intercepts raw/output report calls. Program execution can continue, modify buffer size, or abort with an error. Per-device state persists in `hid_device.bpf`, including dynamically allocated data buffers, program lists protected by mutex for updates and SRCU for reads, and a `destroyed` flag that prevents new assignment during teardown.

## Dependencies And Integration Points
The header depends on BPF, mutex, SRCU, and uapi HID definitions. It is included from `hid.h`, and its dispatch functions sit on HID core input and request/output paths. It also identifies request sources such as kernel or hidraw file pointers.

## Risks
Risks include breaking user-facing BPF ABI, buffer size enforcement bugs, recursion when BPF-originated requests reenter HID paths, SRCU lifetime mistakes, descriptor fixup memory ownership, and mismatch between `allocated_size` and changed `size`. The comments warn that the user-facing portion must be edited carefully because out-of-tree BPF programs can depend on it.

## Test Signals
Run HID-BPF selftests for descriptor fixup, event rewrite/drop, raw request interception, output report interception, attach/detach during device removal, multiple programs and `BPF_F_BEFORE` ordering, disabled-config stubs, and boundary sizes including the 4 KiB descriptor fixup buffer.
