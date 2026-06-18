# sources/distributed-fs/ceph-client/include/xen/interface/io/fbif.h

Purpose: defines the older Xen virtual framebuffer shared-page protocol for simple display updates and resize notifications.

Important APIs/types/functions: outbound event types `XENFB_TYPE_UPDATE` and `XENFB_TYPE_RESIZE`; `struct xenfb_update`, `struct xenfb_resize`, `union xenfb_out_event`, `union xenfb_in_event`; ring constants and helpers `XENFB_IN_RING_*`, `XENFB_OUT_RING_*`; and `struct xenfb_page` with framebuffer metadata and page directory `pd[256]`.

Control flow: frontend-to-backend out events report updated rectangles or resize changes when negotiated by XenStore features. Backends may define future inbound events, but none are currently defined and frontends should ignore unknown ones.

State and persistence: `xenfb_page` stores ring indexes, visible framebuffer geometry, memory length, depth, and a page directory mapping framebuffer pages. The shared page and backing framebuffer grants persist while the device is connected.

Dependencies and integration points: integrates with Xen virtual keyboard/mouse through shared default resolution definitions under `__KERNEL__`, XenBus feature keys (`feature-update`, `request-update`, `feature-resize`), grant-table mapped framebuffer pages, and event-channel notifications.

Risks: `unsigned long pd[256]` has ABI implications across 32-bit/64-bit domains. The protocol is less expressive than `displif`; using it for modern display workflows can limit multi-output and buffer management. Out events are errors unless requested by the backend.

Test signals: framebuffer update rectangle delivery, resize negotiation, page directory mapping at 32-bit and 64-bit ABI widths, default resolution users, and backend tolerance for unknown inbound event types.
