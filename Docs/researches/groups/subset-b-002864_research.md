# Research: subset-b-002864

Grouped research for AMD MP register metadata headers. These files are generated C preprocessor register descriptions used by AMDGPU SMU, display clock-manager, and RAS/MCA code. They contain no executable functions, but they define the ABI between driver code and MP/SMU hardware register layouts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_offset.h

## Purpose

`mp_13_0_6_offset.h` declares register offset macros for the MP block on SMU/MP ASIC version 13.0.6. It is an address map, not an implementation unit. Consumers include it to form MMIO/SMN addresses for MP0 and MP1 command/message mailboxes, interrupt handoff registers, MP1 scratch registers, and an MP1 public firmware-flags register.

The header uses `_mp_13_0_6_OFFSET_HEADER` as an include guard and carries AMD's permissive license block. Address comments identify three generated register blocks: `aid_mp_SmuMp0_SmnDec`, `aid_mp_SmuMp1_SmnDec`, and `aid_mp_SmuMp1Pub_CruDec`, all with base address `0x0`.

## Important APIs, Types, And Macros

There are no C types or functions. The exported API is the macro namespace:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_103`, with offsets `0x0060` through `0x00a7`, plus matching `_BASE_IDX` macros set to `0`.
- `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL` at offsets `0x00c1` through `0x00c3`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_127`, with offsets `0x0260` through `0x02bf`, plus matching `_BASE_IDX` macros set to `0`.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_PUB_CTRL` at offsets `0x02c1` through `0x02c5`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31` at `0x0340` through `0x035f`, except scratch9 is absent.
- `regMP1_FIRMWARE_FLAGS` at `0xbee00a`.

Every listed register has a companion `reg..._BASE_IDX` macro, currently `0`. Consumer-side helpers such as `SOC15_REG_OFFSET()` or local `REG(reg_name)` macros combine the base index with an IP base table to compute the final address.

## Control Flow

The file has no runtime control flow. Build-time control flow is limited to include-guard selection. Runtime behavior is induced by consumers that use these constants to read or write PMFW/SMU mailbox registers. Typical flows include writing a message ID to a `C2PMSG` register, passing arguments through other mailbox registers, polling a response mailbox, and checking firmware interrupt readiness through `regMP1_FIRMWARE_FLAGS` or its hand-written SMN alias in PPT code.

## State And Persistence

The header itself stores no state. The macros name persistent hardware-visible registers. `C2PMSG` registers are command, argument, response, or scratch mailboxes depending on the SMU protocol used by a caller. `EXT_SCRATCH` registers provide firmware/driver scratch state across transactions and possibly across some reset scopes. `MP1_FIRMWARE_FLAGS` exposes firmware status, including the interrupt-enabled bit described in the paired sh/mask header.

Because the values are hard-coded ABI constants, any mismatch with ASIC register programming guides persists as incorrect hardware access until the header or consumer override is fixed.

## Dependencies And Integration Points

This header pairs with `mp_13_0_6_sh_mask.h`, which defines fields for the registers named here. `smu13/smu_v13_0_6_ppt.c` includes both files, undefines generic `MP1_Public` and `smnMP1_FIRMWARE_FLAGS`, and supplies local TODO-tagged final offsets before checking `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`. RAS/MCA code such as `umc_v12_0.c` includes the 13.0.6 mask for MCA field decoding.

The register names match the broader AMDGPU register macro pattern used by display and power-management code: a `reg...` offset macro, a `reg..._BASE_IDX`, and field macros in the companion mask header. Integration depends on the correct IP base table and on callers selecting the ASIC-specific header that matches the device.

## Risks

The main risk is silent hardware misaddressing. The file's `regMP1_FIRMWARE_FLAGS` value is `0xbee00a`, while the 13.0.6 PPT code overrides firmware flags with `0x3010028` and notes that final register offsets need checking. That is a strong signal that public-register addressing may require special handling outside the generated offset namespace.

Another risk is assuming the 13.0.6 layout matches nearby 13.0.x variants. Compared with 13.0.8, 13.0.6 exposes more MP1 scratch registers and `regMP1_SMN_PUB_CTRL`; its firmware flag offset also differs. Consumers that reuse 13.0.8 constants on 13.0.6 could address the wrong firmware flag or omit required scratch/control registers.

## Test Signals

Useful validation signals are successful compilation of consumers including this header, SMU firmware boot/status checks returning success, mailbox message transactions completing without timeout, and interrupt enable checks through `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`. Runtime tests should exercise SMU command paths, display clock-manager interactions where applicable, suspend/resume, reset, and RAS/MCA error collection on ASICs that use 13.0.6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_sh_mask.h

## Purpose

`mp_13_0_6_sh_mask.h` defines bit shifts and masks for the MP 13.0.6 registers named in the companion offset header. It lets driver code encode and decode full-register mailbox payloads, interrupt-credit fields, software-interrupt fields, firmware flags, scratch data, and a small set of MCA-style 64-bit status fields.

The file uses `_mp_13_0_6_SH_MASK_HEADER` as its include guard. It contains no executable code and exports only preprocessor constants.

## Important APIs, Types, And Macros

The main exported groups are:

- `MP0_SMN_C2PMSG_32__CONTENT__SHIFT` through `MP0_SMN_C2PMSG_103__CONTENT_MASK`, all representing a 32-bit `CONTENT` field at shift `0x0` with mask `0xFFFFFFFFL`.
- `MP1_SMN_C2PMSG_32__CONTENT__SHIFT` through `MP1_SMN_C2PMSG_127__CONTENT_MASK`, also full 32-bit mailbox payload fields.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT` fields: `CREDIT_VALUE` at shift `0x0` with mask `0x00000003L`, and `CLIENT_ID` at shift `0x10` with mask `0x00FF0000L`.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT` fields: `ID` at shift `0x0` and `VALID` at shift `0x8`.
- `MP0_SMN_IH_SW_INT_CTRL` and `MP1_SMN_IH_SW_INT_CTRL` fields: `INT_MASK` at shift `0x0` and `INT_ACK` at shift `0x8`.
- `MP1_SMN_FPS_CNT__COUNT`, `MP1_SMN_PUB_CTRL__LX3_RESET`, and `MP1_SMN_EXT_SCRATCHn__DATA` for scratch registers 0-8 and 10-31.
- `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED` and `MP1_FIRMWARE_FLAGS__RESERVED`.
- 64-bit MCA field masks for `MCMP1_IPIDT0`, `MCMP1_STATUST0`, and `MCMP1_MISC0T0`.

No structs or inline helpers are provided. Consumers usually apply these masks with shifts manually or through AMD register helper macros such as `FD()`.

## Control Flow

The header has no runtime control flow. It influences control paths in consumers that branch on decoded fields, for example PMFW readiness checks that test `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`, software interrupt control that sets or acknowledges interrupt bits, and MCA/RAS paths that test status-valid, uncorrected, or processor-context-corrupt bits.

## State And Persistence

The file stores no state. Its constants describe how hardware state is represented. Mailbox `CONTENT` fields are 32-bit opaque values whose persistence depends on firmware mailbox protocol and reset behavior. Firmware flags are status bits set by MP1 firmware. MCA fields describe error-reporting state and may persist until firmware, hardware, or driver code clears the related status registers.

## Dependencies And Integration Points

This mask header is coupled to `mp_13_0_6_offset.h`; a field macro is meaningful only when used with the corresponding register address. It is included by `smu13/smu_v13_0_6_ppt.c` for PMFW status and by `umc_v12_0.c` for MCA decoding. It follows the same naming pattern as older MP mask files, so common AMDGPU code can refer to stable names such as `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`.

The MCA field macros are notable because they are 64-bit masks with `L` suffixes. On 64-bit Linux builds this is normally safe, but code should use 64-bit storage when reading or combining these fields.

## Risks

The biggest risk is using a mask with the wrong ASIC generation or wrong offset header. Most mailbox fields are full-width, so a wrong mapping may still compile and look plausible while addressing the wrong register. The firmware flag mask names are shared across generations, but the register address can differ or be overridden by consumers.

The MCA masks require correct width handling. If a consumer truncates these values to 32 bits, high status bits such as `PCC`, `UC`, and `Val` will be lost. Another risk is treating `RESERVED_MASK` bits as writable policy bits; they should be preserved or ignored according to hardware guidance.

## Test Signals

Build coverage should compile all consumers with `-Wshift-count-overflow` and related warnings cleanly. Runtime signals include PMFW readiness checks passing, software interrupts being acknowledged without stuck bits, SMU mailbox requests completing, and RAS/MCA paths decoding valid/uncorrected error bits correctly during injected or real error events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_offset.h

## Purpose

`mp_13_0_8_offset.h` declares MP register offsets for SMU/MP ASIC version 13.0.8. Like other files in this directory, it is generated register metadata used by AMDGPU code to produce final MMIO/SMN addresses through local base-index helpers.

The header covers MP0 and MP1 SMN decoder mailboxes and a small MP1 public block. It uses `_mp_13_0_8_OFFSET_HEADER` as an include guard.

## Important APIs, Types, And Macros

The exported macro groups are:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_103`, at offsets `0x0060` through `0x00a7`.
- MP0 interrupt handoff registers `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL`, at `0x00c1` through `0x00c3`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_127`, at offsets `0x0260` through `0x02bf`.
- MP1 interrupt handoff registers at `0x02c1` through `0x02c3`, plus `regMP1_SMN_FPS_CNT` at `0x02c4`.
- MP1 extended scratch registers `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH7`, at `0x0340` through `0x0347`.
- `regMP1_FIRMWARE_FLAGS` at `0xbee009`.

Every register macro has a `_BASE_IDX` macro set to `0`. There are no C functions or data types.

## Control Flow

There is no runtime control flow in the header. Consumers use these constants to implement PMFW mailbox transactions and display-clock SMU requests. For example, `display/dc/clk_mgr/dcn316/dcn316_smu.c` includes this header, builds a local `MP0_BASE` table, and defines `REG(reg_name)` as `MP0_BASE.instance[0].segment[reg..._BASE_IDX] + reg...` before issuing VBIOSSMC messages.

## State And Persistence

The macros name hardware state. `C2PMSG` registers carry command, response, and argument data for host-to-firmware communication. `IH_*` registers represent interrupt-credit and software-interrupt state. `EXT_SCRATCH0-7` provide MP1 scratch storage exposed by this ASIC variant. `MP1_FIRMWARE_FLAGS` is a firmware status register whose field layout is defined in `mp_13_0_8_sh_mask.h`.

The header itself is stateless, but changes to its constants directly affect persistent driver behavior across boots because they alter the addresses used for all related transactions.

## Dependencies And Integration Points

This file is paired with `mp_13_0_8_sh_mask.h`. The direct consumer found in this tree is `dcn316_smu.c`, where the offset macros are integrated with display clock-manager register helpers and SMU message definitions. The same macro style is compatible with AMDGPU's broader `SOC15_REG_OFFSET()` and register-helper conventions.

Compared with 13.0.6, this variant uses address-block comments without the `aid_` prefix, lacks `regMP1_SMN_PUB_CTRL`, exposes only scratch0-7, and uses firmware flag offset `0xbee009` rather than `0xbee00a`.

## Risks

Variant drift is the central risk. The 13.0.8 file is close to 13.0.6 but not identical, so mechanical reuse of offsets across ASIC revisions can produce subtle PMFW failures. The reduced scratch-register set is another risk for code that assumes scratch8 or scratch10-31 are available.

Because base indices are all zero, consumers with incorrect local base tables may still compile and produce bad final addresses. The address comments say base `0x0`, so final addressing depends entirely on the external IP base map used by the caller.

## Test Signals

Compile-time validation should ensure `dcn316_smu.c` and other 13.0.8 consumers resolve all `REG()` and `FN()` macros. Runtime validation should cover display clock SMU messages such as PMFW version, display clock, DPP clock, DCF clock, table transfer, and DTB clock requests. Healthy signals are non-timeout SMU replies, correct PMFW version reads, and no display clock programming regressions on DCN316-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_sh_mask.h

## Purpose

`mp_13_0_8_sh_mask.h` defines shift and mask macros for the MP 13.0.8 register offsets. It provides field layouts for mailbox content registers, MP0/MP1 interrupt handoff, MP1 frame/performance count, MP1 scratch registers 0-7, and MP1 firmware flags.

The file is guarded by `_mp_13_0_8_SH_MASK_HEADER` and exports only constants.

## Important APIs, Types, And Macros

Important macro groups include:

- `MP0_SMN_C2PMSG_32__CONTENT` through `MP0_SMN_C2PMSG_103__CONTENT`, all full 32-bit fields at shift `0x0`.
- `MP1_SMN_C2PMSG_32__CONTENT` through `MP1_SMN_C2PMSG_127__CONTENT`, also full 32-bit fields.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT` fields for `CREDIT_VALUE` and `CLIENT_ID`.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT` fields for interrupt `ID` and `VALID`.
- `MP0_SMN_IH_SW_INT_CTRL` and `MP1_SMN_IH_SW_INT_CTRL` fields for `INT_MASK` and `INT_ACK`.
- `MP1_SMN_FPS_CNT__COUNT`, using the full 32-bit register.
- `MP1_SMN_EXT_SCRATCH0__DATA` through `MP1_SMN_EXT_SCRATCH7__DATA`, full 32-bit scratch data.
- `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED` at bit 0 and `MP1_FIRMWARE_FLAGS__RESERVED` for the remaining bits.

No helper functions are supplied. Consumers must combine masks and shifts directly or through register-field helper macros.

## Control Flow

The header has no control flow. It affects consumer branching only when decoded fields are tested. Display clock-manager code includes this file with the 13.0.8 offset header so `FN(reg, field)` style helpers can refer to field definitions while SMU message code polls status and exchanges mailbox values.

## State And Persistence

No state is stored in the header. It documents hardware state encoding. Mailbox `CONTENT` fields are opaque 32-bit protocol values. Interrupt handoff fields describe pending interrupt and acknowledgement state. Scratch data fields expose firmware/driver scratch values. Firmware flags record PMFW readiness, with bit 0 indicating interrupts enabled.

## Dependencies And Integration Points

This file is tightly coupled to `mp_13_0_8_offset.h`. It is included by `display/dc/clk_mgr/dcn316/dcn316_smu.c`, whose local base-table and register helper macros turn these generated names into usable register addresses and fields. It follows the same field naming conventions as older MP generations, making shared SMU status logic easier to port.

Unlike `mp_13_0_6_sh_mask.h`, this file has no MCA field macros and no `MP1_SMN_PUB_CTRL` field. Code needing MCA status decoding or LX3 reset control must not assume this file provides those definitions.

## Risks

The most likely defect class is wrong-ASIC inclusion. The field names look highly similar across MP 13.0.x files, so a source file could compile while decoding the wrong register set. A second risk is assuming scratch registers beyond scratch7 exist because 13.0.6 exposes many more scratch fields.

The firmware flags field names are stable across many generations, but the address source is not. Consumers should validate both offset and mask header pairing, especially where code overrides `smnMP1_FIRMWARE_FLAGS`.

## Test Signals

Compile checks should catch missing field definitions in DCN316 SMU code. Runtime checks should include PMFW alive/version messages, clock frequency set/get commands, table transfer messages, and interrupt-ready paths. Display regressions, SMU timeouts, or stuck busy responses are strong signs of an offset/mask mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_0_offset.h

## Purpose

`mp_14_0_0_offset.h` declares MP1 SMN register offsets for MP/SMU ASIC version 14.0.0. It is narrower than the 13.0.x offset headers in this subset: it only exposes the `mp_SmuMp1_SmnDec` address block and does not define MP0 registers or the MP1 public firmware-flags register in this file.

The header uses `_mp_14_0_0_OFFSET_HEADER` as its include guard. It is generated register metadata used by display and SMU code to address MP1 mailboxes, interrupt handoff, FPS count, and extended scratch registers.

## Important APIs, Types, And Macros

The macro API includes:

- `regMP1_SMN_C2PMSG_0` through `regMP1_SMN_C2PMSG_127`, contiguous from `0x0240` through `0x02bf`. This is broader than the 13.0.x headers in this subset, which start at C2PMSG_32.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, and `regMP1_SMN_FPS_CNT` at `0x0340` through `0x0343`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31`, contiguous from `0x03c0` through `0x03df`.
- Companion `_BASE_IDX` macros, all set to `0`.

No structs, enums, or functions are defined.

## Control Flow

The file has no runtime control flow. It participates in consumer control flow through generated addresses used for mailbox transactions. `display/dc/clk_mgr/dcn35/dcn35_smu.c` includes this offset header and `mp_14_0_0_sh_mask.h`, defines MP1 base segments locally, and computes addresses through `REG(reg_name)`.

Another SMU consumer pattern appears in `smu14/smu_v14_0_2_ppt.c`, where mailbox control uses `SOC15_REG_OFFSET(MP1, 0, regMP1_SMN_C2PMSG_66)`, `regMP1_SMN_C2PMSG_90`, and `regMP1_SMN_C2PMSG_82` as message, response, and argument registers. That example is for a nearby 14.0.x variant, but it shows how these macro names drive SMU message control.

## State And Persistence

The header itself stores no state. It maps hardware state exposed through MP1 registers. The expanded C2PMSG range includes low mailboxes 0-31 plus 32-127, so consumers can use protocol-specific low or high mailboxes. Interrupt handoff and FPS count registers expose live firmware/interrupt state. Scratch0-31 provide firmware/driver scratch storage.

Because these are ABI-like constants, a wrong value persists as a runtime hardware access bug until fixed in source or hidden by a consumer override.

## Dependencies And Integration Points

This header pairs with `mp_14_0_0_sh_mask.h` for field definitions, although the mask file in this tree notably covers `MP1_CRU1_MP1_FIRMWARE_FLAGS` rather than the C2PMSG fields. `dcn35_smu.c` includes both and contains a TODO stating that real headers should be used when correct, then defines local MP1 base segments. That TODO is an important integration signal: consumers may still compensate for incomplete or imperfect generated base metadata.

The file follows AMDGPU's `reg...` and `_BASE_IDX` convention, so it can be consumed by `REG()` helpers and `SOC15_REG_OFFSET()` style macros. It does not define `regMP1_CRU1_MP1_FIRMWARE_FLAGS`; firmware flag addresses for SMU14 are instead represented elsewhere, such as `smu_v14_0.h` constants and newer MP 14.0.2 offset headers.

## Risks

The main risk is assuming MP 14.0.0 layout matches 13.0.x. Here the C2PMSG range starts at index 0, the interrupt registers move to `0x0340` and later, and scratch registers move to `0x03c0` and later. Using 13.0.x offsets on 14.0.0 would direct mailbox and interrupt traffic to wrong addresses.

Another risk is incomplete public-block coverage. Code needing MP1 firmware flags must not expect this file to provide `regMP1_FIRMWARE_FLAGS` or `regMP1_CRU1_MP1_FIRMWARE_FLAGS`. The TODO in `dcn35_smu.c` also suggests that base segment definitions should be treated carefully during future cleanup.

## Test Signals

Compile-time signals include successful resolution of all `regMP1_SMN_C2PMSG_*` and `_BASE_IDX` macros in DCN35 and SMU14 code. Runtime signals should cover DCN35 SMU messages such as PMFW version, display clock, DPP clock, DCF clock, table transfer, IPS/Z-state messages, and mailbox response polling. Failures usually show up as SMU command timeouts, unknown-command responses, display clock programming failures, or firmware status checks that never report interrupts enabled through the separate SMU14 firmware flag path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_0_offset.h -->
