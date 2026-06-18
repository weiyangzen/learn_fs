# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed.h

## Purpose
`qed.h` is the central private header for the QED core driver. It defines common constants, helper macros, device and hardware-function structures, resource and feature enums, tunnel configuration structures, firmware data containers, interrupt parameters, debug structures, register access macros, and internal prototypes shared across QED implementation files.

## Important APIs, Types, and Macros
- Doorbell helpers `qed_db_addr()` and `qed_db_addr_vf()`.
- Field helpers `QED_MFW_GET_FIELD()` and `QED_MFW_SET_FIELD()`.
- Tunnel configuration structures for VXLAN, Geneve, GRE, and classification modes.
- Personality, resource, feature, device capability, WoL, and doorbell recovery enums.
- `struct qed_hw_info`, `struct qed_hwfn`, and `struct qed_dev`, which define most persistent QED core state.
- MMIO helpers `REG_RD()`, `REG_WR()`, `REG_WR16()`, and `DOORBELL()`.
- Internal prototypes for device info, link/bandwidth update, firmware unzip, recovery, protocol stats, slowpath IRQ, TLV handling, WFQ, LLH filters, and doorbell recovery.

## Control Flow
The header mostly defines data contracts. Inline control flow exists in doorbell address helpers and `qed_concrete_to_sw_fid()`. Macros guide runtime selection: personality macros select protocol behavior, `for_each_hwfn()` iterates hardware functions, `QED_IS_CMT()` detects multi-hwfn devices, affinity macros choose protocol-affine hwfns, and resource macros compute resource ranges.

## State and Persistence
`struct qed_dev` persists across the PCI device lifetime and owns BAR mappings, firmware pointers, interrupt mode, recovery flags, protocol callback cookies, debug buffers, and hardware functions. Each `struct qed_hwfn` persists per engine/path and owns slowpath queues, PTTs, protocol contexts, DMAE buffers, QM configuration, doorbell recovery state, debug arrays, and workqueue/tasklet state.

## Dependencies and Integration Points
`qed.h` pulls in Linux kernel headers, public QED interface headers, and generated/hardware-specific headers. It is included broadly by QED implementation files built in the Makefile and forms the private integration contract between core, L2, storage offloads, RDMA, SR-IOV, debug, MCP, PTP, and devlink code.

## Risks and Edge Cases
- Field layout changes have wide blast radius across optional features.
- MMIO macros are thin wrappers; callers must enforce ordering and locking.
- Many pointers are conditionally allocated and require feature/init checks.
- CMT and affinity macros encode subtle multi-engine behavior.
- Doorbell address calculation depends on hardware constants and CID/DEMS encoding.

## Test Signals
Coverage should include full QED build matrices, sparse and W=1 builds, multi-hwfn/CMT paths, SR-IOV enabled/disabled builds, RDMA/storage optional builds, link and bandwidth update paths, firmware recovery, debug dump allocation, doorbell recovery, and LLH filter operations.
