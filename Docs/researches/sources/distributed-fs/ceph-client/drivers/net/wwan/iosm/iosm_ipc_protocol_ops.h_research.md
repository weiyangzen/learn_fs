# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.h

Purpose: defines the IOSM protocol wire structures, completion enums, TD format, message preparation arguments, and public protocol operation prototypes used by the IOSM shared-memory transport layer.

Important APIs/types: `enum ipc_mem_td_cs` documents TD completion states, including partial, end, overflow, abort, and error. `enum ipc_mem_msg_cs` represents message completion. `union ipc_msg_prep_args` groups pipe, sleep, feature, map, and unmap request arguments; map/unmap are declared even though this protocol implementation rejects them. `enum ipc_mem_msg` assigns shared-memory message type values. Message structures such as `ipc_mem_msg_open_pipe`, `ipc_mem_msg_close_pipe`, `ipc_mem_msg_host_sleep`, and `ipc_mem_msg_feature_set` mirror the AP-to-CP ring layout. `struct ipc_protocol_td` is packed and carries a DMA buffer address, size/completion-status word, and chained-descriptor count.

Control flow and state: the header establishes the contract for the implementation in `iosm_ipc_protocol_ops.c`: callers prepare messages, advance message head pointers, process completions, enqueue/reclaim UL descriptors, provision/process DL descriptors, query shared IPC status, and clean pipe resources. `SIZE_MASK`, `COMPLETION_STATUS`, and `RESET_BIT` encode bitfield assumptions shared with CP firmware.

Dependencies and integration points: includes forward dependencies on `struct iosm_imem`, `struct iosm_protocol`, `struct ipc_pipe`, `struct sk_buff`, completions, DMA addresses, and shared IPC state enums from the broader IOSM protocol headers.

Risks and test signals: all structs are ABI-like shared-memory layouts, so packing, endian conversion, size fields, and bit shifts are high-risk. Build tests should catch prototype drift; runtime tests should validate that CP firmware accepts open/close/sleep/feature messages and that TD status bits are interpreted correctly on 32/64-bit DMA platforms.
