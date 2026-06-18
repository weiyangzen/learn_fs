# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.h

## Purpose

This header exposes the MMAL-over-VCHIQ client API and the client-visible component/port data structures used by the BCM2835 V4L2 driver. It abstracts the VideoCore MMAL service behind component, port, parameter, format, tunnel, and buffer operations.

## Important APIs, Types, And Functions

Important constants are `MAX_PORT_COUNT` and `MMAL_FORMAT_EXTRADATA_MAX_SIZE`. `enum vchiq_mmal_es_type` classifies elementary streams. `struct vchiq_mmal_port_buffer` describes buffer count/size/alignment. `struct vchiq_mmal_port` caches firmware port handle, type/index, component backpointer, tunnel peer, buffer requirements, current format, ES-specific format, queued buffers, spinlock, VPU buffer count, and completion callback. `struct vchiq_mmal_component` tracks lifecycle flags, firmware handle, port counts, control port, fixed arrays of input/output/clock ports, and a client component ID.

## Control Flow

Callers initialize a `vchiq_mmal_instance`, create components by name, configure port format and parameters, enable components/ports, submit buffers or connect tunnels, then disable/finalise in reverse. Buffer callbacks run when `mmal-vchiq.c` receives a VideoCore buffer completion or bulk transfer completion.

## State And Persistence

The header declares the client-visible state containers but owns no storage. `enabled`, `connected`, cached handles, buffer queues, and format fields are runtime state populated by `mmal-vchiq.c`. There is no persistence beyond the active driver instance and VideoCore service session.

## Dependencies And Integration Points

It depends on `mmal-common.h` and `mmal-msg-format.h` for MMAL buffers and format types. It is included by `mmal-msg.h`, implemented by `mmal-vchiq.c`, and consumed by Raspberry Pi camera/video drivers.

## Risks

The fixed `MAX_PORT_COUNT` arrays must be large enough for every firmware component used by callers. Callers can mutate exposed port format and buffer fields, so `vchiq_mmal_port_set_format()` and enable paths rely on disciplined API use. Buffer callbacks may arrive asynchronously and must not race buffer cleanup. The `cb_ctx` field is exposed but not centrally managed in this subset.

## Test Signals

Compile coverage of all exported prototypes, successful component and port setup, stream callbacks with correct buffer metadata, tunnel setup between ports, and teardown without leaked contexts or callbacks after free are the main validation signals.
