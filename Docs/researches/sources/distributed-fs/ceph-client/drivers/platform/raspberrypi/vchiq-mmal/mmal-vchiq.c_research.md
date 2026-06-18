# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.c

## Purpose

This source implements the BCM2835 MMAL client transport over Raspberry Pi VCHIQ. It opens the VideoCore `mmal` service, serializes synchronous MMAL control messages, receives asynchronous buffer completions, manages component and port state, and exports the in-kernel API used by the V4L2 camera driver.

## Important APIs, Types, And Functions

Key private types are `struct mmal_msg_context` and `struct vchiq_mmal_instance`. The context is either a synchronous reply waiter or a bulk-buffer context. The instance stores the VCHIQ service handle, serialization mutex, IDR context map, component array, ordered bulk workqueue, and VCHIQ instance pointer. Important helpers include context allocation/lookup/release, `send_synchronous_mmal_msg()`, `mmal_service_callback()`, buffer receive helpers, port info/action/parameter helpers, and component creation/destruction. Exported APIs cover instance lifetime, component lifecycle, port enable/disable/set-format/connect-tunnel, parameter set/get, buffer submit, and buffer context init/cleanup.

## Control Flow

Initialization obtains the parent VCHIQ management state, initializes/connects a VCHIQ instance, allocates the MMAL instance, creates an ordered workqueue, and opens the `mmal` service. Synchronous calls allocate a context ID, queue a message, wait up to `SYNC_MSG_TIMEOUT`, return the reply pointer, and release the VCHIQ message after decoding. Buffer flow is different: each `mmal_buffer` owns a persistent message context, `BUFFER_FROM_HOST` advertises its buffer, firmware responds with inline data or a bulk transfer request, and callback work fills buffer metadata and invokes the port callback outside the VCHIQ callback thread.

## State And Persistence

Mutable state is in the instance context IDR, component slots, cached port fields, buffer queues, atomic `buffers_with_vpu`, and VideoCore handles. Software state is per-driver-instance and destroyed by `vchiq_mmal_finalise()`. Firmware-side component/port state persists until explicit MMAL disable/destroy, service close, or VideoCore reset.

## Dependencies And Integration Points

The file depends on Linux VCHIQ APIs, `videobuf2-vmalloc`, MMAL protocol headers, workqueues, completions, mutexes, spinlocks, atomics, and IDR. It exports symbols for other BCM2835 multimedia drivers and relies on `mmal-msg.h` layout checks to keep the firmware ABI valid.

## Risks

Late replies after a synchronous timeout can arrive after the context has been released, which the source comments call out. Buffer lifecycle is delicate: buffer contexts are reused, callbacks are deferred, and callers must clean up contexts only after firmware no longer owns them. Port array bounds rely on firmware-reported input/output/clock counts fitting `MAX_PORT_COUNT`. `port_parameter_set()` copies caller data into a fixed worker space without an explicit local `value_size` check beyond the global message-size check. `vchiq_mmal_submit_buffer()` returns zero even after queueing on disabled ports.

## Test Signals

Signals include module load/unload, MMAL version query, component create/destroy for camera/encoder/render components, port info get/set readback, parameter boundary tests, tunnel connect/disconnect tests, buffer streaming with inline and bulk payloads, EOS/empty buffer callbacks, disable while buffers are queued, timeout injection, VCHIQ service close handling, and leak checks for IDR contexts and workqueue callbacks.
