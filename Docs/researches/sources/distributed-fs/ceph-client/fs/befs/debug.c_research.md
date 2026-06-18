# sources/distributed-fs/ceph-client/fs/befs/debug.c

Purpose: provides BeFS error/warning/debug logging and optional detailed dump helpers for superblocks, inodes, B+tree superblocks, and B+tree nodes.

Important APIs/types/functions: `befs_error`, `befs_warning`, `befs_debug`, `befs_dump_inode`, `befs_dump_super_block`, `befs_dump_index_entry`, and `befs_dump_index_node`.

Control flow: error and warning logs always format messages with superblock id; debug and dump functions emit only when `CONFIG_BEFS_DEBUG` is enabled.

State and persistence: no persistent state; dumps convert on-disk endian fields at log time without mutating them.

Dependencies and integration: used throughout BeFS parsing, mapping, and VFS code to report corruption and diagnostics.

Risks: debug dumps must avoid trusting malformed fields too deeply. Log volume can be high with debug enabled.

Test signals: build with `CONFIG_BEFS_DEBUG`; mount with `debug`; inject bad magic, bad inode, and B+tree errors to confirm diagnostics.
