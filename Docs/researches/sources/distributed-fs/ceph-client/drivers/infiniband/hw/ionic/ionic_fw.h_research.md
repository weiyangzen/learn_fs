# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_fw.h

Purpose: firmware ABI contract for the Ionic RDMA driver. It defines memory key encoding, MR/QP flag translations, device status translation, WQE/CQE/EQE layouts, admin command payloads, opcodes, stat descriptors, and layout helper functions consumed by control path, datapath, and stats code.

Important APIs/types: `struct ionic_sge`, `union ionic_v1_pld`, `struct ionic_v1_wqe`, `struct ionic_v1_cqe`, `struct ionic_v1_admin_wqe`, admin command structs for AH/MR/CQ/QP/stat operations, `struct ionic_v1_eqe`, and `struct ionic_v1_stat`. Helpers include `ionic_mrid()`, `ionic_mrid_index()`, `to_ionic_mr_flags()`, `to_ionic_qp_flags()`, `from_ionic_qp_flags()`, `ionic_to_ib_status()`, QP type/state translators, CQE/EQE field extractors, and WQE stride capacity helpers.

Control flow: higher layers translate RDMA core state into ABI values with the inline helpers, fill packed admin or data WQEs, and decode CQEs/EQEs by bitfields. Datapath code selects v1 or v2 opcodes via the RDMA version, computes maximum SGE/inline capacities from queue stride, and uses CQE status/type/QID helpers during polling. Stats code normalizes and reads `ionic_v1_stat` descriptors.

State and persistence: no mutable runtime state is stored here. The header defines persistent wire and DMA memory formats shared with firmware. `static_assert()` guards admin payload sizes against accidental ABI drift.

Dependencies and integration: includes Linux kernel helpers and RDMA verbs definitions. It is included by Ionic RDMA object, datapath, page-table, and stats files and must match firmware, device identity capabilities, and RDMA core status semantics.

Risks: packed structures, endian annotations, and bit shifts are hardware ABI. Any change can silently break WQE/CQE interpretation. `to_ionic_qp_state()` returns `0` for unsupported states, which maps to reset-like behavior if caller validation is weak. Capacity helpers use pointer arithmetic from synthetic base addresses, so stride and expanded-doorbell assumptions must stay aligned with hardware.

Test signals: compile-time size assertions, admin command success for create/query/modify/destroy paths, datapath opcode coverage on RDMA version 1 and 2 devices, CQE status translation tests, and stats descriptor decoding with all endian/type variants.
