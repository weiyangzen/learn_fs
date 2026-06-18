# sources/cloud-native/ostree/man/ostree-pull.xml

Purpose: documents `ostree pull`, which downloads refs/commits from a remote repository.

Important APIs/types: required `REMOTE`, optional `BRANCH`; options `--commit-metadata-only`, `--cache-dir`, `--disable-fsync`, `--localcache-repo`, `--untrusted`, `--disable-static-deltas`, `--mirror`, `--subpath`, `--depth`, `--network-retries`, `--disable-retry-on-network-errors`, `--low-speed-limit-bytes`, `--low-speed-time-seconds`, `--max-outstanding-fetcher-requests`, and `--disable-verify-bindings`.

Control flow: resolves configured remote/branch list, optionally fetches all refs for mirror mode, supports `BRANCH@COMMIT` syntax for pinned fetches, downloads metadata/content/static deltas through curl/soup backends, writes refs under `remotes/REMOTE/` unless mirroring, and honors depth/subpath/cache/retry/concurrency options.

State and persistence: writes repo objects, summaries/cache usage, and refs.

Dependencies and integration: integrates remote config, HTTP fetch backends selected by configure, static deltas, local cache repos, binding verification, retry/low-speed network handling, and mirror publication.

Risks and test signals: risks include disabled verification, partial fetches, mirror ref layout, branch@commit semantics, and backend-specific retry behavior. Signals are network pull tests, mirror tests, static delta tests, depth/subpath tests, and binding verification failures.
