## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uac1_legacy.h

Purpose: declares the legacy UAC1 ALSA-file-backed audio helper API and option state.

Important APIs and types:
- Default paths are `FILE_PCM_PLAYBACK`, `FILE_PCM_CAPTURE`, and `FILE_CONTROL`.
- Legacy constants define OUT endpoint max packet size, request count, and audio buffer size.
- `struct gaudio_snd_dev` stores parent `gaudio`, opened file, PCM substream, access, format, channels, and rate.
- `struct gaudio` embeds `usb_function`, gadget pointer, and control/playback/capture ALSA device wrappers.
- `struct f_uac1_legacy_opts` embeds `usb_function_instance`, request/audio buffer sizing, configurable file paths, bound flag, ownership flags for path strings, `lock`, and `refcnt`.
- Declares `gaudio_setup()`, `gaudio_cleanup()`, `u_audio_playback()`, and playback channel/rate getters.

Control flow and integration:
- Legacy UAC1 function configures file paths/request sizing, calls `gaudio_setup()`, forwards payloads to `u_audio_playback()`, and calls cleanup on unbind.
- Path ownership flags tell configfs cleanup whether to free custom strings.

State and persistence:
- File path strings and request sizing persist in the configfs function instance.
- ALSA file/substream state persists while `gaudio_setup()` is active.

Dependencies:
- Linux device/error/USB composite APIs and ALSA core/PCM parameter headers.

Risks:
- Hard-coded defaults target card 0 device 0 and may be wrong on most systems.
- Kernel file access to ALSA devices couples gadget behavior to local sound-card availability and permissions.
- Ownership flags for path strings must be accurate.

Test signals:
- Override all three file paths and verify ownership cleanup.
- Test missing capture path is tolerated as implemented while missing control/playback fails setup.
