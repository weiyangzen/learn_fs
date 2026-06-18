## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crashdump-ppc64.h

Purpose: defines the PPC64 kdump backup source region used by purgatory trampoline code.

Important APIs/types/functions: `BACKUP_SRC_START`, `BACKUP_SRC_END`, and `BACKUP_SRC_SIZE` describe the first 64 KiB of system RAM.

Control flow: constants only; crash/purgatory code copies or preserves this region during kexec crash handling.

State and persistence: no live state in the header. The region describes persistent physical memory content needed across crash transition.

Dependencies and integration: documented assumptions are consumed by `arch/powerpc/purgatory/trampoline_64.S` and kdump tooling.

Risks and test signals: constants must remain less than `UINT32_MAX` and at least 8-byte aligned. Changing them breaks purgatory assumptions. Test signals include PPC64 kdump, purgatory build/relocation checks, and crash dump validation of low-memory backup data.
