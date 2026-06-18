# sources/distributed-fs/glusterfs/xlators/nfs/server/src/exports.c

## Purpose
Parses an NFS exports file into lookup dictionaries used by Gluster's mount authorization path. It recognizes export directories, host entries, netgroup entries, and per-entry options, and builds both directory-name and UUID-like maps so later file-handle authorization can find the export originally mounted by a client.

## APIs, Types, and Functions
External functions are `exp_file_parse()`, `exp_file_deinit()`, `exp_file_get_dir()`, `exp_dir_get_host()`, `exp_dir_get_netgroup()`, and `exp_file_dir_from_uuid()`. Internal helpers initialize/deinitialize parsers and objects, print exports, destroy dict contents, parse options (`__exp_line_opt_parse()` and `__exp_line_opt_key_value_parse()`), parse host/netgroup strings (`__exp_line_ng_host_str_parse()`), parse netgroups and hosts from a line, parse directory names, parse full lines, and insert export dirs with `_exp_file_insert()`. `enum gf_exp_parse_status` distinguishes success, not found, parse failure, mount-state mismatch, and ignored lines.

## Control Flow, State, and Persistence
`exp_file_parse()` opens the file, initializes regex parsers, reads lines with `getline()`, strips newlines, and calls `_exp_line_parse()`. `_exp_line_parse()` ignores comments/blank/leading-space lines, extracts the directory token, optionally validates it against `mount3_state`, parses netgroup and host items, and returns a populated `struct export_dir`. Parsed dirs are inserted into `exports_dict` by directory name and into `exports_map` by a UUID string whose first bytes contain `SuperFastHash()` of the directory with leading slashes removed. Host lookup first tries the exact host and then wildcard `"*"`. Directory lookup normalizes missing leading slash. Persistent state is the in-memory `struct exports_file` graph of dicts, refcounted `export_item` values, option strings, and the hash map used by NFS file-handle mount IDs.

## Dependencies and Integration
Depends on Gluster dict/data/refcount APIs, `SuperFastHash`, parser utilities, mount3 export lookup, NFS logging, and memory types. It integrates with `mount3-auth.c` for host/netgroup authorization and with file-handle paths that need `exp_file_dir_from_uuid()`.

## Risks and Test Signals
Risks include regex grammar limitations, comments or whitespace semantics that ignore leading-space lines, option parser accepting only `root`, `ro`, `rw`, `nosuid`, `anonuid`, and `sec`, hash collisions in the UUID-like exports map, double destruction hazards because `exports_dict` and `exports_map` can reference the same `export_dir` data, and inconsistent refcount handling for dict-held `export_item` values. Test signals include parsing mixed host/netgroup lines, wildcard host fallback, trailing slash normalization, mount-state filtering, invalid option rejection, exports-map lookup from generated mount IDs, reload/deinit under sanitizer, and long directory/FQDN boundary cases.
