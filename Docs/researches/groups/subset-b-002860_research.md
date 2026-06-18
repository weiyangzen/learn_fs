# Research: subset-b-002860

Grouped research for `subset-b-002860`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_default.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_default.h

Purpose: generated AMD MP 10.0 register-default header for the SMU MP0 and MP1 SMN decode blocks. It defines reset/default values for the MP0/MP1 `C2PMSG_32..103` mailbox registers plus interrupt-handler helper registers, giving driver code a compile-time source of expected reset contents for SMU/PSP mailbox state.

Important APIs and state: the exported interface is only preprocessor constants named `mmMP0_SMN_*_DEFAULT` and `mmMP1_SMN_*_DEFAULT`. All listed defaults are `0x00000000`, including the 72 MP0 C2P message slots, the 72 MP1 C2P message slots, `IH_CREDIT`, `IH_SW_INT`, `IH_SW_INT_CTRL`, and MP1-only `FPS_CNT`. There are no C types, functions, inline helpers, or storage objects.

Control flow: none in this file. Compile-time users include it through SMU10 include stacks and then combine these constants with offset and mask headers when they need reset-value comparisons or register-table initialization.

State and persistence: the header does not persist kernel state, but it documents hardware reset state. Runtime state lives in the device registers addressed by the matching offset header; these default macros should not be mistaken for cached software values after firmware, PSP, or SMU command traffic starts mutating the mailbox registers.

Dependencies and integration: guarded by `_mp_10_0_DEFAULT_HEADER` and designed to pair with `mp_10_0_offset.h` and `mp_10_0_sh_mask.h`. In this tree it is pulled by `pm/powerplay/hwmgr/smu10_inc.h`, which exposes MP 10.0 register definitions to the older PowerPlay SMU10 manager path. Consumers typically use AMDGPU register access macros rather than this header directly.

Risks and test signals: because every value is zero, the main risk is assuming a zero default is still valid after firmware boot or after mailbox ownership changes. Regeneration mistakes can silently break register-table code because these macros are untyped and unchecked. Test signals are compile coverage of the SMU10 include path and runtime bring-up on MP 10.0 ASICs where reset-state checks, if present, do not report unexpected nonzero mailbox defaults immediately after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_offset.h

Purpose: generated AMD MP 10.0 register-offset header for MP0 and MP1 SMN mailbox access. It maps symbolic `mmMP*_SMN_*` names to SOC15-style register indices so PSP and SMU code can address firmware mailbox registers without hard-coded numeric offsets.

Important APIs and state: the interface is a macro table. MP0 `C2PMSG_32..103` occupy `0x0060..0x00a7`; MP0 `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL` are `0x00c1..0x00c3`. MP1 mirrors the mailbox range at `0x0260..0x02a7`, then defines `IH_CREDIT`, `IH_SW_INT`, `IH_SW_INT_CTRL`, and `FPS_CNT` at `0x02c1..0x02c4`. Every register has a companion `_BASE_IDX` macro with value `0`, indicating the register belongs to base aperture 0 for the SOC15 access helpers.

Control flow: none in the header itself. Runtime control flow appears in consumers such as `psp_v10_0.c`, which writes MP0 C2P mailbox registers to initialize PSP rings and poll firmware responses, and SMU paths that configure `msg_reg`, `resp_reg`, and argument registers through `SOC15_REG_OFFSET(MP1, 0, mmMP1_SMN_C2PMSG_*)`.

State and persistence: the macros do not hold state. They name hardware-backed registers whose contents persist in the device until reset or firmware/driver writes. C2P registers are command and argument mailboxes, interrupt registers carry software interrupt mask/ack state, and `FPS_CNT` is a counter-style MP1 register. Any software cache of values must be maintained by the caller, not inferred from this header.

Dependencies and integration: protected by `_mp_10_0_OFFSET_HEADER` and paired with `mp_10_0_default.h` and `mp_10_0_sh_mask.h`. It is included by `amdgpu/psp_v10_0.c` and by `pm/powerplay/hwmgr/smu10_inc.h`. The values are consumed by AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`, which apply the block instance and base-index metadata.

Risks and test signals: wrong offsets can brick early PSP/SMU handshakes by sending ring addresses or commands to the wrong mailbox. MP0 and MP1 names are similar but target different firmware engines, so copy/paste mistakes are high impact. Compile tests catch missing macros; real validation requires MP 10.0 boot, PSP ring setup, SMU message-response traffic, interrupt mask/ack paths, and checks that polling loops do not timeout on C2P/P2C responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_sh_mask.h

Purpose: generated AMD MP 10.0 bitfield shift/mask header. It defines how to pack and unpack the MP0/MP1 SMN mailbox registers, public MP interrupt registers, firmware flags, C2P/P2C message registers, active-function IDs, and counters used by AMDGPU PSP and SMU code.

Important APIs and state: the interface is a set of `REG__FIELD__SHIFT` and `REG__FIELD_MASK` macros. Most `C2PMSG_*` and `P2CMSG_*` registers expose a full 32-bit `CONTENT` field at shift `0`. SMN interrupt credit fields are `CREDIT_VALUE` bits `0..1` and `CLIENT_ID` bits `16..23`. SMN software interrupt fields differ by register family: `MP*_SMN_IH_SW_INT` uses `VALID` bit 0 and `ID` bits `1..8`, while public `MP*_IH_SW_INT` uses `ID` bits `0..7` and `VALID` bit 8. `*_IH_SW_INT_CTRL` exposes mask and ack bits at bit 0 and bit 8. `MP*_ACTIVE_FCN_ID` uses `VFID` bits `0..3` and `VF` bit 31. `MP1_FIRMWARE_FLAGS` exposes `INTERRUPTS_ENABLED` bit 0 and a reserved upper field. `MP1_P2CMSG_INTEN` covers four interrupt-enable bits, and `MP1_P2CMSG_INTSTS` exposes individual status bits 0..3. `FPS_CNT` and ordinary message content are full-width fields.

Control flow: no executable control flow exists here, but these masks drive read-modify-write paths. `REG_SET_FIELD` consumers set interrupt masks and acknowledgements, and firmware-ready checks read `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` before deciding whether SMU interrupt handling is enabled. Mailbox polling compares `MP1_C2PMSG_90__CONTENT_MASK`-filtered response values in common SMU code.

State and persistence: bit definitions are stateless. The fields they describe are hardware/firmware state: command payloads, firmware responses, interrupt credits, software interrupt valid/ack bits, active SR-IOV function state, and MP1 firmware flags. These values can change asynchronously with firmware execution and interrupt delivery, so callers must use the proper register accessors and synchronization expected by the AMDGPU subsystem.

Dependencies and integration: protected by `_mp_10_0_SH_MASK_HEADER` and meant to accompany the offset/default headers. The macros are used by AMDGPU register helper infrastructure (`REG_GET_FIELD`, `REG_SET_FIELD`, masks in polling loops) and by SMU/PSP paths that include ASIC register headers through SMU10 or related include stacks. It also provides public MP1 mailbox masks not present in the narrower offset-only tables.

Risks and test signals: the main risk is semantic mismatch between similarly named SMN and public interrupt fields; the valid and ID bit positions are not identical. Any incorrect mask can lose interrupts, acknowledge the wrong event, or corrupt firmware mailbox payloads. Test signals include compile coverage of all `REG_SET_FIELD`/`REG_GET_FIELD` uses, SMU interrupt enable/disable cycles, PSP/SMU command-response polling, SR-IOV active-function queries, and stress cases with repeated firmware interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_offset.h

Purpose: generated AMD MP 11.0.8-specific register-offset header. It gives PSP/SMU code symbolic offsets for the MP0 and MP1 SMN mailbox blocks on ASICs using the 11.0.8 MP layout, including the extended scratch registers needed by that firmware generation.

Important APIs and state: the file exports `mmMP0_SMN_C2PMSG_32..103` at `0x0060..0x00a7`, MP0 interrupt helper registers at `0x00c1..0x00c3`, `mmMP1_SMN_C2PMSG_32..103` at `0x0260..0x02a7`, MP1 interrupt helpers and `FPS_CNT` at `0x02c1..0x02c4`, and `mmMP1_SMN_EXT_SCRATCH0..7` at `0x03c0..0x03c7`. All `_BASE_IDX` values are `0`.

Control flow: none in this header. Its offsets feed PSP 11.0.8 runtime flows: `psp_v11_0_8.c` writes MP0 C2P registers to program ring base, size, write pointers, doorbells, TMR metadata, and bootloader commands; it also reads MP0 response/status registers while polling for firmware progress.

State and persistence: the macros are compile-time constants only. The underlying MP0 registers hold PSP boot and ring state, and MP1 scratch registers expose firmware-owned scratch data across driver interactions until reset or firmware overwrite. Because the extended scratch registers are full hardware locations, they must be treated as live device state rather than stable configuration.

Dependencies and integration: protected by `_mp_11_0_8_OFFSET_HEADER`. It is directly included by `amdgpu/psp_v11_0_8.c`, whose register access uses `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`. It mirrors much of the generic MP 11.0 offset layout but omits generic-only entries such as `ACTIVE_FCN_ID`, `PUB_CTRL`, and PMI public MMU decode macros while adding the scratch range required for this ASIC-specific path.

Risks and test signals: MP 11.0.8 PSP initialization depends on exact MP0 mailbox offsets; a single wrong constant can leave firmware rings uninitialized or cause response polling to timeout. Extended scratch offsets are adjacent and easy to mis-index. Test signals include PSP boot on an MP 11.0.8 ASIC, ring create/destroy, TMR programming, secure display or firmware command traffic if supported, and no timeouts in the MP0 C2P polling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_sh_mask.h

Purpose: generated AMD MP 11.0.8-specific shift/mask header for SMN mailbox, interrupt, counter, and extended scratch registers. It tells consumers how to pack fields for the offsets in `mp_11_0_8_offset.h`.

Important APIs and state: most `MP0_SMN_C2PMSG_*` and `MP1_SMN_C2PMSG_*` registers have a full 32-bit `CONTENT` mask at shift `0`. `MP*_SMN_IH_CREDIT` uses `CREDIT_VALUE` bits `0..1` and `CLIENT_ID` bits `16..23`. For 11.0.8 SMN software interrupts, `MP*_SMN_IH_SW_INT` uses `ID` bits `0..7` and `VALID` bit 8, and `MP*_SMN_IH_SW_INT_CTRL` uses `INT_MASK` bit 0 and `INT_ACK` bit 8. `MP1_SMN_FPS_CNT` and `MP1_SMN_EXT_SCRATCH0..7` are full-width `COUNT`/`DATA` fields.

Control flow: no executable control flow. These constants are used by register-field helpers and low-level firmware interface code when extracting mailbox payloads, setting software interrupt masks, acknowledging interrupt events, or interpreting MP1 scratch values. The file is narrower than the generic MP 11.0 mask header and focuses on the SMN names used by the 11.0.8 PSP path.

State and persistence: stateless macro definitions. The described registers carry volatile hardware state: firmware command payloads, response data, interrupt mask/ack state, interrupt credits, FPS counters, and extended firmware scratch values. Firmware may update these registers asynchronously, so readers must expect change between accesses.

Dependencies and integration: protected by `_mp_11_0_8_SH_MASK_HEADER` and logically paired with `mp_11_0_8_offset.h`. Although the 11.0.8 PSP file in this tree includes only the offset header directly, these masks provide the companion field contract for code that needs `REG_SET_FIELD`/`REG_GET_FIELD` style access to the same registers.

Risks and test signals: the interrupt field layout differs from MP 10.0 SMN software interrupt macros, where `VALID` is bit 0 and `ID` starts at bit 1. Reusing the wrong generation's mask would corrupt interrupt programming. Test signals include field-helper compile coverage, SMN interrupt enable/ack behavior, firmware command/response integrity, and any diagnostics that read the MP1 extended scratch registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_offset.h

Purpose: generated generic AMD MP 11.0 register-offset header, despite the include guard name `_mp_11_0_2_OFFSET_HEADER`. It supplies the broader MP 11.0 SMN mailbox and public/PMI offsets used by PSP 11.0 and SMU 11 code paths.

Important APIs and state: MP0 `C2PMSG_32..103` are `0x0060..0x00a7`; MP0 additionally has `ACTIVE_FCN_ID` at `0x00c0`, `IH_CREDIT` at `0x00c1`, `IH_SW_INT` at `0x00c2`, and `IH_SW_INT_CTRL` at `0x00c3`. MP1 `C2PMSG_32..103` are `0x0260..0x02a7`; MP1 then defines `ACTIVE_FCN_ID`, `IH_CREDIT`, `IH_SW_INT`, `IH_SW_INT_CTRL`, `FPS_CNT`, `PUB_CTRL`, and `EXT_SCRATCH0..7` at `0x02c0..0x02c5` and `0x03c0..0x03c7`. The public MMU decode block adds SMN absolute addresses `smnMP1_PMI_3_START` (`0x3030204`), `smnMP1_PMI_3_FIFO` (`0x3030208`), and `smnMP1_PMI_3` (`0x3030600`). Register-index macros have `_BASE_IDX 0`.

Control flow: no control flow is defined here. Runtime users include `amdgpu/psp_v11_0.c`, `pm/swsmu/smu11/smu_v11_0.c`, `sienna_cichlid_ppt.c`, and `nv.c`. Typical flows write MP0 C2P registers during PSP ring setup, configure MP1 message/response/argument registers for SMU messages, and read/write MP1 interrupt registers while enabling, disabling, or acknowledging SMU interrupts.

State and persistence: macro constants are stateless. The addressed hardware state includes firmware mailbox contents, interrupt mask/ack bits, active virtual-function status, FPS counters, public-control state, extended scratch words, and PMI registers. These values persist in hardware until reset or firmware/driver writes and may also change asynchronously as MP firmware runs.

Dependencies and integration: protected by the include guard and paired with `mp_11_0_sh_mask.h` for bitfield definitions. The offsets are consumed by SOC15 register infrastructure, especially `SOC15_REG_OFFSET(MP0/MP1, instance, macro)`, `RREG32_SOC15`, and `WREG32_SOC15`. SMU common code also relies on matching mask macros for `MP1_FIRMWARE_FLAGS` and C2P response fields, while PSP code relies on exact MP0 mailbox locations.

Risks and test signals: this is a central hardware ABI header, so incorrect values break early firmware boot, SMU message routing, interrupt delivery, SR-IOV active-function tracking, or PMI access. The generic 11.0 file differs from 11.0.8 by adding active-function, public-control, and PMI entries; using the wrong header for an ASIC can address nonexistent or shifted registers. Test signals include PSP 11 ring initialization, SMU 11 message timeout-free operation, interrupt mask/unmask and ack paths, SR-IOV validation where applicable, and compile coverage for all included ASIC-specific PPT files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_offset.h -->
