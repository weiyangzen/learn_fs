# sources/distributed-fs/ceph-client/lib/raid6/neon.h

Purpose: declares ARM NEON RAID6 generated syndrome and recovery helper functions.

Important APIs and flow: declares `raid6_neon{1,2,4,8}_gen_syndrome_real()` and `raid6_neon{1,2,4,8}_xor_syndrome_real()` plus low-level recovery helpers `__raid6_2data_recov_neon()` and `__raid6_datap_recov_neon()`.

State and persistence: no state; interface only.

Dependencies and integration: shared by NEON wrappers and NEON inner recovery implementation.

Risks and test signals: prototype mismatch would break compilation or corrupt calls. Signals include NEON build coverage and RAID6 parity/recovery tests.
