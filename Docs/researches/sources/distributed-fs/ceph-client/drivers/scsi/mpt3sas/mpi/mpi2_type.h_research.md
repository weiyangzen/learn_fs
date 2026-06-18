# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpi/mpi2_type.h

Purpose: provides the foundational MPI v2 scalar and pointer typedefs used by all neighboring Fusion-MPT MPI protocol headers. It maps MPI names onto Linux fixed-width little-endian types so on-wire structures can express firmware byte order directly.

Important APIs/types/functions: when `MPI_TYPE_H` has not already provided them, it defines `U8` as `u8`, `U16` as `__le16`, `U32` as `__le32`, and `U64` as aligned `__le64`. Pointer aliases `PU8`, `PU16`, `PU32`, and `PU64` are also provided. There are no functions or runtime APIs.

Control flow: there is no runtime behavior. The include guard and `MPI_TYPE_H` check prevent duplicate typedefs when an older/common MPI type header is already included.

State and persistence: no state is stored. The persistent effect is compile-time: every MPI request, reply, config page, event, and SGE structure using these aliases documents little-endian firmware fields.

Dependencies and integration: depends on Linux kernel type definitions already being visible through the including path. It is included directly or indirectly by the MPI header set under `drivers/scsi/mpt3sas/mpi`, including IOC, SAS, PCIe, RAID, toolbox, config, and image headers.

Risks: endian annotations matter. Treating `U16`/`U32`/`U64` as CPU-native integers without `le16_to_cpu()`, `cpu_to_le16()`, and related helpers can break on big-endian systems and obscure sparse warnings. The explicit 4-byte alignment on `U64` is part of the firmware ABI; changing it can shift fields in packed-like protocol structures. Pointer aliases are legacy style and should not encourage unchecked casts from arbitrary buffers without size validation.

Test signals: compile with sparse/endian checking, build on architectures with strict alignment and non-little-endian configurations where possible, and run structure-size/offset-sensitive driver tests that exercise IOC init, passthrough, events, config pages, and diagnostic buffer requests.
