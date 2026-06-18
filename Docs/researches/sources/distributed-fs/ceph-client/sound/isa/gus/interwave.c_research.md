<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/interwave.c

Purpose: ALSA ISA/PNP driver for AMD InterWave cards and, when included with `SNDRV_STB`, InterWave STB cards with TEA6330T tone control. It combines InterWave GF1-compatible synth, WSS codec, optional ROM/RAM bank detection, MIDI UART, and PM restoration.

Important APIs/types/functions: `struct snd_interwave` stores card, GUS, WSS, IRQ/status ports, PnP handles, and STB I2C state. Key functions include `snd_interwave_detect()`, `snd_interwave_detect_memory()`, `snd_interwave_init()`, `snd_interwave_mixer()`, `snd_interwave_pnp()`, `snd_interwave_probe_gus()`, `snd_interwave_probe()`, ISA/PNP probe paths, and PM restore helpers. STB builds add I2C bit ops and `snd_interwave_detect_stb()`.

Control flow: module init registers an ISA driver and PnP-card driver. ISA probe auto-selects IRQ/DMAs and optionally ports, creates a card, creates GUS resources, detects InterWave by reset/version-register behavior, detects STB tone control if enabled, records status ports, initializes InterWave compatibility registers, detects RAM/ROM layout, starts common GUS, requests a shared IRQ, creates WSS codec PCM/timer/mixer, optional GF1 PCM, InterWave mixer renames/additions, optional STB TEA6330T mixer, rawmidi, card names, and registers the card. PnP probe activates logical devices first and feeds resources into the same probe.

State and persistence: memory bank sizes, ROM presence, revision, joystick DAC, InterWave flags, WSS/GUS pointers, and STB I2C state live in card/GUS structs. PM resumes GUS, restores InterWave compatibility and memory-config registers, resumes WSS, and restores TEA6330T mixer if present.

Dependencies and integration: shared GUS library, ALSA WSS, Linux ISA/PNP, legacy resource helpers, optional ALSA I2C and TEA6330T. Combined IRQ routes GF1 and WSS by polling status.

Risks: InterWave memory configuration detection writes RAM test bytes and relies on known layout codes. ISA auto-port loop returns early after `snd_interwave_probe_gus()` success without running full probe in one branch, a path worth regression-checking. STB/non-STB behavior is controlled by include-time macro. Test signals include PnP and manual ISA probing, RAM/ROM proc entries, WSS codec audio, GF1 synth PCM, rawmidi with `midi` parameter, shared IRQs, STB tone-control mixer, and suspend/resume restoring memory layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave.c -->
