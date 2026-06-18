# File Research: sources/block-storage/parted/libparted/fs/r/hfs/journal.c

HFS+ journal replay and journal-location update helpers.

Key behavior:
- Computes Apple-style journal checksums.
- `hfsj_update_jib()` updates the volume header’s journal info block pointer and writes the volume header.
- `hfsj_update_jl()` updates the journal info block’s journal offset.
- `hfsj_replay_journal()` reads the journal info block and journal header, validates in-volume journal placement, sector-size alignment, magic values, size consistency, header sizes, and checksum.
- Detects journal endianness and uses endian-conversion macros from `journal.h`.
- Prompts before replaying non-empty journals.
- `hfsj_replay_transaction()` walks journal block-list headers, validates checksums and block sizes, reads transaction blocks from the circular journal, writes them to target sectors, syncs, and advances journal start.
- Warns and aborts open if replay changed the volume header or wrapper MDB.

Important dependencies:
- HFS+ relocation header for `hfsplus_update_vh()`.
- HFS/HFS+ journal structures from `hfs.h`.
- Libparted geometry read/write/sync and exception APIs.

Notable constraints:
- Journals outside the volume are unsupported.
- Only 512-byte journal sectors are supported.
