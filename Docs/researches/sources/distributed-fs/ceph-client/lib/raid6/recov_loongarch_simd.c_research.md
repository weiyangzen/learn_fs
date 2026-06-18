# sources/distributed-fs/ceph-client/lib/raid6/recov_loongarch_simd.c

Purpose: implements LSX and LASX RAID6 recovery for LoongArch.

Important APIs and flow: LSX and LASX recovery first compute syndrome deltas through `raid6_call.gen_syndrome`, restore `ptrs`, then use `raid6_vgfmul` nibble tables and vector shuffle instructions to compute two-data or data+P reconstruction. LSX publishes priority 1; LASX publishes priority 2 because recovery selection is priority-only rather than benchmarked.

State and persistence: temporarily mutates and restores `ptrs`; mutates failed data and P buffers; wraps vector work in `kernel_fpu_begin/end`.

Dependencies and integration: depends on `loongarch.h`, GF vector tables, selected syndrome generator, and `raid6_recov_algos[]`.

Risks and test signals: priorities assume future LASX is not slower than LSX, unlike syndrome generation. Signals include LoongArch recovery tests, CPU feature gating, and boot logs selecting `lsx` or `lasx`.
