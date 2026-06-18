# sources/distributed-fs/coda/coda-src/vol/vicelock.h

Purpose: defines the persistent advisory lock record embedded in vnode disk objects.

Important APIs/types: `ViceLock` contains `lockCount` and `lockTime`. `VICELOCKWAIT` is 30 minutes. `ViceLockCheckLocked` and `ViceLockClear` are simple macros for checking/clearing lock fields.

Control flow/state: the lock is part of `VnodeDiskObject`, so advisory lock state can be persisted or copied with vnodes. The "locked" check tests `lockTime == 0`, which is counterintuitive and should be verified against callers.

Dependencies/integration: included by `cvnode.h` and therefore by all vnode users. Risks include macro semantics, absence of owner identity in this structure, and stale persistent lock data. Test signals: vnode lock/unlock paths, timeout behavior against `VICELOCKWAIT`, and salvage/restore clearing behavior.
