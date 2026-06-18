# sources/distributed-fs/orangefs/src/client/windows/client-service/cred.c

## Purpose
This file creates, signs, copies cleanup responsibility for, and queries OrangeFS `PVFS_credential` objects used by the Windows client service.

## Important APIs, types, and functions
- `get_system_credential` creates a root uid/gid credential for the Windows `SYSTEM` user or fallback system operations.
- `sign_credential` reads or reuses an OpenSSL private key and signs stable credential fields with SHA1.
- `init_credential` allocates issuer/group/certificate/signature fields and applies security-mode-dependent signing.
- `cleanup_credential` frees fields allocated by `init_credential`.
- `credential_in_group` checks group membership.
- Disabled helpers show prior support for adding groups and setting timeout.

## Control flow
Callers allocate a `PVFS_credential` struct and call `init_credential`. It zeroes the struct, allocates an issuer string prefixed `C:` plus the local hostname, allocates and copies group ids, sets UID and long timeout, optionally attaches certificate bytes, and signs when `goptions->security_mode` is key or certificate. On failure it cleans allocated fields. `sign_credential` chooses a cached private key in key mode or loads a PEM key file, signs uid, group count, groups, issuer, and timeout, and stores signature bytes plus size.

## State and persistence behavior
Credentials are heap-backed and caller-owned. Signing may read persistent PEM key files. `goptions->private_key`, `security_mode`, and `key_file` influence behavior. Credential timeout is set to `time(NULL) + PVFS2_SECURITY_TIMEOUT_MAX`.

## Dependencies and integration points
It depends on OpenSSL EVP/PEM, OrangeFS request protocol types, `pint-util`, global `goptions`, Windows sockets hostname APIs, and service logging. `config.c`, `cert.c`, and `dokan-interface.c` all depend on these credential helpers.

## Risks and edge cases
- SHA1 signing is legacy and may be unacceptable in stricter security contexts.
- `EVP_MD_CTX_new` is not checked for null before use.
- `sign_credential` returns raw `errno` on key-file open failure after reporting a mapped PVFS error, while most callers expect negative PVFS/Windows-style errors.
- `cleanup_credential` does not free `cred->certificate.buf`, so certificate mode can leak attached certificate data.
- `init_credential` uses `gethostname` but assumes Winsock is initialized by the service.
- Timeout is always maximum, with TODO comments about server timeout/caching revision.

## Test signals
Test default root credential, list-mode unsigned credentials, key-mode signing with valid/missing/invalid PEM keys, cert-mode with attached certificate bytes, cleanup under all modes with leak detection, and hostname failure behavior.
