# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_pci.h

Purpose: supplies small MPI3 PCIe/NVMe constants used by NVMe encapsulated passthrough commands.

Important APIs/types/functions: defines `MPI3_NVME_ENCAP_CMD_MAX` when not already supplied and bit masks/values for `MPI3_NVME_FLAGS_FORCE_ADMIN_ERR_REPLY_*` and `MPI3_NVME_FLAGS_SUBMISSIONQ_*`. These distinguish IO versus Admin submission queue behavior and whether admin error replies are forced for fail-only or all cases.

Control flow: there is no executable flow. The flags are consumed when constructing or interpreting MPI3 NVMe encapsulated command messages, particularly BSG passthrough code that inspects NVMe command data format and builds PRP or SGL lists.

State and persistence behavior: no state or persistence. The constants are ABI values placed in request flags passed to firmware.

Dependencies and integration points: included by `mpi3mr.h` with the other MPI headers. It complements NVMe encapsulated request structures from `mpi30_init.h`/transport definitions and the PRP/SGL construction paths in `mpi3mr_app.c`.

Risks and test signals: risk is mostly semantic drift against firmware specifications. Tests should cover NVMe BSG passthrough for admin and IO queue commands, forced admin error reply behavior, and compile coverage where `MPI3_NVME_ENCAP_CMD_MAX` may already be defined by another included header.
