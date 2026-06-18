# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq.h

Purpose: defines the public in-kernel VCHIQ client API for Raspberry Pi VideoCore communication: service setup, callbacks, message queuing, message release/hold, bulk transfers, and version/userdata queries.

Important APIs and types: `VCHIQ_MAKE_FOURCC()` builds service identifiers. `enum vchiq_reason` reports service opened/closed, message availability, and bulk completion/abort reasons. `enum vchiq_bulk_mode` selects callback, blocking, no-callback, or internal waiting behavior. `enum vchiq_service_option` controls autoclose, quotas, synchronous mode, and tracing. `struct vchiq_header`, `struct vchiq_element`, `struct vchiq_service_base`, `struct vchiq_completion_data_kernel`, and `struct vchiq_service_params_kernel` define callbacks and message payload metadata. API functions cover instance initialization/shutdown/connect, service open/close/use/release, queue/release/hold message, bulk transmit/receive, userdata, and peer version.

Control flow: a client initializes an instance, connects to the firmware side, opens a FOURCC service, receives callbacks for messages or bulk completions, releases message headers after processing, and can queue in-band or bulk data.

State and persistence: state is per-instance/service runtime state in VCHIQ core structures and shared memory; messages and bulk transfers are transient.

Dependencies and integration points: integrates kernel clients with the VCHIQ core, character-device/user interfaces, and Raspberry Pi firmware/VideoCore services.

Risks and test signals: risks include callback reentrancy, failure to release messages, mismatched service versions, invalid handles, bulk mode confusion, and user pointer lifetime for callback userdata. Test service open/close, callback delivery order, message hold/release, peer-version negotiation, blocking and callback bulk transfers, abort paths, and shutdown with pending messages.
