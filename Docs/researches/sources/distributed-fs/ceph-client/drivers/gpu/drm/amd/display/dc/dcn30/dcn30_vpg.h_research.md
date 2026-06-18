# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h

Purpose: Declares the DCN 3.0 VPG hardware wrapper, register lists, field shift/mask layouts, and constructor/API prototypes used by display resource construction.

Important APIs/types/functions: `DCN30_VPG_FROM_VPG()` converts the base `struct vpg` to `struct dcn30_vpg`. `VPG_DCN3_REG_LIST()` names the five VPG registers. `DCN3_VPG_MASK_SH_LIST()` and `VPG_DCN3_REG_FIELD_LIST()` enumerate conflict, data, frame-update, and immediate-update fields for 15 generic packet slots. `struct dcn30_vpg_registers`, `struct dcn30_vpg_shift`, `struct dcn30_vpg_mask`, and `struct dcn30_vpg` define the object contract.

Control flow: This header has no runtime control flow; it enables generated/static resource tables to create register, shift, and mask instances consumed by `dcn30_vpg.c`.

State/persistence: `struct dcn30_vpg` stores the embedded base object plus immutable pointers to register/field metadata. Hardware state is external.

Dependencies/integration: Includes `vpg.h` and depends on register-list macros such as `SRI` and `SE_SF` supplied by AMD DC resource files. Its prototypes are implemented by `dcn30_vpg.c` and are reused by DCN31 VPG code for packet writes.

Risks: Macro lists must stay synchronized with silicon register definitions and the switch statements in `vpg3_update_generic_info_packet()`. Omitting a field breaks register helper expansion at compile time or silently prevents a packet slot from updating.

Test signals: Build coverage with DCN3 resources is the primary signal. Register-table smoke tests should confirm all 15 frame and immediate update fields resolve.
