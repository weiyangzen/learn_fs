<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_0_sh_mask.h

Purpose: generated AMD MP 14.0.0 SMU/MP1 bitfield metadata for register consumers in the amdgpu DRM driver. It complements an offset header by defining `__SHIFT` and `_MASK` constants used to pack, unpack, and test fields in MP1 firmware, client-to-processor message, interrupt-handler, frame-count, and scratch registers.

Important APIs/types/functions: this file exposes preprocessor constants only. The public names are field helpers such as `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED__SHIFT`, `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`, `MP1_SMN_C2PMSG_N__CONTENT__SHIFT`, `MP1_SMN_C2PMSG_N__CONTENT_MASK`, `MP1_SMN_IH_CREDIT__CREDIT_VALUE_MASK`, `MP1_SMN_IH_SW_INT__VALID_MASK`, `MP1_SMN_IH_SW_INT_CTRL__INT_ACK_MASK`, `MP1_SMN_FPS_CNT__COUNT_MASK`, and `MP1_SMN_EXT_SCRATCHN__DATA_MASK`.

Control flow: there is no executable control flow. Inclusion is guarded by `_mp_14_0_0_SH_MASK_HEADER`; downstream code includes the header and uses the constants in register read/modify/write paths, usually with sibling `reg...` offset macros and common AMD register helper macros.

State and persistence: no runtime or persistent state is allocated. The constants describe persistent hardware state in MP1/SMN registers: C2P message registers are full 32-bit payload slots, interrupt registers encode credit/client/id/valid/ack bits, scratch registers are full 32-bit data slots, and `MP1_CRU1_MP1_FIRMWARE_FLAGS` persists firmware-visible flags such as interrupt enablement.

Dependencies and integration points: depends only on the C preprocessor and the AMD register-generation naming convention. It integrates with the amdgpu MP/SMU firmware communication stack, generated offset headers for the same ASIC generation, and register access code that combines an address macro with these masks and shifts.

Risks: constants must exactly match the silicon register specification; a wrong mask or shift can silently corrupt firmware messages or interrupt acknowledgement. The many `MP1_SMN_C2PMSG_0` through `MP1_SMN_C2PMSG_127` definitions are mechanically repetitive, so missing or off-by-one generated entries are the main review risk. Full-width `0xFFFFFFFFL` masks rely on downstream code using an integer type wide enough for 32-bit hardware values. ASIC-generation mixups are also risky because these names are versioned only by the containing header, not by each macro name.

Test signals: compile coverage should catch missing macro names where this header is included. Stronger validation comes from register-header generation checks, comparing mask/shift pairs against AMD register databases, and runtime SMU smoke tests that exercise C2P message submission, interrupt signalling, and scratch-register exchanges on MP 14.0.0 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_0_sh_mask.h -->
