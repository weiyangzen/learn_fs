# sources/distributed-fs/orangefs/src/client/webpack/d.authn/mod_authn_orangefs.c

## Purpose
This file implements an Apache HTTPD authentication provider named `orangefs`. It authenticates HTTP Basic credentials against OrangeFS management services, retrieves a short-lived OrangeFS user certificate and private key, stores them on disk for later OrangeFS client use, and caches a salted PBKDF2 password verifier so an unexpired certificate can be reused without contacting the OrangeFS servers again.

## Important APIs, Types, and Functions
- Apache integration uses `authn_provider`, `authn_status`, `request_rec`, `ap_register_provider`, `ap_hook_post_config`, `AP_INIT_TAKE1`, and the exported `authn_orangefs_module`.
- OpenSSL integration includes `X509`, `RSA`, `EVP_PKEY`, `PEM_read_X509`, `X509_cmp_time`, `X509_get_notAfter`, `RAND_bytes`, and `PKCS5_PBKDF2_HMAC`.
- OrangeFS/PVFS integration uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_mgmt_get_user_cert`, `PINT_cert_to_X509`, `PINT_save_cert_to_file`, `PINT_save_privkey_to_file`, `PINT_cleanup_cert`, and `PINT_cleanup_key`.
- `is_valid_cert()` reads an existing PEM certificate and treats it as valid only when its `notAfter` timestamp is still in the future.
- `store_password()` writes a 128 byte local verifier: 64 random salt bytes followed by a 64 byte PBKDF2-HMAC-SHA512 derived value using 10,000 iterations.
- `check_password()` loads the verifier, recomputes PBKDF2-HMAC-SHA512 with the stored salt, and compares the derived value with `memcmp`.
- `authn_check_orangefs()` is the provider entry point. It decides whether to reuse cached artifacts or obtain new credentials from OrangeFS.

## Control Flow
1. `register_hooks()` sets certificate validity to 60 minutes, registers `post_config`, and registers the provider as `AUTHN_PROVIDER_GROUP` name `orangefs`.
2. Apache configuration directives populate global `certpath`, `exp`, `mntpt`, and `pvfsinit`.
3. `post_config()` initializes PVFS only when `PVFSInit` selected this module, then appends the module version component.
4. On authentication, `authn_check_orangefs()` constructs `<certpath>/<user>-cert.pem`, `<user>-key.pem`, and `<user>-hash`.
5. If all cached files exist and the certificate is unexpired, the module verifies the password hash and grants access.
6. Otherwise it deletes cache files, resolves the configured OrangeFS mount point, discovers server addresses, requests a user cert/key from OrangeFS, saves them, stores the verifier, and grants access.

## State and Persistence Behavior
- Module settings are process-global static variables rather than per-server or per-directory config objects.
- Persistent auth cache files live under `AuthOrangeFSCertPath` and are named from the Apache username.
- The private key file is chmodded to `0600`; the password hash file is created with owner read/write mode.
- A stale or incomplete credential triplet is removed with `unlink()` before a fresh certificate request.
- Certificate lifetime is controlled by `AuthOrangeFSCertValidity` and passed to `PVFS_mgmt_get_user_cert()`.

## Dependencies and Integration Points
- Requires Apache HTTPD authn provider APIs, APR, OpenSSL, and OrangeFS/PVFS management APIs.
- The saved cert/key files are consumed by other OrangeFS client paths, especially the WebDAV module's `DAVpvfsCertPath`/`credInit()` flow.
- `PVFSInit` coordinates process-wide OrangeFS initialization with other OrangeFS Apache modules.

## Risks and Edge Cases
- `certpath` is not checked before constructing paths.
- Path buffers are fixed at 256 bytes and `snprintf` truncation is not checked.
- Username text is inserted into filesystem paths without sanitization.
- `memcmp` is not constant time for password verifier comparison.
- `open()` in `store_password()` does not use `O_TRUNC`.
- `chmod()` failure is logged but authentication still succeeds.
- Global static config is not virtual-host safe.
- Concurrent requests for the same user can race while unlinking or rewriting cache files.

## Test Signals
- Test certificate validation with expired, future, malformed, and missing PEM files.
- Test password verifier success, wrong password, truncated file, and permission errors.
- Integration-test OrangeFS success and ENOENT/EACCES/EINVAL mappings.
- Test Apache directives and `PVFSInit` coordination.
- Add concurrency tests for first login and cache refresh of the same user.
