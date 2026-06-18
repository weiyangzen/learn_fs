# sources/distributed-fs/ceph-client/arch/m68k/amiga/amisound.c

Purpose: simple Amiga system beeper using Paula audio channel 2 and Chip RAM waveform data.

Important APIs are `amiga_init_sound()` and `amiga_mksound(hz, ticks)`. Exported variables `amiga_audio_min_period` and `amiga_audio_period` coordinate with framebuffer and DMA sound code. Initialization allocates Chip RAM for a 20-sample sine waveform via `amiga_chip_alloc_res()`, copies `sine_data`, computes a color-clock-based period constant, and may turn video off if no Amiga framebuffer is configured.

Control flow for `amiga_mksound()` deletes any pending stop timer, clamps requested frequency into Paula period limits, programs audio location/length/period/volume, optionally schedules `sound_timer`, and enables audio DMA. Invalid or zero frequencies call `nosound()`, which disables channel 2 DMA and restores the prior audio period.

State includes the Chip RAM waveform pointer, exported period values, `clock_constant`, Paula audio registers, DMA control, and a timer. Local IRQ disable protects register/timer updates.

Dependencies include `amiga_chip_alloc_res()`, `amiga_colorclock`, `amiga_custom`, jiffies/timers, and optional framebuffer hooks. Integration is through `mach_beep` in `config.c` and possible audio/fb driver cooperation.

Risks and test signals: failure to allocate Chip RAM disables beep; competing audio users can see period/DMA interference; incorrect min-period clamping can produce bad tones. Test by enabling `CONFIG_INPUT_M68K_BEEP`, calling console bell, and checking that audio DMA stops after `ticks`.
