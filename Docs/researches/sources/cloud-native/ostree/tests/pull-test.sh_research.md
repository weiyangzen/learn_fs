# sources/cloud-native/ostree/tests/pull-test.sh

Purpose: sourced TAP integration suite for pull behavior across HTTP, file URLs, mirrors, static deltas, GPG, corruption, timestamp checks, custom remotes, and bad server responses. It assumes a prepared HTTP server and `repo_mode` from the caller.

Important APIs/functions: local `repo_init()` recreates `repo` and adds `origin`; `verify_initial_contents()` checks checkout content. It drives `ostree pull`, `pull-local`, `remote add/delete`, `summary -u`, `static-delta generate`, `fsck`, `checkout`, `show`, and `rev-parse`.

Control flow: initializes a repo, verifies ordinary and per-object-fsync pulls, mirrors subsets/all refs, rejects unsafe bare-user-only content, injects corrupted objects/path traversal, tests detached metadata and timestamp rollback prevention, then exercises static delta dry-run, required-delta success/failure, inline and byteswapped deltas, custom backend errors, 404s, GPG signatures, and invalid ref HTML.

State/persistence: mutates `repo`, `mirrorrepo`, `ostree-srv/gnomerepo`, summaries, deltas, refs, commitpartial markers, remote config, and checkout trees. Dependencies include `libtest.sh`, `ostree-trivial-httpd`, xattrs, optional gpgme, tar fixtures, and shell assertions.

Integration/risk/test signals: covers the main network pull path and many security-sensitive failure modes. Fragility comes from exact progress regexes, HTTP fixture layout, feature-dependent branches, and compression-size tolerances. TAP `ok` lines and `fsck` calls are the primary success signals.
