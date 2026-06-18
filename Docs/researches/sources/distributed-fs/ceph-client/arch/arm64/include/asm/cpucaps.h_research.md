## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpucaps.h

Purpose: exposes the generated arm64 CPU capability numbers and compile-time possibility checks.

Important APIs/types/functions: includes `asm/cpucap-defs.h` and defines `cpucap_is_possible`, which returns true when a capability is within `ARM64_NCAPS` and is not known impossible under the current configuration.

Control flow: compile-time and inline capability validation only.

State and persistence: no state; it indexes into capability bitmaps declared elsewhere.

Dependencies and integration: used by cpufeature, alternatives, static branches, and code that guards capability-specific paths.

Risks: mismatched generated capability numbers break alternative patching and feature checks. Test signals are generated header consistency checks, allconfig builds, alternative patching tests, and cpufeature boot logs.
