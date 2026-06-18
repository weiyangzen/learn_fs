<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigahw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigahw.h

## Purpose
This header is the central Amiga hardware map for m68k Linux. It describes detected hardware flags, global clock/memory properties, custom chip register layouts, CIA registers, Zorro-II address translation, chip RAM allocation APIs, display shutdown behavior, and Amiga TOD clock register formats.

## Important APIs, Types, And Functions
- Global state includes `amiga_chipset`, `amiga_eclock`, `amiga_colorclock`, `amiga_chip_size`, `amiga_vblank`, `amiga_hw_present`, and `amiga_audio_min_period`.
- `struct amiga_hw_present` records available video, audio, storage, I/O, clock, chipset, PCMCIA, and Zorro features.
- `struct CUSTOM` maps the large Amiga custom chip register block, including DMA, blitter, copper, bitplanes, sprites, audio channels, colors, beam timing, and fetch mode.
- `struct CIA` maps CIAA/CIAB timers, ports, serial, and interrupt registers.
- `amiga_custom`, `ciaa`, `ciab`, `ZTWO_PADDR()`, and `ZTWO_VADDR()` provide fixed register and Zorro-II translations.
- `amiga_chip_init()`, `amiga_chip_alloc()`, `amiga_chip_alloc_res()`, `amiga_chip_free()`, and `amiga_chip_avail()` expose chip RAM allocation.
- `amifb_video_off()` programs ECS/AGA display timing and adjusts minimum audio period.

## Control Flow
Most use is direct volatile hardware access. Platform setup fills hardware-present flags and globals from bootinfo. Drivers probe flags, access `amiga_custom` or CIA registers, and allocate chip RAM. `amifb_video_off()` conditionally writes display timing registers when the chipset supports ECS/AGA.

## State And Persistence Behavior
Persistent kernel state is in the exported globals and `amiga_hw_present`; hardware state persists in custom chips and CIAs. Chip RAM allocations are tracked by the implementation behind the declared allocator APIs. TOD clock structs map battery-backed hardware clock nibbles.

## Dependencies And Integration Points
The file depends on Amiga bootinfo and Linux resource types. It is used by framebuffer, sound, input, serial/parallel, floppy, SCSI/IDE, PCMCIA, Zorro, RTC, and platform initialization code.

## Risks And Edge Cases
- `struct CUSTOM` layout must match the hardware reference exactly; padding or type changes can redirect register writes.
- Chip RAM is shared with DMA-capable custom chips, so allocation alignment/lifetime bugs can corrupt display/audio/disk DMA.
- `amifb_video_off()` changes beam timing and audio limits globally.
- Zorro-II address translation assumes the `zTwoBase` virtual mapping.

## Test Signals
Amiga platform boot, hardware detection, chip RAM allocator stress, framebuffer on/off, audio DMA, CIA timer/interrupt handling, floppy/IDE/SCSI access, RTC reads, and Zorro device probing validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigahw.h -->
