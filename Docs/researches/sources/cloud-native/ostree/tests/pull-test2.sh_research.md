# sources/cloud-native/ostree/tests/pull-test2.sh

Purpose: small sourced continuation for pull checkout semantics, focused on the state produced by a remote pull into the selected repository mode.

Important APIs/functions: defines the same `repo_init()` pattern as `pull-test.sh`, computes `COMMIT_ARGS`, `CHECKOUT_U_ARG`, and `CHECKOUT_H_ARGS` based on bare, bare-user, or bare-user-only mode, then relies on caller-provided `$OSTREE`, `${CMD_PREFIX}`, `is_bare_user_only_repo`, and assertion helpers.

Control flow: creates a fresh repo, adds `origin` without signature verification, normalizes checkout/commit flags for the repo mode, and runs compact pull/checkout checks rather than the broad corruption and delta matrix in `pull-test.sh`.

State/persistence: recreates `${test_tmpdir}/repo` and writes remote configuration. It is intentionally sourced, so environment variables and shell options propagate into the caller.

Integration/risk/test signals: validates mode-sensitive checkout behavior through command success and assertions. The main risk is duplicated flag-selection logic drifting from `basic-test.sh` and `pull-test.sh`.
