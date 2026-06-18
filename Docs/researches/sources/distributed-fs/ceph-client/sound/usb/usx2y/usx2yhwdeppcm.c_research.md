<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.c

## Purpose
Alternative "rawusb" hwdep PCM path for US-X2Y devices, optimized for mmaped low-latency JACK operation by sharing USB DMA buffers and isochronous packet metadata with userspace.

## APIs, Types, and Functions
Exports `usx2y_hwdep_pcm_new()` when packet count is one or variable. It includes `usbusx2yaudio.c` to reuse normal PCM helpers. Important functions include `usx2y_usbpcm_urb_capt_retire()`, `usx2y_hwdep_urb_play_prepare()`, `usx2y_usbpcm_urb_capt_iso_advance()`, `usx2y_usbpcm_usbframe_complete()`, `i_usx2y_usbpcm_urb_complete()`, `usx2y_usbpcm_urbs_allocate()`, `snd_usx2y_usbpcm_prepare()`, `snd_usx2y_usbpcm_open()`, hwdep open/release/mmap callbacks, and page-fault mapping.

## Control Flow, State, and Persistence
Opening the hwdep PCM device sets `USX2Y_STAT_CHIP_MMAP_PCM_URBS` if normal PCMs are idle. The PCM open path is only available in that mode. Prepare allocates `hwdep_pcm_shm`, sets rate/format, starts capture, waits until enough captured isochronous frames exist, then starts playback. Capture URBs write directly into shared capture areas and record packet frame/offset/length rings. Playback URBs use captured packet lengths and shared playback buffer offsets, zeroing when not running. Mmap exposes `snd_usx2y_hwdep_pcm_shm` pages to userspace.

## Dependencies and Integration
Depends on ALSA hwdep/PCM, USB isochronous APIs, shared US-X2Y PCM helpers, and `usx2yhwdeppcm.h` shared-memory layout. Created after firmware load by `usX2Yhwdep.c`.

## Risks and Test Signals
Risks include source-level inclusion of another `.c` file, duplicate call to `usx2y_hwdep_urb_play_prepare()`, volatile shared-memory cursors, mmap lifetime, single-packet-mode gating, and tight coupling with JACK userspace. Test signals are hwdep open exclusivity, mmap size/faults, low-latency playback/capture, 4-channel capture on US-428, and switching back to normal PCM after release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.c -->
