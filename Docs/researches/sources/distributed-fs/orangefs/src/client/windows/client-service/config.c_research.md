# sources/distributed-fs/orangefs/src/client/windows/client-service/config.c

## Purpose
This file parses the Windows OrangeFS client-service configuration file, populates `ORANGEFS_OPTIONS`, and seeds the user credential cache from configured user-to-UID/GID mappings.

## Important APIs, types, and functions
- Keyword table: `config_keyword_defs` maps textual options to callback functions.
- File handling: `get_module_dir`, `open_config_file`, `close_config_file`.
- Argument parsing: `get_args`, `free_args`.
- Keyword callbacks: `keyword_cb_mount`, `threads`, `user_mode`, `user`, `perms`, `write_time`, `debug`; security and LDAP callbacks are present but compiled out.
- Defaults and public API: `get_default_mount_point`, `set_defaults`, `get_config`, `add_users`.
- State: global `QLIST_HEAD(user_list)` accumulates configured users until `add_users`.

## Control flow
`get_config` opens a config file from `ORANGEFS_CONFIG_FILE`, `PVFS2_CONFIG_FILE`, or `orangefs.cfg` beside the executable. It applies defaults, reads each non-comment line, splits the keyword and argument string, finds a matching keyword definition, parses arguments with quote support, and calls the callback. After parsing, it validates required user mode and mutually exclusive debug outputs. `add_users` walks the accumulated `user_list`, initializes a credential for each `user name uid:gid` entry, and inserts it into the global user cache.

## State and persistence behavior
Persistent input is the config file. Parsed service state is stored in `ORANGEFS_OPTIONS`; configured users are temporarily stored in `user_list` and then persisted in the process user cache via `add_cache_user`. Defaults include first available drive from E: onward, permissions `0755`, list user mode, and a default debug file beside the executable.

## Dependencies and integration points
It depends on Windows drive/module APIs, OrangeFS types, `quicklist`, `security-util`, `cred.c`, and `user-cache`. `dokan-interface.c` consumes mount point, thread count, permissions, debug settings, write-time setting, and user/security modes.

## Risks and edge cases
- The keyword extraction loop uses `(*pline != ' ' || *pline == '\t')`, which does not stop on tabs as intended; it should likely use `&&`.
- `free_args` frees individual strings but not the outer `out_args` array, and `get_config` never calls `free_args`, leaking per-line allocations.
- `keyword_cb_mount` uses `strncpy` without guaranteeing null termination when input length is `MAX_PATH` or longer.
- Only `list` user mode is accepted; constants and code for cert/LDAP/server remain elsewhere, so config/service capabilities can diverge.
- `new-file-perms` rejects octal `0000`, which may be intentional but prevents no-access defaults.
- `get_config` returns early on overlong lines without closing the config file.
- `add_users` frees list entries but does not remove all links or clean remaining entries after an error.

## Test signals
Use config fixtures for valid list mode, quoted paths, tabs as separators, too many/missing args, long lines, invalid uid/gid, duplicate users, missing config file, both `debug-stderr` and `debug-file`, and no users. Verify user cache contains expected credentials and memory/leak tools show no parser leaks.
