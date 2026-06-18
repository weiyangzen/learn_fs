# sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.h

Purpose: Defines the optional deferred-intent drain interface that coordinates online fsck with in-flight group metadata intent chains.

Important APIs, types, and functions: Under `CONFIG_XFS_DRAIN_INTENTS`, defines `struct xfs_defer_drain` and declares init/free, waiter gate, group intent get/put, drain, and busy helpers. Without the config, it defines an empty struct and maps group get/put to ordinary group refs.

Control flow: Intent creators increment as soon as work is added to a transaction and decrement only after finish or cancel. Drain callers wait only when they will not block intent completion.

State and persistence: Defines transient in-memory counters only.

Dependencies and integration points: Used by deferred work, allocation group/realtime group code, and online scrub/repair.

Risks and test signals: Risks are config-dependent behavior differences and misuse as a hard lock. Test `CONFIG_XFS_DRAIN_INTENTS=y/n` builds and scrub collision scenarios with chained intents.
