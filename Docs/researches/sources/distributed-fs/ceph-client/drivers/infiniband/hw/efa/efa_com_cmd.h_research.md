# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.h

Defines the internal EFA admin-command API. It provides compact parameter and result structs that let verbs and probe code avoid raw admin queue descriptor layouts.

Important types cover QP creation, modification, query, and destruction; CQ creation and destruction; AH creation and destruction; device attributes; hardware hints; memory address and control-buffer metadata; MR registration/deregistration; PD and UAR allocation; and stats result unions. `efa_com_get_device_attr_result` is the central capability aggregate consumed by `efa_main.c` and `efa_verbs.c`.

There is no runtime control flow, but the declarations define the control boundary: callers validate RDMA state and fill these structs, `efa_com_cmd.c` submits firmware commands, then callers persist returned handles and limits. MR structs are especially important because they encode inline PBL arrays and direct or indirect control-buffer PBLs.

State is transient per command, except returned identifiers and limits become persistent fields in EFA device, QP, CQ, MR, AH, PD, and ucontext objects. Dependencies include `efa_com.h` and admin enums such as `enum efa_admin_aq_feature_id`.

Risks are ABI-style: field size or semantic drift can corrupt command descriptors. The MR PBL union is a high-risk contract because mode flags decide how firmware interprets the same memory. Test signals include compile coverage across call sites, correct device attribute population, object allocation success, and MR registration across all PBL paths.
