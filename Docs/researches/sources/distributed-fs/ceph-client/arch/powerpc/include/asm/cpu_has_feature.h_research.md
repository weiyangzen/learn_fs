## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_has_feature.h

Purpose: provides fast PowerPC CPU feature tests for kernel code.

Important APIs/types/functions: `early_cpu_has_feature()` checks `CPU_FTRS_ALWAYS`, `CPU_FTRS_POSSIBLE`, and `cur_cpu_spec->cpu_features`. `cpu_has_feature()` either delegates to early checks or uses jump-label-backed `cpu_feature_keys`.

Control flow: constant feature masks are required in jump-label mode. Always-present features return true, impossible features return false, and possible runtime features index `cpu_feature_keys` with `ctzl(feature)`. Debug mode warns if jump-label checks run before initialization.

State and persistence: reads global `cur_cpu_spec`, static key state, and feature mask constants. It does not mutate state.

Dependencies and integration: depends on `asm/cputable.h`, `linux/jump_label.h`, and `static_key_feature_checks_initialized` from feature-fixup code. Used broadly for CPU errata, barrier selection, DCR access, FPU availability, SMT layout, and instruction alternatives.

Risks and test signals: multi-bit feature arguments are rejected because the static-key array is one bit per feature. Wrong possible/always masks can compile out required code or leave dead paths. Test signals include early boot before static-key init, jump-label enabled/disabled builds, feature-dependent alternatives, and CPU matrix boots.
