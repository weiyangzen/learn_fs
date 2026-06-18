<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/galaxy.c -->
# sources/distributed-fs/ceph-client/sound/isa/galaxy/galaxy.c

Purpose: shared implementation for Aztech AZT1605/AZT2316 Sound Galaxy ISA cards. It probes the Sound Blaster-compatible DSP, writes the board configuration latch, switches to WSS mode, and registers ALSA WSS PCM/mixer/timer plus optional MPU-401 and OPL3 devices.

Important APIs/types/functions: `struct snd_galaxy` stores mapped DSP/config/WSS ports, saved config, and resources. DSP helpers are `dsp_reset()`, `dsp_command()`, `dsp_get_version()`. WSS helpers are `wss_detect()` and `wss_set_config()`. Main driver functions are `snd_galaxy_match()`, `galaxy_init()`, `galaxy_set_config()`, `galaxy_config()`, `galaxy_wss_config()`, `__snd_galaxy_probe()`, and `module_isa_driver()`.

Control flow: the ISA match callback validates module parameters and encodes them into `config[n]` and `wss_config[n]`. Probe allocates an ALSA card, requests/maps SB DSP ports, verifies the DSP signature and expected version/type, requests/maps the high config port, saves current config and writes the new config, requests/maps WSS ports, validates WSS signature, writes WSS IRQ/DMA config, switches the card to WSS mode, creates WSS PCM/mixer/timer, and optionally creates MPU-401 and OPL3 resources before registering the card.

State and persistence: module parameter arrays are mutated from IRQ 2 to 9 and from unspecified optional ports to `-1`. `struct snd_galaxy.config` preserves masked board bits and `snd_galaxy_free()` restores the original config and clears WSS config on card cleanup.

Dependencies and integration: relies on wrapper macros from `azt1605.c`/`azt2316.c`, Linux ISA/I/O mapping, ALSA WSS, MPU401, OPL3, and devres card/resource cleanup.

Risks: parameter validation is strict, so auto-probe is intentionally not implemented. Config port writes are hardware-latch sensitive and preserve only masked fields. Shared WSS/MPU IRQ is rejected. Test signals are module load with known valid resources, failure on invalid resource combinations, WSS PCM playback/capture, optional MIDI/FM, and unload restoring the original config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/galaxy.c -->
