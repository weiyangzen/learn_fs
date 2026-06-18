<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyctl_pkey.c -->
# sources/distributed-fs/ceph-client/security/keys/keyctl_pkey.c

## Purpose
`keyctl_pkey.c` implements asymmetric public-key `keyctl` operations for query, encrypt, decrypt, sign, and verify. It is a syscall adapter around key-type-provided asymmetric callbacks.

## Important APIs, Types, and Functions
Entry points are `keyctl_pkey_query()`, `keyctl_pkey_e_d_s()`, and `keyctl_pkey_verify()`. Helpers include `keyctl_pkey_params_get()`, `keyctl_pkey_params_get_2()`, `keyctl_pkey_params_parse()`, and `keyctl_pkey_params_free()`. It parses `enc=<encoding>` and `hash=<digest>` into `struct kernel_pkey_params`.

## Control Flow
The query path copies the info string, parses unique options, looks up the key with search permission, requires `asym_query`, and copies `struct keyctl_pkey_query` back to userspace. Encrypt/decrypt/sign/verify copy user parameter lengths, call `asym_query` to validate them against maximum sizes, allocate input/output buffers, map the requested operation enum, and invoke the relevant key-type callback.

## State and Persistence
No durable state is owned here. Per-call state consists of copied info text, a referenced key, parsed parameter pointers into the info buffer, and temporary input/output buffers. `keyctl_pkey_params_free()` releases both the info buffer and key reference.

## Dependencies and Integration Points
This file integrates with asymmetric key types through `asym_query`, `asym_eds_op`, and `asym_verify_signature`. It depends on `lookup_user_key()`, user copy helpers, parser match tables, and the `KEYCTL_PKEY_*` syscall cases in `keyctl.c`.

## Risks
The parser rejects duplicate or empty options; relaxing that could make algorithm selection ambiguous. Length validation depends on key-type query results and must precede allocation/copy. A callback returning more bytes than `out_len` would break the copy contract, so key-type implementations must obey `kernel_pkey_params`.

## Test Signals
Test RSA/ECDSA or available asymmetric key types for raw and encoded operations, duplicate/unknown info options, oversized input/output lengths, missing callback support, invalid user buffers, verify failure, and disabled `CONFIG_ASYMMETRIC_KEY_TYPE` returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyctl_pkey.c -->
