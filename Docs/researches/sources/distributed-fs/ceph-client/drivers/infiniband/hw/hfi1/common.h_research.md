# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/common.h

Purpose: kernel/user shared HFI1 protocol definitions. It defines protocol versioning, capability-mask layout and mutation macros, default/reserved capability policy, receive header flag (RHF) bitfields, receive type constants, LRH/KDETH constants, MTU/padding/PKey constants, and inline RHF decoders.

Important APIs/types: `HFI1_CAP_*` macros manipulate the global `hfi1_cap_mask` for kernel and user capability domains. `HFI1_CAP_WRITABLE_MASK`, `HFI1_CAP_RESERVED_MASK`, `HFI1_CAP_MUST_HAVE_KERN`, `HFI1_CAP_MASK_DEFAULT`, and `HFI1_CAP_K2U` define policy. Inline helpers include `rhf_to_cpu()`, `rhf_err_flags()`, `rhf_rcv_type()`, `rhf_rcv_type_err()`, `rhf_pkt_len()`, `rhf_egr_index()`, `rhf_rcv_seq()`, `rhf_hdrq_offset()`, `rhf_use_egr_bfr()`, `rhf_dc_info()`, and `rhf_egr_buf_offset()`.

Control flow: no complex flow exists here. Runtime receive code reads the 64-bit RHF from the header queue, decodes packet type, length, eager-buffer index/offset, sequence, and error bits through these helpers, then dispatches to type-specific handlers in `driver.c`.

State and persistence: capability state persists in the module-global `hfi1_cap_mask`, with separate kernel/user bit ranges and a locked bit. RHF values are persistent hardware-produced queue entries until the receive head is advanced. The header also defines constants shared with user-space ABI via `rdma/hfi/hfi1_user.h`.

Dependencies and integration: includes the public HFI1 user ABI header and is consumed by receive, user-context, and TID paths. Its RHF decoders are on the performance-sensitive receive hot path, and its capability masks are used by module parameter parsing in `driver.c`.

Risks: capability policy mistakes can expose unsupported features to user processes or allow user contexts without kernel support. RHF length and offset units differ by field: packet length returns bytes, header/eager offsets are derived from dword or 64-byte block units. Any change to bit positions must match hardware and user ABI.

Test signals: cap-mask module parameter tests, user-context open tests, receive packet parsing across expected/eager/IB/bypass/error types, error flag reporting, and ABI compatibility checks against user-space libraries.
