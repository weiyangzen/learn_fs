# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/Kbuild

This Kbuild fragment declares generated and generic asm header wiring for Alpha. It asks kbuild to generate `syscall_table.h` and to use generic versions of `agp.h`, `asm-offsets.h`, `kvm_para.h`, `mcs_spinlock.h`, and `text-patching.h`.

There is no runtime control flow or persistence; the file affects generated header availability and include resolution during builds. Dependencies are kbuild's `generated-y` and `generic-y` mechanisms. Risks are missing generated syscall tables or accidentally shadowing a generic header with an incomplete arch-local version. Test signals are clean Alpha header generation and compile coverage for includes that expect these generic fallbacks.
