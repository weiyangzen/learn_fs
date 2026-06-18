# sources/distributed-fs/ceph-client/arch/x86/kernel/tls.c

## Purpose
`tls.c` implements x86 `set_thread_area`/`get_thread_area` TLS descriptor management and TLS regset access for ptrace/core-dump interfaces.

## Important APIs, Types, And Functions
Key functions are `do_set_thread_area()`, `set_thread_area`, `do_get_thread_area()`, `get_thread_area`, `regset_tls_active()`, `regset_tls_get()`, and `regset_tls_set()`. Internals include `get_free_idx()`, `tls_desc_okay()`, `set_tls_desc()`, and `fill_user_desc()`.

## Control Flow
Set copies a `user_desc`, accepts empty or historical zero descriptors, rejects 16-bit/non-data/non-present descriptors, optionally allocates a free slot, validates bounds, writes descriptors under `get_cpu()`, reloads TLS for current task, and refreshes segment registers or FS/GS bases as needed. Get validates or reads the index, masks it with nospec, converts the descriptor back to `user_desc`, and copies to userspace. Regset set validates alignment/count and descriptors before bulk update.

## State, Persistence, Dependencies, Integration
Persistent state is `thread.tls_array` and, on x86-64, possibly `thread.fsbase`/`gsbase`. Dependencies include descriptor helpers, LDT semantics, segment load helpers, nospec masking, regset/membuf APIs, and user access. IA32 TLS syscalls, clone TLS setup, ptrace regsets, and core dumping consume these helpers.

## Risks And Test Signals
TLS descriptors expose segmentation corner cases; rejecting 16-bit and non-present DPL3 descriptors avoids espfix/sandbox hazards. Segment reloads are critical on x86-64. Test slot allocation, empty/zero descriptors, invalid descriptors, bounds, current/non-current updates, FS/GS base propagation, ptrace regsets, and IA32 clone TLS.
