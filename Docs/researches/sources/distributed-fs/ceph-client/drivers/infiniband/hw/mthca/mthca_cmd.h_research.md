# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.h

## Purpose
`mthca_cmd.h` declares the firmware command ABI and shared data structures used by mthca initialization, resource management, QP/CQ/SRQ transitions, MAD handling, and multicast operations.

## Important APIs, types, and functions
It defines command status codes, QP transition identifiers, device-limit feature flags, `MTHCA_MAILBOX_SIZE`, `struct mthca_mailbox`, `struct mthca_dev_lim`, `struct mthca_adapter`, `struct mthca_init_hca_param`, `struct mthca_init_ib_param`, and `struct mthca_set_ib_param`. It declares command lifecycle functions, mailbox allocation, firmware/system commands, ICM mapping, resource SW2HW/HW2SW commands, QP modify/query, special QP config, `mthca_MAD_IFC()`, MGM commands, and `mthca_NOP()`.

## Control flow
Callers allocate mailboxes, fill one of the declared parameter structures or hardware context buffers, call the relevant wrapper, and inspect returned output buffers or immediate values. The implementation selects polling or event completion based on command state.

## State and persistence
The header describes firmware-owned state but stores none itself. Structures mirror persistent hardware capabilities and initialization parameters such as resource table bases, log sizes, port GUIDs, capability masks, and limits.

## Dependencies and integration points
It depends on RDMA verbs types and is included by main setup, EQ/CQ/QP/SRQ/MR/MCG/MAD modules. It is the compile-time contract for `mthca_cmd.c`.

## Risks
Firmware status and layout definitions are ABI-sensitive. Typos in status meanings or structure fields can mislead callers. The comment typo "unallocaterd" is harmless, but the command declarations are broad enough that any signature drift would break many subsystems.

## Test signals
Compile all users, validate command wrapper prototypes against implementations, verify QP transition enums match `mthca_MODIFY_QP()`, and test device-limit parsing against known firmware dumps for Tavor, Arbel native, Arbel compatibility, and Sinai.
