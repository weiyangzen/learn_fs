# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_main.c

## Purpose

`emu10k1_main.c` is the central hardware-control implementation for the EMU10K1/Audigy driver. It initializes and shuts down the chip, identifies card models, configures DMA memory, firmware-backed E-MU 1010/Hana hardware, ECARD/CardBus variants, interrupts, voice defaults, FX engine setup, and suspend/resume register preservation.

## Important APIs, Types, and Functions

Core entry points are `snd_emu10k1_create()`, `snd_emu10k1_done()`, `snd_emu10k1_voice_init()`, `snd_emu10k1_suspend_regs()`, `snd_emu10k1_resume_init()`, and `snd_emu10k1_resume_regs()`. Hardware init helpers include `snd_emu10k1_init()`, `snd_emu10k1_audio_enable()`, `snd_emu10k1_ecard_init()`, `snd_emu10k1_ecard_write()`, `snd_emu10k1_ecard_setadcgain()`, `snd_emu10k1_cardbus_init()`, `snd_emu10k1_emu1010_init()`, `snd_emu1010_load_firmware()`, `snd_emu1010_load_dock_firmware()`, `emu1010_dock_event()`, `emu1010_clock_event()`, `emu1010_work()`, and `emu1010_interrupt()`. `emu_chip_details[]` maps PCI IDs/subsystems/revisions to model capabilities such as EMU10K1, Audigy, CA0102/CA0108, CA0151/P16V, CardBus, E-MU 1010, ECARD, AC97, speaker layouts, and quirks.

## Control Flow

`snd_emu10k1_create()` enables the PCI device, initializes locks/lists/work, reads subsystem identity, selects a capability table entry, detects IOMMU workaround needs, sets DMA masks and register bases, requests I/O regions, allocates the page table and silent page, creates the synth sample memory header, sets PCI bus mastering, applies extin/extout masks, and runs variant-specific initialization. It then requests the IRQ, initializes S/PDIF bits, fills the page table with silent-page mappings, assigns voice numbers, runs `snd_emu10k1_init()`, allocates PM buffers, initializes FX8010, enables audio, and optionally registers procfs.

`snd_emu10k1_init()` disables interrupts/audio, resets capture buffers and voices, configures Audigy/P16V/P17V special registers, SPI DAC and I2C ADC init where present, sets page table and silent mappings, writes HCFG according to model, optionally toggles IR, and enables expanded memory. E-MU 1010 setup loads Hana firmware, optional dock firmware, programs FPGA routing, default clocks, MIDI routing, IRQ enables, and unmute state. Shutdown disables interrupts, silences voices, stops DSP execution, resets buffers/page table, and locks/mutes hardware.

Suspend saves per-voice and global registers into allocated buffers; resume reruns variant init, core init, audio enable, HCFG/A_IOCFG restore, and register replay.

## State and Persistence Behavior

Persistent driver state includes `struct snd_emu10k1` fields for capability model, port, IRQ, DMA mask, page tables, silent page, memory header, voice table, S/PDIF bits, FX8010 state, E-MU 1010 firmware pointers/dock state/clock state, saved PM registers, and IOMMU workaround flag. Firmware objects are retained for reuse and released in `snd_emu10k1_free()`. PM state is stored in `saved_ptr`, `saved_hcfg`, and `saved_a_iocfg`.

## Dependencies and Integration Points

The file depends on Linux PCI, firmware, DMA, IOMMU, workqueue, mutex/spinlock, vmalloc, and ALSA core APIs. It integrates with sibling IRQ, I/O, memory, voice, FX, mixer, PCM, P16V, procfs, and synth code through exported driver helpers and shared `sound/emu10k1.h` types.

## Risks and Test Signals

Risks include model-table misidentification, DMA mask/page-table mistakes, IOMMU over-read workaround regressions, variant-specific GPIO/HCFG ordering, E-MU firmware load failures, workqueue versus suspend/shutdown races, and PM register coverage gaps. Test with builds across PM/procfs configs, probe on representative SB Live/Audigy/Audigy2/E-MU/CardBus models, firmware load and dock hotplug events, DMA playback/capture under IOMMU, FX8010 operation, suspend/resume, and module unload cleanup.
