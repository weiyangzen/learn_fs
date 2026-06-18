<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/access-helper.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/access-helper.h

Purpose: provides small helpers for exception-safe instruction/address fetching from user or kernel context.
Important APIs and types: defines `__get_inst` and `__get_addr`, choosing `get_user` for user addresses and direct/kernel nofault access for kernel addresses.
Control flow: exception emulation code passes a user flag; helpers fetch the instruction or address and report fault status.
State and persistence: no persistent state; outputs are copied into caller variables.
Dependencies and integration: used by unaligned access and instruction emulation paths, depends on `linux/uaccess.h`.
Risks and test signals: wrong user/kernel selection can fault in atomic context or bypass access checks. Signals include unaligned access tests and fault injection with invalid user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/access-helper.h -->
