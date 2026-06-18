<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_main.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_main.c

Purpose: common GUS card allocation, resource management, plain GF1 memory detection, DMA/IRQ latch programming, version detection, ALSA joystick control, and suspend/resume wrappers.

Important APIs/types/functions: exported `snd_gus_create()`, `snd_gus_initialize()`, `snd_gus_suspend()`, and `snd_gus_resume()`. Internal work is in `snd_gus_free()`, `snd_gus_init_dma_irq()`, `snd_gus_check_version()`, and `snd_gus_detect_memory()`. The file also exports symbols implemented by other GUS helper objects.

Control flow: board drivers call `snd_gus_create()` to allocate `struct snd_gus_card`, initialize locks and register addresses, request I/O/IRQ/DMA, clamp voice/channel counts, and register a low-level ALSA device. `snd_gus_initialize()` checks plain GF1 version unless InterWave, detects memory, programs DMA/IRQ latches, and starts GF1 hardware. Suspend suspends PCM then GF1; resume reprograms latches and resumes GF1.

State and persistence: `struct snd_gus_card` owns all GF1 resource descriptors, flags such as `max_flag`, `ace_flag`, `ess_flag`, DMA/IRQ sharing flags, memory bank allocator state, mixer latch state, and joystick DAC. Hardware latch state is reprogrammed on init/resume and cleared on free.

Dependencies and integration: all board drivers depend on this allocator. It integrates with ALSA `snd_device_new()`, raw ISA resource APIs, DMA APIs, and `snd_gf1_start/stop`.

Risks: manual resource cleanup is mixed with ALSA device lifetime; failure paths must call `snd_gus_free()`. Negative IRQ values are used by some board drivers to indicate shared IRQ arrangements before external request. Test signals are create/fail cleanup, plain GF1 memory sizing, version flag detection, DMA/IRQ latch programming, joystick mixer control, and PM resume restoring playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_main.c -->
