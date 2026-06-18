<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_snd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_snd.h

Purpose: defines the virtio sound ABI for jacks, PCM streams, channel maps, mixer/control elements, events, and PCM I/O statuses.

Important APIs and types: `struct virtio_snd_config` exposes counts of jacks, streams, channel maps, and controls. Queue IDs define control, event, TX, and RX queues. Request/status codes cover jack info/remap, PCM info/set_params/prepare/release/start/stop, channel map info, control info/read/write/TLV, and event notifications. PCM definitions include feature bits, formats, rates, stream info, set parameters, transfer headers, and latency status. Control element structures define roles, value types, access rights, value unions, IEC958 data, and notify events.

Control flow, state, and persistence: control queue discovers and configures ALSA-like topology, TX/RX queues carry PCM data, and event queue reports jack, period, xrun, and control changes. Runtime mixer/stream state is device maintained.

Dependencies and integration points: integrates with ALSA PCM/control/jack/channel-map APIs and virtio core.

Risks and test signals: risks include bitmap width overflow, unsupported format/rate selection, PCM state-machine errors, period/xrun notification loss, and large control value parsing. Test stream setup/start/stop, duplex audio, jack events, mixer read/write, TLV operations, and invalid IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_snd.h -->
