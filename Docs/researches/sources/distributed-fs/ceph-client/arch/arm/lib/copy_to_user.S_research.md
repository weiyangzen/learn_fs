# sources/distributed-fs/ceph-client/arch/arm/lib/copy_to_user.S

Purpose: implements `arm_copy_to_user`/`__copy_to_user_std`, copying kernel memory to user memory and returning bytes not copied.

Control flow mirrors `copy_from_user` with kernel loads and user stores, optional Spectre range masking, and `copy_template.S` for aligned/unaligned forward copies. Exception-table fixups compute the remaining byte count. State is the destination user memory only. Dependencies include user store assembler macros, exception tables, PAN/domain configuration, and possible replacement by `uaccess_with_memcpy.c`. Risks are partial-copy accounting, stale user access permissions, unaligned destination paths, and faults after some bytes were stored. Test signals include valid/invalid user copies, page-boundary faults, and small/large copy thresholds.
