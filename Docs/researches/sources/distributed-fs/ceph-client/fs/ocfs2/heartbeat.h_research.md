# sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.h

Purpose: declares OCFS2 heartbeat/node-map helpers used to initialize node tracking, react to node death, and update/test recovery maps.

Important APIs and types: declares `ocfs2_init_node_maps`, `ocfs2_do_node_down`, `ocfs2_node_map_set_bit`, `ocfs2_node_map_clear_bit`, and `ocfs2_node_map_test_bit` over `struct ocfs2_super` and `struct ocfs2_node_map`.

Control flow: no active control flow; callers use these declarations from superblock and cluster callback setup.

State and persistence behavior: declared helpers mutate in-memory node-map bitmaps under `node_map_lock` and initiate recovery on node-down notifications. There is no direct persistent format in the header.

Dependencies and integration points: consumed by DLM/cluster connection setup, journal recovery, orphan directory recovery, and any code tracking mounted or recovering nodes.

Risks: the API assumes callers pass valid node numbers except for the set/clear `-1` legacy case implemented in `heartbeat.c`. Callers must use the helpers rather than open-coding bitmap access to preserve locking.

Test signals: build coverage, node map initialization at mount, heartbeat callback wiring, and recovery map updates observed during simulated node failure.
