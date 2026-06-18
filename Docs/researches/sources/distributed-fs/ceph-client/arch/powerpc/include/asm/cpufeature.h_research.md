## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpufeature.h

Purpose: exposes module-loader CPU feature numbers and a helper for testing user-visible CPU feature bits.

Important APIs/types/functions: defines `MAX_CPU_FEATURES`, `PPC_MODULE_FEATURE_VEC_CRYPTO`, `PPC_MODULE_FEATURE_P10`, `cpu_feature(x)`, and `cpu_have_feature()`.

Control flow: `cpu_have_feature()` selects `cur_cpu_spec->cpu_user_features` for feature numbers below 32 and `cpu_user_features2` for numbers 32 and above.

State and persistence: reads the current CPU specification’s user feature masks. No mutation or persistence.

Dependencies and integration: depends on `asm/cputable.h` and UAPI feature bits. Used by module CPU feature matching so modules can require vector crypto, POWER10 ISA features, or future user-visible capabilities.

Risks and test signals: feature numbers must remain synchronized with UAPI and module metadata. Off-by-32 errors can accept incompatible modules or reject valid ones. Test signals include module loading with feature requirements, POWER10/vector-crypto module tests, and compile checks when new `PPC_FEATURE2_*` bits are added.
