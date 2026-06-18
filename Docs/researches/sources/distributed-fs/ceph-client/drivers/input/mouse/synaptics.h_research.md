<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.h

## Purpose
`synaptics.h` defines the protocol constants, capability-bit helpers, packet types, and private data structures shared by the Synaptics PS/2 implementation and the psmouse core.

## Important APIs, Types, and Functions
The header exports query command IDs such as `SYN_QUE_IDENTIFY`, mode bits such as `SYN_BIT_ABSOLUTE_MODE`, model/capability extraction macros, and special command IDs used by PS/2 sliced commands. `enum synaptics_pkt_type` identifies oldabs/newabs validation modes. `struct synaptics_hw_state` is the decoded packet representation, `struct synaptics_device_info` is the queried hardware descriptor, and `struct synaptics_data` is the per-device runtime state. Function prototypes expose detection, initialization, SMBus initialization, module init, and reset.

## Control Flow
The header itself has no execution path, but it encodes the contract used by `synaptics.c`: queries populate `struct synaptics_device_info`, device mode is built from `SYN_BIT_*` flags, packets are decoded to `struct synaptics_hw_state`, and initialization returns one of the psmouse protocol selections.

## State and Persistence
The structs describe volatile kernel runtime state only. `struct synaptics_data` persists while the `psmouse` binding is active and holds pass-through state, advanced gesture last-contact state, and ForcePad timing state.

## Dependencies and Integration Points
The declarations assume Linux kernel bit macros such as `BIT()` and `GENMASK()`, psmouse types, and serio pointers. The header is included by the PS/2 Synaptics implementation and referenced by the psmouse protocol dispatch layer.

## Risks and Edge Cases
The macros encode hardware ABI details; incorrect bit interpretation changes user-visible capabilities and packet decoding. Some comments document ambiguous firmware meanings, especially extended query 0x0c/0x10 fields, so downstream code must treat those fields conservatively.

## Test Signals
Compile coverage is the primary signal for this header. Runtime validation comes from matching reported device properties, capability flags, and input event capabilities against known Synaptics hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics.h -->
