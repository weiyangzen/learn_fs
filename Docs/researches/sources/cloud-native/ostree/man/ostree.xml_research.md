# sources/cloud-native/ostree/man/ostree.xml

Purpose: This is the top-level `ostree(1)` manpage. It explains OSTree as a system for managing multiple bootable, versioned, read-only filesystem trees installed under `/ostree`, and it indexes administrative and regular subcommands.

Important commands and concepts: Global options are `--repo`, `--verbose`, and `--version`. It lists administrative commands such as cleanup, deploy, init-fs, os-init, status, switch, undeploy, and upgrade, plus repository/tree commands such as cat, checkout, checksum, commit, config, create-usb, diff, find-remotes, fsck, init, log, ls, prune, pull, refs, remote, reset, rev-parse, show, static-delta, and summary. The terminology section defines branch, checksum, commit, ref, rev/refspec, and SHA256.

Control flow and state: The manpage documents the OSTree operating model: the running tree is not modified in place; upgrades prepare a new tree, perform a three-way config merge, and activate after reboot. Repository discovery falls back from explicit `--repo` to current directory, `OSTREE_REPO`, and then the system repository.

Dependencies and integration points: Integrates the CLI namespace, sysroot deployment model, repository model, bootable OS deployment workflow, GPG trust roots, per-remote keyrings, and subcommand manpages. It also describes trust integration through `/usr/share/ostree/trusted.gpg.d`, remote `gpgkeypath`, and per-remote trusted keyrings.

Risks: Because this file is an index, stale command lists or repository paths can mislead users broadly. Security-sensitive GPG guidance must remain accurate, especially the warning that private keys should not be stored in trusted public key directories. There is a typo in the SHA256 glossary text ("bites") that is documentation quality risk, not runtime risk.

Test signals: Manpage generation should verify every cited `ostree-*` and `ostree-admin-*` page exists. CLI integration tests should cover repository discovery order, `--version` feature output, GPG key import paths, and read-only deployment assumptions.
