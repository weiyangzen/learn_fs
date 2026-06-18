# sources/distributed-fs/ipfs-kubo/repo/fsrepo/doc.go

Purpose: package documentation sketching the intended filesystem repo layout and lock/profiling files.

Important APIs and control flow: no executable APIs. The comment documents a conceptual `.ipfs` tree with `client/`, `daemon/`, config, datastore, `repo.lock`, and version files.

State and persistence: describes persistent repo files and lock boundaries. The actual current implementation in `fsrepo.go` uses `repo.lock`, `config`, `datastore_spec`, `version`, `api`, `gateway`, `swarm.key`, keystore, and datastore directories; the doc still contains TODO roadmap text.

Dependencies and integration: package-level documentation for the `fsrepo` package.

Risks and test signals: because it is a TODO roadmap, it may be stale relative to actual files and should not be used as an authoritative layout contract without checking implementation and tests.
