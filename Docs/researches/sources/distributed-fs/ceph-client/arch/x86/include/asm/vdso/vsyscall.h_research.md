# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/vsyscall.h

Purpose: Provides x86 vDSO/vsyscall layout constants and includes the generic vDSO-vsyscall interface after the architecture page layout is defined.

Important APIs/types/functions: `__VDSO_PAGES` is 6. `VDSO_NR_VCLOCK_PAGES` is 2. `VDSO_VCLOCK_PAGES_START(base)` computes where clock pages begin inside the vDSO mapping. `VDSO_PAGE_PVCLOCK_OFFSET` and `VDSO_PAGE_HVCLOCK_OFFSET` index the paravirtual and Hyper-V clock pages.

Control flow: No runtime code here. Generic vDSO code uses the constants to locate architecture vclock pages.

State and persistence: Describes per-mm vDSO mapping layout. The vclock pages are shared kernel/hypervisor-updated pages mapped with the vDSO.

Dependencies and integration points: Includes `vdso/datapage.h`, `asm/vgtod.h`, and then `asm-generic/vdso/vsyscall.h`. It pairs with x86 vDSO mapping code and `gettimeofday.h`.

Risks: Page count and offset mismatches break vDSO image layout or cause time code to read the wrong page. The include order matters because generic code expects architecture constants to be defined first.

Test signals: vDSO mapping layout tests, clock mode tests for pvclock and Hyper-V, and build coverage.
