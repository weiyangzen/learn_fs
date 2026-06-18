# sources/distributed-fs/juicefs/pkg/object/file_windows.go


Purpose: supplies Windows-specific filesystem metadata helpers for `filestore`.

Important APIs and flow: `getOwnerGroup` returns empty owner and group strings. `lookupUser` and `lookupGroup` are stubs returning 0. `(*filestore).Chtimes` maps the object key to a local path and calls `os.Chtimes` with zero atime and requested mtime.

State and persistence: changes local Windows filesystem timestamps through `os.Chtimes`; no owner/group state is tracked.

Dependencies and integration: compiled on Windows in place of Unix helpers. It lets `filestore` satisfy `FileSystem` with reduced ownership semantics.

Risks: ownership information is unavailable and chown behavior in `file.go` relies on `utils.LookupUser`/`LookupGroup`, not these stubs, so Windows permission semantics remain limited. `os.Chtimes` follows normal Windows behavior and does not provide the Unix no-follow symlink semantics used elsewhere.

Test signals: no Windows-specific test in this subset. Cross-platform filesystem tests can cover basic storage behavior when run on Windows.
