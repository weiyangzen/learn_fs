# sources/distributed-fs/ceph-client/include/xen/interface/io/kbdif.h

Purpose: defines the Xen virtual keyboard, pointer, and multi-touch shared-page protocol plus XenStore feature negotiation keys.

Important APIs/types/functions: event codes `XENKBD_TYPE_MOTION`, `KEY`, `POS`, and `MTOUCH`; multi-touch subcodes `XENKBD_MT_EV_*`; XenStore field macros for feature and request nodes; event structs `xenkbd_motion`, `xenkbd_key`, `xenkbd_position`, `xenkbd_mtouch`; `union xenkbd_in_event`, `union xenkbd_out_event`; ring helpers; and `struct xenkbd_page`.

Control flow: the backend advertises supported keyboard, pointer, absolute, raw, and multi-touch capabilities. The frontend requests desired features and grants a shared page. Backend-to-frontend events report relative motion, key/button state, absolute position, or multi-touch contact lifecycle; no frontend-to-backend events are currently defined.

State and persistence: shared page state is limited to in/out producer/consumer indexes; device capabilities and dimensions persist in XenStore. Multi-touch contact IDs are reused after UP events.

Dependencies and integration points: integrates with XenBus, event channels, Linux input key codes, framebuffer/display sizing, and guest input stacks. Ring layouts are fixed 40-octet event packets in fixed offsets within one page.

Risks: unknown backend-to-frontend events must be ignored, while unknown frontend-to-backend events are backend errors. Absolute/raw coordinate scaling depends on negotiated dimensions. Reserved fields must be zero to maintain forward compatibility.

Test signals: key press/release, relative and absolute pointer movement, wheel events, raw pointer range checks, multi-touch down/move/shape/orientation/sync/up sequences, and feature negotiation with disabled keyboard or pointer.
