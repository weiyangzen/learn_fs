# sources/cloud-native/composefs-rs/examples/common/run-repart

Purpose: creates a raw disk image with ESP and sysroot partitions, applying ownership/SELinux labels and optional fs-verity copy/fix behavior.

Important APIs/types/functions: `chown`, `chcon`, repart definitions `01-esp.conf` and `02-sysroot.conf`, env `SYSTEMD_REPART_MKFS_OPTIONS_EXT4=-O verity`, `FS_VERITY_MODE`, `FS_FORMAT`, `COPY_FILES_FLAG`, and `systemd-repart`.

Control flow: normalizes ownership and labels, writes partition definition files, sets `CopyFiles` to include `fsverity=copy` in repart mode, runs `systemd-repart` offline with `TMPDIR=$PWD/tmp`, then optionally runs fix-verity.

State/persistence: writes `tmp/repart.d`, mutates `tmp/sysroot` metadata, and produces the raw image path supplied as `$1`.

Dependencies/integration: depends on SELinux tools, systemd-repart fs-verity support, `install-systemd-boot` output under `tmp/efi`, and optional `fix-verity`.

Risks/test signals: label patterns are example-specific and may fail on non-SELinux hosts. CopyFiles fs-verity support is version-sensitive; `check-config` protects this path.
