# sources/distributed-fs/ceph/src/mds/Anchor.cc

## Purpose
This file implements serialization, formatting, test-instance generation, and stream printing for `Anchor`, the MDS structure that records primary inode linkage for path reconstruction through the anchor table.

## Important APIs, Types, and Functions
`Anchor::encode()` writes version 2 records containing `ino`, `dirino`, `d_name`, `d_type`, and `frags`. `Anchor::decode()` reads versioned records and only decodes `frags` when `struct_v >= 2`, preserving compatibility with older serialized anchors. `dump()` emits formatter fields except `frags`. `generate_test_instances()` creates an empty anchor and a sample directory anchor. `operator<<` prints a compact human-readable representation.

## Control Flow
Serialization is straightforward versioned encode/decode with `ENCODE_START` and `DECODE_START`. The decode path first loads core fields and conditionally loads the newer fragment set.

## State and Persistence Behavior
Anchors are persisted through Ceph buffer encoding, likely into the MDS anchor table. The versioning choice means existing v1 records remain readable and v2 records carry fragment membership. `omap_idx` is not encoded here, so it is runtime placement metadata rather than part of the durable anchor payload.

## Dependencies and Integration Points
It depends on `Anchor.h`, Ceph `Formatter`, denc/buffer helpers, and directory-entry type constants from `<dirent.h>`. It integrates with MDS anchor-table code that stores ancestor chains and with Ceph encoding tests via `generate_test_instances()`.

## Risks and Test Signals
The main risk is serialization compatibility: adding fields before existing v2 content would break decode. Tests should round-trip v1/v2 anchors, verify `frags` survives v2 encode/decode, and ensure dump/print output remains usable for debugging.
