# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor_arch.h

Purpose: defines x86 XOR implementation selection.

Important APIs and flow: `arch_xor_init()` forces `xor_block_avx` if AVX and OSXSAVE are available. Otherwise it registers SSE variants on x86-64 or XMM-capable x86, MMX variants on MMX-only CPUs, and generic scalar fallbacks when no SIMD path is available.

State and persistence: uses XOR core forced-template state for AVX, or registration list for measured selection of other candidates.

Dependencies and integration: depends on x86 CPU feature helpers and templates from AVX, SSE, MMX, and generic files.

Risks and test signals: AVX is forced without benchmarking, and SIMD availability must match kernel FPU save support. Signals include boot logs, KUnit, and CPU feature matrix boot tests.
