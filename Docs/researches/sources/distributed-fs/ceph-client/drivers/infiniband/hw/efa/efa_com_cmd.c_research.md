# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.c

Implements the EFA admin-command facade used by verbs and PCI setup. It marshals driver-facing structs into `efa_admin_*` queue entries, submits them through `efa_com_cmd_exec`, and translates completions back into hardware handles, keys, capabilities, stats, and feature data.

Important APIs include QP create/modify/query/destroy, CQ create/destroy, MR register/deregister, AH create/destroy, PD/UAR allocation, feature get/set, AENQ configuration, and stats retrieval. `efa_com_get_device_attr` is the main discovery sequence: device attributes populate `edev->supported_features`, then queue, network, and optional event-queue attributes fill `struct efa_com_get_device_attr_result`.

Control flow is uniform: zero a command, set an opcode, fill fields and bit masks, execute against `edev->aq`, ratelimit-log failures, and copy completion fields into result structs. MR registration is the most complex path because inline, direct control-buffer, and indirect control-buffer PBL modes share a command union and require correct admin descriptor flags.

State is mostly returned to callers rather than owned here. The file updates only `edev->supported_features`; QP/CQ/MR/AH/PD/UAR lifetime is persisted by `efa_verbs.c` or `efa_main.c`. Dependencies are `efa_com.h`, `efa_com_cmd.h`, admin descriptors, `EFA_GET`/`EFA_SET`, `efa_com_set_dma_addr`, and the admin queue implementation.

Risks include bitfield drift, optional feature gate mistakes, incorrect control-buffer flags for indirect MRs, and incomplete validation for unexpected stat types. Test signals include successful probe capability discovery, object create/destroy loops, unsupported-feature failures, inline/direct/indirect MR registration, AENQ group negotiation, and hw stats queries under traffic.
