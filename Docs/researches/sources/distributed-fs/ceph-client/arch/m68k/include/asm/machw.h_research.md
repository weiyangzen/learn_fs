<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/machw.h

## Purpose
`machw.h` defines Macintosh video memory mapping constants.

## Important APIs, Types, and Functions
It defines `VIDEOMEMBASE` as `0xf0000000`, `VIDEOMEMSIZE` as 4 MiB, and `VIDEOMEMMASK` as the negative 4 MiB mask.

## Control Flow, State, and Persistence
There is no code. The constants describe the virtual video-memory mapping installed by early assembly.

## Dependencies and Integration Points
Mac framebuffer and early console code use these constants to address mapped video RAM.

## Risks
The constants assume `head.S` installed the mapping. Incorrect size or mask assumptions can wrap or alias framebuffer access.

## Test Signals
Signals include working early framebuffer access and no video memory access beyond the mapped 4 MiB range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machw.h -->
