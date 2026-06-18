# sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.c

## Purpose
This file implements `OstreeGpgVerifier`, the internal trusted-keyring manager and detached-signature verifier built on GPGME.

## Important APIs, Types, And Functions
`struct OstreeGpgVerifier` stores keyring `GFile`s, in-memory keyring data, and ASCII key file paths. Class init calls `gpgme_check_version()`. `_ostree_gpg_verifier_import_keys()` concatenates binary keyrings/data into a temporary `pubring.gpg`, then enables armor and imports ASCII keys with GPGME. `_ostree_gpg_verifier_list_keys()` builds a temporary GPG home, imports keys, and returns selected or all keys. `_ostree_gpg_verifier_check_signature()` creates an `OstreeGpgVerifyResult`, creates/imports into its temporary GPG home, wraps `GBytes` as GPGME data without copying, runs `gpgme_op_verify()`, refs the verify result details, and weak-ref hooks cleanup to result finalization. Add APIs support keyring files, keyring data, ASCII files, keyfile paths/dirs, keyring dirs, and global trusted keyring dir.

## Control Flow, State, And Persistence
Verification state is intentionally scoped to a temporary GPG home. On success, that temporary directory persists until the result object is finalized so later result inspection can resolve signing keys. On failure, the result and temporary directory are cleaned up. Global keyring defaults to `OSTREE_GPG_HOME` or `DATADIR/ostree/trusted.gpg.d/`.

## Dependencies And Integration Points
It depends on GPGME, ot-gpg-utils, libglnx, GLib/GIO, and the private result layout. Repository summary/commit verification code configures verifier keyrings and consumes `OstreeGpgVerifyResult`.

## Risks And Test Signals
Temporary home lifecycle and GPG agent cleanup are sensitive. Missing keyring files are ignored in one path but directory/open errors propagate elsewhere. Directory import filters only regular `.gpg` files excluding trustdb/secring. Tests should cover binary and ASCII key imports, global keyring env override, list-by-id and list-all, detached signature success/failure, missing/revoked/expired keys, tempdir cleanup on result finalize and error, cancellation, and directory traversal limitations.
