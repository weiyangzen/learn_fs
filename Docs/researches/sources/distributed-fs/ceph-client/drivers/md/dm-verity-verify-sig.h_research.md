# sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.h

## Purpose
`dm-verity-verify-sig.h` declares the optional root-hash signature verification interface for dm-verity and supplies disabled-build stubs when signature verification support is not configured.

## Important APIs, Types, and Functions
The header defines the feature label, the `root_hash_sig_key_desc` option string, `struct dm_verity_sig_opts`, and `DM_VERITY_ROOT_HASH_VERIFICATION_OPTS`. Enabled builds declare root hash verification, option recognition/parsing, option cleanup, and module init/exit helpers. Disabled builds return neutral or rejecting stubs as appropriate.

## Control Flow
The main target uses `verity_verify_is_sig_opt_arg()` during optional argument parsing, `verity_verify_sig_parse_opt_args()` to consume the descriptor and fetch signature bytes, `verity_verify_root_hash()` after fixed arguments are parsed, and `verity_verify_sig_opts_cleanup()` on both success and error paths. Module init/exit are chained through the dm-verity target module lifecycle.

## State and Persistence Behavior
The header's only data type, `dm_verity_sig_opts`, stores a temporary signature buffer and size. Persistent or security-visible signature state lives in `struct dm_verity` under `CONFIG_SECURITY` in `dm-verity.h` and is populated by the target implementation.

## Dependencies and Integration Points
It integrates compile-time configuration with the main dm-verity target and `dm-verity-verify-sig.c`. The stubs keep the target code simple while ensuring signature options are unrecognized when verification is disabled.

## Risks and Test Signals
Tests should verify feature option count accounting, disabled-build behavior for signature options, cleanup after partial parse failure, and that enabled builds require exactly one argument for `root_hash_sig_key_desc`.
