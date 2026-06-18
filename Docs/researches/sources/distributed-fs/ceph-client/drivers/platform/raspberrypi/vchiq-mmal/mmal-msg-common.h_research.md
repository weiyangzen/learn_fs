# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-common.h

Purpose: Common MMAL message status values and basic geometry structure for MMAL protocol messages.

Important APIs, types, and functions: `enum mmal_msg_status` mirrors firmware status/error codes including success, memory/resource errors, invalid argument, not implemented, device/address errors, I/O/corrupt data, not ready/configured, connection state errors, retry, and bad address. `struct mmal_rect` contains signed x/y/width/height fields.

Control flow: no executable flow; these definitions are embedded in request/response structures and status conversion logic elsewhere.

State and persistence: no state.

Dependencies and integration points: includes `linux/types.h`; used by MMAL format and port message headers and by MMAL VCHIQ response handlers.

Risks: enum numeric order is part of the protocol contract with firmware; inserting or reordering values would break status decoding. `mmal_rect` signed fields must match firmware structure layout.

Test signals: ABI/layout checks against firmware expectations, status-to-errno mapping tests in MMAL implementation, and crop/rectangle round-trip tests.
