# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.h

## Purpose
`opfn.h` documents and declares HFI1 Omni-Path Feature Negotiation. It defines the protocol constants, feature codes, per-QP OPFN state, reserved work-request opcode mapping, and public hooks used by QP and receive paths.

## Important APIs, types, and functions
- Documentation block describes OPFN architecture: peer discovery through BTH bit 24, compare-swap opcode and `U64_MAX` address, and ULP-transparent negotiation.
- `IB_BTHE_E_SHIFT` defines the extended-bit position in BTH1.
- `HFI1_VERBS_E_ATOMIC_VADDR` defines the special atomic virtual address for OPFN packets.
- `enum hfi1_opfn_codes` currently includes `STL_VERBS_EXTD_TID_RDMA`.
- `struct hfi1_opfn_data` stores peer support, requested/completed masks, current feature, spinlock, and work item.
- `IB_WR_OPFN` maps OPFN sends to `IB_WR_RESERVED3`.
- Function prototypes expose send, response, reply, error, QP init, trigger, module init, and module exit hooks.

## Control flow
The header defines the public lifecycle: initialize OPFN workqueue at driver/module setup, initialize per-QP OPFN state during QP changes, trigger requests when incoming packets advertise the extended bit, process request/response/reply packets from the RC path, handle QP errors, and destroy the workqueue at exit.

## State and persistence
`struct hfi1_opfn_data` is per-QP runtime state. It is guarded by its spinlock and has no persistence beyond QP lifetime.

## Dependencies and integration points
The header includes Linux workqueues, RDMA verbs, and rdmavt QP definitions. It is consumed by HFI1 QP/RC/TID RDMA code that needs to negotiate feature support without exposing the protocol to upper-layer protocols.

## Risks
- The `IB_WR_OPFN` alias uses a reserved work-request opcode; changes in RDMA core reserved opcode use could conflict.
- The protocol encodes feature code in low data bits and masks in 16-bit fields, so adding features requires careful bounds checks.
- The spelling in the documentation says "Feature Negotion"; harmless for code, but searchability/documentation polish may suffer.

## Test signals
- Compile all QP, RC, and TID RDMA users after changing constants or structure fields.
- Protocol tests should confirm bit 24 detection, special atomic address matching, and feature-code extraction.
- Add-feature tests should validate mask capacity, handler table bounds, and backward compatibility with peers that do not set the extended bit.
