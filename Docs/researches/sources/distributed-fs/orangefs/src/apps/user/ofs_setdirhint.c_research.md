<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_setdirhint.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_setdirhint.c

## Purpose
Sets OrangeFS directory hints as extended attributes on one or more directories, optionally recursively. Hints include distribution name/parameters, layout algorithm, server list, and datafile count.

## Important APIs, Types, And Functions
`user_options` stores selected hints and traversal flags. `layout_table_s` maps textual layouts (`none`, `round_robin`, `random`, `list`, `local`) and numeric strings to `PVFS_SYS_LAYOUT_*` values. `main` traverses with FTS, opens directories, and calls `fsetxattr` for `user.pvfs2.dist_name`, `dist_params`, `layout`, `server_list`, and `num_dfiles`. `translate_layout`, `parse_args`, and `usage` provide parsing.

## Control Flow
Without `-r`, child directories are skipped. For each preorder directory, optional interactive confirmation precedes setting requested xattrs. List layout converts a colon/list input into a `PVFS_sys_layout` using `pvfs_layout_fd`, serializes it with `pvfs_layout_string`, writes `user.pvfs2.server_list`, and derives `num_dfiles` from the layout count.

## State And Persistence
Persists user xattrs on directories, affecting later file placement/layout choices. Runtime state is the FTS traversal and allocated option strings.

## Dependencies And Integration Points
Depends on FTS, Linux xattr APIs, `orange.h`, OrangeFS layout helpers, and kernel-client xattr support. It complements `ofs_cp` creation hints by setting defaults on directories.

## Risks And Test Signals
Risks include flag string mismatch (`p` parsed as dist params but switch also has unreachable `s`), long-option names with underscores only, fixed 10-byte numeric buffers, possible descriptor leaks on early returns, typo/unreachable message in `translate_layout`, and limited validation of conflicting hints. Test signals are setting each xattr, recursive traversal, list layout conversion, invalid layout rejection, interactive skip, non-directory inputs, and verifying newly created files inherit expected hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_setdirhint.c -->
