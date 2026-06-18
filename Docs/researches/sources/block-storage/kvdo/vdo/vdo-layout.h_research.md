# File Research: sources/block-storage/kvdo/vdo/vdo-layout.h

This header documents and declares fixed-layout and VDO-layout APIs. A fixed layout is a simple partitioning scheme where partitions are carved from a free span; `vdo_layout` wraps it with knowledge of required VDO partitions and physical-growth state.

It declares partition creation, lookup, translation, encoding/decoding, standard VDO partitioned-layout construction, VDO-layout decode/free, partition retrieval, growth preparation/query/swap/cleanup, partition copying, and fixed-layout access.

`struct vdo_layout` holds current, next, and previous fixed layouts, starting offset, and optional `dm_kcopyd_client` used during grow-physical copy operations.
