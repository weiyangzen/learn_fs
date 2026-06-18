# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front.c

## Purpose
Implements the Xen sound frontend core: XenBus driver registration/state handling and synchronous request helpers for backend stream operations.

## Important APIs, Types, And Functions
- `be_stream_prepare_req()`, `be_stream_do_io()`, and `be_stream_wait_io()` prepare a ring request, push it to the backend, and wait for completion.
- Public stream helpers issue `XENSND_OP_HW_PARAM_QUERY`, `OPEN`, `CLOSE`, `WRITE`, `READ`, and `TRIGGER`.
- `sndback_changed()` drives frontend behavior from backend XenBus state transitions.
- `sndback_initwait()` reads XenStore config, creates event channels, and publishes ring refs/ports.
- `sndback_connect()` creates ALSA card/PCM devices once backend reaches Connected.
- `xen_drv_probe()`, `xen_drv_remove()`, `xen_drv_init()`, and `xen_drv_fini()` implement XenBus module lifecycle.

## Control Flow
On module init, the driver checks it runs in a Xen PV-capable domain and that `XEN_PAGE_SIZE == PAGE_SIZE`, then registers as a XenBus frontend. Probe allocates `xen_snd_front_info` and switches to Initialising. On backend InitWait, the frontend disconnects stale state, parses XenStore, allocates/publishes request and event channels, then switches Initialised. On backend Connected, it initializes ALSA and switches Connected. Closing/Closed/Unknown states free ALSA and event-channel resources.

Synchronous stream operations serialize on `req_io_lock`, fill one request under `ring_io_lock`, flush the ring/event channel, and wait up to `VSND_WAIT_BACK_MS` for the matching response interrupt to complete.

## State And Persistence
`xen_snd_front_info` stores the XenBus device, ALSA card info, event-channel pairs, and parsed config. Request channels store ids and completions so one outstanding request per stream is serialized. No disk persistence; configuration is sourced from XenStore and rebuilt on reconnect.

## Dependencies And Integration Points
Depends on XenBus, Xen page/grant helpers, `xen-front-pgdir-shbuf`, `xen/interface/io/sndif.h`, `xen_snd_front_cfg`, `xen_snd_front_evtchnl`, and `xen_snd_front_alsa`.

## Risks
- Backend is assumed to respond within 3 seconds; timeout propagates to ALSA operations.
- Removal manually polls backend state because normal XenBus callbacks are disconnected.
- Only matching Xen/kernel page sizes are supported.
- Unexpected backend reset triggers disconnect/reinitialize paths that must free all old event channels and cards safely.

## Test Signals
Boot in Xen guest with a compatible backend, exercise backend state transitions InitWait/Connected/Closed, timeout a request, remove the frontend module, simulate backend restart, and verify ALSA devices disappear/reappear without leaked event channels.
