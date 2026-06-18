<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/gpg-verify-data/gpg.conf -->
## sources/cloud-native/ostree/tests/gpg-verify-data/gpg.conf

Purpose: minimal GPG configuration fixture for signature verification tests.

Important APIs/functions: not executable; the file supplies GPG runtime settings used with a test homedir.

Control flow/state: no control flow. It influences `gpg` behavior when copied or referenced by shell tests.

Dependencies/integration: integrates with `libtest.sh` GPG fixture setup, exported test key IDs/fingerprints, and OSTree GPG verification tests.

Risks/test signals: small config changes can alter trust, keyring, or agent behavior. Test signal is successful deterministic signature verification in higher-level tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/gpg-verify-data/gpg.conf -->
