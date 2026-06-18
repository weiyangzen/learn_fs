# sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_scm.h

## Purpose
This header is the broad public contract for Qualcomm Secure Channel Manager calls. It lets Linux drivers invoke secure firmware services for boot vectors, remote processor PAS authentication, IOMMU and memory ownership, secure IO, crypto/ICE keys, HDCP, GPU setup, shared memory bridges, QSEECOM, and QTEE callbacks.

## APIs, types, and control flow
Important types include `struct qcom_scm_vmperm`, OCMEM and secure device enums, ICE cipher ids, and `struct qcom_scm_pas_context`, which carries remoteproc metadata, memory address/size, DMA/TZ allocation state, and device ownership. PAS users typically allocate a context, initialize/authenticate metadata, set memory, authenticate/reset, then shut down or release metadata. Memory assignment uses `qcom_scm_assign_mem()` with source VM mask and destination permissions. QSEECOM functions are compiled to real declarations only with `CONFIG_QCOM_QSEECOM`; otherwise they return `-EINVAL`.

## State and dependencies
The header has no storage but defines firmware-visible ids, permission bits, and context fields that implementations persist across calls. It depends on firmware device tree bindings, cpumasks, device/resource-table users, DMA/TZ memory, and secure monitor availability.

## Integration, risks, and tests
This interface sits below remoteproc, storage encryption, GPU, display, IOMMU, and trusted-app drivers. Risks include wrong PAS id, mismatched physical addresses, bad VM permissions that strand memory, unsupported optional calls, and key-size/cipher mistakes in ICE. Tests should cover `qcom_scm_is_available()`, feature-available predicates, disabled QSEECOM stubs, PAS happy/failure sequencing, memory assign rollback, and firmware error propagation.
