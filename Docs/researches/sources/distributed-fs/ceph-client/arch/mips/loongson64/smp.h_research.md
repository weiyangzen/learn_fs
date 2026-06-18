<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.h -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.h

Purpose: Defines Loongson-3 legacy SMP mailbox/IPI register base macros and offsets.

Important APIs/types/functions: Declares `smp_group[4]`; defines group bases, core offsets, and offsets for status, enable, set, clear, mask, and mailbox buffer registers.

Control flow: Header constants are used by `smp.c` to construct per-core MMIO pointers.

State and persistence: No state; references global firmware-initialized `smp_group`.

Dependencies and integration: Coupled to Loongson-3 legacy IPI register layout.

Risks: Offsets assume four cores per group and at most four groups.

Test signals: Legacy IPI path should compute addresses matching firmware-documented mailbox registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.h -->
