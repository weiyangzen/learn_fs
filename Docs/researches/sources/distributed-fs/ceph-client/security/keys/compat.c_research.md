# sources/distributed-fs/ceph-client/security/keys/compat.c

Purpose: Implements 32-bit compatibility dispatch for the `keyctl` syscall on 64-bit kernels.

Important APIs/types/functions: `COMPAT_SYSCALL_DEFINE5(keyctl, ...)` switches over `KEYCTL_*` operation codes and forwards to native helpers, converting 32-bit user pointers with `compat_ptr()` where needed.

Control flow: Each case calls the corresponding keyctl helper for keyring ids, joining, update, revoke, describe, clear/link/unlink/search/read, ownership/permission, instantiate/reject/invalidate, persistent keyrings, DH compute, keyring restriction, public-key operations, move, capabilities, and watch keys. Unknown operations return `-EOPNOTSUPP`.

State and persistence: No local state; all state changes occur in core key/keyring code.

Dependencies and integration: Depends on compat syscall layer, keyctl helper APIs, optional compat DH helper, public-key helpers, and watch queue support.

Risks and test signals: Risks are pointer conversion mistakes, argument width truncation, missing new KEYCTL operations in compat dispatch, and invalid reserved-argument handling for public-key query. Compat syscall tests should compare 32-bit userspace behavior to native keyctl for all supported options.
