# sources/distributed-fs/ceph-client/include/uapi/linux/vfio_zdev.h

Purpose: defines s390 zPCI-specific VFIO device-info capability payloads that extend the common VFIO capability chain.

Important APIs/types/functions: exports `vfio_device_info_cap_zpci_base`, `vfio_device_info_cap_zpci_group`, `vfio_device_info_cap_zpci_util`, and `vfio_device_info_cap_zpci_pfip`. Base capability fields describe DMA range, physical channel ID, virtual function number, measurement block length, PCI function type, group ID, and function handle. Group capability fields describe DMA address-space mask, MSI address, flags including `VFIO_DEVICE_INFO_ZPCI_FLAG_REFRESH`, measurement intervals, MSI limits, store block limits, PCI version, and interpreted store block length. Utility and PFIP capabilities carry variable-length byte strings.

Control flow: userspace calls `VFIO_DEVICE_GET_INFO`, detects `VFIO_DEVICE_FLAGS_CAPS`, walks `vfio_info_cap_header` links, and interprets capability IDs declared in `vfio.h` as these structures. Version comments mark field growth boundaries so older userspace can consume v1 subsets while newer userspace can read added fields when `argsz` permits.

State and persistence: the header describes read-only descriptive device/group state provided by the kernel. Variable-length strings are sized by `size` and are not NUL-terminated by contract. Persistent ABI behavior depends on capability header versioning and stable offsets.

Dependencies and integration: includes `linux/types.h` and `linux/vfio.h`. It integrates with s390 zPCI VFIO devices, zPCI DMA/MSI setup in userspace VMMs, and the VFIO info capability chain.

Risks: EBCDIC utility strings and raw path strings need length-aware handling. DMA range and group parameters are device-specific and must feed later IOMMU/iommufd setup correctly. Userspace must guard versioned tail fields and not assume all kernels expose `fh` or `imaxstbl`.

Test signals: capability-chain parsing tests, zPCI VFIO device-info tests on s390, ABI layout checks, version compatibility tests with truncated `argsz`, and VMM startup tests that consume DMA/MSI metadata.
