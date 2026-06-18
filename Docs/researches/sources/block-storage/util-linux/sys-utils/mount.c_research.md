# File Research: sources/block-storage/util-linux/sys-utils/mount.c

This file implements the `mount(8)` frontend around libmount. It creates a `libmnt_context`, parses command-line options, configures sources, targets, fstab tables, option modes, namespace targets, bind/move/propagation operations, ID-mapped mount options, helper policy, fake mode, fork mode, canonicalization, and mtab behavior, then delegates the actual operation to libmount.

Major execution paths are listing current mounts, `mount -a`, `mount -a -o remount`, single-source/target mounting, bind/rbind/move operations, and propagation-only changes. `print_all()` reads the current mtab through libmount and prints classic `source on target type fstype (opts)` lines. `mount_all()` and `remount_all()` iterate libmount’s fstab-driven operation APIs and produce aggregate exit codes for all-success, all-failed, and mixed results.

The code contains compatibility and safety logic for setuid execution. Restricted users may only use a narrow option subset until `suid_drop()` permanently drops elevated privileges and restores sanitized environment variables. `sanitize_paths()` uses restricted canonicalization so non-root users cannot exploit unreadable path resolution. Parser callbacks convert fstab parse errors into warnings.

Option parsing translates traditional CLI flags into libmount option strings or context flags, including `-L`/`-U`, `--source`, `--target`, `--target-prefix`, `--options-mode`, `--options-source`, `--onlyonce`, `--exclusive`, `--beneath`, `--namespace`, and `--map-users`/`--map-groups`. Final status comes from `mk_exit_code()`, which asks libmount for backward-compatible mount exit codes and prints libmount warnings/info plus SELinux and systemd hints when applicable.
