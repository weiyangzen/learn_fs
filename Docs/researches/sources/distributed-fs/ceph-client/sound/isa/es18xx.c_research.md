<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es18xx.c -->
# sources/distributed-fs/ceph-client/sound/isa/es18xx.c

Purpose: standalone ALSA ISA/PNP driver for ESS ES18xx AudioDrive chips. It probes ES1868/1869/1878/1879/1887/1888 variants, configures chip-specific mixer and PCM capabilities, registers PCM playback/capture, OPL3, and optional MPU-401 UART devices.

Important APIs, types, and functions: `struct snd_es18xx` stores card resources, chip version/caps, active stream bits, DMA shifts, PCM substreams, rawmidi, mixer controls, locks, and PnP handles. Low-level register access is via `snd_es18xx_dsp_command()`, `snd_es18xx_read/write/bits()`, mixer helpers, and control-port helpers. PCM entry points are `snd_es18xx_playback_*`, `snd_es18xx_capture_*`, `snd_es18xx_pcm()`. Probe paths are `snd_es18xx_new_device()`, `snd_es18xx_identify()`, `snd_es18xx_probe()`, `snd_audiodrive_probe()`, ISA probe, PNPBIOS probe, and PnP-card probe. PM uses `snd_es18xx_suspend()` and `snd_es18xx_resume()`.

Control flow: module init registers an ISA driver and, when enabled, PnP and PnP-card drivers. Probing allocates an ALSA card, activates or auto-selects resources, requests I/O/IRQ/DMA, resets and identifies the chip, maps version to capability flags, initializes chip registers, creates PCM and mixer devices, then attaches OPL3 and MPU-401 when ports are valid. PCM prepare programs rate, format, period count, and ISA DMA; triggers toggle device DMA bits; interrupt dispatch reads status and calls `snd_pcm_period_elapsed()` for active DAC/ADC streams or `snd_mpu401_uart_interrupt()` for MIDI.

State and persistence: runtime state is volatile in `struct snd_es18xx`; mixer state lives in hardware registers and ALSA controls. PnP resource arrays are overwritten from activated devices. PM only saves the PM register and restores power state, so full mixer/PCM state is not deeply serialized. Active stream masks and substream pointers gate half/full-duplex restrictions.

Dependencies and integration: uses Linux ISA, PnP, ISAPnP, I/O port, IRQ, and DMA APIs; ALSA core, control, PCM, OPL3, MPU401, and initval helpers. The driver integrates with `/proc` and userspace through normal ALSA card, PCM, mixer, rawmidi, and hwdep registration.

Risks: hardware timings are busy-wait based, and comments document pops plus questionable 16-bit DMA behavior. Duplex mode has chip-specific constraints and shared DMA cases disable some capabilities. Mixer control arrays rely on exact version/capability mapping. IRQ status handling always returns handled once status is nonzero and must keep hardware ack order correct. PnP activation has legacy vendor-register side effects.

Test signals: module load with explicit/auto resources, PnP and non-PnP detection, `aplay`/`arecord` at mono/stereo 8/16-bit rates, duplex conflict checks, mixer control enumeration per chip, OPL3 and MPU-401 creation, interrupt period progress, suspend/resume smoke tests, and resource failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es18xx.c -->
