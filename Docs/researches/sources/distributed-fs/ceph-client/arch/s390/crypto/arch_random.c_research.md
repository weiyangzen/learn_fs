<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/arch_random.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/arch_random.c

Purpose: Defines shared s390 architecture random-number availability and accounting state.

Important APIs/types/functions: Defines `DEFINE_STATIC_KEY_FALSE(s390_arch_random_available)` and exported `atomic64_t s390_arch_random_counter`.

Control flow: No local runtime functions; other s390 arch-random code toggles or consumes the static key and counter.

State and persistence: The static key records whether architectural random support is available. The exported atomic counter tracks arch-random usage or output accounting for other code.

Dependencies and integration points: Included unconditionally by the crypto Makefile. Depends on `asm/archrandom.h`, CPACF headers, static keys, atomics, and Linux random infrastructure.

Risks: This file is only state definition; mismatched extern declarations elsewhere would break linking. Counter semantics must remain consistent with consumers.

Test signals: s390 builds with arch random support, symbol export checks, and runtime toggling/usage through the arch random implementation.

Source read size: 20 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/arch_random.c -->
