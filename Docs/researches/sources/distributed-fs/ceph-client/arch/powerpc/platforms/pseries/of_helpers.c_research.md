# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.c

## Purpose
Provides small Open Firmware helper routines used by pSeries runtime device-tree and DRC handling code.

## Important APIs, Types, And Functions
Defines `pseries_of_derive_parent` and exports `of_read_drc_info_cell`. The latter fills `struct of_drc_info` fields from a packed `ibm,drc-info` style property cell.

## Control Flow
`pseries_of_derive_parent` rejects root, computes the dirname of a node path, finds that node with `of_find_node_by_path`, and returns either the parent node or an encoded error. `of_read_drc_info_cell` walks a property cursor through two encoded strings and five big-endian integer fields, updates the caller's cursor to the next entry, and calculates the last DRC index.

## State And Persistence
No persistent state is kept. Callers receive referenced OF nodes or decoded stack/caller-owned data and are responsible for node references.

## Dependencies And Integration Points
Depends on Linux OF string/u32 property iteration helpers, allocation APIs, and `struct of_drc_info` from PowerPC OF code. It supports pSeries DLPAR and mobility-style dynamic tree manipulation.

## Risks And Edge Cases
Malformed property buffers return `-EINVAL`. Allocation failure while deriving a parent returns `-ENOMEM`. The DRC parser stores string pointers into the original property data, so the property lifetime must outlive the decoded struct use. Root path has no parent and is rejected.

## Test Signals
Unit-style tests can feed valid and truncated DRC-info entries, root and nested paths, missing parent paths, and allocation-failure injection. Runtime signals are successful DLPAR connector parsing and dynamic OF node attachment.
