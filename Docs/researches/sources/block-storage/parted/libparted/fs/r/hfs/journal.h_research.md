# File Research: sources/block-storage/parted/libparted/fs/r/hfs/journal.h

Declares HFS+ journal helpers and endian conversion macros.

Exports:
- `hfsj_replay_journal()`.
- `hfsj_update_jib()`.
- `hfsj_update_jl()`.

Defines:
- `HFS_16_TO_CPU`, `HFS_32_TO_CPU`, `HFS_64_TO_CPU`.
- `HFS_CPU_TO_16`, `HFS_CPU_TO_32`, `HFS_CPU_TO_64`.

Role:
- Shared journal API for HFS+ open/relocation code.
