
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.h

## Purpose
Defines Kunpeng HCCS driver data models, firmware command IDs, request/response payload structures, PCC descriptor layout, capabilities, and topology objects shared by `kunpeng_hccs.c`.

## Important APIs, Types, and Functions
- Topology/state structures: `hccs_dev`, `hccs_chip_info`, `hccs_die_info`, `hccs_port_info`, `hccs_type_name_map`, and `hccs_mbox_client_info`.
- Version-specific operations: `struct hccs_verspecific_data`.
- Firmware protocol definitions: `enum hccs_subcmd_type`, request parameter structs, `hccs_link_status`, request/response heads, `hccs_fw_inner_head`, `hccs_req_desc`, `hccs_rsp_desc`, and union `hccs_desc`.

## Control Flow
No executable flow. The header establishes the memory layout consumed by PCC command send/receive paths and sysfs topology code.

## State and Persistence
No state is stored in the header. The structs describe in-memory driver state and firmware message layout.

## Dependencies and Integration Points
Assumes Linux kernel types, kobjects, mailbox/PCC types included by the C file, and a 64-byte PCC communication region. It is private to the driver directory.

## Risks
Packed layout is not explicitly requested; the current small integer fields and `u32` data arrays depend on normal kernel ABI alignment matching firmware expectations. `HCCS_DIE_MAX_PORT_ID` avoids 255 because `next_id` loop termination relies on a greater-than check.

## Test Signals
Compile-time size/layout checks for descriptor structures, maximum response/request data calculations, command enum stability, and firmware compatibility for bitfield layouts.
