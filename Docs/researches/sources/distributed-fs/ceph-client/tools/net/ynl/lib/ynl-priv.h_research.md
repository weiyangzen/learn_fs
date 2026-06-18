# sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl-priv.h

Purpose: Defines the private C runtime ABI used by generated YNL C bindings and `ynl.c`: policy metadata, parse callbacks, request/dump state, notification metadata, message construction helpers, dump-list traversal internals, and netlink attribute helpers.

Important APIs and types: Core types include `enum ynl_policy_type`, `enum ynl_parse_result`, `struct ynl_policy_attr`, `struct ynl_policy_nest`, `struct ynl_parse_arg`, `struct ynl_req_state`, `struct ynl_dump_state`, and `struct ynl_ntf_info`. It declares `ynl_exec()`, `ynl_exec_dump()`, `ynl_msg_start_req()`, `ynl_msg_start_dump()`, generic-netlink start helpers, parse error helpers, and `__ynl_attr_validate()`.

Control flow: Generated code uses start helpers to build requests, inline `ynl_attr_put_*()` helpers to append attributes, validation helpers while parsing responses, and `ynl_exec()` or `ynl_exec_dump()` to send and receive. Dump results are represented as a linked list whose data payload can be iterated with public macros from `ynl.h`.

State and persistence: `YNL_SOCKET_BUFFER_SIZE` fixes the internal tx/rx buffer size. During construction, `nlmsg_pid` is temporarily repurposed to store the output buffer size or overflow sentinel until `ynl_msg_end()` clears it.

Dependencies and integration: Pulls Linux netlink types through `linux/types.h`; generated family-specific code supplies policy tables and parse callbacks conforming to these structures.

Risks: The inline attribute writers rely on caller discipline around `ynl_msg_end()`. `ynl_attr_get_*()` casts unaligned payloads for small scalars, while 64-bit getters use `memcpy`; portability depends on target alignment behavior. `YNL_ARRAY_SIZE` handles zero-sized arrays defensively but remains macro-sensitive. Overflow signaling through `nlmsg_pid` is a local convention that must not leak to kernel send paths.

Test signals: Attribute put overflow, nested attribute start/end, scalar and string get/put, malformed attribute iteration, dump list empty/nonempty iteration, validation failures for every policy type, and generated-code request/dump paths.
