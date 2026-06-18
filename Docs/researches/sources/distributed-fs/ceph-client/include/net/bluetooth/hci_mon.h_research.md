# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_mon.h

## Purpose

`hci_mon.h` defines the Bluetooth HCI monitor record header and monitor opcode payloads used by the kernel monitor channel and tools such as `btmon`.

## Important APIs, Types, and Functions

`struct hci_mon_hdr` is a packed 6-byte header containing opcode, controller index, and payload length. Monitor opcodes cover controller index lifecycle, command/event packets, ACL/SCO/ISO TX/RX, open/close, index info, vendor diagnostics, system notes, user logging, control channel traffic, and HCI driver TX/RX. `struct hci_mon_new_index` carries controller type, bus, address, and short name; `struct hci_mon_index_info` carries address and manufacturer.

## Control Flow

HCI core emits monitor records when controllers appear/disappear, sockets open/close, commands/events/data pass through HCI, and diagnostic/control/user logging records are generated. Consumers parse `hci_mon_hdr` then dispatch by opcode to the corresponding fixed or packet payload.

## State and Persistence Behavior

No persistent state is stored here. Monitor packets are transient observations of HCI activity.

## Dependencies and Integration Points

The header depends on Bluetooth address types and endian annotations. It integrates with HCI monitor sockets, control sockets, driver diagnostic packet paths, and userspace tracing tools.

## Risks and Edge Cases

Payload length must be validated against the monitor opcode before parsing. The name field is marked `__nonstring`, so consumers must not assume NUL termination. New opcodes require userspace tooling updates.

## Test Signals

Validate monitor header sizes, new/delete index records, packet direction opcodes for ACL/SCO/ISO/driver traffic, control channel open/close/command/event records, non-NUL names, and malformed short monitor frames.
