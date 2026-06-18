# sources/cloud-native/nydus-snapshotter/integration/entrypoint.sh

Purpose: integration test harness for containerd-nydus-snapshotter behavior across daemon modes, images, recovery, cache cleanup, OCI/stargz/referrer paths, and fscache.

Flow: defines retry helpers, process cleanup, config mutation, containerd/snapshotter reboot, cache validation, and many scenario functions that pull/run/create/remove images, kill nydusd/snapshotter, restart services, and detect Go race reports. It runs containerd and `containerd-nydus-grpc` directly in the test container.

State/dependencies: mutates `/etc/nydus/config.toml`, `/var/lib/containerd`, `/run/containerd`, snapshotter root/cache, and process table. Uses nerdctl, ctr, killall, mount/umount, nydusd, containerd.

Integration points: central to `make integration`.

Risks/tests: highly destructive inside its container namespace and privileged mounts. Some CLI flags in older helper paths (`--config-path`, `--enable-stargz`) may drift from current flag definitions.
