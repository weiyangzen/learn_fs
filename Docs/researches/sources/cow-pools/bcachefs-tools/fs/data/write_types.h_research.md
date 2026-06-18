# File Research: sources/cow-pools/bcachefs-tools/fs/data/write_types.h

## Role

Defines write flags and the core in-memory write operation structures used by `write.c`, data update, and debug code.

## Write Flags

`BCH_WRITE_FLAGS()` defines flags for allocation behavior, cached writes, pre-encoded data, page stability/ownership, specified-device allocation, mandatory EC, inline data, ENOSPC checking, sync mode, move/update writes, worker context, submitted state, and unwritten conversion.

The file defines both internal bit indices (`enum __bch_write_flags`) and public bit masks (`enum bch_write_flags`).

## `struct bch_write_bio`

Wraps a bio with bcachefs write metadata:

- Filesystem, parent split bio, and pinned device pointer.
- Submit time, logical inode offset, and nocow bucket.
- Failure list and target device id.
- Bitfields for split, bounce, bio ownership, nocow, mempool use, and first-btree-write state.
- Embedded `struct bio`.

The stored `bch_dev *ca` avoids re-looking up a device after removal has cleared `c->devs[]`.

## `struct bch_write_op`

Represents a complete write operation:

- Closure, filesystem, end callback, start time, optional async-object list index.
- Written sector count, flags, error, and IO-error state.
- Compression/checksum/replica/watermark settings and EC stripe wait state.
- Existing device list, target, nonce, inode options, subvolume, position, and version.
- Encoded-input CRC for move/data-update writes.
- Write point, disk reservation, open buckets, new file size, sector delta, insert keylist, inline key storage, nocow flush mask, and final embedded write bio.
