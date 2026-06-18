<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.c -->
# sources/distributed-fs/orangefs/src/common/security/security-util.c

## Purpose
Provides common helpers for formatting, copying, debugging, and cleaning `PVFS_capability`, `PVFS_credential`, and Windows security path data.

## Important APIs, Types, And Functions
Exports `PINT_print_op_mask`, `PINT_null_capability`, `PINT_capability_is_null`, `PINT_dup_capability`, `PINT_copy_capability`, `PINT_debug_capability`, `PINT_cleanup_capability`, `PINT_dup_credential`, `PINT_copy_credential`, `PINT_debug_credential`, `PINT_cleanup_credential`, and Windows-only `PINT_get_security_path`.

## Control Flow
Copy helpers first value-copy the structure, clear owned pointer fields, then deep-copy issuer, signatures, handle arrays, groups, and certificate buffers as applicable. Cleanup helpers free owned internals and clear or zero fields. Debug helpers emit issuer, ids, signatures, timeouts, masks, handles, groups, and certificate summaries. Windows path substitution replaces `%USERNAME%` tokens after checking output length.

## State And Persistence
No global state is owned. Functions allocate and free memory inside caller-provided structures and write debug logs. Windows path substitution is purely string processing.

## Dependencies And Integration Points
Depends on PVFS types/errors, gossip, `pint-util`, server config for declarations, and certificate-mode compile flags. Used by all security caches, signing/verification code, stubs, and client capability cache.

## Risks And Test Signals
Risks include assert-based issuer assumptions, cleanup setting credentials partially rather than full `memset`, copy failure cleanup paths, handling of the static `PVFS2_BLANK_ISSUER`, and Windows substitution edge cases. Tests should cover deep-copy independence, empty/null signatures, zero handles/groups, certificate-mode credential copies, repeated cleanup, op-mask formatting, and `%USERNAME%` path expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.c -->
