# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_rdma.h

Purpose: Defines internal RDMA resource, device, and QP state shared by the generic RDMA layer plus RoCE/iWARP implementations.

Important APIs/types/functions: Constants encode RDMA limits for PKEYs, WQEs, SRQs, page sizes, ACK delay, MR size, CQE modes, and XRCD count. `struct qed_bmap` wraps a named bitmap. `struct qed_rdma_info` stores all RDMA bitmaps, event callbacks, device/port pointers, resource counts, protocol, queue-zone data, and active flag. `struct qed_rdma_qp` stores software-visible QP state, handles, IDs, access flags, address vectors, requester/responder PBLs and DMA memory, SRQ/XRC fields, MACs, and iWARP/EDPM fields. Inline `qed_rdma_is_xrc_qp()` identifies XRC QP types. Public internal declarations expose DPM, info alloc/free, bitmap helpers, MAC conversion, and allocated-QP detection.

Control flow: Build-time `CONFIG_QED_RDMA` stubs allow non-RDMA builds to compile core callers. The data structures are filled by `qed_rdma.c` and consumed heavily by `qed_roce.c`/`qed_iwarp.c`.

State and persistence: The header describes the long-lived per-hwfn RDMA state and per-QP state that survive across API calls until stop/destroy.

Dependencies/integration: Includes public QED RDMA interface, QED device/core/HSi headers, and iWARP/RoCE headers, making it the bridge between common RDMA code and protocol-specific modules.

Risks: Structure fields encode firmware assumptions such as paired RoCE CIDs, reserved lkey, page counts, and queue-zone layout. Disabled stubs return `-EINVAL`, so callers need feature checks. The header includes both iWARP and RoCE types, increasing coupling and recompilation scope.

Test signals: Compile with RDMA enabled/disabled, validate QP field initialization for RoCE and iWARP, bitmap naming/size limits, XRC QP detection, and DPM stub behavior in non-RDMA builds.
