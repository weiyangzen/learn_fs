# sources/cloud-native/ostree/man/ostree-remote.xml

Purpose: documents `ostree remote`, which manages remote repository configuration, GPG keys, remote refs/summaries, and remote-specific cookies.

Important APIs/types: subcommands `add`, `delete`, `show-url`, `list`, `gpg-import`, `gpg-list-keys`, `refs`, `summary`, `add-cookie`, `delete-cookie`, and `list-cookies`. Options include add `--set`, `--if-not-exists`, `--force`, `--no-gpg-verify`, `--gpg-import`, `--collection-id`; list `--show-urls`; refs `--revision`, `--cache-dir`; gpg-import `--keyring`, `--stdin`; summary `--cache-dir`, `--raw`.

Control flow: adds/replaces/deletes remotes, displays URLs/listings, imports/list GPG keys, fetches remote refs/summary metadata, and manages per-remote cookie jar entries.

State and persistence: mutates repository remote config, keyrings, and cookies; refs/summary queries may use cache dirs.

Dependencies and integration: central to pull/upgrade, GPG verification, collection-id P2P sharing, repo config pages, HTTP authentication cookies, and summary parsing.

Risks and test signals: risks include disabling GPG verification, conflicting `--keyring`/`--stdin`, replacing remotes with `--force`, and leaking cookies. Signals are remote config round trips, GPG import/list tests, summary raw output tests, cookie tests, and pull behavior against configured remotes.
