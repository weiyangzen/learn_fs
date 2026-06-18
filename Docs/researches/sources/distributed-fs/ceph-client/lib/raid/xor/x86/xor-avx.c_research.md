# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-avx.c

Purpose: implements AVX-accelerated x86 XOR parity generation.

Important APIs and flow: `xor_avx_{2,3,4,5}` process 512-byte units using sixteen 32-byte YMM blocks. Each block loads the highest-numbered source, XORs lower sources and destination with `vxorps`, stores back with `vmovdqa`, and advances pointers. `DO_XOR_BLOCKS(avx_inner, ...)` builds grouped-source dispatch, and `xor_gen_avx()` wraps it in `kernel_fpu_begin/end`. `xor_block_avx` is the published template.

State and persistence: no persistence; in-place destination mutation plus temporary FPU state ownership.

Dependencies and integration: x86 selection forces this template when AVX and OSXSAVE are present.

Risks and test signals: risks are AVX state handling, alignment, and forcing without calibration. Signals include boot selection logs, KUnit XOR tests on AVX systems, and RAID parity stress.
