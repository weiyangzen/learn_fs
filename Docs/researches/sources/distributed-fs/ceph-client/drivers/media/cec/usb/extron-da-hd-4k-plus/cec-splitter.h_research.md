# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.h

## Purpose
This header defines the state and local API for Extron splitter CEC policy.

## Important APIs, Types, and Functions
`struct cec_splitter_port` stores adapter pointer, port number, active-source flag, sink detection, pending power/latency query sequence IDs and timestamps, video latency, and power status. `struct cec_splitter` stores device, output count, output port array, request destinations, and standby state. The declared functions handle output configuration, input/output received messages, canceled output transmits, and periodic polling.

## Control Flow
The Extron adapter callbacks call these functions when ports are configured/unconfigured, when CEC messages are received, when non-blocking transmits fail, and once per second from the setup thread.

## State and Persistence
All fields are volatile runtime policy state. `STATE_CHANGE_MAX_REPEATS` defines a repeat limit for state-change behavior, though this header’s constant is not used in the reviewed implementation.

## Dependencies and Integration Points
The header forward-declares the splitter and relies on CEC adapter types from including source files. It is private to the Extron module.

## Risks and Test Signals
State fields are updated from workqueue and polling contexts, so tests should verify synchronized access through the owning driver and adapter locks. Sequence IDs use the high bit as an internal marker, which should be preserved consistently.
