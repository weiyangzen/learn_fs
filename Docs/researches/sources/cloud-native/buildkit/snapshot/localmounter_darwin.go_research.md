## sources/cloud-native/buildkit/snapshot/localmounter_darwin.go

Purpose: Darwin implementation of local mount/unmount.

Important APIs/types/functions: `(*localMounter).Mount` lazily obtains mounts from the mountable, short-circuits writable single `bind` mounts by returning the source, otherwise creates a temp dir and calls `mount.All`. `Unmount` recursively unmounts with `unix.MNT_FORCE`, removes the temp dir, and calls the mountable release.

Control flow: mutex protects idempotent mount/unmount. Existing target is reused. Writable bind shortcut avoids requiring mount privileges for simple local directories.

State and persistence: temporary directory path in `target`, release callback from mountable, and mounted filesystem state. Cleanup removes the target directory.

Dependencies and integration points: used whenever BuildKit needs to inspect a snapshot on Darwin.

Risks and test signals: `forceRemount` is not honored in the Darwin shortcut, unlike FreeBSD/Linux; callers expecting forced remount on writable binds may get source path. Errors during mount remove the temp directory. No Darwin tests in subset.
