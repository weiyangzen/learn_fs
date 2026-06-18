# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.h

Purpose: defines cxgb4 scheduler class constants, state structures, bind types, capability helpers, and public scheduler APIs.

Important APIs/types: `SCHED_CLS_NONE`, `FW_SCHED_CLS_NONE`, `SCHED_MAX_RATE_KBPS`, scheduler state enum, `enum sched_fw_ops`, `enum sched_bind_type`, `struct sched_queue_entry`, `struct sched_flowc_entry`, `struct ch_sched_class`, `struct sched_table`, `can_sched`, `valid_class_id`, and prototypes for lookup/bind/unbind/alloc/free/init/cleanup.

Control flow/state: the header models a per-port scheduler table with active/unused class entries, binding lists, and refcounts. Inline helpers gate use on `pi->sched_tbl` presence and validate class ids while allowing `SCHED_CLS_NONE`.

Dependencies/integration: includes spinlock and atomic headers and relies on cxgb4 `port_info`, `ch_sched_params`, `ch_sched_queue`, and `ch_sched_flowc` definitions from core headers.

Risks: `sched_size` is an 8-bit field, so hardware class counts must fit. `valid_class_id` assumes a non-null scheduler table; callers should call `can_sched` first as the implementation does.

Test signals: build coverage where scheduler support is absent/present, validation of boundary class ids, and consumers in matchall/mqprio using queue and flowc bind types.
