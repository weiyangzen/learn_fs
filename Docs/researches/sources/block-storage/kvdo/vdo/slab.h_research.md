# File Research: sources/block-storage/kvdo/vdo/slab.h

This header declares `struct vdo_slab`, the allocator-owned unit containing data blocks, reference-count metadata, and a slab journal. It records allocator ownership, journal/ref-count pointers, slab number, start/end PBNs, metadata origins, admin state, rebuild status, scrub tracking, and allocation priority.

The persisted/operational status enum covers rebuilt, replaying, requiring scrubbing, high-priority scrubbing, and rebuilding. Inline helpers classify unrecovered, replaying, and rebuilding slabs, and convert list entries back to slabs.

Public functions expose slab construction/freeing, ref-count allocation, zone lookup, recovery marking, opening, free-block query, reference modification, provisional reference acquisition, PBN-to-slab-block translation, save decision, admin action start/load/drain/resume notification, scrub completion, and debug dump.
