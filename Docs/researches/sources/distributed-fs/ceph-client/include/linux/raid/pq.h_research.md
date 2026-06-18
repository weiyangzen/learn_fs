# sources/distributed-fs/ceph-client/include/linux/raid/pq.h

Purpose: declares RAID6 P/Q syndrome generation, recovery algorithms, Galois-field tables, algorithm selection, and user-space test scaffolding for the RAID6 library.

Important APIs and types: `struct raid6_calls` contains `gen_syndrome`, `xor_syndrome`, `valid`, algorithm name, and priority. `struct raid6_recov_calls` contains two-data and data-plus-P recovery functions. Externs list scalar and architecture-optimized implementations for MMX/SSE/AVX/AVX512/Altivec/S390/NEON/LoongArch/RISC-V variants. `raid6_call`, `raid6_select_algo()`, `raid6_2data_recov`, `raid6_datap_recov()`, `raid6_dual_recov()`, and GF tables form the public surface. `raid6_get_zero_page()` supplies a zero page in kernel or test mode.

Control flow: initialization benchmarks or validates available algorithms, chooses `raid6_call`, and sets recovery function pointers. RAID5/6 code calls syndrome generation on writes and recovery functions when one or two devices are missing.

State and persistence: runtime state is selected function pointers and immutable GF tables. Persistent data is array parity on disks, not owned here.

Dependencies and integration points: depends on kernel block/MM headers in-kernel and provides replacements for userspace test builds. It integrates MD RAID5/6, crypto-like optimized math routines, and architecture feature detection.

Risks and test signals: risks include wrong CPU feature `valid()` checks, SIMD state handling, GF table alignment, algorithm priority mistakes, and recovery corruption for edge disk counts/byte sizes. Test RAID6 selftests/benchmarks, syndrome consistency across all algorithms, degraded one/two-disk recovery, unaligned sizes, userspace test builds, and CPU hotplug/feature variants.
