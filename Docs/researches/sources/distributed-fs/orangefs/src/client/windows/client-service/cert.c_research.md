# sources/distributed-fs/orangefs/src/client/windows/client-service/cert.c

## Purpose
This file loads, verifies, and converts certificate material into OrangeFS `PVFS_credential` objects for the Windows client service. It supports proxy certificates that embed UID/GID policy data and user certificates signed with local private keys for server-side identity mode.

## Important APIs, types, and functions
- OpenSSL lifecycle: `openssl_init`, `openssl_cleanup`.
- Thread-safe ex-data index helpers: `get_proxy_auth_ex_data_cred`, `get_proxy_auth_ex_data_user_name`, protected by `CRYPTO_ONCE` and `CRYPTO_RWLOCK`.
- Credential parsing: `parse_credential` accepts `uid/gid` text from proxy certificate policy data.
- Verification callback: `verify_callback` extracts proxy cert policy and initializes the output `PVFS_credential`.
- Certificate verification: `verify_cert` builds an `X509_STORE`, attaches CA cert/chain, enables proxy certs, and calls `X509_verify_cert`.
- Path helpers: `get_profile_dir`, `get_module_dir`.
- Public credential loaders: `get_proxy_cert_credential` and `get_user_cert_credential`.

## Control flow
For proxy certificates, `get_proxy_cert_credential` resolves the certificate directory from `goptions->cert_dir_prefix` or the Windows user profile, loads `cert.0` as the proxy cert and other `cert.*` files as chain certificates, loads `goptions->ca_file`, and calls `verify_cert`. During OpenSSL verification, `verify_callback` sees proxy certs, extracts `NID_proxyCertInfo`, parses the policy text as UID/GID, and initializes the credential. Successful verification duplicates the certificate expiration and gives the credential the maximum security timeout.

For user certificates, `get_user_cert_credential` resolves a key file path and certificate file path from configured paths, the module directory for `SYSTEM`, or the user's profile. It loads `orangefs-cert.pem`, converts X509 to `PVFS_certificate`, duplicates the expiration time, and calls `init_credential` with `PVFS_UID_MAX`, group `PVFS_GID_MAX`, the private key file, and attached certificate data.

## State and persistence behavior
The file reads certificate/key files from profile directories, configured certificate prefixes, module directories, and a configured CA file. It returns heap-owned credential internals through `init_credential` and an expiration `ASN1_UTCTIME` pointer used by the user cache. It also maintains process-global OpenSSL ex-data indexes and a lock.

## Dependencies and integration points
It depends on Windows profile APIs, OpenSSL X509/proxy certificate APIs, OrangeFS certificate utility functions (`PINT_load_cert_from_file`, `PINT_X509_to_cert`, `PINT_get_security_path`, `PINT_cleanup_cert`), credential initialization from `cred.c`, global `goptions`, `client_debug`, and `report_error`. It is called by `dokan-interface.c` when user mode is certificate or server.

## Risks and edge cases
- OpenSSL cleanup functions used here include APIs deprecated or changed across OpenSSL versions.
- `verify_callback` directly dereferences proxy extension fields; malformed extensions can expose null-pointer paths.
- Proxy credential parsing accepts up to 15 digits and uses `atoi`, so overflow and empty component handling are weak.
- Directory/path concatenation uses `strcpy`/`strcat`; some length checks exist but not all intermediate filenames are bounded after `FindFirstFile`.
- If loading a chain cert succeeds, ownership transfers into the stack; if a later push fails it is not handled.
- `get_proxy_cert_credential` treats `SYSTEM` as root credentials, which is operationally convenient but high trust.
- `get_user_cert_credential` sets UID/GID to max sentinel values and relies on server-side certificate handling; callers must not use those as local POSIX identities.

## Test signals
Test valid proxy certificate chains with UID/GID policies, missing `cert.0`, malformed policy strings, expired/untrusted certs, custom `cert_dir_prefix`, long profile paths, `SYSTEM` requests, user cert mode with missing key/cert, and OpenSSL initialization/cleanup under repeated service start/stop.
