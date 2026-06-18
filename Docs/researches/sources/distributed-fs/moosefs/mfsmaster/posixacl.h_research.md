# sources/distributed-fs/moosefs/mfsmaster/posixacl.h

## Purpose
`posixacl.h` declares the master ACL API used by filesystem metadata code, restore/load code, and permission checks. It intentionally hides the ACL table layout behind opaque `void *` handles for get-data workflows.

## Important APIs, Types, And Functions
The header includes `<inttypes.h>` and `bio.h`. It exports mode synchronization (`posix_acl_getmode`, `posix_acl_setmode`), permission checks (`posix_acl_accmode`), lifecycle operations (`posix_acl_set`, `posix_acl_remove`, `posix_acl_copy`, `posix_acl_copydefaults`), serialization helpers (`posix_acl_get_blobsize`, `posix_acl_get_data`, `posix_acl_getall`, `posix_acl_store`, `posix_acl_load`), comparison (`posix_acl_check`), and lifecycle (`posix_acl_cleanup`, `posix_acl_init`).

## Control Flow
Callers usually set or remove ACLs through filesystem-level operations rather than manipulating nodes directly. Query paths ask for blob size and opaque node pointer first, then call `posix_acl_get_data()` to fill permissions and the packed named-entry blob. Metadata load/store paths pass a `bio` stream to the module.

## State, Persistence, And Dependencies
The header exposes no concrete state. Persistence is delegated to the implementation through `bio *` streams. ACL type and permission constants are expected from `MFSCommunication.h` in callers and implementation.

## Integration Points
`filesystem.c` is the main caller for ACL flags, permission checks, FACL packets, and metadata mutations. `restore.c` indirectly feeds ACL mutations by parsing `SETACL`. Metadata loaders/storers call `posix_acl_load()` and `posix_acl_store()`.

## Risks
The declaration of `posix_acl_set()` returns `int`, but the implementation returns `void`. That is the main header-level risk.

The opaque pointer returned by `posix_acl_get_blobsize()` is only valid while the ACL node remains present and unmodified. Callers should not cache it across mutations.

## Test Signals
Compile warnings or errors around `posix_acl_set()` are important. API tests should also confirm callers tolerate missing ACLs (`posix_acl_get_blobsize()` returns `-1`) and use `posix_acl_get_data()` only after a successful size query.
