<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-verify-result.c -->
# sources/cloud-native/ostree/tests/test-gpg-verify-result.c

## Purpose
`test-gpg-verify-result.c` unit-tests `OstreeGpgVerifyResult`, the object that exposes GPGME verification details to OSTree callers. It validates counts, lookup, per-signature attributes, and valid-signature requirements across multiple signature states.

## Important APIs, Types, And Functions
Important helpers include `assert_no_gpg_error`, `assert_str_contains`, `TestFixture`, `test_fixture_setup`, and `test_fixture_teardown`. The tests call `ostree_gpg_verify_result_count_all`, `count_valid`, `lookup`, `get`, `get_all`, and `require_valid_signature`. GPGME APIs include `gpgme_data_new_from_file`, `gpgme_data_write`, `gpgme_op_verify`, and `gpgme_op_verify_result`.

## Control Flow
The fixture points `GNUPGHOME` at `tests/gpg-verify-data`, loads `lgpl2` plus either the full detached signature or selected signature fragments, runs `gpgme_op_verify`, and attaches the referenced verify result to the fixture. Individual tests inspect tuple type strings, common attributes, valid/expired/revoked/missing states, lookup by full and abbreviated fingerprint, and error text from `require_valid_signature`.

## State And Persistence
The test is read-only except for process environment updates. Verification state is held in the fixture's `OstreeGpgVerifyResult`, GPGME data buffers, and referenced `gpgme_verify_result_t`.

## Dependencies And Integration Points
It uses private OSTree GPG headers, GPGME, GLib test fixtures, and static test key/signature data. It validates the low-level result object used by CLI show, pull verification, and other signature reporting paths.

## Risks And Test Signals
The test depends on stable GPGME status interpretation and fixture files. Passing signals include expected all/valid counts, lowercase fingerprint lookup, exact `GVariant` tuple shape, correct fallback names for missing keys, and failure messages for expired, revoked, missing, or expired-signature cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-verify-result.c -->
