# sources/cloud-native/containers-storage/pkg/mount/mount.go

Purpose: provides high-level mount and unmount API wrappers plus formatted mount errors.

Important APIs, types, and functions: `mountError`, `Mount`, `ForceMount`, `Unmount`, `RecursiveUnmount`, and deprecated `ForceUnmount`.

Control flow: `Mount` parses options, checks whether the target is already mounted unless this is a remount, then delegates to platform `mount`. `ForceMount` skips the mounted check. `Unmount` and `ForceUnmount` delegate to platform `unmount` with lazy/detach flags. `RecursiveUnmount` reads all mounts, sorts deepest mountpoints first, unmounts descendants under the target, and only returns an error for the final relevant unmount failure.

State and persistence: mutates kernel mount table state through platform calls. No package-level persistent state.

Dependencies and integration points: depends on `sort`, `strconv`, and `strings`; integrates with `mountinfo` for mounted checks and with OS-specific mounter/unmounter files.

Risks and edge cases: `RecursiveUnmount` uses simple string prefix matching, so paths like `/foo2` can match target `/foo` unless callers pass normalized boundaries. Mounted-check races remain possible between check and mount.

Test signals: Linux tests exercise `Mount`, `Unmount`, `Mounted`, read-only bind behavior, and mountinfo visibility.
