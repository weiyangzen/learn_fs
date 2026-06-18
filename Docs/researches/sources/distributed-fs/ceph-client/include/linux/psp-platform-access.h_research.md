# sources/distributed-fs/ceph-client/include/linux/psp-platform-access.h

Purpose: declares AMD PSP platform-access mailbox APIs used by non-CCP drivers to communicate with platform firmware features such as firmware version queries, secure firmware services, HSTI, I2C requests, and dynamic boost parameters.

Important APIs and types: `enum psp_platform_access_msg` lists platform mailbox commands. `struct psp_req_buffer_hdr` and `struct psp_request` describe payload size/status and buffer pointer. APIs include `psp_send_platform_access_msg()`, `psp_ring_platform_doorbell()`, and `psp_check_platform_access_status()`.

Control flow: a client checks platform access status, prepares a request buffer with header and payload, sends a typed platform-access message, or rings a doorbell and reads the firmware result. The PSP driver serializes mailbox access and reports busy, timeout, absent-device, or I/O failures.

State and persistence: request state is transient; platform firmware may persist settings depending on message type. Mailbox recovery/busy state is owned by the PSP driver.

Dependencies and integration points: depends on `linux/psp.h`, AMD PSP/CCP driver binding, mailbox registers, and external platform feature drivers.

Risks and test signals: risks include wrong packed buffer layout, payload size mismatch, mailbox contention, timeout handling, and using the API before PSP platform features are ready. Test success and firmware error statuses, busy/recovery paths, timeout injection, absent PSP device, and each client message format.
