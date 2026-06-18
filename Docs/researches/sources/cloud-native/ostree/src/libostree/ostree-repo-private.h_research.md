# sources/cloud-native/ostree/src/libostree/ostree-repo-private.h

Purpose: central private header for `OstreeRepo`, repository transaction state, locks, feature flags, configuration constants, and internal helper declarations shared across libostree implementation files.

Important APIs/types/functions: defines summary/cache constants, commit metadata keys, `OstreeRepoCommitModifier`, `OstreeRepoSysrootKind`, `OstreeRepoTxn`, `OstreeRepoLock`, feature-support enums, bootloader option enums, and the private `struct OstreeRepo`. It declares internal helpers for tmpdir allocation/locking, loose object checks, directory metadata writes, ref updates, repo file creation, traversal, commit modifier application, remote add/remove/get, GPG verification, object import, fs-verity, composefs, auto transactions, and object listing.

Control flow: this header has no executable flow, but it shapes the control flow of most repo operations by exposing fd-based repo internals, transaction fields, cache locks, remotes/config state, repo mode, object dirs, and feature flags to implementation units.

State and persistence: `struct OstreeRepo` holds persistent repository descriptors and cached configuration: repo/cache/object fds, remotes hash table, `GKeyFile` config, collection ID, repo mode, payload link threshold, default repo finders, sysroot/boot settings, fs-verity/composefs support, transaction state, and mutable caches. Many fields mirror on-disk repo layout or config and must stay synchronized with open/init code.

Dependencies/integration: included by nearly every libostree repo implementation in this group, including finders, libarchive, prune, and pull verification. It bridges public headers with internal subsystems such as remotes, refs, object storage, commit traversal, GPG, fs-verity, composefs, and sysroot configuration.

Risks: because it exposes the full private instance layout, unrelated implementation files can become tightly coupled to fields like `device`, `inode`, `repo_finders`, `payload_link_threshold`, and fd members. ABI is private but source churn can be high. Concurrency-sensitive fields are protected by different mutexes/locks, so callers must respect comments and established locking conventions.

Test signals: no single test covers this header; coverage is distributed across repo open/config, pull, commit, checkout, prune, finder, and storage tests. Changes here require broad build and integration testing.
