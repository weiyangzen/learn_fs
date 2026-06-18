# sources/cloud-native/ostree/src/libostree/ostree-repo-pull-verify.c

Purpose: implements signature verification support for pulls and public detached commit verification, covering GPG and OSTree signapi backends.

Important APIs/types/functions: `_signapi_init_for_remote`, `_sign_verify_for_remote`, `_process_gpg_verify_result`, `ostree_repo_signature_verify_commit_data`, and `_verify_unwritten_commit`. Internal helpers include `get_signapi_remote_option`, `_signapi_load_public_keys`, `string_is_gkeyfile_truthy`, `verifiers_from_config`, and `validate_metadata_size`.

Control flow: signapi initialization reads remote options `sign-verify` and `sign-verify-summary`. Boolean true means all compiled sign types with optional configured keys; a list means explicit required sign types whose keys must load from `verification-<type>-file` and/or `verification-<type>-key`. Verification scans configured signers, looks up each signer's metadata key in detached metadata, and accepts the first valid signature. Public commit verification validates metadata sizes, requires detached metadata, checks remote GPG/signapi configuration, runs enabled verifiers, and returns textual results. Pull-time `_verify_unwritten_commit` verifies GPG and/or signapi before writing a commit and records verified checksums.

State and persistence: verification itself is read-only, but pull verification updates `verified_commits` and `signapi_verified_commits` caches and emits the repo `gpg-verify-result` signal. It consumes remote config and detached metadata.

Dependencies/integration: depends on `OstreeSign`, GPGME-backed repo verification when enabled, remote option readers, pull state in `OtPullData`, metadata variant formats, and fetch/pull code that calls verification before object import.

Risks: commit metadata is mandatory for signapi and public verification; missing detached metadata fails. If both GPG and signapi are enabled, both must succeed. Boolean/list parsing follows GKeyFile truthiness and list semantics, so config mistakes can change enforcement strength. Error reporting preserves only the first signapi verification error with a count of other invalid signatures. GPG code is excluded when `OSTREE_DISABLE_GPGME` is defined.

Test signals: `tests/test-signed-pull.sh`, `tests/test-signed-pull-summary.sh`, `tests/test-pre-signed-pull.sh`, and `tests/test-commit-sign-sh-ext.c` cover signapi/GPG configuration, missing metadata, invalid keys/signatures, public verification, and pull failures.
