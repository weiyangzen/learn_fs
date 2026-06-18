# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-summary.c

Purpose: implements `ostree remote summary`, fetching and dumping a remote summary file, selected metadata, or raw variant data, with optional signature display.

Important APIs/functions: `ot_remote_builtin_summary()` parses `--list-metadata-keys`, `--print-metadata-key`, `--cache-dir`, and `--raw`. It sets an optional cache dir, calls `ostree_repo_remote_fetch_summary()`, dumps metadata via `ot-dump` helpers, and when GPGME is enabled verifies/prints summary signatures with `ostree_repo_verify_summary()` and `ostree_print_gpg_verify_result()`.

Control flow: parse/open repo, validate remote name, configure cache, fetch summary/signature bytes, error if no summary exists, choose one of metadata-key listing, single metadata value, or full summary dump, then optionally print GPG signature details for non-raw output.

State/persistence: read-only from repo config; may use remote network/cache state. No repository config mutation.

Dependencies/integration: `ot-dump.h`, libostree remote summary fetch/verify APIs, optional GPGME support, GLib bytes/variant handling.

Risks: raw mode suppresses signature display. Summary verification happens during fetch; later signature parsing is for display. Missing summary is a command error. Cache-dir selection can affect test reproducibility.

Test signals: broader tests include summary update/view/pull summary scripts. This subset’s admin tests rely on summary/remote flows indirectly through pull/upgrade.
