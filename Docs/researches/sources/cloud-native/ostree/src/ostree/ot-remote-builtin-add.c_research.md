# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add.c

Purpose: implements `ostree remote add`, creating or replacing a remote configuration, optional branch restrictions, verification settings, content URL/custom backend settings, collection ID, and optional GPG import.

Important APIs/functions: `add_verify_opt()` parses `KEYTYPE=inline:DATA` or `KEYTYPE=file:/path` sign verification specs and adds `verification-<keytype>-key/file` variants. `ot_remote_builtin_add()` parses options, opens repo or sysroot via `ostree_parse_sysroot_or_repo_option()`, validates positional args, builds an `a{sv}` option variant, chooses `OstreeRepoRemoteChange`, calls `ostree_repo_remote_change()`, and optionally imports all GPG keys from `--gpg-import`.

Control flow: option parsing precedes sysroot/repo resolution. Custom backend mode permits `NAME` without URL; normal mode requires `NAME URL`. Branch arguments after URL become a `branches` string array. `--set` key/value options are parsed generically and inserted into the variant. GPG and sign verification flags are reconciled before remote change. GPG import is a post-create convenience path.

State/persistence: mutates repository remote configuration, either in repo config or sysroot remote config locations depending on libostree policy. Optional GPG import writes remote keyring data. No local state survives except static parsed option variables for the process.

Dependencies/integration: depends on `ot-main` repo/sysroot parsing, libostree remote APIs, signature plugin lookup via `ostree_sign_get_by_name()`, GVariant option passing, and optional GPGME code.

Risks: `--if-not-exists` with `--gpg-import` imports regardless of whether the remote already existed. `--no-sign-verify` conflicts with `--sign-verify`, but `--no-gpg-verify` also disables GPG verification when compiled with GPGME. Option names in `--set` pass through to config and need library-side validation.

Test signals: `tests/admin-test.sh` exercises remote add on a physical sysroot, nonphysical sysroot, and `core.add-remotes-config-dir=false`; it verifies whether remote config lands in repo config or deployment `/etc/ostree/remotes.d`.
