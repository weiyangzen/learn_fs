# sources/cloud-native/ostree/man/ostree-sign.xml

Purpose: documents `ostree sign`, which adds or verifies non-GPG signatures on commits.

Important APIs/types: required `COMMIT` and `KEY-ID...`; options `--verify`, `-s/--sign-type` with `ed25519`, `spki`, and `dummy`, `--keys-file`, and `--keys-dir`. It documents trusted/revoked key files and `.d` directories under `/etc/ostree` and `/usr/share/ostree`.

Control flow: signing appends a new signature even if the key already signed; verify reads keys from command line/files/system key dirs and validates signatures according to selected engine.

State and persistence: signing mutates commit signature metadata; verification is read-only. Trust/revocation files are persistent external policy state.

Dependencies and integration: depends on configure-enabled Ed25519/SPKI support via OpenSSL/libsodium, system key directories, pull/status verification, and commit metadata.

Risks and test signals: risks include duplicate signatures, private key leakage through command args, trust/revocation search path mistakes, and engine-specific key encoding. Signals are sign/verify tests for ed25519, spki, dummy, keys-file, keys-dir, trusted/revoked keys, and duplicate signature handling.
