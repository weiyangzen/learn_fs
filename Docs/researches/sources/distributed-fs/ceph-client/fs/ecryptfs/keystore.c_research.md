# sources/distributed-fs/ceph-client/fs/ecryptfs/keystore.c

## Purpose

`keystore.c` implements eCryptfs key-packet parsing and generation. It translates between persistent OpenPGP-inspired metadata packets, kernel keyring auth tokens, FEK encryption/decryption, public-key daemon callouts, and FNEK filename packets. It is the policy enforcement point for which mount/auth tokens can unlock or wrap a file encryption key.

## Important APIs, types, and functions

Exported functions include `ecryptfs_parse_packet_length()`, `ecryptfs_write_packet_length()`, `ecryptfs_keyring_auth_tok_for_sig()`, `ecryptfs_parse_packet_set()`, `ecryptfs_generate_key_packet_set()`, `ecryptfs_add_keysig()`, `ecryptfs_add_global_auth_tok()`, `ecryptfs_write_tag_70_packet()`, and `ecryptfs_parse_tag_70_packet()`.

Important packet helpers handle tag 1 public-key encrypted FEKs, tag 3 passphrase encrypted FEKs, tag 11 literal signature packets, tag 64/65/66/67 userspace-daemon messages, and tag 70 FNEK-encrypted filenames. Helper structs named `*_silly_stack` move large temporary state off the kernel stack for tag 70 operations.

## Control flow

For existing files, `ecryptfs_parse_packet_set()` walks metadata packets until a non-auth-token packet appears. Tag 3 packets produce password candidate tokens and must be followed by a tag 11 literal packet containing the auth-token signature. Tag 1 packets produce private-key candidate tokens. The function then searches mount-wide tokens first, optionally falls back to the user keyring, copies the matching secret material into the candidate token, decrypts the FEK via passphrase or PKI flow, computes the root IV, and initializes the crypt context. Failed candidates are removed and the next matching token is tried.

For new files, `ecryptfs_generate_key_packet_set()` iterates inode key signatures. For password tokens it writes a tag 3 packet containing the FEK encrypted by the session-key-encryption key, followed by a tag 11 signature packet. For private-key tokens it writes a tag 1 packet, potentially using ecryptfsd through tag 66 request and tag 67 response to encrypt the FEK. A boundary byte terminates the packet set.

Filename encryption uses tag 70. `ecryptfs_write_tag_70_packet()` finds the FNEK auth token, pads the plaintext name with deterministic non-null bytes derived from MD5 over the FNEK material, encrypts with the filename cipher and zero IV, and writes FNEK signature, cipher code, and encrypted name. `ecryptfs_parse_tag_70_packet()` validates size, resolves the FNEK token, decrypts, finds the null separator, and returns the plaintext suffix.

## State and persistence behavior

Persistent state is the packet set embedded in the lower file header or xattr and encrypted filename tag 70 packets embedded in lower dentry names. Runtime state includes mount-wide global auth-token references, per-inode key signature lists, per-call auth token candidate lists, and keyring references locked through key semaphores. Invalid global tokens are flagged and their key references dropped.

## Dependencies and integration points

The file depends on Linux keyrings, encrypted/user key payloads, skcipher, scatterlists, random/MD5 support, messaging APIs for ecryptfsd, and constants/types from `ecryptfs_kernel.h`. It is called by `crypto.c` for metadata and filename operations, by `main.c` while registering mount auth tokens, and by public-key flows through `messaging.c`/`miscdev.c`.

## Risks

This is a high-risk parser and key-management file. Packet length handling, maximum sizes, signature matching, and key semaphore lifetime must be correct. Legacy crypto choices include MD5, OpenPGP S2K MD5, CBC/ECB-like FEK wrapping paths, and unauthenticated packet contents. Verbose logging can dump secret material. Public-key support depends on a live userspace daemon for the caller's euid; timeouts and malformed daemon responses must fail closed.

## Test signals

Tests should cover packet length one-byte/two-byte boundaries and rejection of unsupported five-byte lengths, valid/invalid tag 1, 3, 11, 65, 67, and 70 packets, multiple key signatures with first-candidate failure fallback, missing/expired/revoked key errors, `ECRYPTFS_GLOBAL_MOUNT_AUTH_TOK_ONLY`, password and private-key mount flows, filename encryption/decryption round trips, malformed separator and oversize filename rejection, and messaging-disabled public-key failure behavior.
