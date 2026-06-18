# sources/distributed-fs/ceph-client/include/xen/interface/io/sndif.h

Purpose: defines the Xen paravirtual sound protocol for virtual sound cards, PCM devices, streams, command rings, shared audio buffers, and asynchronous position events.

Important APIs/types/functions: `XENSND_PROTOCOL_VERSION`, PCM format constants and string names, XenStore field names, operations `XENSND_OP_OPEN`, `CLOSE`, `READ`, `WRITE`, `SET_VOLUME`, `GET_VOLUME`, `MUTE`, `UNMUTE`, `TRIGGER`, `HW_PARAM_QUERY`, trigger codes, event `XENSND_EVT_CUR_POS`, request structs `xensnd_open_req`, `xensnd_rw_req`, `xensnd_trigger_req`, `xensnd_query_hw_param`, `xensnd_req`, `xensnd_resp`, `xensnd_evt`, `xensnd_page_directory`, and `xensnd_event_page`.

Control flow: XenBus configures card/device/stream hierarchy, sample rates/formats, channels, buffer size, request ring, and event ring. Frontend opens a stream with PCM parameters and a grant-backed buffer directory, issues read/write/control requests by offset/length into that buffer, triggers start/stop/pause/resume, and receives responses plus optional current-position events.

State and persistence: opened stream state includes selected PCM configuration, shared buffer grants, period size, volume/mute data in the shared buffer, and event position state. XenStore configuration persists for the virtual sound device lifetime.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with XenBus, event channels, guest ALSA-like PCM layers, backend mixers/devices, and grant-table buffer sharing.

Risks: lower-layer stream capabilities must be subsets of card/device capabilities. Offset/length requests can address audio or control data in the same buffer, so validation is essential. Recovery from backend failure may require frontend reconfiguration while existing clients drain.

Test signals: stream open parameter validation, read/write playback/capture, trigger transitions, volume/mute round trips, hardware-parameter narrowing, period event delivery, multi-device stream indexing, and grant cleanup on close.
