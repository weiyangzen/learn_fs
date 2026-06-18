# sources/distributed-fs/ceph-client/security/selinux/status.c

## Purpose
`status.c` implements the mmap-visible SELinux status page used by userspace to observe enforcing-mode and policy-load changes without a syscall on every access check.

## Important APIs, Types, and Functions
The exported functions are `selinux_kernel_status_page()`, `selinux_status_update_setenforce()`, and `selinux_status_update_policyload()`. They update a `struct selinux_kernel_status` located at the head of a lazily allocated page.

## Control Flow
`selinux_kernel_status_page()` takes `selinux_state.status_lock`, allocates and zeroes the page if needed, initializes version, sequence, enforcing, policyload, and deny_unknown, then returns the page reference. Update functions lock, check whether the page exists, increment `sequence` to an odd value, issue a write memory barrier, update fields, issue another barrier, and increment `sequence` again to an even value.

## State and Persistence
The status page is kernel memory owned by `selinux_state.status_page` and exposed through the SELinux status filesystem interface. It is not durable storage; it mirrors current kernel SELinux state. The sequence field implements seqlock-style observation for userspace readers.

## Dependencies and Integration Points
It depends on `selinux_state.status_lock`, `enforcing_enabled()`, and `security_get_allow_unknown()`. `services.c` calls `selinux_status_update_policyload()` after policy commit, and setenforce paths call `selinux_status_update_setenforce()`.

## Risks
Memory ordering is the main risk: userspace relies on odd/even sequence transitions and barriers. Updates are skipped if userspace has not yet requested the page. The initial `deny_unknown` value depends on active policy unknown-permission handling.

## Test Signals
Tests should mmap `/selinux/status`, verify initial fields, toggle enforcing mode, load policy, and ensure userspace sees even sequence changes with matching field updates. Race tests should poll while setenforce/policyload loops run.
