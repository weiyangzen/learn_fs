<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mixer.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_mixer.c

Purpose: ALSA mixer controls for the GF1 board mixer latch and optional ICS2101 mixer chip.

Important APIs/types/functions: exported `snd_gf1_new_mixer()`. GF1 controls use `GF1_SINGLE()` with `snd_gf1_get_single()`/`snd_gf1_put_single()`. ICS controls use `ICS_DOUBLE()` with `snd_ics_get_double()`/`snd_ics_put_double()`.

Control flow: `snd_gf1_new_mixer()` names the mixer, adds component metadata for ICS2101, then registers either simple GF1 boolean switches or full ICS volume/switch controls. Put handlers update cached `mix_cntrl_reg` or `gf1.ics_regs` under `reg_lock` and write the hardware mixer/control ports. Some ICS boards flip master/GF1 channels.

State and persistence: mixer latch and ICS register cache live in `struct snd_gus_card`. ALSA controls reflect these cached/hardware values. State is volatile and restored only by driver initialization/resume paths.

Dependencies and integration: board flags from `snd_gus_check_version()` decide whether ICS controls exist. Extreme boards later rename ES1688 controls around GF1 synth routing, while MAX/InterWave use WSS mixer code for codec paths.

Risks: non-ICS controls are minimal, and Extreme `ess_flag` limits simple GF1 controls to avoid duplicate routing. Hardware writes depend on exact port sequencing. Test signals are mixer control enumeration on Classic 2.4/3.5/3.7, switch toggling affecting latch register, ICS volume write/readback, and mixer names/components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mixer.c -->
