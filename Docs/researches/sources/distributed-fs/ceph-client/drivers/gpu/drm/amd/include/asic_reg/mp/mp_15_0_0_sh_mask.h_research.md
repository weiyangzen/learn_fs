<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_sh_mask.h

Purpose: generated AMD MP 15.0.0 bitfield metadata for MPASP and MP1 firmware communication registers. It provides the shifts and masks that pair with `mp_15_0_0_offset.h` so driver code can safely encode C2P messages, software interrupts, scratch data, and firmware-flag operations for this ASIC generation.

Important APIs/types/functions: this file defines C preprocessor constants only. MPASP SMN helpers cover `MPASP_SMN_C2PMSG_60` through `79`, `100` through `103`, and `109` `CONTENT` fields, plus `MPASP_SMN_IH_CREDIT` credit/client fields, `MPASP_SMN_IH_SW_INT` id/valid fields, and `MPASP_SMN_IH_SW_INT_CTRL` mask/ack fields. MPASP public PCRU helpers cover `MPASP_PCRU1_MPASP_C2PMSG_64` through `71` full-width `CONTENT` fields. MP1 SMN helpers cover `MP1_SMN_C2PMSG_0` through `127`, the MP1 IH registers, `MP1_SMN_FPS_CNT__COUNT_MASK`, and `MP1_SMN_EXT_SCRATCH0` through `31` `DATA` fields. MP1 public CRU helpers cover `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` and reserved bits.

Control flow: there is no executable control flow. Inclusion is guarded by `_mp_15_0_0_SH_MASK_HEADER`; consumers use the constants during register composition and extraction after choosing offsets from the matching MP 15.0.0 offset header.

State and persistence: no in-memory state is allocated. The constants describe hardware state layout: C2P and PCRU C2P messages are 32-bit payload fields, IH credit carries low-bit credit and high-bit client id, software interrupt registers expose id and valid bits, interrupt control exposes mask and acknowledgement bits, scratch registers are full-width data slots, and firmware flags expose interrupt enablement while reserving the remaining bits.

Dependencies and integration points: depends only on the C preprocessor and generated AMD register naming. It integrates with `mp_15_0_0_offset.h`, amdgpu SMU/MP firmware mailbox code, interrupt handling paths, and any ASIC dispatch table that selects the MP 15.0.0 register header set.

Risks: MPASP coverage differs from MP 14.0.2, especially because the public PCRU C2P registers are distinct from the SMN C2P subset; callers must use the matching offset family for each mask family. Reserved firmware-flag bits should be preserved by downstream writes. Full-width masks should be treated as 32-bit unsigned values to avoid sign or truncation issues on unusual compiler/type combinations. Any generator drift between this mask file and the offset file can create macros that compile but access the wrong field shape.

Test signals: compile-only coverage confirms symbols exist. Register-spec validation should compare every `__SHIFT` and `_MASK` pair against the MP 15.0.0 hardware database and check for corresponding offset definitions. Runtime signals include successful SMU mailbox commands, MPASP PCRU message transactions if used by the driver, interrupt delivery/acknowledgement, scratch register readbacks, and firmware flag reads on MP 15.0.0 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_sh_mask.h -->
