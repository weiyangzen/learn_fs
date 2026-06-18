# sources/distributed-fs/openafs/src/afs/LINUX/osi_groups.c

## Purpose
This file implements Linux PAG management through process groups and, when configured, Linux keyrings. It handles `setpag`, preserves PAGs across `setgroups` syscall interception on non-keyring systems, defines the AFS PAG key type, and registers/unregisters keyring support.

## Important APIs, types, and functions
- `afs_linux_pag_from_groups` and `afs_linux_pag_to_groups` encode/decode PAGs in Linux `group_info`, either one-group or two-group style.
- `osi_get_group_pag` extracts the group-based PAG from an AFS credential.
- `afs_setgroups` installs a new group list in the AFS credential/current task and optionally parent task on old kernels.
- `__setpag` generates or applies a PAG value and rewrites group info.
- `setpag` wraps `__setpag`, installs a session keyring and `_pag` key when keyrings are enabled, and rolls back on failure.
- Non-keyring `afs_xsetgroups`, `afs_xsetgroups32`, `afs32_xsetgroups`, and `afs32_xsetgroups32` wrap setgroups syscalls to restore a lost PAG.
- Keyring callbacks `afs_pag_describe`, `afs_pag_instantiate`, `afs_pag_match`, and `afs_pag_destroy` define `key_type_afs_pag`.
- `osi_keyring_init`, `osi_keyring_shutdown`, and `osi_get_keyring_pag` register and query keyring PAG state.

## Control flow and behavior
For group-based PAGs, `__setpag` optionally calls `afs_genpag`, references the old group list, constructs a new group list with PAG groups inserted/replaced, installs it through `afs_setgroups`, and returns the old groups to the caller for rollback. `setpag` then optionally creates a session keyring, allocates an `_pag` key as root-owned, instantiates it with the new PAG, and converts negative keyring errors to positive AFS syscall errors. On failure it restores old groups, expires the newly marked user, and clears the output PAG.

Without keyring support, setgroups syscall wrappers record the old PAG, invoke the real syscall, then restore the PAG if the new groups dropped it. Architecture-specific 32-bit syscall variants are provided for PPC64, SPARC64, and AMD64.

With keyring support, `afs_pag_instantiate` verifies root ownership, payload size, current group PAG, and payload/PAG match before storing the PAG. Destroying a PAG key expires the corresponding AFS user under `AFS_GLOCK` as needed. `osi_get_keyring_pag` searches the session keyring, validates the key, returns the PAG, and may reinsert the PAG into current groups when the credential belongs to the current process.

## State and persistence
State lives in Linux task credentials/groups, session keyrings, the registered `key_type_afs_pag`, and AFS user/token state expired by PAG destruction. PAGs persist for the life of credentials/session keyrings and are mirrored between groups and keyrings in keyring builds.

## Dependencies and integration points
This code depends on Linux group-info, syscall hook pointers, credentials, keyring APIs, tasklist/RCU lookup for keyring type discovery, and OpenAFS PAG/token/user functions. It integrates with syscall-table probing/hooking, credential handling, and NFS translator behavior (`NFSXLATOR_CRED` is excluded from keyring PAG installation).

## Risks
PAG encoding in group lists is sensitive to sorted group order and kernel gid types. The non-onegroup branch contains assignments through `GROUP_AT(new, ...)` even though `new` is a pointer-to-pointer, making macro expectations important and worth compile coverage. Keyring install must handle quotas, restrictions, session keyring lifetime, and credential commit semantics. Syscall interception paths depend on locating writable syscall tables and correct 32-bit ABI hooks. Rollback paths must preserve group-info references exactly.

## Test signals
Run `setpag`/token tests with keyring and non-keyring builds, group list preservation across `setgroups`, one-group/two-group PAG encodings, root/non-root keyring quota behavior, session keyring absence, key destruction token expiry, NFS translator credentials, and 32-bit compatibility syscall wrappers on affected architectures. Reference-count and keyring leak tests are important.
