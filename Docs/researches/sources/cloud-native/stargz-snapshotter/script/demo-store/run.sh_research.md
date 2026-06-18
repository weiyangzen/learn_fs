# sources/cloud-native/stargz-snapshotter/script/demo-store/run.sh

Purpose: Builds and starts stargz-store inside the Podman demo container.
Important APIs/types/functions: `retry`, `kill_all`, `cleanup`; constants for repo, config, root, and mountpoint.
Control flow: resets Podman/store state, copies demo configs into `/etc`, builds and installs project binaries, starts `stargz-store`, and waits for the pool directory.
State and persistence: clears `/var/lib/stargz-store`, resets Podman, copies configs, installs binaries under `PREFIX=/tmp/out` target paths.
Dependencies and integration points: used with `demo-store/docker-compose.yml`; depends on make, podman, FUSE, and stargz-store.
Risks: destructive state cleanup and broad process kill make it demo-container only.
Test signals: manual/demo validation when pool link appears and Podman can use store.
