# sources/cloud-native/ostree/tests/test-delta-sign.sh

Purpose: tests static delta signing through the dummy signature module and signature verification enforcement during offline apply.

Important APIs/functions: environment `OSTREE_DUMMY_SIGN_ENABLED=1`, `static-delta generate`, `--inline`, `--sign-type=dummy`, `--sign`, `static-delta verify`, `static-delta apply-offline`, and `core.sign-verify-deltas`.

Control flow: creates old/new commits from permuted binaries, confirms unsigned deltas fail verification, generates signed non-inline and inline deltas that verify, checks bad keys fail, applies offline without verification, then enforces verification to require keys and tests good/bad dummy keys.

State/persistence: writes archive repo deltas and repeated `repo2` bare-user apply targets. Dependencies include user xattrs and dummy signing feature flag.

Integration/risk/test signals: protects generic delta signature plumbing independent of real crypto. Risks are dummy module availability and exact error messages. Seven TAP cases cover verification and offline apply modes.
