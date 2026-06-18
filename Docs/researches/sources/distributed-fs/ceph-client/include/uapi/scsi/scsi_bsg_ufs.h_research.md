# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_ufs.h

## Purpose
`scsi_bsg_ufs.h` defines the UFS transport BSG SG_IO v4 ABI for UPIU transaction requests and advanced RPMB/ARPMB commands. It exposes UFS query, command, UIC, and RPMB metadata structures to userspace tools that interact with UFS host controllers through BSG.

## Important APIs, Types, and Constants
`UFS_CDB_SIZE` and `UIC_CMD_SIZE` define CDB and UIC command sizing. `enum ufs_bsg_msg_code` selects `UPIU_TRANSACTION_UIC_CMD` or `UPIU_TRANSACTION_ARPMB_CMD`. `enum ufs_rpmb_op_type` identifies RPMB operations such as write key, read counter, write, read, read response, secure configuration read/write, purge enable, and purge status read.

`struct utp_upiu_header` overlays raw dwords with field accessors for transaction code, flags, LUN, task tag, command set, query/task management function, response, status, EHS length, device information, and data segment length. It uses endian-conditional bitfield order for `iid` and `command_set_type`. Request bodies are `struct utp_upiu_query`, `utp_upiu_query_v4_0`, `utp_upiu_cmd`, and `utp_upiu_req`.

RPMB/EHS support uses `struct ufs_arpmb_meta` and `struct ufs_ehs`. BSG wrappers are `struct ufs_bsg_request`, `ufs_bsg_reply`, `ufs_rpmb_request`, and `ufs_rpmb_reply`.

## Control Flow and State
Userspace constructs a `ufs_bsg_request` with a msgcode and UPIU request, submits it through BSG, and receives `ufs_bsg_reply` with a result, payload receive length, and response UPIU. ARPMB operations add EHS request/reply metadata and MAC key material around the BSG wrapper. Query request format differs for UFS 4.0 and later, where `utp_upiu_query_v4_0` exposes OSF fields.

## State and Persistence Behavior
This ABI can touch persistent UFS state: query write operations can update descriptors/attributes/flags, RPMB write-key permanently programs authentication material, secure configuration and purge operations can change device security state. The header itself does not store state; it defines one transaction's serialized UPIU and metadata.

## Dependencies and Integration Points
It includes `<asm/byteorder.h>` and `<linux/types.h>`. Integration points are the UFS host controller driver, SCSI BSG transport, UFSHCI/UPIU protocol handlers, RPMB security tooling, and SCSI command payloads embedded in `utp_upiu_cmd`.

## Risks and Test Signals
Risks include endian/bitfield portability, mixing raw dword and structured header views, wrong EHS length interpretation, and destructive RPMB operations. Tests should compile on big- and little-endian targets, validate UPIU dword field packing, round-trip query and SCSI command requests through a mock UFS BSG handler, and gate RPMB write-key/purge tests to explicit hardware-safe environments.
