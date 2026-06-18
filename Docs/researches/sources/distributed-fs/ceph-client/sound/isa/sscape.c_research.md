# sources/distributed-fs/ceph-client/sound/isa/sscape.c

## Purpose
This is the ALSA ISA and ISA PnP driver for ENSONIQ SoundScape cards, including MediaFX/SoundFX, SoundScape, SoundScape PnP, and SoundScape VIVO variants. It detects and configures the SoundScape board, uploads MIDI firmware over ISA DMA for non-VIVO boards, creates the AD1845/WSS PCM and mixer path, and creates MPU-401 MIDI support.

## Important APIs, Types, and Functions
`struct soundscape` stores lock, IO bases, IRQs, DMA channels, IC type, card type, resources, WSS chip, MIDI volume, joystick and firmware/MIDI enable state, and device pointer. Low-level helpers access ODIE/OPUS registers and host-mode ports: `sscape_write_unsafe()`, `sscape_read_unsafe()`, `set_host_mode_unsafe()`, `set_midi_mode_unsafe()`, `host_read_ctrl_unsafe()`, and `host_write_ctrl_unsafe()`. Firmware upload is handled by `upload_dma_data()`, `sscape_upload_bootblock()`, and `sscape_upload_microcode()`. Board setup uses `detect_sscape()` and `sscape_configure_board()`. Device creation is split into `create_ad1845()`, `create_mpu401()`, and `create_sscape()`.

## Control Flow
Legacy ISA probing requires explicit IO, IRQ, MPU IRQ, and DMA. PnP probing reads resources from the logical device, distinguishes VIVO from PnP by ID, derives WSS and second DMA settings, and stores them in `struct soundscape`. `create_sscape()` reserves IO, requests DMA, initializes the lock, detects the hardware with port/register tests, configures DMA/IRQ/codec routing and joystick state, creates the AD1845/WSS PCM/mixer/timer path, and then handles MIDI firmware for non-VIVO cards.

Firmware upload allocates a 32 KiB DMA buffer, resets the board, configures channel A DMA, copies firmware in chunks, starts board DMA, waits for completion, boots the board, and waits for OBP and host startup acknowledgements. The bootblock firmware `scope.cod` returns a microcode version, and the driver then loads `sndscape.coN`. After firmware upload, it creates MPU-401 rawmidi, initializes MIDI volume state, and restores MIDI host commands.

## State and Persistence
Runtime state includes stored module/PnP settings, board type, IC type, WSS chip state, MIDI volume, and whether MIDI firmware was enabled. Suspend saves WSS state. Resume reconfigures board registers, reloads MIDI firmware when enabled, restores MIDI state, resumes WSS, and marks power D0. No disk persistence exists, but firmware files are required at probe and resume.

## Dependencies and Integration Points
The file depends on Linux ISA, PnP, firmware loading, IO ports, ISA DMA, ALSA WSS, MPU-401, and ALSA control APIs. It registers both an ISA driver and, when configured, a PnP card driver. It declares firmware dependencies for `scope.cod` and `sndscape.co0` through `sndscape.co4`.

## Risks and Edge Cases
The driver contains many undocumented magic values and comments noting behavior inferred from OSS code. Firmware upload uses DMA and mixed spinlock/sleeping waits, so lock boundaries are critical. MIDI is deliberately disabled if MPU-401 verification fails to avoid hangs. Resume can partially fail MIDI restore but still resumes WSS. PnP and ISA registration share module state flags.

## Test Signals
Probe should identify the card type and IO/IRQ/DMA settings, create WSS PCM/mixer/timer, create the MIDI mixer control for non-VIVO cards, load `scope.cod` and a matching `sndscape.coN`, expose MPU-401 only after firmware, reject MIDI open when firmware verification fails, and reload firmware plus restore MIDI volume after suspend/resume.
