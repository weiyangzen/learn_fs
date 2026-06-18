# File Research: sources/block-storage/util-linux/sys-utils/switch_root.c

This file implements `switch_root(8)`, used during early boot to move from an initramfs root to a real root filesystem and exec the new init. It has no libmount dependency; it works directly with `stat`, `mount(MS_MOVE)`, `chroot`, `fork`, and `execv`.

`recursiveRemove()` deletes directory contents below an fd without crossing mount points. It uses `fdopendir()`, compares each entry's `st_dev` to the root directory device, recurses into same-device directories with `openat()`, and removes entries with `unlinkat()`. The input fd is always closed, either by `closedir()` or directly on failure before `fdopendir()`.

`switchroot()` first records old and new root device numbers. It attempts to move `/dev`, `/proc`, `/sys`, and `/run` into corresponding directories under the new root when the old location is a separate mount and the new destination is still part of the new root. If moving fails, it force-unmounts the old mount; if the new destination is already mounted or not usable, it lazily detaches the old one.

After moving auxiliary mounts, `switchroot()` changes to `newroot`, opens the old `/`, moves `newroot` onto `/`, performs `chroot(".")`, and changes to `/`. A child process checks whether the old root fd is `ramfs` or `tmpfs`; only then does it recursively delete the old initramfs contents. The parent closes the fd and returns so `main()` can verify and exec the requested init.

`main()` only supports `--help` and `--version`, requires `<newrootdir> <init> [args...]`, calls `switchroot()`, warns if the init is not executable, and replaces itself with `execv(init, initargs)`.
