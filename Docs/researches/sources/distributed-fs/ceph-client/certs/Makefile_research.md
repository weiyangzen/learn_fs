<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Makefile -->
# sources/distributed-fs/ceph-client/certs/Makefile

## Purpose

`certs/Makefile` builds kernel certificate and blacklist artifacts. It compiles trusted keyring, blacklist, and revocation objects based on Kconfig, generates or extracts signing certificates, validates blacklist hash lists, embeds certificate lists, and builds the host `extract-cert` utility.

## Important APIs, Types, And Functions

Key build targets are `blacklist_hash_list`, `x509_certificate_list`, `signing_key.pem`, `x509.genkey`, `signing_key.x509`, and `x509_revocation_list`. Important commands are `cmd_check_and_copy_blacklist_hash_list`, `cmd_extract_certs`, `cmd_gen_key`, and `cmd_copy_x509_config`. The host program is `extract-cert`.

## Control Flow

Object inclusion follows `CONFIG_SYSTEM_TRUSTED_KEYRING`, `CONFIG_SYSTEM_BLACKLIST_KEYRING`, and `CONFIG_SYSTEM_REVOCATION_LIST`. The blacklist hash list is either generated as `NULL` or validated with the AWK checker and copied with a trailing `NULL`. Trusted certificate lists are produced by running `extract-cert` over configured PEM/PKCS#11 inputs. If the module signing key is the default path, the build generates a long-lived self-signed PEM key/cert using OpenSSL and the chosen key type.

## State And Persistence Behavior

The Makefile creates build-tree artifacts that are embedded into kernel objects by assembly files and C includes. Generated signing keys persist in the object tree unless removed. It does not mutate source files except through normal build outputs.

## Dependencies And Integration Points

It integrates with Kbuild variables, OpenSSL, `HOSTPKG_CONFIG`, `check-blacklist-hashes.awk`, `extract-cert.c`, `system_certificates.S`, `revocation_certificates.S`, and `blacklist_hashes.c`.

## Risks And Edge Cases

Build reproducibility and key secrecy matter. Auto-generated `signing_key.pem` must not be accidentally treated as a source-controlled production key. PKCS#11 URIs require special dependency filtering. Blacklist hash validation must run before C inclusion to avoid malformed source. ML-DSA key generation depends on host OpenSSL support.

## Test Signals

Tests should cover empty and populated certificate inputs, PKCS#11 input selection, generated key paths for each key type, invalid blacklist hashes failing the build, and object dependencies rebuilding when configured inputs change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Makefile -->
