<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.h -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.h

## Purpose
Defines HSR/PRP frame metadata and node registry structures plus the public frame-registry API used by forwarding, device, debugfs, and netlink code.

## APIs, Types, and Functions
Defines `struct hsr_frame_info`, `struct hsr_seq_block`, and `struct hsr_node`, sequence block constants and index/bit macros, inline `hsr_seq_block_size()`, and declarations for node deletion, lookup, supervision handling, address substitution, frame in/out registration, pruning timers, self-node creation, node iteration/data export, PRP SAN handling, database membership, and KUnit-only `hsr_get_seq_block()`.

## Control Flow, State, and Persistence
The header has no executable flow except the inline size helper, which warns if `seq_port_cnt` is zero and computes the flexible bitmap allocation size. It documents persistent node state: MAC identity, AddrB port, per-port ingress times/staleness, SAN markers, removal marker, duplicate-detection XArray, fixed sequence block backing buffer, next block cursor, and RCU head.

## Dependencies and Integration
Depends on `hsr_main.h` for protocol and port definitions. Used by `hsr_forward.c`, `hsr_framereg.c`, `hsr_device.c`, `hsr_debugfs.c`, and netlink code that reports node state.

## Risks and Test Signals
Risks include the pseudo-flexible `seq_nrs` layout depending on `struct_size_t()`, mismatched `seq_port_cnt`, ABI-like expectations between frame info producers and consumers, and enum indexes used directly for arrays. Test signals include build-time structure use, KUnit duplicate-discard tests, node-table debugfs reads, and netlink node data queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.h -->
