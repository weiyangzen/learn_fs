# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx.h

Purpose: Public interface and register definition header for the OcteonTX2 CGX/RPM MAC driver. It exposes register offsets, bit masks, LMAC mode enums, event callback types, and the API surface consumed by RVU Admin Function and NIC code.

Important APIs/types/functions: The file defines PCI/device constants, CGX CMR/SPU/GMP/SMU register offsets, DMAC CAM masks, pause/PFC/PTP bits, firmware scratch register aliases, command timeout, and LMAC mode enum values. Types include `struct cgx_link_event` and `struct cgx_event_cb`. Function declarations cover CGX discovery, LMAC count/IDs, register access, pkind setup, event callback registration, MAC address filters, promisc, flow control/PFC, loopback, link info/linkup, firmware data base discovery, PTP, FEC, link mode setting, feature queries, reset, and FIFO length.

Control flow and integration: `cgx.c`, `rvu_cgx.c`, and related AF code include this header to call into the MAC service layer. The `extern struct pci_driver cgx_driver` allows driver registration from AF module initialization. Register macros are used directly by CGX and RPM operations.

State and persistence: No storage is allocated here. It defines how state is addressed in hardware registers and how callbacks deliver state changes through `struct cgx_link_event`.

Dependencies: Includes `mbox.h`, `cgx_fw_if.h`, and `rpm.h`, so it binds the MAC API to mailbox-visible link structures, firmware command ABI, and RPM variant operations.

Risks: This is a high-fanout ABI inside the driver. Renaming or changing prototypes affects AF, PF, and possibly representor/e-switch code. Register macros using `mac_ops->csr_offset` depend on a local variable named `mac_ops` in calling functions, which is concise but fragile if copied without that variable.

Test signals: Build coverage across AF users, successful CGX/RPM probe, RVU-to-CGX link management, filter programming, and PFC/PTP/FEC operations validate this header contract.
