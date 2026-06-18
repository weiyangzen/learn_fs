# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-types.h

## Purpose
This UAPI header defines core LNet public types and constants shared by kernel code, user utilities, and wire-facing structures. It covers legacy 64-bit NID helpers, large `struct lnet_nid` helpers, LNet process IDs, memory descriptor configuration, event queue records, counters, and UDSP action identifiers.

## Important APIs, Types, And Functions
Key NID helpers include `LNET_NIDADDR()`, `LNET_NIDNET()`, `LNET_NETNUM()`, `LNET_NETTYP()`, `LNET_MKNET()`, `LNET_MKNID()`, `lnet_nid4_to_nid()`, `lnet_nid_to_nid4()`, `nid_same()`, `nidhash()`, `LNET_NID_NET()`, `nid_is_nid4()`, and `nid_addr_is_set()`. `struct lnet_handle_md` plus `LNetInvalidateMDHandle()` and `LNetMDHandleIsInvalid()` define the public memory descriptor handle contract. `struct lnet_process_id` is the old NID4 process ID, while `struct lnet_processid` carries large NIDs; `lnet_pid4_to_pid()` and `lnet_pid_to_pid4()` bridge them. `struct lnet_md`, `enum lnet_md_options`, `enum lnet_event_kind`, `struct lnet_event`, `struct lnet_counters`, and `enum lnet_ack_req` are the main user-visible LNet API payloads.

## Control Flow
The file is almost entirely inline conversion and predicate logic. NID4 conversion maps the 32-bit network and 32-bit address into `struct lnet_nid` fields using big-endian storage for `nid_num` and `nid_addr[0]`; converting back reconstructs a legacy `lnet_nid_t`. MD and event structures are passive ABI payloads consumed by LNet API calls and event handlers. `nid_addr_is_set()` scans the address byte span reported by `NID_ADDR_BYTES()` to distinguish network-only from full NID input, with an explicit ambiguity for address zero.

## State, Persistence, And Dependencies
There is no runtime state or persistence. The header depends on fixed UAPI layout from `lnet-idl.h`, Linux integer types, byte-order helpers, and `PAGE_SHIFT`. Because many structures cross the user/kernel or wire boundary, field order, sizes, endian handling, and reserved values are persistent ABI.

## Integration Points
It is included by LNet UAPI headers, LNet kernel internals, utilities that parse NIDs, LND implementations, and selftest/fault-injection ioctls. EFA LND uses the large-NID helpers and the old/new NID conversion paths for protocol compatibility.

## Risks
The main risk is ABI drift: changing enum values, structure layout, or NID encoding breaks user tools and peer compatibility. `nid_addr_is_set()` can misclassify valid zero-address NIDs as unset, so callers must not use it as a proof that a user omitted the address. NID4 conversion loses large-NID address bytes. Event handlers are documented as nonblocking and unable to call LNet APIs; violations can deadlock or corrupt event sequencing.

## Test Signals
Useful tests exercise NID4 to large-NID round trips, any-NID handling, zero-address NID parsing, MD option validation, event field population for PUT/GET/ACK/REPLY/SEND/UNLINK, and ABI size checks for UAPI structs compiled in kernel and userspace.
