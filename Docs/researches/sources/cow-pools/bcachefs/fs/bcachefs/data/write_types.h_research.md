# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/write_types.h

Core write-path structures and write flag definitions.

Key contents:
- Defines `BCH_WRITE_FLAGS()` and corresponding bit flags: allocation behavior, cached/data-encoded/page ownership, device targeting, EC requirement, inline write marker, ENOSPC checking, sync/move/in-worker/submitted state, and unwritten conversion.
- `struct bch_write_bio` embeds `struct bio` plus filesystem/device refs, parent split bio pointer, submit metadata, failure state, device id, nocow bucket, and state bits.
- `struct bch_write_op` is the full write operation: closure, completion callback, async debug index, status/error fields, checksum/compression/replica options, target/write point, inode/subvolume/position/version, encoded CRC, reservation, open buckets, inode size/sector deltas, insert keylist, flush mask, and embedded first `bch_write_bio`.

Important invariants:
- `bch_write_bio.ca` doubles as “we hold an IO ref” state and is stashed so completion does not re-derive a device pointer after removal.
- `struct bch_write_bio` must be last in `struct bch_write_op`.
- `inline_keys` provides initial storage for up to two maximum-size extent keys.
