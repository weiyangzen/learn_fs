<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_timer.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_timer.c

Purpose: exposes the two GF1 AdLib-compatible timers as ALSA card timers.

Important APIs/types/functions: `snd_gf1_timers_init()`, `snd_gf1_timers_done()`, and `snd_gf1_timers_resume()` manage timer lifecycle. Timer hardware callbacks are `snd_gf1_timer1_start/stop()` and `snd_gf1_timer2_start/stop()`. IRQ callbacks are `snd_gf1_interrupt_timer1()` and `snd_gf1_interrupt_timer2()`.

Control flow: init installs timer interrupt handlers, creates timer #1 with 80us resolution and timer #2 with 320us resolution, and stores them in `gus->gf1`. Start writes the count register, sets `timer_enabled` bits, updates sound-blaster control, and writes AdLib timer control. IRQ callbacks call `snd_timer_interrupt()`. Done restores default handlers and frees timer devices. Resume reinstalls handlers and restarts timers that were enabled.

State and persistence: `gus->gf1.timer1`, `timer2`, and `timer_enabled` hold timer state. Hardware timer registers are volatile and reprogrammed on start/resume.

Dependencies and integration: initialized by GF1 start and used by ALSA timer clients. The main IRQ dispatcher calls the installed handlers.

Risks: timer control bits are shared with GF1 sound-blaster control register; stop/start must preserve other timer bit. Test signals include ALSA timer creation, start/stop tick delivery, interrupt counters under debug, timer free cleanup, and resume rearming previously enabled timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_timer.c -->
