# sources/distributed-fs/ceph-client/drivers/interconnect/debugfs-client.c

Purpose: optional debugfs test client for manual source/destination interconnect votes. It is compiled only if the source is edited to define `INTERCONNECT_ALLOW_WRITE_DEBUGFS`.

Important APIs/types/functions: enabled builds expose `icc_debugfs_client_init()`, `icc_get_set()`, `icc_commit_set()`, and `struct debugfs_path` for cached path handles. Disabled builds return success without creating files.

Control flow: users write `src_node`/`dst_node`, write `get` to find or reuse a path, set `avg_bw`, `peak_bw`, and `tag`, then write `commit` to call `icc_set_tag()` and `icc_set_bw()`.

State and persistence: static globals hold a synthetic platform device, current path, strings, vote values, and cached path list. Cached paths are intentionally long-lived for debug sessions.

Dependencies/integration: debugfs, platform devices, RCU string dereference from `debugfs_create_str()`, and internal name-based `icc_get()`.

Risks and test signals: if enabled, test invalid names, duplicate path reuse, allocation failures, commit-before-get, concurrent writes, and teardown leaks. The feature can affect live hardware votes.
