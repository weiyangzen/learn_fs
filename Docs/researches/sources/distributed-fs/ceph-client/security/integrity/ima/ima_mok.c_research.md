<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_mok.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_mok.c

## Purpose
Initializes the optional IMA blacklist keyring used to reject revoked binary hashes or keys during appraisal.

## Important APIs, Types, And Functions
- Global `struct key *ima_blacklist_keyring`.
- `ima_mok_init()` allocates `.ima_blacklist` during `device_initcall`.

## Control Flow
At device init time, the code allocates a `key_restriction`, sets its check function to `restrict_link_by_builtin_trusted`, then creates a persistent root-owned keyring named `.ima_blacklist` with view/read/write/search permissions and keep-in-memory allocation flags. Allocation failure panics.

## State And Persistence
The keyring persists for the boot and is kept out of quota. It stores blacklist entries consulted by IMA appraisal paths such as `ima_check_blacklist()`.

## Dependencies And Integration Points
Depends on the Linux keyring subsystem, built-in trusted key restriction, current credentials during init, and blacklist lookup helpers used from appraisal code.

## Risks And Edge Cases
Failure to allocate the restriction or keyring panics the kernel when this feature is configured. Link restrictions mean blacklist entries must be trusted according to built-in key policy.

## Test Signals
Boot should log allocation of the IMA blacklist keyring. Loading a revoked hash/key should make appraisal fail with blacklist behavior, while untrusted additions should be rejected by the keyring restriction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_mok.c -->
