## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crash_reserve.h

Purpose: supplies PowerPC crash-kernel reservation policy constants and hooks.

Important APIs/types/functions: defines `CRASH_ALIGN` as `PAGE_SIZE` and, with generic crashkernel reservation, `arch_add_crash_res_to_iomem()` returning false.

Control flow: no runtime control flow beyond the inline hook. Generic crashkernel code queries whether the crash reservation should be added to `/proc/iomem`.

State and persistence: no state. It constrains crashkernel memory reservation alignment and resource reporting.

Dependencies and integration: integrates with generic crashkernel reservation and kdump memory setup.

Risks and test signals: alignment must match PowerPC crash/purgatory expectations. Incorrect resource reporting can confuse kexec-tools. Test signals include `crashkernel=` reservation, `/proc/iomem` inspection, kdump boot, and builds with/without generic reservation.
