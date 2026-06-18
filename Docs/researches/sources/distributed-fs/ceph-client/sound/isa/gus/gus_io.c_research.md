<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_io.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_io.c

Purpose: low-level GF1/InterWave I/O primitives for register access, voice address conversion, DRAM byte access, AdLib timer writes, and active-voice selection.

Important APIs/types/functions: exported helpers include `snd_gf1_delay()`, `snd_gf1_write8/look8/write16/look16()`, interrupt-safe `snd_gf1_i_*()` variants, `snd_gf1_ctrl_stop()`, `snd_gf1_adlib_write()`, `snd_gf1_write_addr()`, `snd_gf1_read_addr()`, `snd_gf1_dram_addr()`, `snd_gf1_poke()`, `snd_gf1_peek()`, and `snd_gf1_select_active_voices()`.

Control flow: the internal `__snd_gf1_*` routines perform raw port writes and memory barriers. Public unlocked variants assume caller serialization; `i_` variants take `reg_lock`. Voice address helpers translate linear byte addresses into GF1 split start/end/current registers, handling enhanced mode and 16-bit addressing. `snd_gf1_select_active_voices()` clamps voice count, computes playback frequency, and writes active voice count on plain GF1.

State and persistence: writes mutate hardware registers and update `gus->gf1.active_voices` and `playback_freq`. DRAM poke/peek reads and writes onboard memory. No higher-level ALSA objects are created.

Dependencies and integration: every GUS file depends on this layer through `include/sound/gus.h`. Reset, PCM, memory detection, DMA, UART, timer, and board probes all call these helpers.

Risks: lock discipline is split between caller-locked and self-locking APIs; mixing them incorrectly can race register selection/data ports. Address conversion is hardware-specific and easy to break for enhanced/16-bit modes. Test signals are register readback during detection, voice setup, DRAM read/write, PCM pointer correctness, and running with lockdep/IRQ stress where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_io.c -->
