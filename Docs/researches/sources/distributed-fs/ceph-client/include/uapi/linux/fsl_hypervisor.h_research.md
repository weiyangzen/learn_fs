# sources/distributed-fs/ceph-client/include/uapi/linux/fsl_hypervisor.h

This UAPI header defines Freescale/NXP hypervisor ioctl interfaces used by guests to interact with hypervisor-managed resources, including doorbells, partitions, byte channels, DMA windows, and device tree/resource information.

Important exports include ioctl command numbers under the Freescale hypervisor magic, structures for doorbell management, partition status/control, memory or DMA window operations, byte-channel send/receive, and interrupt/event routing. The ABI uses fixed-width integer types and ioctl payload structs to pass guest physical addresses, handles, status codes, and resource IDs.

Control flow is guest userspace ioctl into a hypervisor-facing kernel driver: userspace requests resource information or operations, the driver validates permissions and forwards hypercalls or platform calls, and hypervisor state changes are reflected back through output fields or events. State lives in hypervisor partition/resource tables, guest-visible device nodes, interrupt channels, and any shared buffers. Persistence depends on hypervisor configuration, not the header.

Dependencies include `linux/types.h`, `linux/ioctl.h`, PowerPC/Freescale hypervisor support, device tree resource descriptions, and platform-specific hypercalls. Integration points are embedded PowerPC virtualization, management tools, guest drivers, and board support packages.

Risks include privileged resource misuse, guest/host ABI drift, endianness and physical-address width issues, stale handles after partition changes, and insufficient validation of user-provided guest physical addresses. Test signals include platform hypervisor ioctl tests, device-tree resource discovery tests, 32/64-bit guest ABI checks, negative permission tests, and hypercall error-path validation.
