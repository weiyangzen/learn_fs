# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre.h

## Purpose
This header defines the shared HPRE contract between `hpre_main.c` and `hpre_crypto.c`: hardware SQE layout, algorithm IDs, debugfs structures, capability table indexes, the top-level HPRE wrapper around `struct hisi_qm`, and cross-file function declarations.

## Important APIs, Types, and Functions
Important constants include `HPRE_SQE_SIZE`, `HPRE_PF_DEF_Q_NUM`, `HPRE_PF_DEF_Q_BASE`, `HPRE_V2_ALG_TYPE`, and `HPRE_V3_ECC_ALG_TYPE`. `enum hpre_alg_type` maps HPRE hardware algorithm opcodes such as non-CRT RSA, CRT RSA, DH, ECC multiply, and Curve25519 multiply. `struct hpre_sqe` is the hardware submission queue entry with `dw0`, task lengths, DMA addresses for key/input/output, and a software tag. `struct hpre` embeds `struct hisi_qm` plus HPRE debug state and status.

The header declares `hpre_create_qp()`, `hpre_algs_register()`, `hpre_algs_unregister()`, and `hpre_check_alg_support()`. Debugfs helper structures include `struct hpre_debugfs_file`, `struct hpre_dfx`, and `struct hpre_debug`.

## Control Flow
There is no executable control flow. The header defines the compile-time interface: device lifecycle code allocates QPs and exposes capabilities, while crypto code creates request contexts, fills `struct hpre_sqe`, and uses algorithm IDs to submit work.

## State and Persistence Behavior
No state is allocated by the header. It defines the shape of runtime state embedded in HPRE devices and request SQEs. Capability table enum values persist the index contract used by `qm->cap_tables.dev_cap_table`.

## Dependencies and Integration Points
The header depends on `<linux/hisi_acc_qm.h>` for queue-manager types and is included by both HPRE implementation files. Its SQE layout must match HPRE hardware and the queue-manager SQE size configured in `hpre_qm_init()`.

## Risks and Edge Cases
Any change to `struct hpre_sqe`, algorithm opcode values, or capability enum ordering can break hardware ABI or table lookups. `HPRE_DEBUGFS_FILE_NUM` relies on enum arithmetic that assumes cluster control files follow the base debug file entries. Unsupported algorithms such as x448 are documented as sharing an opcode family but not currently supported.

## Test Signals
Build tests should catch cross-file prototype drift. Runtime signals are successful SQE submission/completion for RSA, DH, and ECDH, correct capability lookup in `hpre_check_alg_support()`, and debugfs file creation for all clusters within `HPRE_CLUSTERS_NUM_MAX`.
