# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_arm.h

Purpose: defines the ARM-host side VCHIQ management structures for driver state, user instances/services, completion queues, bulk waiters, debugfs nodes, character-device registration, and service use/release management.

Important APIs and types: constants set per-instance completion, service, element, message queue, and deferred-callback limits. `struct vchiq_platform_info` records cache-line size. `struct vchiq_drv_mgmt` owns firmware handle, platform info, connection state, deferred callbacks, fragment buffers/semaphores, MMIO registers, and `vchiq_state`. `struct user_service` tracks a service visible to userspace, message queue positions, completion events, and close/dequeue state. `struct bulk_waiter_node` links blocking bulk waiters by PID. `struct vchiq_instance` owns completions, mutexes, connection/closing flags, PID, tracing, bulk waiter list, and debugfs node.

Control flow: platform probe initializes `vchiq_drv_mgmt`, registers cdev if configured, creates instances, dispatches service callbacks into completion/message queues, and coordinates service use/release to keep firmware resources active while clients hold references.

State and persistence: all state is runtime host-side state: queues, completions, semaphores, fragments, connection flags, and debugfs nodes. It does not persist across driver unload or reboot.

Dependencies and integration points: depends on platform devices, firmware API, semaphores, mutexes, atomics, VCHIQ core/debugfs, optional cdev support, and user-copy-facing service data.

Risks and test signals: risks include completion queue overflow, fragment allocator races, close/dequeue ordering, leaked bulk waiters, cdev disabled behavior, and connected callback ordering. Test character-device and in-kernel client paths, many concurrent services, close with queued messages, blocking bulk cancellation, debugfs lifetime, driver unbind, and firmware reconnect.
