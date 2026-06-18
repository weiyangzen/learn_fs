# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.c

Purpose: debugfs observability for the usNIC driver.

Important APIs/functions: `usnic_debugfs_init()` creates `/sys/kernel/debug/usnic_verbs`, `flows`, and `build-info`; `usnic_debugfs_exit()` removes the tree; `usnic_debugfs_flow_add()` and `usnic_debugfs_flow_remove()` add/remove per-flow files. Read handlers emit version/build date and flow transport metadata.

Control flow: module init creates the debugfs root; QP group flow creation adds a file named by firmware flow ID; flow teardown removes it. Flow reads lock the owning QP group, format QP group ID and transport, and include custom RoCE port or UDP socket address.

State and persistence: global dentries hold debugfs root and flow directory. Per-flow debugfs dentry/name are stored in `struct usnic_ib_qp_grp_flow`. State is transient and removed on flow/module teardown.

Dependencies and integration: depends on Linux debugfs, QP group structures, transport formatting, and driver version macros.

Risks: debugfs flow file private data points at live QP flow objects, so teardown ordering must prevent use-after-free. `flowinfo_read()` uses `count` as remaining buffer size against a fixed 512-byte stack buffer, so very large userspace read counts can make `left` exceed the actual buffer capacity.

Test signals: debugfs tree creation/removal, build-info content, creating/destroying RoCE and UDP QPs while reading flow files, and KASAN/lockdep coverage for concurrent teardown/read.
