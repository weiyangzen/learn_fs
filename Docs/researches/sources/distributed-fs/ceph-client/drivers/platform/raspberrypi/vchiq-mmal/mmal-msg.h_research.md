# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg.h

## Purpose

This header defines the wire-level message ABI used by the BCM2835 V4L2 MMAL client to communicate with the VideoCore firmware over VCHIQ. It gives fixed-size C layouts for control messages, component lifecycle requests, port information, port actions, buffer hand-off, port parameters, and asynchronous events.

## Important APIs, Types, And Functions

Important definitions are `VC_MMAL_VER`, `VC_MMAL_MIN_VER`, `MMAL_MSG_MAX_SIZE`, `MMAL_MSG_MAX_PAYLOAD`, `enum mmal_msg_type`, `enum mmal_msg_port_action_type`, `struct mmal_msg_header`, and the top-level `struct mmal_msg` union. Payload structures include component create/destroy/enable/disable messages, port info get/set messages, port action messages, `mmal_msg_buffer_from_host`, port parameter set/get messages, and `mmal_msg_event_to_host`. Buffer flags such as `MMAL_BUFFER_HEADER_FLAG_EOS`, `FRAME_START`, `FRAME_END`, `KEYFRAME`, `CONFIG`, and `CORRUPTED` are consumed by `mmal-vchiq.c`.

## Control Flow

The header itself has no runtime control flow. `mmal-vchiq.c` constructs `struct mmal_msg` instances, fills `h.type`, `h.magic`, and `h.context`, queues them through VCHIQ, and dispatches replies by `h.type`. Synchronous operations use the header context to match replies, while buffer messages use `mmal_driver_buffer.client_context` to recover a reusable buffer context.

## State And Persistence

There is no mutable state in this file. Its structures define transient in-memory serialization formats that must match the firmware ABI. State represented by these messages exists in VideoCore components, MMAL ports, queued host buffers, and client-side context maps.

## Dependencies And Integration Points

The file depends on `mmal-msg-common.h`, `mmal-msg-format.h`, `mmal-msg-port.h`, and `mmal-vchiq.h`. It is integrated by `mmal-vchiq.c` and indirectly by the BCM2835 camera/video stack using the exported MMAL VCHIQ API.

## Risks

The file explicitly warns that the protocol assumes 32-bit pointer fields and no unexpected structure padding. Any layout drift breaks firmware communication, so compile-time size checks in `vchiq_mmal_init()` are key. Several payload sizes are bounded by fixed arrays; callers must validate lengths before copying. Status is represented both in the common header and in some payload replies, which increases interpretation risk.

## Test Signals

Useful signals are successful `BUILD_BUG_ON()` layout checks, successful MMAL service open, component create/destroy round trips, port info get/set round trips, short-payload and bulk buffer completion tests, port-parameter set/get tests with boundary sizes, and firmware compatibility checks against version 15/minimum 10.
