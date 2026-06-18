<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/vsyscall.h

Purpose: Connects PowerPC vDSO datapage definitions to the generic vDSO vsyscall implementation.

Important APIs/types/functions: Includes `asm/vdso_datapage.h` before `asm-generic/vdso/vsyscall.h`; it defines no standalone functions.

Control flow: Generic vDSO code is compiled after architecture datapage definitions are visible, allowing generic helpers to use PowerPC-specific layout/macros.

State and persistence: No runtime state is owned; it is an include-order integration header.

Dependencies and integration points: Depends on `asm/vdso_datapage.h` and generic vDSO vsyscall code. Used during PowerPC vDSO object builds.

Risks: Include order matters. Moving generic inclusion before the architecture datapage can create missing or mismatched definitions.

Test signals: PowerPC vDSO compile coverage and runtime vDSO syscall/time smoke tests.

Source read size: 14 lines, 358 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/vsyscall.h -->
