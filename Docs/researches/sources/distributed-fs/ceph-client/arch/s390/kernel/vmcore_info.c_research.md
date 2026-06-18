## sources/distributed-fs/ceph-client/arch/s390/kernel/vmcore_info.c

Purpose: Adds s390-specific metadata to vmcore notes for crash dump consumers and records the physical vmcore-info note address in absolute lowcore.

Important API: `arch_crash_save_vmcoreinfo()`.

Control flow: Emits symbols and lengths for `lowcore_ptr` and `high_memory`, appends s390 address-mode and relocation values (`SAMODE31`, `EAMODE31`, `IDENTITYBASE`, `KERNELOFFSET`, `KERNELOFFPHYS`), writes the physical note address into absolute lowcore `vmcore_info`, and releases the lowcore mapping.

State and persistence: Persists data in the vmcoreinfo note and absolute lowcore for dump tools/firmware.

Dependencies and integration: Depends on vmcore info helpers, absolute lowcore access, linker symbols for AMODE31, setup/KASLR state, and crash dump tooling expectations.

Risks and test signals: Risks are stale/missing relocation metadata and incorrect absolute lowcore update. Test signals include kdump vmcoreinfo contents, crash tool lookup of lowcore and AMODE31 ranges, and KASLR offset correctness.
