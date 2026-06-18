<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_2_sh_mask.h

Purpose: generated AMD MP 14.0.2 bitfield metadata for MP1 and MPASP SMU register blocks. It supplies the masks and shifts paired with `mp_14_0_2_offset.h`, allowing amdgpu code to construct full-width C2P message payloads and manipulate interrupt, scratch, FPS-count, public-control, and firmware-flag fields.

Important APIs/types/functions: the file defines preprocessor field helpers only. MP1 SMN helpers include `MP1_SMN_C2PMSG_0` through `MP1_SMN_C2PMSG_127` `CONTENT` fields, `MP1_SMN_IH_CREDIT` fields `CREDIT_VALUE` and `CLIENT_ID`, `MP1_SMN_IH_SW_INT` fields `ID` and `VALID`, `MP1_SMN_IH_SW_INT_CTRL` fields `INT_MASK` and `INT_ACK`, `MP1_SMN_FPS_CNT__COUNT_MASK`, `MP1_SMN_PUB_CTRL__WREN_MASK`, and `MP1_SMN_EXT_SCRATCH0` through `31` `DATA` fields. MPASP helpers mirror the C2P subset and IH fields. The public CRU helper is `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` plus reserved-bit metadata.

Control flow: no executable control flow exists. Consumers combine these constants with offsets from the matching offset header in register read/modify/write operations. Full-register C2P and scratch fields use shift `0` and mask `0xFFFFFFFFL`; structured interrupt and control registers use narrow masks.

State and persistence: no software state is stored. The header describes the shape of hardware state: message payload registers hold 32-bit command words, interrupt registers expose credit/client and software interrupt valid/id bits, control registers provide mask/ack bits, `MP1_SMN_PUB_CTRL` exposes a write-enable bit, and public firmware flags expose interrupt-enabled plus reserved bits.

Dependencies and integration points: depends only on include guards and C preprocessor expansion. It integrates with generated offsets for MP 14.0.2, AMD SMU/MP firmware messaging code, and shared bitfield helper macros that expect `REG__FIELD__SHIFT` and `REG__FIELD_MASK` names.

Risks: the MPASP section covers only selected C2P message registers, so consumers must not assume the full MP1 0-127 set is available for MPASP. The field metadata should stay synchronized with `mp_14_0_2_offset.h`; an offset-only entry without a corresponding mask, or the reverse, can create dead or unsafe register accesses. Reserved bits in `MP1_CRU1_MP1_FIRMWARE_FLAGS` should remain preserved by downstream read/modify/write code rather than overwritten. `0xFFFFFFFFL` masks are correct for 32-bit payloads but should be handled with unsigned-width discipline in callers.

Test signals: compile tests catch missing macro names. Register-generation validation should compare every shift/mask against the source register spec and cross-check mask coverage against offsets. Runtime validation is through SMU command submission, MPASP message paths, interrupt acknowledgement, and public firmware flag reads on MP 14.0.2 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_2_sh_mask.h -->
