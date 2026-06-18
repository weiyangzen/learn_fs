# sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.h

## Purpose
`ibmvmc.h` defines the public and internal contract for the IBM VMC driver. It contains protocol constants, ioctl numbers, message opcodes/status codes, global and per-HMC state enums, CRQ message layouts, DMA-buffer descriptors, and session/container structures shared by `ibmvmc.c`.

## Important APIs, types, and functions
The user ABI constants are `VMC_IOCTL_SETHMCID`, `VMC_IOCTL_QUERY`, and `VMC_IOCTL_REQUESTVMC`; `struct ibmvmc_query_struct` is copied to user space. The wire format is represented by `struct ibmvmc_admin_crq_msg` for capability exchange and `struct ibmvmc_crq_msg` for ordinary VMC commands. Driver structures include `struct ibmvmc_buffer`, `struct crq_queue`, `struct crq_server_adapter`, `struct ibmvmc_struct`, `struct ibmvmc_hmc`, and `struct ibmvmc_file_session`.

## Control flow
The header itself has no executable flow, but it encodes the state transitions implemented in the C file. `enum ibmvmc_states` progresses from initial to CRQ init, capabilities, ready, failed, with a negative scheduled-reset state. `enum ibmhmc_states` progresses from free to initial, opening, ready, or failed. Message opcodes describe the request/response sequence: capability exchange, open/close, add/remove buffer, and signal messages.

## State and persistence
`struct ibmvmc_buffer` tracks whether each DMA buffer is valid, free, local or hypervisor owned, its id, size, message length, local/remote DMA addresses, and local virtual address. `struct ibmvmc_hmc` persists each HMC session's state, id string, buffer pool, queue, and attached file session. `struct ibmvmc_struct` carries global negotiated values and VMC DRC index.

## Dependencies and integration points
The header depends on Linux types, `cdev`, and PowerPC `asm/vio.h`. Endian-annotated fields (`__be16`, `__be32`) are part of the CRQ ABI and must match hypervisor expectations exactly. The ioctl constants form the user/kernel ABI for management applications.

## Risks
Changing structure layout, opcode values, endian annotations, ioctl numbers, or limits is ABI-sensitive. `MAX_HMCS` and `MAX_BUF_POOL_SIZE` are compile-time array limits, while negotiated values are runtime clamps; callers must never index by module parameters without validating against negotiated maximums.

## Test signals
Build validation should confirm this header compiles on the intended PowerPC VIO configurations. ABI tests should verify ioctl numbers and struct sizes remain stable, and runtime tests should confirm capability negotiation honors the declared min, max, and default limits.
