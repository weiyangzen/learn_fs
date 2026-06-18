<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_reset.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_reset.c

Purpose: GF1 hardware start/stop, default interrupt handlers, voice allocation/freeing, voice stopping, and GF1 suspend/resume support.

Important APIs/types/functions: exported `snd_gf1_set_default_handlers()`, `snd_gf1_smart_stop_voice()`, `snd_gf1_stop_voice()`, `snd_gf1_stop_voices()`, `snd_gf1_alloc_voice()`, `snd_gf1_free_voice()`, `snd_gf1_start()`, `snd_gf1_stop()`, `snd_gf1_suspend()`, and `snd_gf1_resume()`. Internals initialize software state, clear registers, clear voices, and run `snd_gf1_hw_start()`.

Control flow: startup resets GF1, initializes callback pointers and voices, optionally enables enhanced mode and memory control, computes default silent voice address, clears DRAM silence bytes, clears all voices, enables IRQ/DAC, initializes timers, memory allocator/proc entries, and debug IRQ profiling. Voice allocation finds unused voices, respecting PCM reservation, and can steal idle MIDI voices. Free restores default handlers, clears hardware voice state, and invokes private cleanup.

State and persistence: mutates `gus->gf1` voice table, callback pointers, LFO flags, default voice address, timer state, memory allocator, UART command state, and hardware reset/mode registers. Resume preserves software state but restarts hardware and timers/UART.

Dependencies and integration: used by `snd_gus_initialize()`, PCM voice management, DMA/UART/timer handlers, and board PM callbacks.

Risks: voice stop ramping sleeps when not in interrupt; callers must avoid sleeping contexts. Hardware start has different initial vs resume paths. Test signals include all voices cleared after init/stop, PCM voice allocation limits, MIDI voice stealing, GF1 reset register transitions, timer/proc setup, suspend draining DMA/UART and disabling capture DMA, and resume restoring active timers/UART.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_reset.c -->
