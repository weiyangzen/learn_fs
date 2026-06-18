# sources/distributed-fs/ceph-client/drivers/md/dm-verity-verify-sig.c

## Purpose
`dm-verity-verify-sig.c` implements optional dm-verity root-hash signature verification. It parses the `root_hash_sig_key_desc` target option, fetches a PKCS#7 signature blob from a user key, verifies the root hash against trusted keyrings, and owns the dm-verity keyring lifecycle.

## Important APIs, Types, and Functions
Important functions are `verity_verify_is_sig_opt_arg()`, `verity_verify_get_sig_from_key()`, `verity_verify_sig_parse_opt_args()`, `verity_verify_root_hash()`, `verity_verify_sig_opts_cleanup()`, `dm_verity_verify_sig_init()`, and `dm_verity_verify_sig_exit()`. Module parameters include `keyring_unsealed` and `require_signatures`.

## Control Flow
During target option parsing, `verity_verify_sig_parse_opt_args()` rejects duplicate signature descriptors, consumes the key description argument, retrieves the user key payload into `dm_verity_sig_opts`, and records the descriptor on `struct dm_verity`. Later `verity_verify_root_hash()` validates the root hash and signature: missing signatures are accepted unless `require_signatures` is set; supplied signatures are checked against the secondary or platform keyring if configured, then against the `.dm-verity` keyring if it contains keys and is restricted.

## State and Persistence Behavior
The file maintains a module-global `.dm-verity` keyring and module parameters. Per-target signature bytes are temporary in `dm_verity_sig_opts` until the main target copies them into security-facing target state; cleanup frees the temporary buffer. The keyring is allocated at module init, optionally sealed with `keyring_restrict()`, revoked and put at module exit.

## Dependencies and Integration Points
It depends on device-mapper argument parsing, Linux key/user-key APIs, PKCS#7 verification, optional secondary/platform keyrings, module parameters, and `dm-verity.h`. The main target calls init/exit at module registration, parser hooks during optional argument parsing, and root hash verification before accepting the table.

## Risks and Test Signals
Risks include accepting unsigned roots when policy requires signatures, mishandling revoked user keys, leaking signature buffers on parse failure, and unexpected keyring fallback behavior. Tests should cover no signature with and without `require_signatures`, invalid key description, revoked key payload, valid signature in each configured keyring, duplicate option rejection, keyring sealing behavior, and cleanup idempotence.
