<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adb.h -->
# sources/distributed-fs/ceph-client/include/linux/adb.h

## Purpose
`adb.h` declares the kernel Apple Desktop Bus interface for low-level ADB drivers and clients.

## Important APIs, types, and functions
`struct adb_request` carries command data, replies, flags, completion callback, argument, and queue linkage. `struct adb_ids` stores discovered device IDs. `struct adb_driver` defines low-level bus operations: probe, init, request send, autopoll, poll, and reset. Request flags are `ADBREQ_REPLY`, `ADBREQ_SYNC`, and `ADBREQ_NOSEND`. `enum adb_message` describes notifier events, and `adb_client_list` is the blocking notifier head. APIs include request, register/unregister handler, poll, input, reset, handler-change, and info lookup.

## Control flow
Clients build `adb_request` objects and submit them through the active low-level driver. Completion is callback-driven or synchronous based on flags. Bus reset notifications let clients reinitialize after topology changes.

## State and persistence behavior
ADB bus/device/handler state is global to the subsystem. Requests carry mutable completion/reply state until finished.

## Dependencies and integration points
The header includes UAPI ADB definitions and integrates legacy Apple input/power devices, notifier chains, and architecture-specific ADB controllers.

## Risks and test signals
Risks include request lifetime bugs, reply buffer length mistakes, notifier misuse during reset/powerdown, and handler ID conflicts. Test signals include ADB probe/register, sync and async request completion, reset notification ordering, autopoll behavior, and handler-change validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adb.h -->
