# sources/distributed-fs/ceph-client/include/linux/pti.h

Purpose: provides a generic include wrapper for Page Table Isolation initialization and finalization.

Important APIs and types: with `CONFIG_MITIGATION_PAGE_TABLE_ISOLATION`, it includes architecture `asm/pti.h`; otherwise `pti_init()` and `pti_finalize()` are empty inline stubs.

Control flow: architecture/init code can call `pti_init()` early and `pti_finalize()` later without open-coding config guards. Enabled builds dispatch to arch-specific PTI setup.

State and persistence: no state is defined here; enabled architectures maintain PTI page table and mitigation state.

Dependencies and integration points: depends on architecture PTI implementation and mitigation config. It integrates boot-time CPU vulnerability mitigation with generic init code.

Risks and test signals: risks include init ordering bugs, disabled stubs masking missing mitigation, and architecture header drift. Test PTI-enabled and disabled boot paths, CPU vulnerability reporting, and page table isolation correctness under syscall/interrupt transitions.
