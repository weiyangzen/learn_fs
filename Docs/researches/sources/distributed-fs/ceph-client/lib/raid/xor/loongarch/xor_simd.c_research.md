# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.c

Purpose: instantiates LoongArch LSX and LASX SIMD XOR assembly loops.

Important APIs and flow: defines a 64-byte `LINE_WIDTH` and macro families for LSX (`vld`, `vst`, `vxor.v`) and LASX (`xvld`, `xvst`, `xvxor.v`). It includes `xor_template.c` twice with `XOR_FUNC_NAME()` mapped to `__xor_lsx_N` or `__xor_lasx_N` so each flavor gets 2 through 5 source helper functions.

State and persistence: no persistent state; vector code mutates destination memory in place.

Dependencies and integration: linked to `xor_simd_glue.c` through declarations in `xor_simd.h`. SIMD instructions must only be called inside the glue's FPU critical section.

Risks and test signals: risks include macro-template drift, vector instruction availability, and assuming 64-byte multiples. Signals include LSX/LASX build coverage, boot calibration, and KUnit randomized XOR correctness.
