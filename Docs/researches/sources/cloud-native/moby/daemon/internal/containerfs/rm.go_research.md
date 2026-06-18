# sources/cloud-native/moby/daemon/internal/containerfs/rm.go

## Purpose
Provides a robust Unix/non-Darwin container filesystem removal helper that handles mounts and common removal races.

## APIs, Control Flow, and Integration
`EnsureRemoveAll` first recursively unmounts beneath the target, then loops around `os.RemoveAll`. It ignores/reruns certain `ENOENT` races for child paths, retries once on `ENOTEMPTY`, handles `EBUSY` by unmounting the reported path, and retries busy paths up to 50 times with 100ms sleeps.

## State, Dependencies, and Risks
State is local retry maps. External effects are destructive filesystem deletion and mount unmounting. Risks include broad recursive unmount scope, up to five seconds waiting per busy path, and returning wrapped unmount errors instead of original removal errors. Tests cover absent paths, files, dirs, and root-only bind mount removal.
