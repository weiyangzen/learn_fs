# File Research: sources/block-storage/mdadm/super-gpt.c

Purpose: pseudo metadata handler for devices with GPT partition tables.

Behavior:
- GPT is not usable for creating or assembling md arrays directly.
- It exists so mdadm can load, examine, store, and report partition-table metadata when preparing bare devices whose partitions may become md members.

Key functions:
- `load_gpt()` reads protective MBR, validates GPT partition type, reads GPT header at sector size offset, validates GPT signature, limits partition count to less than 128, and reads partition entries.
- `examine_gpt()` prints GPT magic, revision, and partition extents.
- `store_gpt()` writes stored GPT/entry data back, calls `fsync()`, then asks the kernel to reread partitions with `BLKRRPART`.
- `getinfo_gpt()` fills mdinfo with text/name `"gpt"` and component size derived from highest partition ending LBA.
- `validate_geometry()` always rejects GPT as normal md metadata.

Risks and notes:
- Comments acknowledge incomplete GPT writing: backup GPT copy and non-512-byte block handling are FIXME areas.
- Load uses actual sector size for reading header/entries, but store comments still note 512-byte assumptions.
