# sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_uvc.h

Purpose: Defines UVC gadget-specific event and request codes used by userspace video gadget functions.

Important APIs/types/functions: The header exposes UVC gadget event constants for connect/disconnect, setup, data, stream on/off, and request handling, plus payload structures for UVC control exchanges where present.

Control flow: Userspace UVC gadget code receives events from the gadget/video device, responds to class-specific control setup/data phases, and starts/stops streaming in response to host negotiation.

State and persistence behavior: Streaming state, negotiated probe/commit controls, and control values are runtime gadget state maintained by userspace and kernel gadget glue.

Dependencies and integration points: Integrates with USB gadget UVC, V4L2, UVC class descriptors from `usb/video.h`, and host webcam drivers.

Risks: Probe/commit negotiation must match descriptors and frame intervals. Incorrect event handling can stall enumeration or streaming.

Test signals: Enumerate UVC gadget on a host, handle probe/commit controls, stream video frames, test stream on/off events, and fuzz malformed class control requests.
