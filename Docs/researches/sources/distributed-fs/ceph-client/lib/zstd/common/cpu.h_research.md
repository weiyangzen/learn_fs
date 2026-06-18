# sources/distributed-fs/ceph-client/lib/zstd/common/cpu.h

Purpose: Provides CPUID feature detection helpers used by zstd dynamic dispatch, especially BMI2 support checks on x86.

Important APIs/types:
- `ZSTD_cpuid_t` stores selected CPUID feature registers.
- `ZSTD_cpuid()` executes CPUID where supported and returns feature bits.
- Macro-generated predicates such as `ZSTD_cpuid_bmi1()`, `ZSTD_cpuid_bmi2()`, `ZSTD_cpuid_sse2()`, and many other x86 feature checks.

Control flow:
- On i386 PIC with GCC, preserves EBX around CPUID manually.
- On x86/x86_64, queries leaves 0, 1, and 7 when available.
- On non-x86, returns zeroed feature registers.

State and persistence:
- Stateless. Callers can cache `ZSTD_cpuid_t` if desired.

Dependencies and integration:
- Includes `mem.h` for `U32`.
- `zstd_internal.h` uses this to implement `ZSTD_cpuSupportsBmi2()`.

Risks:
- Inline assembly constraints must preserve ABI registers, especially 32-bit PIC EBX.
- CPUID only reports hardware support; OS support for wider vector state is not fully evaluated here.
- Non-x86 returns no features, which should force generic code paths.

Test signals:
- x86 and i386 PIC build/run tests.
- Verify BMI2 dispatch only on CPUs with both BMI1 and BMI2.
- Non-x86 build should compile and report no x86 features.
