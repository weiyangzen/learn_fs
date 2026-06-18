# sources/distributed-fs/ceph-client/sound/pci/cmipci.c

## Purpose

`cmipci.c` is the complete ALSA PCI driver for C-Media CMI8338/CMI8738-family sound cards, including later multichannel CMI8768/8769/8770-style variants. It handles PCI probe, register I/O, PCM playback/capture, second DAC/multichannel playback, IEC958/SPDIF playback and capture, AC3 mode handling, mixer controls, OPL3/FM, MPU-401 MIDI, optional gameport support, proc diagnostics, interrupt handling, and suspend/resume.

## Important APIs, Types, and Functions

- Module parameters: `index`, `id`, `enable`, `mpu_port`, `fm_port`, `soft_ac3`, and optional `joystick_port` configure card creation and legacy resources.
- `struct cmipci` is the device state: ALSA card/PCM/rawmidi pointers, PCI device, I/O base, IRQ, register shadow `ctrl`, chip capability flags, IEC958 status, open-mode tracking, mixer restore state, two DMA channel descriptors, gameport pointer, lock state, and suspend caches.
- `struct cmipci_pcm` stores one hardware channel's substream, running flag, format bits, DAC/capture role, DMA size, sample shift, channel index, and buffer address.
- `snd_cmipci_create()` performs PCI enablement, I/O region request, IRQ registration, chip detection, hardware reset, feature setup, FM/MIDI/gameport setup, PCM device creation, and mixer creation.
- `snd_cmipci_probe()` allocates the ALSA card and registers it with the PCI core through `module_pci_driver()`.
- PCM paths are implemented through `snd_cmipci_*_open()`, `snd_cmipci_pcm_prepare()`, `snd_cmipci_pcm_trigger()`, `snd_cmipci_pcm_pointer()`, and close/hw_free functions.
- SPDIF and AC3 handling is centered in `setup_spdif_playback()`, `setup_ac3()`, IEC958 control callbacks, and mixer auto-save/restore helpers.
- Mixer creation is handled by `snd_cmipci_mixer_new()` using SB-compatible register controls plus native CMI controls.
- Power management is implemented by `snd_cmipci_suspend()` and `snd_cmipci_resume()`.

## Control Flow

Probe begins in `snd_cmipci_probe()`, which selects a driver name based on PCI device ID and calls `snd_cmipci_create()`. Creation enables the PCI device, requests I/O regions, installs a shared IRQ handler, initializes locks and default channel state, queries chip capabilities, resets codec/channel registers, enables bus mastering, configures chip-specific quirks, sets card names, and then builds optional FM, proc, PCM, mixer, MIDI, and gameport interfaces.

PCM open uses `open_device_check()` to reserve channel A or B. Channel A is the primary DAC/playback path; channel B is capture or second DAC/multichannel playback depending on mode. Prepare computes sample format bits, frame-to-hardware shifts, DMA buffer and period counts, channel direction, rate selector fields, format register fields, and multichannel routing. Trigger starts, stops, pauses, or resumes by updating interrupt enable bits and `CM_REG_FUNCTRL0` channel enable/pause/reset bits. Pointer reads hardware remaining count and converts it back to ALSA frames.

IEC958 playback is enabled conditionally for normal playback when stream properties are compatible, and unconditionally for the dedicated SPDIF PCM. `setup_spdif_playback()` updates SPDIF routing bits, sample-rate bits, double-speed flags, and AC3 mode. During AC3 playback, `save_mixer_state()` disables or freezes selected mixer controls and `restore_mixer_state()` later restores them.

Interrupt handling first checks `CM_REG_INT_STATUS` for a real CMI interrupt. It acknowledges channel interrupts by toggling hold/clear bits, dispatches MPU-401 UART interrupts when present, and calls `snd_pcm_period_elapsed()` for running channel substreams. Mixer controls read and write either SB-compatible mixer ports or native CMI registers under `reg_lock`.

## State and Persistence Behavior

All runtime state is in memory and hardware registers. `cm->ctrl` shadows `CM_REG_FUNCTRL0` so channel enable, pause, and direction bits remain coherent across trigger operations. `opened[2]` serializes channel ownership and prevents incompatible playback/capture/multichannel combinations. `dig_status` and `dig_pcm_status` persist IEC958 default and stream status while the module is loaded. `mixer_res_status[]` stores mixer values temporarily while AC3 mode marks controls inactive.

Suspend saves selected dword registers and mixer registers into `saved_regs[]` and `saved_mixers[]`, disables interrupts, and resumes by resetting channels/mixer then restoring saved values. No persistent storage survives module unload or reboot.

## Dependencies and Integration Points

The driver integrates with ALSA core, control, PCM, rawmidi, MPU-401 UART, OPL3, SB mixer definitions, proc info, PCI, IRQ, gameport, and Linux module/PM infrastructure. Hardware access uses port I/O (`inb/outb/inw/outw/inl/outl`) rather than MMIO. The PCI ID table includes C-Media and ALi aliases for CM8338/CM8738 devices.

## Risks and Edge Cases

- Channel sharing is complex: channel B can be capture, second DAC, or multichannel output, so `opened[]` and `is_dac` transitions are critical.
- Multichannel setup only supports stereo 16-bit hardware format internally and rejects incompatible formats.
- SPDIF/AC3 mode changes temporarily alter mixer controls; failed allocation in `save_mixer_state()` can abort setup.
- Pointer reads retry only a few times before reporting `SNDRV_PCM_POS_XRUN` on invalid remaining counts.
- Several chip-version paths depend on undocumented or partly guessed register behavior, especially legacy AC3 and model detection.
- The silence hack writes zeros through an existing DMA buffer to avoid residual channel-A data contaminating rear DAC output.
- Optional legacy FM, MIDI, and joystick resources can fail independently; creation paths often disable the feature and continue.

## Test Signals

Validation should cover PCI probe and card registration across representative chip versions, duplex PCM playback/capture, second DAC and 4/6/8-channel modes, SPDIF PCM open/prepare/hw_free, AC3 non-audio stream handling, mixer control read/write and inactive behavior during AC3, MPU-401 interrupt traffic, optional FM/gameport registration, suspend/resume restoration, and shared IRQ behavior. Kernel logs for invalid PCM pointers, missing legacy ports, and chip-detection names are important signals.
