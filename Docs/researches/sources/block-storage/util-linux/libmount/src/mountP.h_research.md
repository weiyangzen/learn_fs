# File Research: sources/block-storage/util-linux/libmount/src/mountP.h

This is libmount's private umbrella header. It defines internal structs, flags, paths, debug masks, iterator helpers, and cross-module prototypes used throughout `libmount/src`. It includes public `libmount.h`, util-linux support headers, and private utility headers, then layers libmount-specific internal state on top.

The header defines debug categories (`MNT_DEBUG_*`) and the `DBG`/`DBG_OBJ` wrappers, library paths such as `MNT_PATH_UTAB`, `MNT_PATH_TMPTGT`, and `MNT_MNTTABDIR_EXT`, test harness types under `TEST_PROGRAM`, and prototypes for utility functions, table parsing, listmount/statmount support, btrfs support, context helpers, option string/list functions, filesystem helpers, and update/event functions.

The central internal data structures are `struct libmnt_fs`, `struct libmnt_table`, and `struct libmnt_context`. `libmnt_fs` represents one fstab/mountinfo/utab/swaps row and stores identifiers, parent IDs, unique statmount IDs, namespace IDs, device numbers, source/tag/root/target/fstype strings, VFS/FS/user option strings, mount attributes, swap metadata, status flags, optional statmount state, comments, and user data. It defines internal flags for pseudo, network, swap, kernel, merged, attached, and detached status, plus inline helpers to mark attach, detach, or move.

`libmnt_table` owns a list of filesystems plus parse format, refcount, comment state, path/tag cache, parser error/filter callbacks, optional listmount and statmount references, noautofs behavior, and userdata. The generic `libmnt_iter` macros provide forward/backward traversal over libmount list heads and are used heavily by table, option-list, monitor, and diff code.

`libmnt_context` is the high-level mount/umount operation state: action, privilege mode, patterns, current filesystem, fstab/mountinfo/utab tables, parser callbacks, password callbacks, option mode, mount data, cache/lock/update objects, option lists and maps, target prefixes, flags, helper process status, syscall status, messages, namespace state, hook data, and feature booleans. The header also defines internal context flags and hook stages.

With `USE_LIBMOUNT_MOUNTFD_SUPPORT`, the header defines `struct libmnt_sysapi` for fsopen/fsmount/open_tree-style mount APIs and an accessor for hookset data. Overall, this header is the dependency hub that connects the monitor, option, parser, table, context, and update subsystems.
