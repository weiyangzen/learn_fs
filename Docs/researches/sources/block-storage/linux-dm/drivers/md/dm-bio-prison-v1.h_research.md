# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.h

Declares the v1 bio-prison API and exposes `struct dm_bio_prison_cell` layout so callers can preallocate and manage cell memory. A cell contains a client `user_list`, rb-tree node, range key, current holder bio, and detained bio list.

`struct dm_cell_key` identifies a virtual or physical block range for a thin device. The comments define the key semantic: bios in the same overlapping cell are detained until unlock, preventing conflicting operations from running concurrently.

The API separates cell allocation from insertion so callers can avoid allocation under locks or in constrained contexts. `dm_get_cell()` retrieves/creates without a bio; `dm_bio_detain()` atomically retrieves/creates and appends a bio if the cell already exists; release variants expose holder/inmate control.

The header also declares deferred-set primitives used by thin/cache code to hold pending work behind outstanding operations. Its comments document the core safety reason: avoid installing a new mapping until prior reads of the old shared block have completed.
