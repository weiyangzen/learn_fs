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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_2_offset.h

Purpose: generated AMD MP 14.0.2 register-address metadata for SMU/MP1 and MPASP blocks. It maps symbolic register names to offsets and base-index selectors so the amdgpu driver can address MP1 firmware messaging, interrupt, scratch, and public firmware-flag registers for this ASIC revision.

Important APIs/types/functions: this header exports `reg...` and `reg..._BASE_IDX` macros. Major families include `regMP1_SMN_C2PMSG_0` through `regMP1_SMN_C2PMSG_127` at offsets `0x0040` through `0x00bf` with base index `1`, MP1 interrupt/status registers `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, `regMP1_SMN_FPS_CNT`, `regMP1_SMN_PUB_CTRL`, scratch registers `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31`, MPASP C2P message subset macros such as `regMPASP_SMN_C2PMSG_32` through `39`, `60` through `89`, `100` through `103`, `109`, `115`, `116`, and `regMPASP_SMN_C2PMSG_119_BASE_IDX`, plus `regMPASP_SMN_IH_*` and public `regMP1_CRU1_MP1_FIRMWARE_FLAGS`.

Control flow: there is no executable flow. Register access code selects a symbolic offset and its `_BASE_IDX`, then the AMD register accessor infrastructure resolves that pair to the correct MMIO/SMN aperture. The header separates address blocks with comments: `mp_SmuMp1_SmnDec`, `mp_SmuMpASP_SmnDec`, and `Mp1MmioPublic_SmuMp1Pub_CruDec`.

State and persistence: no software state is stored. The constants address persistent hardware state held by MP1/MPASP firmware-facing registers. C2P message registers carry host-to-microcontroller commands and parameters, IH registers carry software interrupt and acknowledgement state, scratch registers provide firmware/driver exchange slots, and the public firmware-flags register advertises firmware interrupt state.

Dependencies and integration points: depends on the generated AMD ASIC register layout and on downstream register accessor macros that consume `reg*` and `reg*_BASE_IDX`. It is intended to pair with `mp_14_0_2_sh_mask.h` for field extraction and with amdgpu SMU/MP firmware code that selects ASIC-specific headers through build-time includes.

Risks: the most notable irregularity is `regMPASP_SMN_C2PMSG_119_BASE_IDX` without a matching `regMPASP_SMN_C2PMSG_119` offset macro in this file; that may be deliberate if the offset is inherited or unused, but it is worth validating against the generator input because consumers cannot address that register from this header alone. Public firmware flags use base index `7` in this revision, while similar MP1 public blocks in other revisions may use different base indexes; accidental cross-version inclusion would direct accesses to the wrong aperture. Repetitive C2P sequences also create off-by-one and omitted-register risk.

Test signals: build coverage should reveal missing symbols used by MP 14.0.2 code. Better tests are generated-header diff checks against the AMD register database, scripts that ensure every `_BASE_IDX` has an intended offset partner or an explicit exception, and hardware/firmware tests that send SMU messages through MP1 and MPASP paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_2_offset.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_offset.h

Purpose: generated AMD MP 15.0.0 register-address metadata for MPASP, MPASP public PCRU, MP1 SMN, and MP1 public CRU blocks. It gives the amdgpu driver symbolic offsets and base indexes for MP firmware communication registers in the newer ASIC generation.

Important APIs/types/functions: the file exports address macros, not functions or types. MPASP SMN includes C2P message registers `60` through `79`, `100` through `103`, `109`, plus `regMPASP_SMN_IH_CREDIT`, `regMPASP_SMN_IH_SW_INT`, and `regMPASP_SMN_IH_SW_INT_CTRL`, all with base index `0`. `mp_SmuMpASPPub_PcruDec` adds public PCRU C2P registers `regMPASP_PCRU1_MPASP_C2PMSG_64` through `71` at offsets `0x4280` through `0x4287` with base index `3`. MP1 SMN provides the full `regMP1_SMN_C2PMSG_0` through `127` sequence, IH registers, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_EXT_SCRATCH0` through `31`, generally with base index `1`. MP1 public firmware flags are exposed as `regMP1_CRU1_MP1_FIRMWARE_FLAGS` with base index `5`.

Control flow: no executable control flow exists. Downstream code uses each `reg*` macro and matching `_BASE_IDX` to form register accesses through AMD's MMIO/SMN access helpers. The address-block comments identify the required base aperture for each register family.

State and persistence: no software state is stored. The constants address hardware state used for host-to-firmware messages, software interrupt delivery and acknowledgement, scratch exchanges, and public firmware status flags. The MPASP public PCRU registers add a public-addressed path for selected MPASP C2P messages.

Dependencies and integration points: depends on the AMD register-generation scheme and the amdgpu register accessor layer. It pairs with `mp_15_0_0_sh_mask.h` for field masks and with ASIC-specific SMU/MP code selecting MP 15.0.0 definitions.

Risks: compared with MP 14.0.2, the MPASP register set is narrower at the SMN level and adds a public PCRU block; copying assumptions between generations can route MPASP accesses through the wrong block. The `regMP1_CRU1_MP1_FIRMWARE_FLAGS_BASE_IDX` value is `5`, unlike MP 14.0.2's public block base index, so version selection is safety-critical. Repetitive full MP1 C2P sequences can hide missing entries, and any offset/base-index mismatch can cause reads or writes against unrelated hardware.

Test signals: generated-header linting should verify paired `reg*` and `_BASE_IDX` macros, monotonic C2P offset ranges, and expected base indexes per address block. Build tests catch missing references; hardware tests should cover MP1 message submission, MPASP message submission through both SMN and PCRU paths where used, interrupt handling, and scratch register communication on MP 15.0.0 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_offset.h -->

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
