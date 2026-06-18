# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rcu.h

Purpose: Provides glusterd's small wrapper around liburcu headers and defines an RCU callback head that can carry the current xlator pointer into deferred callbacks.

Important APIs and types: Includes URCU bulletproof, RCU list, compiler, atomic, and call-rcu headers, optionally includes `rculist-extra.h` for older URCU, and defines `gd_rcu_head` with `struct rcu_head head` followed by `xlator_t *this`.

Control flow: There is no runtime logic in this header. Users embed `gd_rcu_head` in larger objects and pass `&obj->rcu_head.head` to `call_rcu()`. The callback can recover the containing object and restore `THIS` from the saved xlator pointer.

State and persistence: `gd_rcu_head` stores transient deferred-free metadata and the xlator pointer needed when the callback runs. It has no on-disk persistence.

Dependencies and integration points: Used by peer utilities in this group for deferred `glusterd_peerinfo_t` destruction. It integrates liburcu callback semantics with Gluster's global `THIS` convention.

Risks: The comment and implementation rely on `struct rcu_head` being the first member of `gd_rcu_head`; changing field order would break `caa_container_of()` usage in callbacks. Saved `THIS` must remain valid until callback execution.

Test signals: Peer cleanup under RCU, repeated peer detach, sanitizer/valgrind runs around deferred frees, and builds against both old and current URCU variants.
