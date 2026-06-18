# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-verify-sig.c

## Purpose
Implements optional dm-verity root-hash signature verification. It retrieves a PKCS#7 signature from a user key, verifies the root hash against trusted kernel keyrings, and supports a module parameter requiring signatures.

## Main Interfaces
- `verity_verify_is_sig_opt_arg()` recognizes the `root_hash_sig_key_desc` option.
- `verity_verify_sig_parse_opt_args()` parses the key description, loads signature bytes from the keyring, and stores the key description on `struct dm_verity`.
- `verity_verify_root_hash()` verifies a root hash and signature with `verify_pkcs7_signature()`.
- `verity_verify_sig_opts_cleanup()` frees temporary parsed signature data.

## Control Flow
Optional argument parsing consumes the key description following `root_hash_sig_key_desc`, requests a user key by that description, reads the user-key payload under the key semaphore, copies the signature into temporary constructor options, and records the key description in the verity target state. After all table arguments are parsed, `verity_verify_root_hash()` validates the root digest bytes against the signature. If no signature is supplied, verification succeeds unless the `require_signatures` module parameter is set.

## State And Synchronization
The file has a read-only module parameter `require_signatures`. Key payload access is protected by `down_read(&key->sem)` and released with `up_read()`. Temporary signature memory is held in `struct dm_verity_sig_opts` until constructor cleanup.

## Integration Points
Used by `dm-verity-target.c` during constructor option parsing and root hash validation. It depends on the Linux key retention service, user key type, and PKCS#7 verification API. Depending on configuration, verification uses the secondary trusted keyring or the default verification keyring argument.

## Notable Behaviors
- The root hash passed to signature verification is the hex-string table argument, not the decoded digest buffer.
- Missing signature returns success by default but `-ENOKEY` when signatures are forced.
- Invalid or revoked keys surface as constructor errors through `ti->error`.

## Risks And Review Focus
- Signature bytes are copied from user-key payloads; payload lifetime and key revocation handling depend on correct key semaphore use.
- `signature_key_desc` allocation happens even after signature retrieval errors unless allocation itself fails; constructor cleanup must free it.
- Callers should understand whether their trust policy requires `require_signatures` or explicit table signature options.
