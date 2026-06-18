<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.h -->
## sources/distributed-fs/ceph/src/mds/locks.h

`locks.h` declares the table-driven MDS cache-lock state-machine schema and the complete `LOCK_*` state/action enum set. It is consumed by both C and C++ code and exposes four external state machines: simple, file, scatter, and local locks.

`sm_state_t` is the core row format. `next` identifies the stable state for transitional states, `loner` indicates exclusive client mode, `replica_state` is what replicas should see, permission chars encode read/projected-read/rdlock/wrlock/force-wrlock/lease/xlock availability, and cap masks describe caps for normal, loner, xlocker, and replica holders. `sm_t` binds a state array to global allowed/careful caps and remote-xlock policy.

The enum assigns numeric values for stable states (`LOCK_SYNC`, `LOCK_LOCK`, `LOCK_EXCL`, `LOCK_MIX`, `LOCK_TSYN`, `LOCK_XSYN`, `LOCK_SCAN`) and many transition states (`LOCK_SYNC_LOCK`, `LOCK_LOCK_SYNC`, `LOCK_PREXLOCK`, etc.). Action constants distinguish replica-directed negative actions from auth-directed positive actions.

State/persistence behavior is by convention: encoded locks elsewhere store enum values, while this header fixes their meaning. Any change in ordering is a compatibility change. Integration points include `SimpleLock`, `ScatterLock`, `Locker`, client capability calculation, journal replay, and MDS replica/auth coordination.

Risks: enum reorder breaks persisted or networked states; permission token semantics are compact and easy to misread; table consumers must handle zero/uninitialized rows; and negative/positive action direction must remain consistent. Test signals are compile coverage from C/C++ users, cap string/locker tests, replay of existing journal states, and assertions around `LOCK_MAX` table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.h -->
