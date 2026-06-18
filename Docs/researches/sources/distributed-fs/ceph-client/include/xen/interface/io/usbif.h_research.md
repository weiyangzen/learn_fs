# sources/distributed-fs/ceph-client/include/xen/interface/io/usbif.h

Purpose: defines the Xen pvUSB split-driver ABI, including USB host connector XenStore setup, URB request/response rings, connection event rings, pipe bitfield helpers, speeds, versions, and status codes.

Important APIs/types/functions: `enum xenusb_spec_version`, pipe masks and helpers such as `xenusb_pipeportnum`, `xenusb_pipeunlink`, `xenusb_pipein`, `xenusb_pipedevice`, `xenusb_pipeendpoint`, and `xenusb_pipetype`; constants `XENUSB_MAX_SEGMENTS_PER_REQUEST`, `XENUSB_MAX_PORTNR`, `XENUSB_RING_SIZE`; `struct xenusb_request_segment`, `xenusb_urb_request`, `xenusb_urb_response`, `xenusb_conn_request`, `xenusb_conn_response`; `DEFINE_RING_TYPES(xenusb_urb, ...)` and `DEFINE_RING_TYPES(xenusb_conn, ...)`.

Control flow: frontend publishes `event-channel`, `urb-ring-ref`, `conn-ring-ref`, and optional ABI protocol string. Backend sends plug/unplug events on the connection ring in response to dummy requests. Frontend submits URBs on the URB ring with pipe encoding, transfer flags, type-specific data, and up to 16 grant-backed buffer segments; backend returns status, actual length, start frame, and ISO error count.

State and persistence: ring state persists per virtual USB connector. Backend private XenStore nodes describe number of ports, USB version, and physical port mapping. In-flight URBs are correlated by request `id`; unlink requests cancel earlier IDs.

Dependencies and integration points: includes `ring.h` and `grant_table.h`; integrates with XenStore ABI strings from `protocols.h`, event channels, host USB backends, and guest USB core URB handling.

Risks: pipe bitfields must be encoded exactly; wrong direction, endpoint, or type corrupts USB semantics. Maximum 31 ports and 16 segments are hard ABI limits. Unlink races and ISO frame descriptors require careful backend validation.

Test signals: plug/unplug events, control/interrupt/bulk/iso URB submission, short-transfer flag behavior, unlink cancellation, status mapping for stalls/nodev/shutdown, ring size assertions, and segment-boundary transfer tests.
