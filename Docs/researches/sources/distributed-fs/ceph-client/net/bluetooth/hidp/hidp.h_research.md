# sources/distributed-fs/ceph-client/net/bluetooth/hidp/hidp.h

## Purpose
Defines the internal and userspace ABI surface for the Bluetooth HIDP implementation: protocol constants, ioctl numbers, request/response structures, session state, `struct hidp_session`, and cross-file function prototypes.

## APIs, Types, and Functions
Protocol definitions include HIDP header masks, transaction types (`HIDP_TRANS_*`), handshake result codes, HID control operation codes, data report type bits, and boot/report protocol constants. Ioctl numbers are `HIDPCONNADD`, `HIDPCONNDEL`, `HIDPGETCONNLIST`, and `HIDPGETCONNINFO`.

Userspace ABI structs are `struct hidp_connadd_req`, `struct hidp_conndel_req`, `struct hidp_conninfo`, and `struct hidp_connlist_req`. Internal state uses `enum hidp_session_state` and `struct hidp_session`, which stores list/refcounting, thread and termination state, L2CAP user/connection, sockets, transmit queues, MTUs, device pointers, report descriptor, keyboard/LED state, raw-report wait state, and a temporary input buffer. Prototypes expose connection management to `sock.c` and socket init/cleanup to `core.c`.

## Control Flow, State, and Persistence
The header itself has no runtime control flow, but it defines the persistent per-session shape used by `core.c`. `HIDP_SESSION_IDLING`, `HIDP_SESSION_PREPARING`, and `HIDP_SESSION_RUNNING` gate startup and asynchronous device registration. Flag bits record user-visible options (`HIDP_VIRTUAL_CABLE_UNPLUG`, `HIDP_BOOT_PROTOCOL_MODE`, `HIDP_BLUETOOTH_VENDOR_ID`) and internal report waits (`HIDP_WAITING_FOR_RETURN`, `HIDP_WAITING_FOR_SEND_ACK`).

## Dependencies and Integration
Depends on kernel type definitions, HID core, kref, Bluetooth core, and L2CAP. It is included by both `core.c` and `sock.c`, and its ioctl structs form the compatibility contract with legacy HIDP userspace tools.

## Risks and Test Signals
Risks include ABI layout stability, pointer-size differences handled separately by compat ioctl code, fixed 128-byte names, user pointer lifetime for report descriptors during add, and the misspelled `HIDP_DATA_RTYPE_OUPUT` constant being part of the source API spelling used throughout the implementation. Test signals include 32-bit compat ioctl coverage, structure size/layout checks for userspace tools, flag validation, and raw report paths for numbered and unnumbered reports.
