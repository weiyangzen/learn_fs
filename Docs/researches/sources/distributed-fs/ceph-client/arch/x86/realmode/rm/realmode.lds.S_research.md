<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.lds.S

## Purpose
`realmode.lds.S` lays out the relocatable `elf32-i386` real-mode image and defines the physical-address symbols used by the blob header and relocation tool.

## Important APIs, types, and functions
It defines sections `.header`, `.rodata`, `.text`, `.text32`, `.text64`, `.data`, `.bss`, `.signature`, `video_cards`, `video_cards_end`, `pa_text_start`, `pa_ro_end`, and includes generated `pasyms.h`.

## Control flow
The linker starts at zero so emitted addresses are offsets within the blob. Text is page aligned for later page-permission changes; data and bss are separated; note/debug sections are discarded.

## State and persistence behavior
State is the binary layout contract. The header and permission code depend on `pa_text_start`/`pa_ro_end`; the video code depends on `video_cards` bounds.

## Dependencies and integration points
It depends on `PAGE_SIZE`, kbuild-generated `pasyms.h`, and all realmode object sections using the expected names.

## Risks and edge cases
Misalignment or misplaced sections can make executable permissions too broad/narrow, hide video-card descriptors, or produce bad relocation offsets.

## Test signals
Signals are link success, inspection of section offsets, real-mode relocation output, and runtime permission checks in `init.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.lds.S -->
