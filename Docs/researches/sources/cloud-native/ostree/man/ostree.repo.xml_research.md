# sources/cloud-native/ostree/man/ostree.repo.xml

Purpose: This DocBook refentry introduces OSTree repository structure and layout. It frames an OSTree repository as a git-like content-addressed object store for filesystem trees, with OS-specific metadata such as uid, gid, permissions, and extended attributes.

Important concepts: The key public concepts are repository modes `bare`, `bare-user`, and `archive-z2`, the default system repository location, and the fact that the only user-editable component is the `config` file. It directs detailed configuration semantics to `ostree.repo-config(5)`.

Control flow and state: This is a documentation-only file, but it defines persistent repository state expectations: object storage, checkouts, archive transport, and default repository discovery. The documented default lookup path is used by CLI commands and many API calls when no command-line repository or `OSTREE_REPO` environment variable is specified.

Dependencies and integration points: Integrates with `ostree(1)`, repository initialization, checkout logic, archive serving over HTTP, and repository config parsing. It is the conceptual entry point for users before the detailed config manpage.

Risks: Default repository paths have changed historically across `/ostree/repo` and `/sysroot/ostree/repo` contexts, so this page must remain synchronized with actual CLI lookup behavior. The mode list is brief and may omit newer modes if implementation expands.

Test signals: Documentation tests should verify referenced manpage names and modes against the implementation and generated manpage set. CLI smoke tests can assert default repository discovery with `--repo`, `OSTREE_REPO`, current-directory repos, and the system repo.
