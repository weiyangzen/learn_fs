# sources/cloud-native/containerd/cmd/ctr/commands/images/unmount.go

Purpose: implements `ctr images unmount`, unmounting an image rootfs target and optionally removing related snapshot/lease state.

Important APIs/functions: `unmountCommand`.

Control flow: validates target, creates client/context, calls `mount.UnmountAll(target, 0)`, and if `--rm` is set, deletes a lease with ID equal to target and removes a snapshot with key equal to target from the chosen snapshotter. Prints target on success.

State and persistence: unmounts host filesystem mounts; optional deletion mutates lease and snapshot state.

Dependencies/integration: mount package, leases service, snapshot service, errdefs.

Risks: cleanup assumes target path equals lease ID and snapshot key, which matches explicit-target mount mode but not random-key/bind-source cases. Snapshotter default handling is delegated to snapshot service behavior; unlike mount.go it does not set defaults explicitly.

Test signals: no local tests.
