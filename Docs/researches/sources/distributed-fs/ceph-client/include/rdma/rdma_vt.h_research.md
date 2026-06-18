# sources/distributed-fs/ceph-client/include/rdma/rdma_vt.h

Purpose: rdmavt shared software verbs transport abstraction for low-level drivers such as hfi1/qib, combining common verbs object management with driver-supplied packet scheduling and hardware-specific behavior.

Important APIs/types/functions: `struct rvt_ibport`, `struct rvt_driver_params`, `struct rvt_ucontext`, `rvt_pd`, `rvt_ah`, `rvt_mmap_info`, `rvt_wss`, `struct rvt_driver_provided`, `struct rvt_dev_info`, inline casts/name/P_Key/atomic helpers, and APIs `rvt_alloc_device`, `rvt_dealloc_device`, `rvt_register_device`, `rvt_unregister_device`, `rvt_check_ah`, `rvt_init_port`, `rvt_fast_reg_mr`, `rvt_invalidate_rkey`, `rvt_rkey_ok`, `rvt_lkey_ok`, and `rvt_mcast_find`.

Control flow: A driver allocates and fills `rvt_dev_info`, params, ports, and callback table, then registers with rdmavt. rdmavt exposes the embedded `ib_device`; send paths invoke driver schedule/setup callbacks; QP transitions call driver check/modify/notification hooks; port and MAD behavior use `rvt_ibport` state.

State and persistence behavior: Runtime kernel state only. Locks protect port, allocation counters, QP/CQ/mcast, mmap, and pending mapping state. Timers manage M_Key lease and trap resend. Driver params should remain stable after registration.

Dependencies and integration points: Depends on Linux locks/lists/hash, `ib_verbs.h`, `ib_mad.h`, and `rdmavt_mr.h`. Integrates with rdmavt QP/CQ/MR/multicast/MAD implementations and provider registration.

Risks: Callback requirements depend on which verbs are shared versus overridden. P_Key table ownership is split between driver allocation and rdmavt use. Timer/list teardown and lock ordering are important during unregister and QP error/reset.

Test signals: Register/unregister, port init with P_Key table, AH validation, QP create/modify/reset/error, send scheduling, MR key validation, multicast lookup, trap timers, mmap offset validation, and NULL optional callbacks.
