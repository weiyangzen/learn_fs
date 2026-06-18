# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.h

## Purpose
`qla_bsg.h` defines the qla2xxx vendor-specific BSG ABI: command opcodes, vendor status codes, loopback constants, 84xx management payloads, destination addressing structures, mailbox passthrough layout, FRU/I2C/SERDES structs, flash update and BBCR data structures, D_Port diagnostic layouts, active flash image status, and driver attribute bits.

## Important APIs, Types, and Constants
- Vendor command opcodes include `QL_VND_LOOPBACK`, `QL_VND_A84_RESET`, `QL_VND_A84_UPDATE_FW`, `QL_VND_A84_MGMT_CMD`, `QL_VND_IIDMA`, `QL_VND_FCP_PRIO_CFG_CMD`, flash read/update, FRU status/version operations, I2C read/write, FX00 management, SERDES operations, flash update capabilities, BBCR, private stats, D_Port diagnostics, EDIF management, driver attributes, host/tgt stats, host-port management, mailbox passthrough, and image-set validation.
- Vendor status constants include `EXT_STATUS_OK`, generic errors, busy, invalid parameter, overrun/underrun, mailbox error, buffer-too-small, no-memory, offline, unsupported, invalid config, DMA error, timeout, data compare failure, D_Port diagnostic states, and image validation/config errors.
- Loopback constants define command-sent values, internal/external loopback options, loopback masks, ELS payload sizing, and ELS opcode byte.
- 84xx structures:
  - `struct qla84_mgmt_param`, `struct qla84_msg_mgmt`, and `struct qla_bsg_a84_mgmt` model memory read/write, config changes, and info requests.
- Addressing and IIDMA structures:
  - `struct qla_scsi_addr`, `struct qla_ext_dest_addr`, and `struct qla_port_param`.
- Mailbox passthrough:
  - `struct qla_mbx_passthru` carries 32 input and 32 output mailbox words plus reserved fields.
- FRU/SFP/I2C:
  - `struct qla_field_address`, `struct qla_field_info`, `struct qla_image_version`, `struct qla_image_version_list`, `struct qla_status_reg`, and `struct qla_i2c_access`.
- SERDES and flash:
  - `struct qla_serdes_reg`, `struct qla_serdes_reg_ex`, and `struct qla_flash_update_caps`.
- BBCR and D_Port:
  - `struct qla_bbcr_data`, `struct qla_dport_diag`, and `struct qla_dport_diag_v2`.
- Image/driver attributes:
  - `struct qla_active_regions` reports active flash image regions.
  - `struct qla_drv_attr` exposes driver capability bits such as `QLA_IMG_SET_VALID_SUPPORT`.
- The header includes `qla_edif_bsg.h`, extending the ABI for EDIF management.

## Control Flow
The header itself has no executable control flow. In `qla_bsg.c`, `vendor_cmd[0]` is matched against the `QL_VND_*` opcodes, and request/reply SG payloads are interpreted using the packed structures defined here. Vendor status constants are written to `bsg_reply->reply_data.vendor_reply.vendor_rsp[0]`.

## State and Persistence
- Structures describe both transient requests and persistent hardware state changes. Flash, FRU, I2C/SFP, mailbox passthrough, SERDES writes, and image validation commands can change adapter firmware or nonvolatile fields.
- Flexible array payloads (`qla84_msg_mgmt.payload[]`, `qla_image_version_list.version[]`) depend on caller-provided BSG payload length.
- Packed structs define ABI layout and must remain stable for user-space tools.

## Dependencies and Integration Points
- Used by `qla_bsg.c` and user-space BSG tooling that speaks the qla2xxx vendor ABI.
- Depends on fixed-width kernel integer types, packing attributes, bit macros, and EDIF definitions in `qla_edif_bsg.h`.
- Integrates indirectly with mailbox firmware, flash update logic, diagnostics, stats, target/initiator controls, and EDIF management.

## Risks and Edge Cases
- ABI stability is critical: changing opcode values, struct packing, field order, or sizes can break existing management tools.
- Several structs contain reserved fields that likely must remain zeroed or ignored for forward compatibility.
- Flexible array and length-bearing structs require strict length validation in the C handlers; otherwise short or oversized BSG payloads may be mishandled.
- Endianness is not annotated in the ABI structs, so user-space/kernel agreement on field byte order must be documented and consistently handled.
- `qla_i2c_access.buffer` is fixed at 0x40 bytes; handlers must reject or clamp larger lengths to avoid copying beyond the embedded buffer.

## Test Signals
- ABI size/layout checks for all packed structs used by user-space.
- BSG command tests that verify each `QL_VND_*` opcode dispatches to the expected handler and returns documented `EXT_STATUS_*` values.
- Fuzz or negative tests for flexible-array counts, I2C lengths, mailbox passthrough payload size, D_Port v2 payload size, and unknown opcodes.
- Compatibility tests with existing qla2xxx management utilities, especially for flash, FRU, D_Port, stats, mailbox passthrough, and EDIF commands.
