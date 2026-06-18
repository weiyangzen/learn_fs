# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_ioctl.h

Purpose: Private ioctl ABI definitions for the VCHIQ character device.

Important APIs, types, and functions: `VCHIQ_IOC_MAGIC` is `0xc4`; `VCHIQ_IOC_MAX` is 17. ABI structures include `vchiq_service_params`, `vchiq_create_service`, `vchiq_queue_message`, `vchiq_queue_bulk_transfer`, `vchiq_completion_data`, `vchiq_await_completion`, `vchiq_dequeue_message`, `vchiq_get_config`, `vchiq_set_service_option`, and `vchiq_dump_mem`. Ioctls define connect, shutdown, create/remove/close service, queue message, queue bulk transmit/receive, await completion, dequeue message, get client id/config, use/release service, set service option, dump physical memory, library version, and close-delivered notification.

Control flow: userspace passes these structures to `vchiq_dev.c`, which dispatches by ioctl number and copies data to/from user buffers. The header itself contains no executable flow.

State and persistence: ABI structures describe per-call state crossing the user/kernel boundary. No runtime state is stored in the header.

Dependencies and integration points: includes `linux/ioctl.h` and public `linux/raspberrypi/vchiq.h` for shared enums and types. It is tightly coupled to `vchiq_dev.c` native and compat handlers and userspace VCHIQ libraries.

Risks: ABI layout is fixed; changing field types, order, or ioctl numbers would break userspace. Function-pointer-looking `callback` in `vchiq_service_params` is a userspace token, not invoked directly by the kernel. Pointer-bearing structures require explicit compat translations.

Test signals: compile userspace/kernel headers together, verify ioctl number stability with static tests, and run native plus 32-bit compat ioctl round trips for every pointer-containing command.
