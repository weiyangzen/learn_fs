# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_heartbeat.h

## Purpose
`ocfs2_heartbeat.h` defines the on-disk heartbeat slot layout shared between kernel heartbeat code and tooling.

## Important APIs, types, and functions
`struct o2hb_disk_heartbeat_block` contains `hb_seq`, `hb_node`, padding, `hb_cksum`, `hb_generation`, and `hb_dead_ms`. Fields are little-endian where multibyte values are persisted.

## Control flow
Heartbeat threads read and write one block per node in a heartbeat region. They zero/compute `hb_cksum`, compare `hb_seq` movement and `hb_generation`, and use `hb_dead_ms` to detect threshold mismatches.

## State and persistence behavior
This structure is persistent shared-disk state. A nonzero generation identifies a running node instance; writing generation zero on clean shutdown signals departure.

## Dependencies and integration points
It depends only on kernel integer/endian types supplied by includers. `heartbeat.h` includes it for in-kernel APIs, and userspace-compatible consumers rely on this exact layout.

## Risks and test signals
Risks include layout changes breaking disk compatibility, endian mistakes, and stale slots after unclean shutdown. Test signals include CRC validation, clean generation-zero shutdown writes, cross-node dead-threshold mismatch detection, and compatibility with existing heartbeat regions.
