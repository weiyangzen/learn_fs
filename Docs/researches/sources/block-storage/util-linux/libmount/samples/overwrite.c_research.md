# File Research: sources/block-storage/util-linux/libmount/samples/overwrite.c

Sample showing how to mount an fstab entry onto a different command-line target.

Key responsibilities:
- Parses `/etc/fstab`.
- Finds an entry by its original fstab target.
- Creates a mount context, installs the found `Fs`, overrides the target, and mounts.
- Prints raw libmount return and context status.

Important behavior:
- Usage is `<mnt-from-fstab> <target>`.
- Reuses fstab options/source/fstype via `mnt_context_set_fs()`.
- Calls `mnt_context_set_target()` after applying the fstab FS to overwrite only the target.

Dependencies:
- Depends on libmount table lookup and mount context APIs.

Notable risks:
- Calls `mnt_context_get_status(cxt)` after `mnt_free_context(cxt)` in the return expression, which is use-after-free.
- Performs real mounts and requires appropriate privileges/environment.
