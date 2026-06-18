# sources/cloud-native/ostree/tests/test-repo-finder-mount-integration.sh

## Purpose
This shell integration test exercises repo-finder mount behavior against a real disposable USB block device formatted as ext4 and vfat. It validates `ostree create-usb`, mount-based `find-remotes`, pull from discovered media, and cross-filesystem consistency.

## Important APIs, Types, And Functions
It uses `skip_without_sudo`, `MOUNT_INTEGRATION_DEV`, `mkfs.ext4`, `mkfs.vfat`, `udisksctl mount`, `ostree_repo_init --collection-id`, `ostree commit --gpg-sign`, `ostree summary --update`, `ostree remote add --collection-id --gpg-import`, `ostree pull`, `ostree create-usb`, `ostree find-remotes --finders=mount`, `find-remotes --pull`, and `diff -ur`.

## Control Flow
The script skips unless sudo is available and `MOUNT_INTEGRATION_DEV` names an unmounted block device. It creates a signed collection repo with five refs, pulls all refs into `local-repo`, then loops over ext4 and vfat. For each filesystem it reformats the device, mounts it through udisks, writes only `test-1` and `test-2` to the USB repo with `create-usb`, validates refs and summary on the mounted media, initializes a peer repo with only the collection keyring, discovers `test-1` through `find-remotes --finders=mount`, pulls it through the same finder, verifies the collection ref exists locally, and unmounts. Finally it diffs the ext4 and vfat peer repos.

## State And Persistence
State includes the real block device contents, mounted USB `.ostree/repo`, collection refs, summaries, GPG-signed commits, keyrings in local and peer repos, and peer repositories `peer-repo_ext4` and `peer-repo_vfat`. Cleanup unmounts the configured device unless cleanup is explicitly skipped.

## Dependencies And Integration Points
This integrates shell fixture setup, sudo, udisks, mkfs tools, removable-media discovery through GIO, collection-aware repo discovery, `create-usb`, GPG keyring resolution, and pull/find-remotes behavior.

## Risks
The test is intentionally destructive to `MOUNT_INTEGRATION_DEV`, so the mounted-device guard is critical. Host dependencies are heavy and can cause skips or flakes. ext4 ownership options and vfat semantics differ, so identical peer repos are the final cross-filesystem guard.

## Test Signals
The TAP plan has three results: end-to-end USB on ext4, end-to-end USB on vfat, and identical peer repositories. It also checks discovery output contains the USB file URI and the exact checksum for `test-1`.
