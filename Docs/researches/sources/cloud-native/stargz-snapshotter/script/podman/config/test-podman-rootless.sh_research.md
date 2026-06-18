# sources/cloud-native/stargz-snapshotter/script/podman/config/test-podman-rootless.sh

Purpose: Wrapper that switches from root to the rootless user and starts the user stargz-store service before running a command.
Important APIs/types/functions: root/user branch, `systemctl start ssh`, `ssh rootless@localhost`, `systemctl --user start podman-rootless-stargz-store`.
Control flow: if running as root, starts SSH and re-execs itself through rootless SSH; otherwise starts the user service and execs the provided command.
State and persistence: starts system/user services; no file persistence itself.
Dependencies and integration points: used inside podman-rootless test image to mimic rootless execution patterns from nerdctl CI.
Risks: requires SSH daemon and password/keyless rootless access configured in image; strict host checking disabled for test convenience.
Test signals: indirectly exercised by Podman rootless test image startup.
