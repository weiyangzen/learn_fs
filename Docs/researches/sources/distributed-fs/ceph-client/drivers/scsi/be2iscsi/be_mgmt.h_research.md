# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.h

## Purpose

`be_mgmt.h` declares the `be2iscsi` management-plane ABI between driver files and firmware command helpers. It defines management constants, firmware command payload structures for ICD invalidation, controller/HBA attributes, BSG vendor flash commands, endpoint state, and prototypes for connection management, network interface management, boot-session commands, sysfs display helpers, offload WRB population, and firmware session cleanup.

## Important APIs, Types, And Constants

Constants include IP add/delete actions, IPv4/IPv6 byte lengths, UE status/mask PCI config offsets, `BE_INVLDT_CMD_TBL_SZ`, and BSG flash operation IDs. `GET_MGMT_CONTROLLER_WS` and `ISCSI_GET_PDU_TEMPLATE_ADDRESS` are helper macros used by management/open-connection paths.

Important structures include:

- `struct invldt_cmd_tbl`, `struct invldt_cmds_params_in`, `struct invldt_cmds_params_out`, and `union be_invldt_cmds_params`: packed firmware payloads for invalidating outstanding iSCSI commands by ICD and CID.
- `struct mgmt_hba_attributes`, `struct mgmt_controller_attributes`, `struct be_mgmt_controller_attributes`, and response variants: packed controller/HBA inventory and firmware version data structures.
- `struct be_bsg_vendor_cmd`: BSG vendor flash command request header with region, offset, and sector fields.
- `struct beiscsi_endpoint`: driver endpoint state tying an open-iscsi endpoint to HBA, connection pointer, destination IPv4/IPv6 address, TCP port, endpoint CID, firmware session handle, and validity flags.

The header declares management entry points for `mgmt_open_connection`, `mgmt_vendor_specific_fw_cmd`, `beiscsi_mgmt_invalidate_icds`, initiator-name retrieval, DHCP/static IP/gateway/NIC/VLAN/interface-info operations, boot session helpers, sysfs display functions implemented in `be_mgmt.c`, connection offload WRB population, connection invalidation/upload, EQ delay modification, and firmware-session logout.

## Control Flow Role

The header is consumed by `be_main.c`, `be_mgmt.c`, and related transport files. Endpoint connect paths allocate/populate `struct beiscsi_endpoint` and call `mgmt_open_connection`. SCSI error handlers build `struct invldt_cmd_tbl` arrays and call `beiscsi_mgmt_invalidate_icds`. Interface parameter callbacks use the declared network configuration functions. Probe and boot work use boot helper prototypes. Completion and recovery paths use connection invalidation/upload prototypes to coordinate firmware state with libiscsi endpoint teardown.

## State And Persistence Behavior

`struct beiscsi_endpoint` is the main stateful type in this header. It persists for the lifetime of a driver/open-iscsi endpoint and records both host-side pointers and firmware-side identifiers. The packed command structures are transient DMA or embedded mailbox payloads. Management operations can update persistent firmware state such as flash contents, configured initiator name, network IP/gateway/VLAN configuration, and boot session data, but the header itself only defines the data shapes and function contracts.

## Dependencies And Integration Points

The header includes `scsi/scsi_bsg_iscsi.h`, `be_iscsi.h`, and `be_main.h`, so it is tightly coupled to SCSI BSG, libiscsi transport types, the main HBA definition, and local firmware command structures. Packed structures must match firmware command ABI. Prototypes bridge user-facing transport callbacks, BSG handling, boot sysfs, and low-level MCC command submission.

## Risks And Edge Cases

The header contains packed firmware structures with fixed-size strings and reserved fields; layout changes are risky. `BE_INVLDT_CMD_TBL_SZ` must remain aligned with SCSI command-per-LUN behavior in `be_main.h`. `struct beiscsi_endpoint` mixes IPv4 `unsigned long` storage with IPv6 byte arrays and firmware/session identifiers, so users must respect `ip_type` and validity fields. Several prototypes return unsigned tags where zero means failure; callers need careful error handling.

## Test Signals

Any changes should trigger build coverage for all be2iscsi files, packed layout review, sparse/endian checks, and runtime management tests for endpoint connect/disconnect, ICD invalidation, interface configuration, boot session discovery, and BSG vendor command handling. ABI-sensitive changes should be verified against firmware command documentation or existing command helper expectations.
