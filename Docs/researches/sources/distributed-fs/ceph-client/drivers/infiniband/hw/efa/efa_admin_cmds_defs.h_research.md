# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_cmds_defs.h

## Purpose

`efa_admin_cmds_defs.h` defines the EFA admin command ABI: command opcodes, feature IDs, QP states/types, stats formats, command and response payloads for QP/CQ/MR/PD/UAR/AH/EQ operations, feature get/set payloads, AENQ groups, MMIO read response format, host-info format, and bit masks for packed fields.

## Important APIs, Types, and Definitions

- Version/opcode enums: `EFA_ADMIN_API_VERSION_*`, `efa_admin_aq_opcode`, `efa_admin_aq_feature_id`, QP type/state, stats type/scope, AENQ groups, and OS type.
- QP ABI: `efa_admin_create_qp_cmd/resp`, `modify_qp`, `query_qp`, and `destroy_qp` structures plus create/modify masks.
- Address and memory: AH create/destroy, `reg_mr`, `dereg_mr`, `alloc_mr`, interconnect ID validity, and permission/page-size masks.
- CQ/EQ ABI: create/destroy CQ and EQ command/response structures with doorbell offsets, sub-CQ depth, UAR, interrupt, and event-bitmask fields.
- Feature/stats ABI: device attributes, queue attributes, network attributes, AENQ config, event queue attributes, hardware hints, and basic/messages/RDMA/network stats.
- Host/MMIO: `efa_admin_mmio_req_read_less_resp` and `efa_admin_host_info`.

## Control Flow

The header has no runtime control flow. Command wrapper code fills these structures, submits them through `efa_com_cmd_exec`, and decodes completion responses. Feature descriptors are retrieved during probe and govern later verbs limits and capabilities.

## State and Persistence Behavior

The structures define firmware-persistent resources: QP handles/numbers/state, PD/UAR IDs, AH handles, lkey/rkey registrations, CQ/EQ indices, doorbell offsets, feature capabilities, and stats counters. Host info persists in firmware after a set-feature command. Packed masks define stable ABI bits and must remain synchronized with firmware.

## Dependencies and Integration Points

It depends on common admin queue descriptors from `efa_admin_defs.h`, memory address structures from `efa_common_defs.h`, and `GENMASK`/`BIT` macros. It is consumed by `efa_com.c` for EQ commands, `efa_com_cmd.*` for most admin command wrappers, `efa_verbs.*` for RDMA object operations, and userspace ABI translation paths.

## Risks and Edge Cases

- This snapshot contains duplicate named fields (`aq_common_desc` in `efa_admin_create_ah_cmd` and `page_size_cap` in `efa_admin_feature_device_attr_desc`), which would be compile-blocking in C unless repaired or generated differently.
- ABI structs include many MBZ/reserved fields; callers must zero-initialize commands before filling fields.
- Feature evolution is sparse (`QUEUE_ATTR_2` jumps to ID 9), so code must check supported feature bits before using newer descriptors.
- MR registration supports physical mode only for privileged clients; command wrappers must enforce privilege and PBL shape.
- Large MR and indirect PBL support depends on control-buffer descriptors and page-list chaining, which are easy to size incorrectly.

## Test Signals

Build tests should catch duplicate field names and layout drift. ABI tests should validate command sizes, offsets, and masks against firmware documentation. Runtime tests should cover create/query/modify/destroy QP, CQ/EQ lifecycle, MR registration variants, stats scopes/types, feature probing/fallback, AENQ configuration, host info set, and negative firmware responses for unsupported or malformed commands.
