<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusextreme.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gusextreme.c

Purpose: ALSA ISA driver for Gravis UltraSound Extreme, combining an ES1688 codec/front-end with a GF1 synth.

Important APIs/types/functions: `struct snd_gusextreme` embeds `struct snd_es1688` and a `struct snd_gus_card *`. Key functions create the ES1688 side, create GF1 side, enable GF1 access through ES1688 mixer/init ports, detect GF1, rename mixer controls, and probe/register the card.

Control flow: probe allocates one ALSA card, normalizes MPU defaults, creates ES1688 resources and optional MPU routing, sets default GF1 port relative to ES1688, creates GF1 resources, writes the ES1688 sequence that exposes GF1, validates GF1 reset behavior, initializes common GUS, requires `ess_flag`, creates ES1688 PCM/mixer, optional GF1 PCM, GF1 mixer, control renames, optional OPL3 and MPU401, and registers the card. Resume resets ES1688, re-enables GF1, then resumes GUS.

State and persistence: combines ES1688 and GF1 state in card private data. `gus->codec_flag` and `ess_flag` drive common helper behavior. Hardware routing through ES1688 is volatile and must be restored on resume.

Dependencies and integration: depends on `sound/es1688.h`, shared GUS library, OPL3, MPU401, ALSA ISA, and legacy auto-probe helpers.

Risks: GF1 enable sequence is reverse-engineered and port-sensitive. Two chips have separate IRQ/DMA resources, so longname and failure paths must reflect both. Test signals include ES1688 PCM/mixer, GF1 synth PCM/mixer, OPL3/MPU optional devices, control renames, suspend/resume re-exposing GF1, and failure when `ess_flag` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusextreme.c -->
