# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.c

## Purpose

This file manages PCXHR firmware loading and the post-firmware hardware setup sequence. Despite the historical "hwdep" name, it uses the kernel firmware API directly, loads the Xilinx/DSP images, validates DSP capabilities, initializes board options, allocates DSP pipes, creates PCM/mixer devices after firmware is ready, and starts the pipes.

## Important APIs, Types, And Functions

- `pcxhr_setup_firmware()` selects a firmware filename set from `mgr->fw_file_set`, requests each image, and calls `pcxhr_dsp_load()`.
- `pcxhr_dsp_load()` dispatches firmware stages by index: internal Xilinx, communication Xilinx, DSP eeprom, DSP boot, and DSP main.
- `pcxhr_init_board()` enables DSP interrupts, verifies supported physical I/O and stream counts with `CMD_SUPPORTED`, sends `CMD_VERSION`, stores DSP version, and delegates board-specific initialization.
- `pcxhr_sub_init()` handles generic PCXHR option detection and input/output unmute.
- `pcxhr_dsp_allocate_pipe()`, `pcxhr_config_pipes()`, and `pcxhr_start_pipes()` define and start DSP playback/capture pipes.
- `pcxhr_reset_board()` mutes and resets hardware during removal or failure cleanup.

## Control Flow

Probe calls `pcxhr_setup_firmware()`. For each required image, the file requests `pcxhr/<name>` firmware, loads it through the lower-level routines in `pcxhr_core.c`, releases it, and records the loaded bit. The final DSP image triggers board initialization: enable interrupts, query DSP capabilities, send driver/DSP version and granularity, run generic or HR222 sub-init, allocate all playback/capture pipes, create PCM devices for each logical chip, create the mixer once through chip 0, register cards, and start all pipes.

## State And Persistence

The file advances `mgr->dsp_loaded`, fills `mgr->dsp_version`, discovers `board_has_analog`, defines pipe status and stream-to-pipe links in each `snd_pcxhr`, and relies on `mgr->hostport` DMA allocated by probe. Firmware files are persistent external dependencies, but the driver stores only loaded-stage bits.

## Dependencies And Integration Points

It depends on firmware filenames matching installed kernel firmware blobs, on `pcxhr_core.c` for binary transfer and RMH commands, on `pcxhr_mix22.c` for HR stereo initialization, on `pcxhr_create_pcm()` from `pcxhr.c`, and on `pcxhr_create_mixer()` from `pcxhr_mixer.c`.

## Risks

- Missing firmware aborts probe with `-ENOENT`.
- The final firmware stage has many side effects after DSP load; failures during PCM/mixer/card registration need complete cleanup through the manager.
- `pcxhr_dsp_allocate_pipe()` assumes audio pin numbering from card index and mono/stereo capture mode; mismatches break channel routing.
- Generic unmute behavior is inverted for some registers: comments note writes/read differences for mute state, so changes need hardware validation.
- `sprintf(path, "pcxhr/%s", ...)` relies on firmware names fitting the fixed 32-byte buffer.

## Test Signals

Test every firmware set used by board parameters, missing-firmware failure paths, DSP capability rejection, mono-capture pipe allocation, card registration after firmware load, mixer creation, pipe start, and cleanup/reset after partial firmware load.
