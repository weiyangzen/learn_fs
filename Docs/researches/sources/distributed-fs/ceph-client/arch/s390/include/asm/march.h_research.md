# sources/distributed-fs/ceph-client/arch/s390/include/asm/march.h

Purpose: This header exposes compile-time machine-architecture level feature macros for s390 builds.

Important APIs/types/functions: `MARCH_HAS_Z10_FEATURES` is always defined, while `MARCH_HAS_Z196_FEATURES` through `MARCH_HAS_Z17_FEATURES` are defined from corresponding Kconfig options outside the decompressor.

Control flow: Architecture code uses these macros to choose instruction sequences or optimized per-CPU atomics at compile time.

State and persistence: There is no runtime state; the macros affect generated code.

Dependencies and integration points: It integrates Kconfig selected march levels with headers such as `percpu.h` and other instruction-selection code.

Risks and test signals: Using instructions above the configured baseline breaks older machines. Tests should include builds for each supported march baseline and boot/runtime checks on compatible emulators or hardware.
