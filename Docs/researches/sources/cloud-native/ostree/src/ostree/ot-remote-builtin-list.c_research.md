# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list.c

Purpose: implements `ostree remote list`, optionally with URLs.

Important APIs/functions: `ot_remote_builtin_list()` opens a repo, obtains `ostree_repo_remote_list()`, and either prints one name per line or aligns names with URLs from `ostree_repo_remote_get_url()` when `--show-urls/-u` is set.

Control flow: parse options, retrieve remotes and count, compute max name length for URL mode, print each row.

State/persistence: read-only inspection of repo remote config.

Dependencies/integration: depends on libostree remote listing/get-url APIs and shared option parsing.

Risks: URL lookup failure for any remote aborts the full listing. Aligned output is human-oriented and script consumers should prefer simpler name-only output.

Test signals: `tests/admin-test.sh` runs `ostree --repo=sysroot/ostree/repo remote list -u` and verifies a changed origin remote URL appears.
