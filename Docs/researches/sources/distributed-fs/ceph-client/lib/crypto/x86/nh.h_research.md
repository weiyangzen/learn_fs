# sources/distributed-fs/ceph-client/lib/crypto/x86/nh.h

Purpose: x86 architecture dispatch for the NH universal hash.

Important APIs/types/functions: declares `nh_sse2()` and `nh_avx2()`, defines static keys `have_sse2` and `have_avx2`, implements `nh_arch()`, and provides `nh_mod_init_arch()`.

Control flow: module init enables SSE2 on `X86_FEATURE_XMM2`, then AVX2 when CPU feature and OS SSE/YMM xfeatures are available. `nh_arch()` uses SIMD only for messages at least 64 bytes, when SSE2 is enabled, and when `irq_fpu_usable()` is true. It brackets the selected SSE2/AVX2 assembly call in `kernel_fpu_begin/end()` and returns true; otherwise it returns false so the generic caller can handle the message.

State and persistence: static branch state persists after init. Per-call state is the caller's key, message, and hash output.

Dependencies: FPU APIs, static keys, CPU feature detection, `NH_NUM_PASSES`, and generic NH caller fallback.

Integration points: included by the NH library as an optional architecture hook, likely for Adiantum/HPolyC-style constructions.

Risks: short messages intentionally use generic code; callers must respect the boolean return. SIMD use depends on IRQ/FPU context. AVX2 xfeature gating must match assembly use or faults can occur.

Test signals: dispatch tests should confirm false return for short/FPU-unusable paths and correct outputs for SSE2 and AVX2 paths compared with generic NH.
