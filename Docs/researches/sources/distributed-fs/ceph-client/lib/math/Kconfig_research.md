# sources/distributed-fs/ceph-client/lib/math/Kconfig

Purpose: Declares optional math-library Kconfig symbols for CORDIC, polynomial evaluation, prime number generation, and rational approximation.

Important APIs/types/functions: Defines `CONFIG_CORDIC` as a tristate visible option with help text, `CONFIG_PRIME_NUMBERS` as a visible test-support generator, and hidden tristates `CONFIG_POLYNOMIAL` and `CONFIG_RATIONAL`.

Control flow: Build-time only. Selected symbols drive `lib/math/Makefile` object inclusion and whether modules or built-ins are produced.

State and persistence: No runtime state. The selected configuration persists in the kernel build `.config`.

Dependencies/integration: Integrates with Kbuild and the math source files in the same directory.

Risks: Hidden symbols rely on users or drivers selecting them. Misconfiguration can omit helpers needed by dependent drivers.

Test signals: KUnit tests are controlled by separate test symbols in the tests Makefile; this Kconfig fragment itself has no tests.
