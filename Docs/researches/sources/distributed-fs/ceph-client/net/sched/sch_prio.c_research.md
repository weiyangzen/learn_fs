# sources/distributed-fs/ceph-client/net/sched/sch_prio.c

Purpose: implements the classful `prio` qdisc, a strict-priority band scheduler with configurable priority-to-band mapping, optional root filters, child qdiscs per band, and hardware offload support.

Important APIs, types, and functions: `struct prio_sched_data` stores band count, root filter block/list, `prio2band` map, and up to `TCQ_PRIO_BANDS` child qdiscs. Core functions are `prio_classify`, `prio_enqueue`, `prio_dequeue`, `prio_peek`, `prio_tune`, `prio_graft`, `prio_offload`, `prio_dump`, class stat/dump helpers, and `prio_tcf_block`.

Control flow: classification first honors class IDs encoded in `skb->priority` for this qdisc, otherwise runs root filters and handles actions. Without a valid filter result, it maps `skb->priority & TC_PRIO_MAX` through `prio2band`; invalid class IDs fall back to priority 0 mapping. Enqueue sends to the selected child and updates root backlog/qlen on success. Dequeue and peek scan bands from lowest index to highest, giving strict priority to lower-numbered bands. Tune validates band count and priomap, preallocates any new child qdiscs before locking, applies offload, commits the new map, purges removed bands, and releases old children.

State and persistence behavior: runtime state is the priomap and child qdisc pointers. Removed bands are purged before being put. Reset clears child qdiscs but keeps mapping. Dump emits `tc_prio_qopt` and optionally refreshes offload stats. There is no persistent storage.

Dependencies and integration points: integrates with classifier blocks, child qdisc grafting/hash, pfifo defaults, `qdisc_offload_dump_helper`, `qdisc_offload_graft_helper`, and `ndo_setup_tc(TC_SETUP_QDISC_PRIO)`. Qevents are not used; filters can still steal/drop/trap packets through TC actions.

Risks: strict priority can starve lower bands by design. Offload errors from `prio_offload` are ignored during tune, so software state may exist without hardware acceleration. The child array is fixed size and depends on validation before access. Backlog accounting must remain aligned between root and child.

Test signals: validate missing/invalid options, band count bounds, priomap entries, filter action handling, priority fallback paths, strict dequeue ordering, child graft defaults, removed-band purging, dump/offload stats, hardware graft notification, and destroy offload teardown.
