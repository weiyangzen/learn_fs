# sources/distributed-fs/ceph-client/arch/x86/boot/cpu.c

Purpose: user-facing wrapper around CPU requirement checks in setup code. It reports a readable failure reason when the CPU family or required feature flags are missing.

Important APIs and state: exports `validate_cpu()`. Helpers `cpu_name()` and `show_cap_strs()` format the required CPU family and missing feature names from generated `x86_cap_strs`.

Control flow: calls `check_cpu()` to populate detected level, required level, and missing feature flags. It prints family mismatch, feature-list mismatch, or KNL erratum failure, returning `-1`; otherwise returns 0.

Dependencies and integration: called by `main()` before BIOS mode setup and protected-mode transition. Depends on `cpucheck.c`, generated `cpustr.h`, and early `printf()`/`puts()`.

Risks and test signals: missing generated cap strings fall back to numeric word:bit output, but incorrect masks can block valid CPUs or permit invalid ones. Test by builds with different `CONFIG_X86_MINIMUM_CPU_FAMILY` and required feature masks, plus QEMU CPU models missing specific flags.
