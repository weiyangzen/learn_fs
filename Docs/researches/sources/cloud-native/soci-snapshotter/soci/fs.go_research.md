# sources/cloud-native/soci-snapshotter/soci/fs.go

Purpose: this small helper ensures the SOCI snapshotter root directory exists with restricted permissions before ORAS/local content-store code can create it with broader defaults.

Important API: `EnsureSnapshotterRootPath(root string) error` substitutes `config.DefaultSociSnapshotterRootPath` when root is empty, stats the path, creates it with mode `0700` if missing, and returns any stat or mkdir errors.

Control flow: the function distinguishes non-existence via `os.IsNotExist`, creates only the final root component, and treats an existing path as success. It does not call `MkdirAll`, so parent directories must exist.

State and persistence: it creates a filesystem directory and does not otherwise persist metadata. The comment says restricted permissions `0711`, but the actual mode is `0700`; the implementation is the source of truth.

Dependencies and integration points: depends on `config.DefaultSociSnapshotterRootPath`. It is relevant before initializing SOCI content stores or artifact DBs under the snapshotter root.

Risks: parent directory absence returns an error. Existing directories with broad permissions are accepted and not tightened. The comment-mode mismatch may confuse hardening reviews.

Test signals: `fs_test.go` covers missing and existing custom roots but not default root substitution, parent-missing failure, or permission assertions.
