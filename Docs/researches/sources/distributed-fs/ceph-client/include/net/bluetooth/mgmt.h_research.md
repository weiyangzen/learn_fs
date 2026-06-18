# sources/distributed-fs/ceph-client/include/net/bluetooth/mgmt.h

## Purpose
This header is the kernel/userspace Bluetooth management protocol contract used by BlueZ management sockets. It defines the common management packet header, status codes, controller indices, command opcodes, event opcodes, packed command parameter and response records, fixed payload size constants, and feature/setting bit masks. It is ABI-like: layout, endian annotations, packing, and flexible-array tails must stay stable because implementation code in `net/bluetooth/mgmt.c` and management clients serialize these records directly.

## Important APIs, Types, And Constants
- `struct mgmt_hdr` is the outer wire header with little-endian `opcode`, controller `index`, and payload `len`.
- `struct mgmt_tlv` and `struct mgmt_tlv_hdr` define typed variable-length configuration elements and include a `static_assert` protecting the flexible payload offset.
- `struct mgmt_addr_info` is the common Bluetooth address plus address-type tuple reused by connection, pairing, discovery, key, device-flag, and mesh commands.
- `MGMT_STATUS_*` constants are command status values returned in command-complete/status events.
- `MGMT_SETTING_*` and `MGMT_PHY_*` bit masks report and configure controller capabilities and selected PHYs.
- `MGMT_OP_*` command definitions cover controller discovery, power/connectability/discoverability, class/name/UUID management, BR/EDR and LE key loading, pairing replies, OOB data, discovery, blocked devices, identity configuration, advertising, PHY configuration, experimental features, default config TLVs, device flags, advertisement monitors, mesh receiver/send, and synchronized HCI command execution.
- `MGMT_EV_*` event definitions cover command completion/status, controller add/remove/error, setting/name/class changes, key notifications, connection and pairing prompts, discovery, device block/unblock/unpair/add/remove, connection parameters, extended index/config/OOB/advertising/PHY/experimental changes, suspend/resume, advertisement monitor reports, and mesh events.

## Control Flow And State
The file itself has no executable control flow; it defines the on-wire state transitions consumed by the Bluetooth management implementation. A command is received as `mgmt_hdr`, decoded by `opcode`, validated against the matching `MGMT_*_SIZE` constant or flexible-array length, then answered through `MGMT_EV_CMD_COMPLETE` or `MGMT_EV_CMD_STATUS`. Long-running procedures such as discovery, pairing, advertising, mesh send, and monitor registration subsequently produce asynchronous `MGMT_EV_*` records. Controller state is represented by `supported_settings`, `current_settings`, selected PHY masks, advertising instance lists, monitor handles, controller indices, and per-device flags.

## State And Persistence Behavior
The records describe persistent and runtime state but do not store it. Persistent inputs include loaded BR/EDR link keys, LE LTKs, IRKs, blocked keys, configured identity/public/static addresses, device flags, and default system/runtime configuration TLVs. Runtime state includes powered/connectable/discoverable modes, advertising instances, discovery state, monitor handles, mesh handles, pending authentication prompts, controller suspend/resume data, and connection telemetry. All multi-byte values are explicitly little-endian and most structs are `__packed`, so padding cannot be relied on for forward compatibility.

## Dependencies And Integration Points
The header depends on Bluetooth core types such as `bdaddr_t`, HCI name length and advertising length constants, Linux integer/endian types, `BIT()`, `__packed`, `__counted_by`, and `__struct_group`. It integrates with `net/bluetooth/mgmt.c`, `net/bluetooth/mgmt_util.h`, HCI controller code, BlueZ userspace, and any tests that exercise management socket ABI compatibility. Variable-tail arrays such as `opcodes[]`, `keys[]`, `uuids[][16]`, `eir[]`, `instance[]`, `handles[]`, and `adv_data[]` are length-governed by adjacent count or length fields.

## Risks
- Any reorder, type-width change, missing `__packed`, endian annotation change, or size constant mismatch can break the management ABI.
- Flexible arrays require strict length validation before dereference; malformed userspace payloads can otherwise cause overread/overwrite bugs in implementation code.
- The file contains many similar opcode/size definitions, so off-by-one or wrong-size constants are a realistic regression risk.
- New settings or event bits must preserve compatibility with older userspace that ignores unknown bits.
- The TLV helper intentionally groups the header members; moving fields outside the group would violate hardened layout assumptions.

## Test Signals
- Build coverage for `net/bluetooth` and management socket users catches layout/name regressions.
- Bluetooth management selftests or BlueZ mgmt tests should cover command-size validation, unknown command/status behavior, key loading, pairing prompt flows, discovery events, advertising instances, and monitor/mesh commands.
- ABI tests should assert `sizeof()` and `offsetof()` for packed public records, especially `mgmt_hdr`, `mgmt_tlv`, address/key records, advertising payload records, and event flexible-array offsets.
