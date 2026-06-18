# sources/distributed-fs/ceph-client/fs/crypto/policy.c

## Purpose
`policy.c` validates fscrypt policies, converts between UAPI policies and persisted contexts, implements policy ioctls, enforces encrypted-directory policy inheritance, writes new inode contexts, and parses test-dummy encryption mount options.

## Important APIs and Functions
- `fscrypt_policies_equal()`, `fscrypt_policy_to_key_spec()`, and `fscrypt_get_dummy_policy()` provide common policy utilities.
- `fscrypt_supported_policy()` dispatches to v1/v2 validation, including mode pairs, flags, casefold, direct-key, IV_INO_LBLK, stable inode, 32-bit inode, and data-unit-size checks.
- `fscrypt_new_context()` and `fscrypt_policy_from_context()` convert between in-memory policy and on-disk context.
- Ioctls: `fscrypt_ioctl_set_policy()`, `fscrypt_ioctl_get_policy()`, `fscrypt_ioctl_get_policy_ex()`, and `fscrypt_ioctl_get_nonce()`.
- `fscrypt_has_permitted_context()` enforces that encrypted directory trees contain only children with the same encryption policy.
- `fscrypt_policy_to_inherit()`, `fscrypt_context_for_new_inode()`, and `fscrypt_set_context()` support new inode creation.
- `fscrypt_parse_test_dummy_encryption()`, `fscrypt_dummy_policies_equal()`, and `fscrypt_show_test_dummy_encryption()` handle the testing mount option.

## Control Flow
Setting a policy copies the versioned policy from userspace, checks ownership/capability, obtains a write reference, locks the inode, and either sets a new policy on an empty live directory or returns `-EEXIST` if a different policy already exists. v2 policy setup verifies that the current user has added the requested key identifier. New inode creation later uses the inherited policy and nonce prepared by `keysetup.c`, builds a context, performs delayed IV_INO_LBLK_32 inode hashing if needed, and calls the filesystem `set_context()` callback.

## State and Persistence
This file is responsible for constructing the persisted fscrypt context bytes that store mode numbers, flags, key descriptor/identifier, data-unit size, reserved fields, and nonce. It also stores test-dummy policy state in the filesystem's mount option structure through caller-provided `fscrypt_dummy_policy`.

## Dependencies and Integration
It depends on filesystem fscrypt operations (`get_context`, `set_context`, `empty_dir`, `get_dummy_policy`, stable-inode queries, data-unit-size support), mount write coordination, inode ownership checks, keyring verification, random nonce generation, and key setup. Hooks and setup code call policy helpers to inherit, compare, and enforce contexts.

## Risks and Edge Cases
- v1 policies are still supported but warned as deprecated and rejected for casefolded directories.
- v2 flags `DIRECT_KEY`, `IV_INO_LBLK_64`, and `IV_INO_LBLK_32` are mutually exclusive.
- IV_INO_LBLK policies require stable 32-bit inode numbers and bounded data-unit-number width.
- `fscrypt_has_permitted_context()` permits two unrecognized policies to match for delete support, but otherwise fails closed on unexpected errors.
- `fscrypt_ioctl_set_policy()` has a gcc workaround when copying variable-size policies from userspace.
- `FS_IOC_GET_ENCRYPTION_NONCE` is explicitly for testing and exposes non-secret per-file nonce.

## Test Signals
Run ioctl coverage for set/get policy v1/v2, non-directory and non-empty directory rejection, policy mismatch returning `-EEXIST`, unsupported mode/flag/data-unit combinations, v2 key-not-added rejection, encrypted-tree child policy checks, context conversion round trips, IV_INO_LBLK capability gates, and test-dummy option conflicts.
