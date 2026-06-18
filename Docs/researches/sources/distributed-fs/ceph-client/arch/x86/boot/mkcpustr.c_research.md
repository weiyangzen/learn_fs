# sources/distributed-fs/ceph-client/arch/x86/boot/mkcpustr.c

Purpose: host-side generator that emits compact CPU feature-name strings for setup-code diagnostics.

Important APIs and state: standalone `main()` includes kernel cpufeature tables and prints C source defining `x86_cap_strs[]`. It only emits strings for features present in `REQUIRED_MASK*`, with each string prefixed by capability word and bit bytes.

Control flow: nested loops over `NCAPINTS` and 32 bits lookup `x86_cap_flags`, conditionally print preprocessor guards, and ensure the last entry is unconditional so the generated string is terminated.

Dependencies and integration: built and run during arch/x86 boot build to generate `cpustr.h`, included by `cpu.c`.

Risks and test signals: generated encoding must match `show_cap_strs()` parser. Test by regenerating after cpufeature table changes and by forcing missing required flags to verify readable output.
