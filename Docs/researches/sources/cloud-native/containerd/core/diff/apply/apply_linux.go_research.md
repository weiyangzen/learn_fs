# sources/cloud-native/containerd/core/diff/apply/apply_linux.go

Purpose: Linux implementation of applying a tar diff stream onto mounted filesystems.

Important functions: `apply` handles overlay fast path, bind-mount sync path, and generic temp mount path. `getOverlayPath` parses `upperdir=` and `lowerdir=` mount options. `doSyncFs` calls `unix.Syncfs` on a path.

Control flow and state: for a single overlay mount outside a user namespace, it extracts directly into `upperdir` with `archive.OverlayConvertWhiteout` and optional lower parents. If overlay options are invalid, it falls back to temp mounting. For single bind mounts with sync requested, it defers `syncfs` on the source after generic apply. All other cases use `mount.WithTempMount` and `archive.Apply`.

Dependencies and integration: containerd mount package, archive apply package, errdefs, `moby/sys/userns`, and `golang.org/x/sys/unix`.

Risks: overlay fast path is disabled in user namespaces because whiteout conversion uses device nodes. Overlay option parsing is string-based and only understands `upperdir`/`lowerdir`. `syncfs` requires opening the target path and may fail due to permissions or missing path.

Test signals: `apply_linux_test.go` covers `getOverlayPath` success and missing upperdir error. Extraction/sync behavior is not directly unit-tested here.
