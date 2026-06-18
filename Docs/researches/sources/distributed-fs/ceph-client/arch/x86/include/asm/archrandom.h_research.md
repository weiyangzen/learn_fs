
# sources/distributed-fs/ceph-client/arch/x86/include/asm/archrandom.h

Purpose: x86 hardware random-number interface for the generic random subsystem.

Important APIs and control flow: `rdrand_long()` retries `rdrand` up to `RDRAND_RETRY_LOOPS` and returns success via carry flag. `rdseed_long()` issues one `rdseed`. `arch_get_random_longs()` and `arch_get_random_seed_longs()` first require a nonzero requested count, then use `static_cpu_has(X86_FEATURE_RDRAND/RDSEED)`, and return one filled `unsigned long` or zero. `x86_init_rdrand()` is declared for CPU initialization outside UML.

State, dependencies, and risks: state is CPU feature state plus hardware RNG behavior. Dependencies include `processor.h`, cpufeatures, and the random core. Risks include trusting firmware/CPU-reported features, RDRAND retry exhaustion, early-boot feature availability, and virtualization quirks. Test signals include random subsystem boot messages, CPU feature masking, and tests that force unavailable hardware random paths.
