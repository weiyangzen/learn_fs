<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.c

## Purpose
Hardware-dependent ALSA interface for older TASCAM US-X2Y devices. It handles user-space firmware/FPGA loading and exposes shared control memory for US-428 surface controls and lights.

## APIs, Types, and Functions
Exports `usx2y_hwdep_new()`. Important internals are `snd_usx2y_hwdep_dsp_status()`, `snd_usx2y_hwdep_dsp_load()`, `snd_us428ctls_mmap()`, `snd_us428ctls_poll()`, `snd_us428ctls_vm_fault()`, `usx2y_create_usbmidi()`, and `usx2y_create_alsa_devices()`.

## Control Flow, State, and Persistence
`usx2y_hwdep_new()` creates an exclusive hwdep device, attaches DSP status/load, mmap, and poll callbacks, names it after the USB bus path, and allocates `us428ctls_sharedmem`. DSP status reports type, two DSP images, driver version, and readiness. DSP load copies user firmware, sets interface 0 altsetting 1, bulk-sends the image to endpoint 2, and after image index 1 initializes async/control URBs, MIDI, audio, hwdep PCM, registers the card, and marks `USX2Y_STAT_CHIP_INIT`. Mmap faults map pages from the control shared memory; poll signals changed control snapshots or hangup.

## Dependencies and Integration
Depends on ALSA hwdep, USB bulk transfers, snd-usbmidi, US-X2Y audio creation, async pipe-4 setup, and `usbus428ctldefs.h` shared-memory layout.

## Risks and Test Signals
Risks include firmware image trust/size, shared hwdep for firmware and control mmap, mmap size validation comparing bytes to page-aligned size, card registration after staged firmware load, and userspace ABI expectations. Test signals are firmware loader operation, poll/mmap control-surface updates, card creation after DSP image 1, and disconnect during open hwdep mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.c -->
