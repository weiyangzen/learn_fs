<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gpib.h

## Purpose
`gpib.h` declares common userspace constants for Linux GPIB devices, including board/descriptor limits, status bits, end-of-string modes, bus-line status encoding, parallel-poll bits, service-request bits, and event IDs.

## Important APIs, types, and functions
The ABI defines `GPIB_MAX_NUM_BOARDS`, `GPIB_MAX_NUM_DESCRIPTORS`, `enum ibsta_bit_numbers`, `enum ibsta_bits`, `enum eos_flags`, `enum bus_control_line`, `enum ppe_bits`, `request_service_bit`, and `enum gpib_events`. `device_status_mask` and `board_status_mask` capture legal status aggregation for device and board APIs.

## Control flow
No functions are defined. GPIB ioctl handlers and libraries update `ibsta`-style status words after read, write, wait, poll, controller, and event operations. Userspace tests bits such as `ERR`, `TIMO`, `END`, `CMPL`, and `RQS` after each operation.

## State and persistence behavior
State is transient bus status and per-board/per-device configuration. EOS and parallel-poll settings may persist for an open descriptor or board until changed, but the header stores no state.

## Dependencies and integration points
This header is paired with `gpib_ioctl.h` and integrates with IEEE-488/GPIB controller drivers and compatibility libraries that emulate NI-488 style status semantics.

## Risks and test signals
Risks include mixing board-only and device-only status bits, missing `ERR`/`TIMO` completion checks, misinterpreting valid-line masks, and EOS mode bit conflicts. Test signals include loopback or instrument tests for read/write completion, serial and parallel poll, SRQ handling, IFC/device-clear events, line-status reads, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib.h -->
