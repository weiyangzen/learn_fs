<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_asc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_asc.h

## Purpose
`mac_asc.h` defines offsets and control bits for the Apple Sound Chip used on classic Macintosh systems.

## Important APIs, Types, and Functions
It maps the ASC sample buffer (`ASC_BUF_BASE`, `ASC_BUF_SIZE`), control, enable, mode, volume, channel register, and per-channel frequency byte offset through `ASC_FREQ(chan, byte)`.

## Control Flow, State, and Persistence
There is no code. State persists in the ASC MMIO buffer and registers.

## Dependencies and Integration Points
Mac sound drivers and platform audio initialization use these constants when programming sample playback, volume, and frequency.

## Risks
The header exposes raw offsets only; users must know the mapped ASC base and required access widths. The `ASC_CHAN` comment marks uncertainty, so callers should avoid relying on undocumented semantics.

## Test Signals
Signals include ASC sample playback, volume control, frequency programming per channel, and no buffer overrun beyond the 0x800-byte buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_asc.h -->
