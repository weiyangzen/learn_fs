<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarihw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarihw.h

## Purpose
This is the central Atari hardware register map for m68k Linux. It declares machine identity globals, NVRAM APIs, hardware-present flags, DMA cache maintenance, and volatile register structs for Atari video, DMA, sound, SCSI, SCC, DSP, MFP, SCU, RTC, ACIA, DMA sound, Microwire, and add-on hardware.

## Important APIs, Types, And Functions
- Machine predicates include `MACH_IS_ST`, `MACH_IS_STE`, `MACH_IS_MSTE`, `MACH_IS_TT`, `MACH_IS_FALCON`, `MACH_IS_MEDUSA`, and `MACH_IS_AB40`.
- `struct atari_hw_present` records available shifters, sound, storage interfaces, MFP/SCC/joystick/Microwire, DMA engines, clocks, SCU, blitter, VME, and DSP56K.
- NVRAM APIs are `atari_nvram_read()`, `atari_nvram_write()`, `atari_nvram_get_size()`, `atari_nvram_set_checksum()`, and `atari_nvram_initialize()`.
- `dma_cache_maintenance()` pushes or clears caches for DMA with Medusa and CPU-specific snooping exceptions.
- Register structs map `SHIFTER_ST`, `SHIFTER_TT`, `VIDEL`, `DMA_WD`, `SOUND_YM`, `TT_DMA`, `TT_5380`, `MATRIX`, `CODEC`, `BLITTER`, `SCC`, `DSP56K_HOST_INTERFACE`, `MFP`, `TT_SCU`, `TT_RTC`, `ACIA`, `TT_DMASND`, `TT_MICROWIRE`, and `MSTE_RTC`.
- Helper macros such as `DMASNDSetBase()`, `DMASNDGetAdr()`, `DMASNDSetEnd()`, and `MW_LM1992_*()` encode hardware register programming values.

## Control Flow
Platform setup fills machine globals and hardware-present flags. Drivers test those flags and write directly to the relevant volatile register structs. DMA users call `dma_cache_maintenance()` before or after transfers depending on direction. Sound, video, RTC, keyboard, serial, and storage drivers use the mapped structs to program hardware.

## State And Persistence Behavior
Persistent kernel state is in machine globals and `atari_hw_present`. Hardware state lives in memory-mapped registers and may change asynchronously through DMA, video counters, interrupts, and device activity. NVRAM persists across reboots.

## Dependencies And Integration Points
The header depends on Atari bootinfo, `asm/kmap.h`, MM/cacheflush support, and CPU feature macros. It is used broadly by Atari platform, framebuffer, sound, storage, serial, input, DSP, RTC/NVRAM, and interrupt code.

## Risks And Edge Cases
- Register layouts and padding are hardware contracts; field changes can silently write wrong addresses.
- DMA cache maintenance depends on machine and CPU snooping behavior and is easy to regress for Medusa/060 combinations.
- Many fixed addresses are accessed directly; mapping assumptions must hold before use.
- Duplicated or shared registers, such as Falcon/TT DMA sound fields, require machine-specific interpretation.

## Test Signals
Atari boot across ST/STE/TT/Falcon, hardware-present detection, NVRAM read/write/checksum, video mode changes, ST-DMA storage, SCSI, SCC/ACIA serial, sound/DMA sound, Microwire volume control, DSP host interface, MFP interrupts, and RTC reads are coverage signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarihw.h -->
