# sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_acl.c

## Purpose
Converts ACLs between NFS-Ganesha FSAL ACL representation and LizardFS ACL representation, and implements get/set ACL helpers.

## Important APIs, Types, And Functions
`lzfs_int_convert_fsal_acl` builds `liz_acl_t` from allow/deny FSAL ACEs. `lzfs_int_convert_lzfs_acl` allocates FSAL ACE storage and creates an `fsal_acl_t` via `nfs4_acl_new_entry`. `lzfs_int_getacl` fetches a LizardFS ACL, applies owner masks, converts it, and replaces any old FSAL ACL. `lzfs_int_setacl` converts and sends FSAL ACLs to LizardFS.

## Control Flow
Conversion preserves ACE type, flags, mask, uid/gid, and maps special owner/group/everyone identifiers between FSAL and LizardFS constants. Unsupported ACE types are skipped on FSAL-to-LizardFS conversion. Get releases any existing ACL entry, fetches remote ACL with request credentials, applies masks using owner id, converts, and destroys the LizardFS ACL.

## State And Persistence Behavior
Conversion allocations are transient. `setacl` persists ACL changes through the LizardFS master/client API. FSAL ACL references are managed through Ganesha ACL allocation/release functions.

## Dependencies And Integration Points
Depends on `context_wrap`, `lzfs_internal`, Ganesha NFSv4 ACL helpers/macros, and LizardFS ACL C API. Called from `handle.c` getattrs/setattr2.

## Risks And Edge Cases
The unused `count` variable in FSAL-to-LizardFS conversion suggests incomplete preallocation logic. Skipping non-allow/deny ACEs changes ACL semantics if other ACE types are expected. Invalid special IDs are logged and skipped or normalized. Memory ownership must be exact: failed conversions need no leaked ACE arrays or ACL handles.

## Test Signals
No direct tests in subset. Round-trip ACL tests for special IDs, group/user IDs, allow/deny masks, empty ACLs, and invalid ACE handling are important.
