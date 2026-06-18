# sources/distributed-fs/ceph-client/include/linux/remoteproc/mtk_scp.h

Purpose: this header exposes MediaTek SCP remoteproc helper APIs and inter-processor interrupt IDs for client drivers such as codecs, image processing, and ChromeOS host-command services.

Important APIs/types/functions: it defines `scp_ipi_handler_t`, opaque `struct mtk_scp`, and `enum scp_ipi_id` values from `SCP_IPI_INIT` through media, MDP, DIP/ISP/FD, CROS host, IMGSYS, namespace service, and `SCP_IPI_MAX`. APIs include `scp_get()`, `scp_put()`, `scp_get_device()`, `scp_get_rproc()`, `scp_ipi_register()`, `scp_ipi_unregister()`, `scp_ipi_send()`, capability getters, and `scp_mapping_dm_addr()`.

Control flow: a client obtains an SCP handle from its platform device, registers IPI handlers for message IDs, sends requests with bounded length and optional wait, maps SCP data-memory addresses when needed, and releases the handle on teardown. `SCP_IPI_INIT` is firmware-to-kernel initialization notification; other IDs are request-triggered.

State and persistence: the header owns no state. Runtime state is inside the SCP driver: handle refcounts, IPI handler table, firmware state, capabilities, and shared memory mappings.

Dependencies and integration points: includes `linux/platform_device.h` and integrates with remoteproc, MediaTek multimedia drivers, SCP firmware mailboxes, and platform device lifetime.

Risks: IPI ID collisions, buffer length mismatches, and use-after-put can break cross-processor communication. Test signals include client probe/remove refcounting, handler registration conflict tests, SCP firmware boot/init IPI, send timeout paths, and address translation checks.
