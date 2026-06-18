# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-list-keys.c

Purpose: implements `ostree remote list-gpg-keys`, dumping configured GPG keys for one remote or all remotes.

Important APIs/functions: `ot_remote_builtin_list_gpg_keys()` opens the repo, treats `argv[1]` as optional remote name, calls `ostree_repo_remote_get_gpg_keys()`, and prints each key with `ot_dump_gpg_key()`.

Control flow: parse/open repo, fetch keys into `GPtrArray`, iterate and dump, stopping on any dump error.

State/persistence: read-only; it inspects remote keyring data and writes text to stdout.

Dependencies/integration: uses `ot-dump.h` formatting helpers and libostree remote key APIs.

Risks: output format is owned by `ot_dump_gpg_key()` and may be consumed by scripts. Large keyrings produce unbounded stdout.

Test signals: likely covered by `tests/test-remote-gpg-list-keys.sh` in the broader tree; not one of this item’s final source files.
