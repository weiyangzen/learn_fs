# sources/distributed-fs/ceph-client/lib/raid6/recov_neon.c

Purpose: wraps ARM NEON RAID6 recovery helpers in SIMD-safe sections and publishes the recovery algorithm.

Important APIs and flow: `raid6_2data_recov_neon()` and `raid6_datap_recov_neon()` perform the standard zero-page syndrome-delta setup, restore `ptrs`, choose vector GF tables, then call `__raid6_2data_recov_neon()` or `__raid6_datap_recov_neon()` inside `scoped_ksimd()`. `raid6_recov_neon` has priority 10.

State and persistence: temporarily mutates `ptrs`, restores it, and updates failed data/P buffers. SIMD state is scoped.

Dependencies and integration: depends on `neon.h`, `raid6_call.gen_syndrome`, GF vector tables, and ARM SIMD support.

Risks and test signals: high priority makes NEON preferred when available, so correctness and SIMD gating are critical. Signals include recovery tests on NEON-capable ARM systems and boot recovery algorithm logs.
