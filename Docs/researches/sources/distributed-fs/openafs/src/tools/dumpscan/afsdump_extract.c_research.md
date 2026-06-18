# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_extract.c

Purpose: extracts files, directories, and symlinks from an AFS volume dump into a destination directory, optionally selecting by vnode number or volume-relative path.

Important APIs/functions: `parse_options` handles `-A`, `-H`, `-i`, `-n`, `-p`, `-q`, and `-v`; it separates requested path names from vnode numbers. `Path_PreScan` builds a vnode/path hash before extraction unless vnode-number mode is used. `directory_cb`, `file_cb`, and `symlink_cb` are registered as `dump_parser` callbacks. `file_cb` seeks to `v->d_offset`, opens the target path, and copies `v->size` bytes with `copyfile`. `symlink_cb` reads link data and calls `symlink`.

State/persistence: it may create the destination directory, `chdir` into it, create nested directories and files, and create symlinks. `-n` suppresses writes. Dependencies are seekable `XFILE` input for path mode, `pathname.c`, `directory.c`, parser callbacks, and POSIX filesystem APIs.

Risks/test signals: selected path matching is prefix-based for directories; file modes and ACL saving are incomplete (`do_acls` is a placeholder, output files use `0644`). Exit status is always zero after parse, even on parse errors. There are also concrete option/allocation risks: when no destination argument is provided, `target` is first set to `"."` and then overwritten with `argv[optind + 1]`; the selection arrays use `malloc(name_count + sizeof(char *))` and `malloc(vnum_count + sizeof(afs_uint32))` instead of element count times element size.
