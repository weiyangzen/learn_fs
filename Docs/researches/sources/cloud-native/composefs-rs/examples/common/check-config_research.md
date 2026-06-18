# sources/cloud-native/composefs-rs/examples/common/check-config

Purpose: preflight script validating host tools and fs-verity support needed to build composefs example disk images.

Important APIs/types/functions: checks for `fsverity`, `mkfs.erofs`, `mkfs.ext4`, `mkfs.vfat`, `mtools`, `skopeo`, `systemd-repart`; functions `check_measure` and `check_metadata`; env `FS_VERITY_MODE`.

Control flow: verifies the working directory supports fs-verity measurement, optionally exits early for `FS_VERITY_MODE=fix|none`, checks `systemd-repart` and `mkfs.ext4` binary strings for fs-verity support, and checks metadata dump ioctl support.

State/persistence: no persistent state; exits non-zero with diagnostic messages when host setup is inadequate.

Dependencies/integration: integrates with example build scripts, `install-patched-tools`, and `fix-verity` fallback mode.

Risks/test signals: binary string probing is heuristic and version-sensitive. It protects against known broken image generation paths, especially `/var/tmp` or filesystems without metadata ioctl support.
