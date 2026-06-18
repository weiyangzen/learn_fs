## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.c

### Purpose
This file implements OrangeFS debugfs controls under `/sys/kernel/debug/orangefs` for kernel debug masks, client debug masks, and debug keyword help.

### Important APIs, types, and functions
- `s_kmod_keyword_mask_map` maps kernel debug keywords to `GOSSIP_*` masks.
- `orangefs_debugfs_init()` creates the debugfs directory and files and normalizes the initial module debug mask.
- `orangefs_prepare_debugfs_help_string()` builds the help text from kernel keywords and, after daemon startup, client-provided keywords.
- `orangefs_debug_read()` and `orangefs_debug_write()` implement `kernel-debug` and `client-debug` file behavior.
- `orangefs_prepare_cdm_array()`, `debug_mask_to_string()`, `debug_string_to_mask()`, and helpers convert between keyword strings and masks.
- `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, and `orangefs_debugfs_new_debug()` receive daemon ioctl-provided debug information.

### Control flow
Module init builds an initial help string saying client keywords are unknown, then creates debugfs files. Writing `kernel-debug` parses the keyword string into `orangefs_gossip_debug_mask` and rewrites the displayed string. Writing `client-debug` requires the daemon to be running, converts keywords into the client's two-mask representation, and sends an `ORANGEFS_VFS_OP_PARAM` request. The daemon can later provide client keyword arrays and masks via ioctls, causing `client-debug` and `debug-help` to be rebuilt.

### State and persistence behavior
Runtime state includes kernel/client debug strings, client keyword array, debugfs dentries, help string allocation, and flags tracking whether module parameters set masks. Settings are volatile and reset on module reload, except the module parameter can seed the initial mask.

### Dependencies and integration points
Depends on debugfs, seq_file, usercopy, `service_operation()`, `is_daemon_in_service()`, protocol debug ioctl structs, and `orangefs_gossip_debug_mask` from `orangefs-mod.c`. Device ioctls call the exported update functions.

### Risks
String parsing and fixed-size buffers must avoid overflow; the code trims and bounds user input but uses several string concatenation paths. Client keyword state is daemon-supplied and must be initialized before client mask conversion. Debug file permissions are `0444` in creation calls despite write handlers, so mode semantics should be checked against `debugfs_create_file_aux_num()` behavior in this tree.

### Test signals
Test `debug-help` before and after daemon starts, write/read `kernel-debug`, invalid keyword filtering, `all` and `verbose` behavior, daemon-provided client masks, client-debug write with daemon down, and cleanup freeing debugfs entries and help memory.
