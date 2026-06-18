# sources/distributed-fs/ceph-client/include/trace/misc/rdma.h

Purpose: Provides RDMA trace formatting helpers for InfiniBand async events, work-completion statuses, IB CM events, and RDMA CM events.

Important APIs/types/functions: Defines list macros `IB_EVENT_LIST`, `IB_WC_STATUS_LIST`, `IB_CM_EVENT_LIST`, and `RDMA_CM_EVENT_LIST`; registers enum values through `TRACE_DEFINE_ENUM`; exports `rdma_show_ib_event`, `rdma_show_wc_status`, `rdma_show_ib_cm_event`, and `rdma_show_cm_event`.

Control flow: RDMA tracepoint headers expand the list macros twice: once to register enums and once to build symbolic tables for `TP_printk`.

State/persistence: No RDMA state is owned. It only maps captured numeric states to stable text.

Dependencies/integration: Depends on RDMA/IB enum definitions and tracepoint formatting. Used by RDMA core, CM, and driver trace events.

Risks: Enum drift is the primary risk; stale maps make transport failures opaque. Macro hygiene matters because list macros redefine helper names.

Test signals: Compile RDMA trace users; exercise connection manager and completion failure paths and confirm symbolic status/event names.
