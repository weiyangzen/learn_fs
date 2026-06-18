# File Research: sources/block-storage/util-linux/sys-utils/umount.c

This file implements `umount(8)` as a command-line driver around libmount's `libmnt_context`. It handles option parsing, restricted-user behavior, namespace switching, recursive/all-target unmounts, libmount exit-code translation, and user-facing diagnostics.

`suid_drop()` drops setuid-root privilege for restricted operations, verifies privilege cannot be regained, forces the libmount context into unrestricted mode, and restores sanitized environment variables. The main parser allows only a small option set for restricted users; security-sensitive options cause the program to drop privileges before continuing. Restricted positional paths are canonicalized with `ul_canonicalize_path_restricted()`, and non-root users may not pass tag specs.

`mk_exit_code()` converts libmount API/syscall state into `MNT_EX_*` exit codes with `mnt_context_get_excode()`, implements `--graceful` success for already-gone targets, and suppresses selected "not mounted" messages under `--quiet`. `success_message()` prints verbose successful unmount messages only when the libmount operation actually succeeded and no helper error is pending.

`umount_all()` iterates mount entries backward through `mnt_context_next_umount()`, respecting libmount's ignore decisions and accumulating exit codes. `umount_one()` sets the target, calls `mnt_context_umount()`, retries after `suid_drop()` for a restricted `-EPERM` path where libmount did not reach the syscall, translates the result, optionally prints success, and resets the context.

`new_mountinfo()` temporarily switches to the target mount namespace configured by `--namespace`, parses `/proc/self/mountinfo` into an independent table with the context cache, and switches back. Recursive unmounting uses that table: `umount_do_recurse()` first handles an overmount, then children in backward order, then the target itself through `umount_one_if_mounted()`. `umount_alltargets()` resolves the source once, then unmounts every mountinfo entry with the same device number, optionally recursively.

`main()` creates the libmount context, installs parser warnings, maps CLI options to libmount context flags (`force`, `lazy`, `fake`, `loopdel`, `rdonly_umount`, no helpers, no mtab, fstype/options patterns), supports PID or path mount namespace selection, enforces incompatible option groups, dispatches `--all`, `--all-targets`, `--recursive`, or positional unmounts, and clamps accumulated exit status to 255.
