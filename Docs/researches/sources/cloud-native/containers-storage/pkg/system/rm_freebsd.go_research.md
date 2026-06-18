# sources/cloud-native/containers-storage/pkg/system/rm_freebsd.go

Purpose: FreeBSD implementation of immutable/file flag reset used before retrying recursive deletion.

Important APIs/types/functions: `resetFileFlags(dir string) error` walks the tree with `filepath.WalkDir` and calls `Lchflags(path, 0)` on each entry.

Control flow: every visited path has flags cleared; any `Lchflags` error aborts the walk and propagates to `EnsureRemoveAll`.

State/persistence: mutates filesystem flags, enabling later deletion of files that were append-only or immutable.

Dependencies/integration: integrates with FreeBSD `chflags` helpers and `EnsureRemoveAll` EPERM recovery.

Risks: the callback ignores the `err` argument from `WalkDir`; if traversal reports an access error, the code still tries `Lchflags` on that path. Clearing all flags is broad and should only happen in removal paths.

Test signals: FreeBSD tests should combine immutable files with `EnsureRemoveAll`; `stat_freebsd_test.go` checks flag preservation through stat helpers.
