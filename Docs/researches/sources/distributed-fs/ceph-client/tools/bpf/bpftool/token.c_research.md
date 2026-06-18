# sources/distributed-fs/ceph-client/tools/bpf/bpftool/token.c

Purpose: Implements `bpftool token show/list`, reporting bpffs mounts configured with delegation token options.

Important APIs, types, and functions: `sets[]` maps display headers to mount option keys. `has_delegate_options()` detects any delegate option. `get_delegate_value()` tokenizes comma-separated mount options and returns the value for one key. `print_items_per_line()` and `split_json_array_str()` format colon-separated option values. `show_token_info_plain()` and `show_token_info_json()` render one mount. `show_token_info()` scans `/proc/mounts`.

Control flow: The command opens `/proc/mounts`, optionally starts a JSON array, visits each mount entry with type prefix `bpf`, filters entries with delegation options, prints all four configured sets, ends JSON, and closes the mount table.

State and persistence: Read-only. It duplicates mount option strings because `strtok_r()` mutates them.

Dependencies and integration points: Depends on bpffs mount options `delegate_cmds`, `delegate_maps`, `delegate_progs`, and `delegate_attachs`, libc mount table APIs, and bpftool JSON globals.

Risks: Type check uses `strncmp(ent->mnt_type, "bpf", 3)`, so any mount type beginning with `bpf` is considered. Token parsing is simple string splitting and assumes colon-separated values with no escaping. Missing delegate key prints empty list/header.

Test signals: Mount bpffs with different delegation options and verify plain alignment and JSON arrays, plus empty output when no delegate options exist.
