# sources/distributed-fs/ceph-client/lib/raid6/recov_rvv.c

Purpose: implements RISC-V vector RAID6 recovery.

Important APIs and flow: internal helpers set vector length to 16 bytes and use RVV loads, XORs, shifts, masks, and `vrgather.vv` table lookups against qmul/pbmul nibbles. Public `raid6_2data_recov_rvv()` and `raid6_datap_recov_rvv()` do standard syndrome-delta setup, restore `ptrs`, then call helpers inside `kernel_vector_begin/end`. `raid6_recov_rvv` has priority 1 and valid callback `rvv_has_vector`.

State and persistence: temporary `ptrs` mutation is restored; failed buffers and P are updated; vector state is scoped.

Dependencies and integration: depends on `rvv.h`, selected syndrome generator, GF vector tables, and recovery selection.

Risks and test signals: risks include fixed 16-byte vector length assumptions, inline assembly constraints, and vector feature gating. Signals include RISC-V vector recovery tests and boot recovery algorithm logs.
