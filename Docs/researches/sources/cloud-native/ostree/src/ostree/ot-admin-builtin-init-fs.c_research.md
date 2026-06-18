<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-init-fs.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-init-fs.c

## Purpose
Implements `ostree admin init-fs`, initializing a filesystem root for OSTree use with legacy or modern top-level directory layouts.

## Important APIs and Types
Exports `ot_admin_builtin_init_fs`. Options are `--modern` and `--epoch`; it uses libglnx directory creation and `ostree_sysroot_ensure_initialized`.

## Control Flow
The command parses without an existing sysroot, opens the target path, always ensures `boot`, validates epoch, maps `--modern` to epoch 1, creates legacy top-level directories for epoch 0, creates private `ostree` for epoch 2, then constructs an `OstreeSysroot` and ensures initialization.

## State and Persistence
Creates directories such as `boot`, `ostree`, and legacy `dev/home/proc/run/sys/root/tmp`, with specific modes. It initializes the sysroot on disk.

## Dependencies and Integration Points
Uses admin parser flags for superuser/unlocked/no-sysroot operation, libglnx mkdir helpers, GFile, and sysroot initialization APIs.

## Risks
Directory mode choices are compatibility-sensitive. Epoch handling accepts epoch 1 by doing only boot plus normal sysroot initialization, while epoch 2 changes `ostree` permissions to 0700. Negative epoch is rejected, but values above 2 currently skip the explicit layout branches.

## Test Signals
Filesystem layout tests for default, `--modern`, epoch 1, epoch 2, invalid negative epoch, permissions on `tmp` and `ostree`, and idempotent reinitialization are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-init-fs.c -->
