<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_api.h

Purpose: Compatibility shim that includes `linux/spinlock.h`. It exists so code including the older or narrower `spinlock_api.h` name receives the full generic spinlock API.

Important APIs/types/functions: Exports no definitions of its own; all visible symbols come from `spinlock.h`.

Control flow: A single preprocessor include redirects users to the canonical header.

State and persistence behavior: No state.

Dependencies: Entirely dependent on `linux/spinlock.h`.

Integration points: Source compatibility for call sites expecting `spinlock_api.h`.

Risks: Direct include can hide accidental dependency on the umbrella spinlock header; any semantic change is inherited from `spinlock.h`.

Test signals: Compile-only tests that include `spinlock_api.h` without separately including `spinlock.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api.h -->
