# sources/cloud-native/containerd/core/runtime/v2/bundle.go

## Purpose
Creates, loads, and deletes runtime v2 OCI bundle directories. A bundle records the task ID, namespace, state path, rootfs directory, optional OCI config, and a symlink to a persistent work directory.

## APIs, Flow, State, Dependencies, Risks, And Tests
`LoadBundle` reconstructs a `Bundle` from state root, namespace, and task ID. `NewBundle` validates the task ID, requires a namespace in context, creates state and work directories, creates `rootfs`, symlinks `work`, applies platform-specific permissions for OCI specs, and writes `config.json` when a non-nil spec is supplied. `Bundle.Delete` recursively unmounts `rootfs`, removes it, atomically renames/removes the bundle path, and does the same for the linked work directory. `atomicDelete` performs rename-to-hidden then recursive deletion.

The main state is filesystem state under `state/<namespace>/<id>` and `root/<namespace>/<id>`. Error handling tracks created paths and removes them on failed creation. Deletion is best-effort across bundle and workdir, but returns joined contextual errors when both paths fail.

Dependencies include namespace extraction, identifier validation, OCI config filename conventions, mount recursive unmount, and typeurl detection for OCI specs. It is used by `TaskManager.Create`, shim reload, and shim cleanup.

Risks include partial cleanup on filesystem races, failure to remove still-mounted rootfs, stale work directories after state loss, nil spec handling for sandboxers, and permission mismatches with user namespaces. Test signals come from bundle creation tests, deletion tests around mounted rootfs/work symlink behavior, and crash/restart recovery tests that reload bundle state.
