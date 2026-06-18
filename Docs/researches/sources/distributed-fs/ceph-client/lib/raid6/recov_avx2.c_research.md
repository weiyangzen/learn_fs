# sources/distributed-fs/ceph-client/lib/raid6/recov_avx2.c

Purpose: implements AVX2-accelerated RAID6 recovery.

Important APIs and flow: after the same syndrome-delta setup as scalar recovery, `raid6_2data_recov_avx2()` uses `raid6_vgfmul` nibble tables with `vpshufb` to compute Q multipliers and P multipliers over 32-byte or 64-byte chunks, reconstructing both failed data blocks. `raid6_datap_recov_avx2()` reconstructs one data block and updates P. `raid6_recov_avx2` has priority 2 and valid callback `raid6_has_avx2()`.

State and persistence: temporarily mutates `ptrs`, restores it, mutates failed buffers/P, and owns AVX state inside `kernel_fpu_begin/end`.

Dependencies and integration: depends on selected `raid6_call.gen_syndrome`, vector GF tables, x86 FPU APIs, and recovery selector.

Risks and test signals: risks include vector table indexing, 32/64-bit chunk differences, and AVX feature gating. Signals include RAID6 recovery tests on AVX2 hardware and boot recovery algorithm logs.
