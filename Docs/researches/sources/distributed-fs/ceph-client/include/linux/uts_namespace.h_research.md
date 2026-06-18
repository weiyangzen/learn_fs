# sources/distributed-fs/ceph-client/include/linux/uts_namespace.h

## Purpose
This header defines the UTS namespace object and helpers for copying, referencing, and freeing namespace-specific host/domain name state.

## Important APIs, types, and functions
Key type is `uts_namespace` containing `new_utsname`, `user_namespace`, `ucounts`, namespace common header, and refcount. APIs include `copy_utsname()`, `free_uts_ns()`, `get_uts_ns()`, `put_uts_ns()`, `uts_ns_init()`, and `to_uts_ns()`. Disabled builds reuse `init_uts_ns` and reject `CLONE_NEWUTS`.

## Control flow, state, and persistence
Clone/unshare calls copy or share the namespace based on flags; ref helpers manage lifetime; namespace operations access `name` under UTS locks in implementation code. State is runtime namespace identity and ownership accounting; there is no filesystem persistence.

## Dependencies and integration points
It depends on namespace proxy/common code, user namespaces, ucounts, sched, and UAPI utsname layout. It integrates with clone/unshare, uname/sethostname/setdomainname syscalls, and proc namespace handles.

## Risks and test signals
Risks include refcount leaks, wrong user namespace ownership, ucount limit bypass, and disabled-config behavior. Tests should cover clone/unshare semantics, namespace lifetime via proc fd, hostname isolation, and init namespace fallback.
