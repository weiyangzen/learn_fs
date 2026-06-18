# sources/distributed-fs/ceph-client/include/linux/ptrace_api.h

Purpose: provides a compatibility include shim that simply includes `linux/ptrace.h`.

Important APIs and types: no new APIs or types are defined; all functionality is inherited from `ptrace.h`.

Control flow: code including this header receives the generic ptrace declarations.

State and persistence: none.

Dependencies and integration points: depends entirely on `linux/ptrace.h`. It exists for include compatibility with code expecting `ptrace_api.h`.

Risks and test signals: risks are limited to include-cycle or stale compatibility expectations. Test by building users that include `ptrace_api.h` directly.
