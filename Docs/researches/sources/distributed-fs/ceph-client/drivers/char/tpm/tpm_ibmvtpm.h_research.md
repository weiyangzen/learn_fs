# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.h

## Purpose
Defines IBM vTPM CRQ message layout, device runtime state, and message constants shared by the IBM VIO vTPM implementation.

## Important APIs, Types, And Functions
Key types are `struct ibmvtpm_crq`, `struct ibmvtpm_crq_queue`, and `struct ibmvtpm_dev`. Constants define CRQ page size, init commands, valid markers, response bit, and vTPM message ids for get version, TPM command, RTCE buffer size, and suspend preparation.

## Control Flow
The header encodes the ring and CRQ command protocol consumed by `tpm_ibmvtpm.c`; responses are distinguished by `VTPM_MSG_RES` and valid bytes.

## State And Persistence
`struct ibmvtpm_dev` tracks the VIO device, CRQ ring, DMA handles, RTCE buffer, locks, waitqueues, response length, version, and command-processing flag.

## Dependencies And Integration Points
Depends on VIO and DMA types via the C file includes. The packed, aligned CRQ layout must match the hypervisor register/memory protocol.

## Risks And Edge Cases
Field endian annotations are part of the ABI. Changing constants or packing can break hypervisor communication. RTCE buffer is declared `void __iomem *` though allocated with `kmalloc()`, which can complicate static analysis.

## Test Signals
CRQ byte layout validation, endian conversion tests, ring index wrap, and ABI compatibility with IBM Power hypervisor vTPM devices.
