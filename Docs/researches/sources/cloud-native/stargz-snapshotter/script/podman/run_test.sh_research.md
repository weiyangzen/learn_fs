# sources/cloud-native/stargz-snapshotter/script/podman/run_test.sh

Purpose: Runs rootless Podman lazy-pull smoke tests against stargz-store.
Important APIs/types/functions: `retry`; service name `podman-rootless-stargz-store`; remote snapshot log marker.
Control flow: waits until `podman unshare mount` shows stargzstore, pulls/runs eStargz images, runs another eStargz image to include lazy pulling, prints store journal remote snapshot lines, runs a non-lazy original image, then stops the user service.
State and persistence: creates `/tmp/test1.sh`, pulls Podman images, and reads/stops user systemd service state.
Dependencies and integration points: depends on rootless Podman, stargz-store service, journalctl, and public ghcr.io test images.
Risks: public image availability and journal log format are external dependencies; smoke test is small but catches gross integration failures.
Test signals: `podman/test.sh` parses its log and validates remote snapshot records.
