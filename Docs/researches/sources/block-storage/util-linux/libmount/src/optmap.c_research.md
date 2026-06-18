# File Research: sources/block-storage/util-linux/libmount/src/optmap.c

This file defines libmount's built-in option maps and the map lookup routine. Option maps describe how textual mount options correspond to mount flags or userspace-only libmount flags, plus masks such as `MNT_INVERT`, `MNT_NOMTAB`, `MNT_NOHLPS`, `MNT_PREFIX`, `MNT_SUPERBLOCK`, and `MNT_NOFSTAB`.

`linux_flags_map` covers filesystem-independent kernel mount flags: `ro`/`rw`, exec/suid/dev inversions, sync/async, dirsync, remount, bind/rbind, optional platform flags such as nosub, silent/loud, mandatory locking, atime variants, lazytime, propagation options, nosymfollow, and move. Entries are conditionally compiled according to available `MS_*` macros.

`userspace_opts_map` covers libmount/mount(8)-specific behavior: defaults, auto/noauto, user/nouser/users/nousers, owner/group, `_netdev`, comments, `x-`/`X-` prefixes, loop-related options, nofail, helper/uhelper, and verity-related userspace options. Many of these are marked not for helpers or not for mtab as appropriate.

`mnt_get_builtin_optmap()` returns one of the two static maps for `MNT_LINUX_MAP` or `MNT_USERSPACE_MAP`. `mnt_optmap_get_entry()` searches one or more maps for a parsed option name. It supports prefix entries (`MNT_PREFIX`) by `ul_startswith()`, otherwise compares the parsed name length and accepts exact names, mandatory-value entries (`name=`), and optional-value entries (`name[=]`). It can return both the containing map and the matched map entry.
