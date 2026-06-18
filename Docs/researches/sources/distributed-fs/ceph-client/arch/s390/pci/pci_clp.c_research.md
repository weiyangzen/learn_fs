<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_clp.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_clp.c

Purpose: This file implements s390 Call Logical Processor access for PCI discovery, PCI function query/group query, function enable/disable/MIO enable, function-handle refresh, state lookup, and the `/dev/clp` misc ioctl interface.

Important APIs/types/functions: Public kernel APIs include `update_uid_checking`, `clp_query_pci_fn`, `clp_setup_writeback_mio`, `clp_enable_fh`, `clp_disable_fh`, `clp_scan_pci_devices`, `clp_refresh_fh`, and `clp_get_state`. Low-level CLP helpers are `clp_get_ilp`, `clp_req`, `clp_alloc_block`, `clp_free_block`, query/store helpers, `clp_set_pci_fn`, list/find callbacks, and ioctl handlers `clp_misc_ioctl`, `clp_normal_command`, and `clp_immediate_command`.

Control flow: Kernel discovery allocates a CLP block, issues `CLP_LIST_PCI` in a resume-token loop, skips empty vendor entries, creates zPCI devices for new functions, and returns them on a scan list. Query flow issues `CLP_QUERY_PCI_FN`, stores BAR/DMA/topology/RID/TID/MIO/util-string data into `struct zpci_dev`, then queries the PCI function group for MSI, DMA mask, FMB, TLB refresh, and bus-speed capability. Enable flow issues `CLP_SET_PCI_FN` with retries on busy responses, and if MIO is usable follows with `CLP_SET_ENABLE_MIO`; failure disables the function again.

State and persistence: `zpci_unique_uid` records firmware UID-checking status and is updated while listing functions. CLP responses populate persistent zPCI device fields such as function handle, DMA limits, PCHID, PFGID, UID, RID, TID, VFN, PFIP, util string, BARs, MSI address/count, max store-block data, and MIO write-back addresses. The CLP blocks are page allocations freed after each request.

Dependencies and integration points: It depends on s390 CLP instruction encoding, exception tables, CLP UAPI structures, zPCI debug logging, `pci_bus.h` device creation/reference helpers, MIO state from PCI I/O code, and the miscdevice subsystem. `/dev/clp` validates user-supplied request blocks before forwarding supported base and PCI CLP commands to firmware.

Risks and test signals: CLP block length, reserved field, response-code, and endian handling are firmware ABI-sensitive. Busy retry loops must avoid unbounded waits, and enabling MIO must roll back correctly if the second command fails. `/dev/clp` exposes privileged firmware command paths, so copy-from/to-user, length limits, and command whitelists are important. Tests include boot-time PCI enumeration, UID-checking sysfs changes, enable/disable under z/VM and LPAR, MIO-capable and non-MIO devices, CLP list resume-token coverage, and ioctl negative tests for malformed request blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_clp.c -->
