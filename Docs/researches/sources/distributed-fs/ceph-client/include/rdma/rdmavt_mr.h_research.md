# sources/distributed-fs/ceph-client/include/rdma/rdmavt_mr.h

Purpose: rdmavt memory-region, L_Key/R_Key table, segment, and SGE progress definitions for software verbs data movement.

Important APIs/types/functions: `struct rvt_seg`, `RVT_SEGSZ`, `struct rvt_segarray`, `struct rvt_mregion`, `RVT_MAX_LKEY_TABLE_BITS`, `struct rvt_lkey_table`, `struct rvt_sge`, `struct rvt_sge_state`, `rvt_put_mr`, `rvt_get_mr`, `rvt_put_ss`, `rvt_get_sge_length`, `rvt_update_sge`, `rvt_skip_sge`, `rvt_ss_has_lkey`, and `rvt_mr_has_lkey`.

Control flow: Data movement validates keys, seeds an SGE state, copies/skips chunks bounded by remaining request, SGE, and segment lengths, then advances through segment arrays. Consumed SGEs optionally release MR refs and load the next SGE.

State and persistence behavior: Runtime MR state tracks PD, user base, IOVA, length, keys, access, segment maps, invalid/published flags, percpu refcount, and completion. SGE state tracks per-operation progress.

Dependencies and integration points: Depends on Linux percpu refcounts and RDMA PD/MR concepts. Integrates with `rdma_vt.h`, rdmavt fast registration, invalidation, key lookup, and QP copy paths.

Risks: Advancement must not overrun segment maps or process zero-length chunks. MR refs must balance on every exit path. Lkey invalidation races can expose stale memory access if lookup/ref ordering is wrong.

Test signals: Lkey/rkey lookup, MR get/put completion, SGE advance across segment-array boundaries, skip/update with and without release, zero-length warnings, invalidation during access, and max lkey table sizing.
