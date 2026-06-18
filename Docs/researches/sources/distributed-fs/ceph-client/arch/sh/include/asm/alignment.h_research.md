# sources/distributed-fs/ceph-client/arch/sh/include/asm/alignment.h



Source read size: 22 lines, 654 bytes.



Purpose: unaligned access accounting and policy declarations.

Important APIs/types/functions: increment helpers, `UM_WARN`, `UM_FIXUP`, `UM_SIGNAL`, `unaligned_user_action()`, `unaligned_fixups_notify()`.

Control flow: trap/fixup code updates counters and consults user policy.

State and persistence: global counters/policy live in trap code.

Dependencies and integration points: exception handling, proc/sysctl policy, user signal delivery.

Risks and test signals: policy mistakes can hide faults or signal valid code. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
