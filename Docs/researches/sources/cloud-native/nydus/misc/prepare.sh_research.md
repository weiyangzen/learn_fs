<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/prepare.sh -->
# sources/cloud-native/nydus/misc/prepare.sh

## Purpose

This script prepares a host for Nydus snapshotter performance testing by installing binaries, downloading dependencies, configuring containerd and nydus, and starting services.

## Important APIs, Types, and Functions

It defaults `INSTALL_TARGET_TYPE=release`, optionally changes snapshotter `recover_policy` for `takeover_test`, queries latest release versions for nydus-snapshotter, nerdctl, and CNI plugins from GitHub, installs local Nydus binaries, downloads/extracts snapshotter, nerdctl, and CNI plugins, installs configs and systemd unit files, restarts containerd, starts nydus-snapshotter, and runs `misc/install-protoc.sh`.

## Control Flow

The script is mostly linear and uses command substitution for latest versions. It does not enable strict shell error handling, so failures may cascade.

## State and Persistence Behavior

It mutates `/usr/local/bin`, `/opt/cni/bin`, `/etc/containerd/config.toml`, `/etc/nydus`, `/etc/systemd/system`, systemd service state, and the working directory via downloaded archives.

## Dependencies and Integration Points

It depends on curl, wget, tar, sudo, systemctl, local built Nydus binaries, GitHub release APIs, and the performance config files in the same directory.

## Risks and Test Signals

It downloads latest external releases without pinning/checksum validation, assumes linux-amd64 archives, and lacks `set -e`. It should be used in controlled test environments, not production hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/prepare.sh -->
