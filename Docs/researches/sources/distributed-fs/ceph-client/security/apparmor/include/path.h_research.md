# sources/distributed-fs/ceph-client/security/apparmor/include/path.h

## Purpose
`path.h` defines path-name generation flags and buffer helpers used by AppArmor path-based mediation.

## Important APIs
`enum path_flags` includes directory marking, socket condition handling, disconnected path connection, chroot-relative lookup, namespace root connection, deleted-file delegation, and deleted-file mediation. `aa_path_name` converts a kernel `struct path` into an AppArmor policy name. `aa_get_buffer` and `aa_put_buffer` manage temporary path buffers, with `IN_ATOMIC` indicating allocation constraints.

## Control flow and integration
File, domain, mount, and AF_UNIX filesystem socket mediation call `aa_path_name` before DFA matching. The flags are combined from profile path flags and operation-specific conditions.

## State and persistence
The header owns no persistent state. Buffers are temporary kernel allocations or per-CPU resources managed by the implementation.

## Dependencies
It depends on Linux path structures through function parameters and AppArmor profile flags.

## Risks
Path generation is a security boundary: disconnected/deleted/chroot-relative behavior determines the policy string that is matched. Buffer allocation failures can deny operations. Callers must release buffers exactly once.

## Test signals
Test normal, chrooted, disconnected, deleted, directory, and socket paths. Include atomic and sleepable buffer allocation paths.
