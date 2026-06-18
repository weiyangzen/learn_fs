<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/usb_stream.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/usb_stream.h

Purpose: defines the ALSA USB stream mmap/ioctl ABI used by low-latency USB audio streaming code to share stream configuration, packet ring metadata, and state with userspace.

Important APIs and types: `USB_STREAM_INTERFACE_VERSION` gates ABI version. `SNDRV_USB_STREAM_IOCTL_SET_PARAMS` accepts `usb_stream_config` with version, sample rate, period frames, and frame size. `usb_stream_packet` and `usb_stream` expose packet offsets/lengths, read/write sizes, period accounting, input packet ring indexes, split packet state, and `usb_stream_state`.

Control flow: userspace sets stream parameters, maps or reads shared stream state, follows output packet descriptors and input packet ring metadata, and reacts to state transitions from stopped/sync/ready/running/xrun.

State and persistence: `usb_stream` is live shared runtime state tracking scheduling, periods, idle sizes, synchronization packet, packet queues, and xruns. Nothing is persisted beyond the stream lifetime.

Dependencies and integration points: integrates with ALSA hwdep/PCM USB streaming, userspace JACK-style low-latency clients, and USB isochronous packet scheduling.

Risks and test signals: risks include flexible-array sizing, ring index races, version mismatch, xrun state handling, and ABI assumptions about `unsigned`/`int` widths. Test parameter negotiation, mmap size calculations, packet wrap/split behavior, xruns, and 32/64-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/usb_stream.h -->
