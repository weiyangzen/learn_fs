# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_abi.h

## Purpose
Defines firmware ABI names, offsets, commands, and structures for the PF runtime-symbol mailbox and shared buffer/devlink shared-buffer operations.

## Important APIs, Types, and Functions
- Mailbox symbols and offsets: `NFP_MBOX_SYM_NAME`, `NFP_MBOX_CMD`, `NFP_MBOX_RET`, `NFP_MBOX_DATA_LEN`, `NFP_MBOX_DATA`, and minimum size.
- `enum nfp_mbox_cmd` defines PF mailbox operations for shared buffer pool get/set and PCIe-side ABM enable/disable.
- Shared buffer symbol names and structures mirror firmware/devlink data: `struct nfp_shared_buf`, `struct nfp_shared_buf_pool_id`, `struct nfp_shared_buf_pool_info_get`, and `struct nfp_shared_buf_pool_info_set`.

## Control Flow
No executable flow. `nfp_main.c` uses the mailbox constants in `nfp_mbox_cmd()`, while devlink/shared-buffer code uses the packed structures and command ids to exchange data with firmware.

## State and Persistence Behavior
Defines the wire format for firmware-owned persistent/runtime state. The driver does not own persistence here; it serializes requests into the runtime symbol mailbox and reads firmware responses.

## Dependencies and Integration Points
Integrated with PF runtime-symbol access, devlink shared buffer callbacks, ABM app support, and firmware ABI. Uses Linux fixed-size little-endian types for cross-endian clarity.

## Risks
ABI drift between firmware and driver can corrupt mailbox commands or interpret pool units incorrectly. The structures are not explicitly marked packed, so layout assumptions rely on natural alignment matching firmware ABI.

## Test Signals
Devlink shared buffer pool get/set, ABM enable/disable, firmware versions with and without PF mailbox support, and endian/layout validation are key. Runtime failures surface as mailbox `-EOPNOTSUPP`, `-EBUSY`, `-ETIMEDOUT`, or firmware-returned errors.
