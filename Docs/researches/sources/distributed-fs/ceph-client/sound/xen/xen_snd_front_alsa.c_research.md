# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_alsa.c

## Purpose
Implements the ALSA-facing layer of the Xen para-virtual sound frontend. It creates ALSA cards/PCM devices from XenStore config, refines hardware parameters with backend queries, manages shared grant-table audio buffers, and maps ALSA PCM callbacks to Xen sound protocol operations.

## Important APIs, Types, And Functions
- Runtime structures represent card, PCM instance, and per-stream state, including `xen_front_pgdir_shbuf`, buffer pages, stream index, hardware constraints, open state, and atomic hardware pointer.
- `ALSA_SNDIF_FORMATS`, `to_sndif_format()`, `to_sndif_formats_mask()`, and `to_alsa_formats_mask()` translate ALSA and Xen sample format encodings.
- `alsa_hw_rule()` sends `XENSND_OP_HW_PARAM_QUERY` to refine formats, rates, channels, buffer, and period sizes.
- `alsa_open()` installs configured hardware constraints, connects the stream event pair, attaches the substream to async event handling, and installs refinement rules.
- `alsa_hw_params()` allocates exact pages, creates a Xen frontend page-directory shared buffer, and maps it.
- `alsa_prepare()` sends `XENSND_OP_OPEN` with shared-buffer grant directory and PCM params.
- Playback/capture `.copy` callbacks move bytes to/from the shared buffer and issue `WRITE`/`READ` requests.
- `xen_snd_front_alsa_handle_cur_pos()` consumes backend current-position events, advances the atomic hw pointer, and emits ALSA period elapsed notifications.
- `new_pcm_instance()`, `xen_snd_front_alsa_init()`, and `xen_snd_front_alsa_fini()` create and destroy ALSA card/PCM state.

## Control Flow
After backend connection, `xen_snd_front_alsa_init()` creates one ALSA card and a PCM for each configured XenStore PCM instance. Opening a substream assigns its event-channel pair, clears stream state, marks channels connected, and adds dynamic hardware rules. During hw_params, the driver allocates a contiguous virtual buffer, collects pages, grants/maps the page directory, and stores shared-buffer metadata. Prepare opens the stream at the backend with the selected format/channel/rate and buffer/period sizes. Playback copies user data into the shared buffer then sends WRITE; capture sends READ then copies data out. Backend `CUR_POS` events update the ALSA pointer and signal periods.

## State And Persistence
Per-stream state owns shared-buffer pages, grant-directory state, open flag, event-pair pointer, current backend frame, atomic hw pointer, and period modulo. `stream_free()` unmaps/free grants and pages and resets fields. No disk persistence; all ALSA devices are regenerated from XenStore on backend connect.

## Dependencies And Integration Points
Depends on ALSA card/PCM/hw-rule APIs, XenBus, `xen-front-pgdir-shbuf`, `xen_snd_front` protocol helpers, parsed config from `xen_snd_front_cfg.c`, and event positions from `xen_snd_front_evtchnl.c`.

## Risks
- `alsa_hw_rule()` performs backend I/O during constraint refinement; backend latency/failure can affect ALSA parameter negotiation.
- Shared-buffer allocation uses `alloc_pages_exact()` and page arrays; failures must unwind all partially allocated grant resources.
- `alsa_hw_free()` always attempts backend close before freeing, so backend errors propagate during ALSA cleanup.
- `xen_snd_front_alsa_handle_cur_pos()` assumes the substream is valid when event channel is connected.
- Period notification uses `out_frames > period_size`; exact equality does not notify until more frames arrive.
- Mmap is intentionally unsupported because there is no user-space completion acknowledgement.

## Test Signals
Test playback and capture `.copy` paths, dynamic hw-params refinement, unsupported formats, backend query timeout, hw_params failure unwind, close after partial open, current-position event progression/wraparound, and backend reconnect. KASAN/lockdep are useful around shared-buffer free and async events.
