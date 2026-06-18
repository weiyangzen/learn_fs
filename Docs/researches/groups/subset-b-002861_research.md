# Research: subset-b-002861

Grouped research report for AMD MP ASIC register headers. Each section is delimited for reconciliation into source-tree-aligned per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_sh_mask.h

## Purpose

`mp_11_0_sh_mask.h` is a generated AMDGPU register field contract for MP/SMU/PSP generation 11.0 hardware. It contains preprocessor-only bit shift and bit mask definitions for MP0 SMN, MP1 public, MP1 SMN, and PMI-related registers. It does not implement executable logic; its job is to let C driver code extract and compose register fields without hard-coded numeric masks at call sites.

The file pairs with MP 11.0 offset headers such as `mp_11_0_offset.h`. Offset headers identify which MMIO or SMN register to read or write, while this header defines the valid fields inside those registers. Consumers include PSP and SMU code paths such as `amdgpu/psp_v11_0.c`, `pm/swsmu/smu11/smu_v11_0.c`, `pm/swsmu/smu11/navi10_ppt.c`, and `pm/swsmu/smu11/sienna_cichlid_ppt.c`.

## Important APIs, Types, and Macros

This file exports macros, not C APIs or types. The major macro groups are:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`, each exposing `CONTENT` at shift `0x0` with mask `0xFFFFFFFFL`.
- `MP0_SMN_ACTIVE_FCN_ID`, exposing `VFID` bits `0:4` and `VF` at bit `31`.
- `MP0_SMN_IH_CREDIT`, `MP0_SMN_IH_SW_INT`, and `MP0_SMN_IH_SW_INT_CTRL`, exposing interrupt-credit, software-interrupt ID/valid, mask, and acknowledge fields.
- `MP1_FIRMWARE_FLAGS`, whose `INTERRUPTS_ENABLED` bit is used to decide whether MP1 firmware has enabled interrupts.
- `MP1_PUB_SCRATCH0` through `MP1_PUB_SCRATCH3`, `MP1_EXT_SCRATCH0` through `MP1_EXT_SCRATCH7`, and `MP1_FPS_CNT`.
- `MP1_C2PMSG_0` through `MP1_C2PMSG_103`, `MP1_P2CMSG_0` through `MP1_P2CMSG_3`, `MP1_P2CMSG_INTEN`, `MP1_P2CMSG_INTSTS`, `MP1_P2SMSG_0` through `MP1_P2SMSG_3`, `MP1_P2SMSG_INTSTS`, and `MP1_S2PMSG_0`.
- `MP1_ACTIVE_FCN_ID`, `MP1_IH_CREDIT`, `MP1_IH_SW_INT`, `MP1_IH_SW_INT_CTRL`, and `MP1_PUB_CTRL`.
- Mirrored `MP1_SMN_*` versions of the SMN mailbox, interrupt, FPS, public-control, and external-scratch register fields.
- `MP1_PMI_3_START__ENABLE_MASK`, `MP1_PMI_3_START__ENABLE__SHIFT`, `MP1_PMI_3_FIFO__DEPTH_MASK`, and `MP1_PMI_3_FIFO__DEPTH__SHIFT`, which support SMU trace-buffer setup in Sienna Cichlid code.

The header has 637 `#define` entries. Field macros follow the AMD register-helper naming expected by `REG_GET_FIELD(reg, REGISTER, FIELD)`, which expands to `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.

## Control Flow and Runtime Behavior

There is no runtime control flow in the header. It participates in runtime control flow when included by driver code that reads, writes, or polls MP registers.

Key observed integrations:

- `psp_v11_0.c` includes this header with `mp_11_0_offset.h` while selecting PSP firmware flows for MP0 versions including 11.0.x and 11.5.x.
- `smu_v12_0.c` has a similar firmware-status check pattern for later MP headers: read `smnMP1_FIRMWARE_FLAGS`, mask `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`, shift by `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED__SHIFT`, and return success only when firmware interrupts are enabled. MP 11 SMU code uses the same generated-mask idiom.
- `sienna_cichlid_ppt.c` reads `MP1_PMI_3_START` and `MP1_PMI_3_FIFO` via `RREG32_PCIE(MP1_Public | smn...)`, then extracts `ENABLE` and `DEPTH` using this header to configure the STB buffer.

## State and Persistence Behavior

The file contains immutable compile-time constants. It does not allocate memory, persist state, or mutate device state on its own.

The state it describes is hardware/firmware-visible register state:

- SMU command mailboxes are represented by C2P/P2C/P2S/S2P message registers.
- Firmware readiness and interrupt state is represented by `MP1_FIRMWARE_FLAGS` and interrupt-control registers.
- STB/PMI state is represented by `MP1_PMI_3_START` and `MP1_PMI_3_FIFO`.

Incorrect masks can cause callers to misinterpret persistent firmware mailbox state or program hardware control bits incorrectly.

## Dependencies and Integration Points

The header depends only on preprocessor inclusion order and matching offset/register names. It is normally used with:

- `mp/mp_11_0_offset.h` or `asic_reg/mp/mp_11_0_offset.h` for register addresses such as `mm...` or `smn...`.
- AMDGPU register helpers including `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and display-core `REG_READ`/`REG_WRITE` wrappers.
- MP1 public base constants such as `MP1_Public`.

The field naming must stay synchronized with the register names that call sites pass to helper macros. A rename from `INT_ACK` to an older spelling such as `SW_INT_ACK`, or from `MP1_PMI_3_FIFO__DEPTH` to a different field, would break builds or produce wrong register operations.

## Risks and Edge Cases

- Generated headers are easy to treat as inert, but a one-bit shift or mask error can break PSP boot, SMU firmware readiness checks, clock-management commands, interrupt delivery, or STB tracing.
- The `L` suffix is used on masks, so consumers rely on C integer promotion. On the Linux targets involved this is normal, but new code should still keep values in `uint32_t`-style paths.
- The file mixes broad full-register mailbox fields with narrow control/status fields. Auditing only the repeated C2PMSG macros can miss special fields near the end, especially `MP1_PMI_3_*`.
- `MP1_PUB_CTRL__RESET_MASK` and `MP1_PMI_3_START__ENABLE_MASK` describe direct control bits; writes using these fields should be limited to hardware sequences that own MP1 state.
- The header guard is `_mp_11_0_2_SH_MASK_HEADER`, while the filename is `mp_11_0_sh_mask.h`. That mismatch is a generated-artifact detail but can be confusing during manual audits.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration signals:

- Build AMDGPU objects that include this header, especially `psp_v11_0.o`, `smu_v11_0.o`, `navi10_ppt.o`, and `sienna_cichlid_ppt.o`.
- Verify `REG_GET_FIELD(..., MP1_PMI_3_START, ENABLE)` and `REG_GET_FIELD(..., MP1_PMI_3_FIFO, DEPTH)` compile and produce expected STB buffer sizing on Sienna Cichlid-capable hardware.
- Exercise SMU/PSP initialization paths and check that firmware readiness, interrupt-enabled checks, and mailbox responses complete without timeout.
- Runtime dmesg signals include PSP firmware loading errors, SMU response timeouts, clock-management failures, and STB initialization logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_offset.h

## Purpose

`mp_11_5_0_offset.h` is the generated register-address map for MP/SMU generation 11.5.0. It defines `mm...` register offsets and matching `..._BASE_IDX` values for MP0 and MP1 SMN register blocks. The display clock-manager path for DCN 3.01 includes it to calculate addresses for Vangogh SMU mailbox communication.

The file is address-only. Field semantics come from `mp_11_5_0_sh_mask.h`; code combines both headers through register helper macros.

## Important APIs, Types, and Macros

This header exports 367 preprocessor defines. For each `mm...` register offset there is a `..._BASE_IDX`, all observed as `0`.

Major register ranges:

- `mmMP0_SMN_C2PMSG_32` through `mmMP0_SMN_C2PMSG_103`, mapped contiguously from `0x0060` through `0x00a7`.
- `mmMP0_SMN_IH_CREDIT`, `mmMP0_SMN_IH_SW_INT`, and `mmMP0_SMN_IH_SW_INT_CTRL`, mapped at `0x00c1`, `0x00c2`, and `0x00c3`.
- `mmMP1_SMN_C2PMSG_32` through `mmMP1_SMN_C2PMSG_127`, mapped contiguously from `0x0260` through `0x02bf`.
- `mmMP1_SMN_IH_CREDIT`, `mmMP1_SMN_IH_SW_INT`, `mmMP1_SMN_IH_SW_INT_CTRL`, and `mmMP1_SMN_FPS_CNT`, mapped at `0x02c1` through `0x02c4`.
- `mmMP1_SMN_EXT_SCRATCH0` through `mmMP1_SMN_EXT_SCRATCH7`, mapped from `0x03c0` through `0x03c7`.

The consumer-facing API is the macro naming convention. Display code defines:

```c
#define REG(reg_name) (MP0_BASE.instance[0].segment[mm ## reg_name ## _BASE_IDX] + mm ## reg_name)
```

That makes `REG_READ(MP1_SMN_C2PMSG_91)` resolve through `mmMP1_SMN_C2PMSG_91` and `mmMP1_SMN_C2PMSG_91_BASE_IDX`.

## Control Flow and Runtime Behavior

There is no executable control flow in this header. Runtime behavior appears in consumers that use these offsets for SMU command mailboxes.

The direct observed consumer is `display/dc/clk_mgr/dcn301/dcn301_smu.c`, which:

- Polls `MP1_SMN_C2PMSG_91` until the SMU response is no longer busy.
- Writes `MP1_SMN_C2PMSG_91` to clear the response register.
- Writes a parameter to `MP1_SMN_C2PMSG_83`.
- Writes a VBIOS SMC message ID to `MP1_SMN_C2PMSG_67`.

The address constants in this file therefore define the physical mailbox endpoints for display clock, DCFCLK, DPPCLK, FCLK, watermarks, and display-idle-optimization messages on the supported ASIC.

## State and Persistence Behavior

The header stores no software state. The offsets point at hardware registers whose contents persist according to SMU/firmware and hardware reset rules.

Stateful hardware concepts described by the map include:

- MP0 and MP1 command-to-processor mailboxes.
- MP1 response/parameter/message registers used by display SMU command sequences.
- MP1 interrupt and credit registers.
- MP1 external scratch registers, which can be used as firmware-driver scratch communication state.

Because all `_BASE_IDX` values are `0`, callers expect the MP0 base segment array entry `0` to be valid for these registers.

## Dependencies and Integration Points

Integration depends on:

- `mp_11_5_0_sh_mask.h` for fields inside the same registers.
- ASIC IP offset headers such as `vangogh_ip_offset.h`, which define `MP0_BASE` segment layout.
- Display register helpers in `reg_helper.h`, including `REG_READ` and `REG_WRITE`.
- SMU/VBIOS message protocol constants local to `dcn301_smu.c`.

The offsets are not self-validating. If the map is used with a mismatched ASIC base table or with MP 11.0/12.0 field headers, the code can compile while targeting the wrong registers.

## Risks and Edge Cases

- `MP1_SMN_C2PMSG_104` through `MP1_SMN_C2PMSG_127` exist in 11.5.0 but not in the 12.0.0 offset header researched in this work item. Cross-generation reuse must not assume identical mailbox depth.
- The file has no active-function-ID or public-control offsets; those fields exist in other MP generations or mask files, so consumers must not infer address availability from similarly named mask macros elsewhere.
- Register offsets are small `mm` offsets, not full SMN absolute addresses. They must be combined with the correct base segment.
- Mailbox register mistakes are high impact: polling the wrong response register can look like a permanent SMU busy timeout, while writing the wrong trigger register can send no command or a malformed command.

## Test Signals

Useful signals include:

- Build `display/dc/clk_mgr/dcn301/dcn301_smu.o` with this header and `mp_11_5_0_sh_mask.h`.
- Exercise Vangogh/DCN301 display clock changes and inspect SMU logs for response values other than busy.
- Check that `REG_READ(MP1_SMN_C2PMSG_91)`, `REG_WRITE(MP1_SMN_C2PMSG_83, ...)`, and `REG_WRITE(MP1_SMN_C2PMSG_67, ...)` access the expected addresses in register traces.
- Hardware symptoms of bad offsets include display clock programming failure, repeated `SMU Response was not OK` messages, hangs in wait loops, or failed watermark/table transfer messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_sh_mask.h

## Purpose

`mp_11_5_0_sh_mask.h` is the generated field mask/shift companion to `mp_11_5_0_offset.h`. It describes the bit layout of MP0/MP1 SMN and MP1 public CRU registers for MP 11.5.0 hardware. It is used by display and SMU-facing code to extract mailbox response fields, interrupt state, firmware flags, and scratch/control fields without local numeric bit constants.

The file is preprocessor-only and has no functions or types. Its correctness is part of the ABI between AMDGPU driver code and the GPU firmware/hardware register map.

## Important APIs, Types, and Macros

The header exports 617 `#define` entries. Major exported groups are:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`, each with full-width `CONTENT` fields.
- `MP0_SMN_IH_CREDIT`, `MP0_SMN_IH_SW_INT`, and `MP0_SMN_IH_SW_INT_CTRL`, with the same `CREDIT_VALUE`, `CLIENT_ID`, `ID`, `VALID`, `INT_MASK`, and `INT_ACK` field pattern as nearby MP generations.
- `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_103`, again full-width `CONTENT` fields.
- `MP1_SMN_IH_CREDIT`, `MP1_SMN_IH_SW_INT`, `MP1_SMN_IH_SW_INT_CTRL`, `MP1_SMN_FPS_CNT`, and `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH7`.
- `MP1_CRU1_MP1_FIRMWARE_FLAGS`, `MP1_CRU1_MP1_PUB_SCRATCH0` through `MP1_CRU1_MP1_PUB_SCRATCH3`, `MP1_CRU1_MP1_C2PMSG_0` through `MP1_CRU1_MP1_C2PMSG_103`, P2C/P2S/S2P message fields, interrupt status fields, and external scratch fields under the `mp_SmuMp1Pub_CruDec` address block.

Most mailbox and scratch fields are `CONTENT` or `DATA` at shift `0x0` with mask `0xFFFFFFFFL`. Important narrow fields include:

- `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` and `...__SHIFT`.
- `MP1_CRU1_MP1_P2CMSG_INTEN__INTEN_MASK`.
- `MP1_CRU1_MP1_P2CMSG_INTSTS__INTSTS0..3_MASK`.
- `MP1_CRU1_MP1_P2SMSG_INTSTS__INTSTS0..3_MASK`.
- interrupt helper fields for MP0/MP1 SMN `IH_*` registers.

## Control Flow and Runtime Behavior

There is no local control flow. Runtime behavior is in consuming SMU/display code.

The direct observed consumer, `display/dc/clk_mgr/dcn301/dcn301_smu.c`, includes this header with `mp_11_5_0_offset.h`, defines `FN(reg_name, field)` as `FD(reg_name##__##field)`, and uses display register helpers to wait for SMU mailbox responses and send messages. The code path mainly reads/writes full `CONTENT` registers, so the field definitions matter both for helper compatibility and any future masked updates.

The CRU1 `FIRMWARE_FLAGS`, interrupt status, and scratch definitions also make the header usable in broader MP1 firmware-status and interrupt paths if this ASIC generation needs those checks.

## State and Persistence Behavior

The header itself is stateless. It describes device state in:

- command, response, and parameter mailboxes;
- firmware interrupt-enabled state;
- interrupt enable/status/ack bits;
- public and external scratch registers;
- frame or frequency-related counters such as `FPS_CNT`.

Mailbox state is inherently persistent across a command transaction until firmware or driver code updates the relevant register. Full-width `CONTENT` masks mean callers can preserve or replace entire register payloads.

## Dependencies and Integration Points

This header must be synchronized with:

- `mp_11_5_0_offset.h`, which provides the `mmMP0_SMN_*` and `mmMP1_SMN_*` offsets.
- Display-core register-helper macros `FD`, `REG_READ`, `REG_WRITE`, and any masked update helpers that derive field names from `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- Firmware message protocols in code such as `dcn301_smu.c`, where C2PMSG indices have semantic meaning: response register `91`, parameter register `83`, and message trigger register `67`.

The CRU1 macro namespace is distinct from the SMN namespace. Consumers must pass the exact register name expected by the helper macro; `MP1_SMN_C2PMSG_91` and `MP1_CRU1_MP1_C2PMSG_91` are different macro prefixes.

## Risks and Edge Cases

- Field-header and offset-header drift is the main risk. A register can compile with a field name from one block and an address from another if code mixes generations or namespaces incorrectly.
- The file contains MP1 CRU public fields that are not represented by the direct `mmMP1_SMN_*` offset set in the 11.5.0 offset header. Those fields require the correct address source from another matching offset namespace.
- Full-width masks hide semantic constraints. For example, C2PMSG contents are 32-bit payloads, but firmware protocols may accept only certain command or parameter values.
- Interrupt status fields are bit-granular; using the full register as a payload field where status bits are expected could clear or acknowledge unintended bits depending on hardware write semantics.
- The header is generated and repetitive, so manual edits are especially risky. Format deviations could break macro-generation assumptions or make future diffs difficult.

## Test Signals

Validation signals include:

- Build display DCN301 SMU code and any MP 11.5.0 firmware-status consumers with both offset and mask headers.
- Exercise `dcn301_smu_wait_for_response()` and message-send paths for display clock, DPP clock, DPREF clock, DCFCLK, FCLK, and table-transfer operations.
- Confirm that `FN(MP1_SMN_C2PMSG_91, CONTENT)`-style macro expansion succeeds if masked helpers are used.
- Runtime failures usually surface as SMU response busy timeouts, unknown/rejected VBIOS SMC messages, bad display clock programming, or missing firmware-interrupt readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_offset.h

## Purpose

`mp_12_0_0_offset.h` is the generated register-address map for MP/SMU generation 12.0.0. It defines MP0 and MP1 SMN `mm...` offsets and `_BASE_IDX` values used by Renoir-era SMU and display code to access mailbox, interrupt, and firmware-status registers.

Like other AMD ASIC register offset headers, it contains no field definitions. It must be used with `mp_12_0_0_sh_mask.h` or equivalent matching field headers for bit extraction and masked writes.

## Important APIs, Types, and Macros

The header exports 303 `#define` entries. For every register offset macro there is a matching `_BASE_IDX`, with all observed base indexes set to `0`.

Major ranges:

- `mmMP0_SMN_C2PMSG_32` through `mmMP0_SMN_C2PMSG_103`, mapped from `0x0060` through `0x00a7`.
- `mmMP0_SMN_IH_CREDIT`, `mmMP0_SMN_IH_SW_INT`, and `mmMP0_SMN_IH_SW_INT_CTRL`, mapped at `0x00c1` through `0x00c3`.
- `mmMP1_SMN_C2PMSG_32` through `mmMP1_SMN_C2PMSG_103`, mapped from `0x0260` through `0x02a7`.
- `mmMP1_SMN_IH_CREDIT`, `mmMP1_SMN_IH_SW_INT`, `mmMP1_SMN_IH_SW_INT_CTRL`, and `mmMP1_SMN_FPS_CNT`, mapped at `0x02c1` through `0x02c4`.

Unlike `mp_11_5_0_offset.h`, this header does not define `mmMP1_SMN_C2PMSG_104` through `mmMP1_SMN_C2PMSG_127` or MP1 external scratch offsets.

## Control Flow and Runtime Behavior

The header has no executable control flow. Consumers define the runtime behavior.

Observed integrations:

- `pm/swsmu/smu12/smu_v12_0.c` includes this header with `mp_12_0_0_sh_mask.h`, reads MP1 firmware flags through a PCIE/SMN path, and uses the matching mask header to test `INTERRUPTS_ENABLED`.
- `display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c` includes this header and uses a `REG(reg_name)` macro that expands `MP0_BASE.instance[0].segment[mm ## reg_name ## _BASE_IDX] + mm ## reg_name`. Its SMU mailbox transaction polls `MP1_SMN_C2PMSG_91`, writes a parameter to `MP1_SMN_C2PMSG_83`, and triggers the message through `MP1_SMN_C2PMSG_67`.
- `amdgpu/psp_v12_0.c` includes this header for PSP generation 12 register addressing.

## State and Persistence Behavior

The header does not store state. It names hardware registers that contain:

- MP0 and MP1 C2P mailbox payloads;
- MP1 firmware/SMU command parameters, command IDs, and responses;
- interrupt credit, software interrupt, interrupt mask, and interrupt acknowledge registers;
- MP1 FPS counter state.

Mailbox and interrupt register contents are persistent hardware state until firmware, the driver, or reset changes them. The constants in this header are therefore part of the driver-firmware communication contract.

## Dependencies and Integration Points

This file depends on matching use with:

- `mp_12_0_0_sh_mask.h` for fields such as `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` and SMN C2P message `CONTENT`.
- ASIC base-offset headers such as `renoir_ip_offset.h`, which define `MP0_BASE`.
- Register helpers such as `REG_READ`, `REG_WRITE`, `RREG32_PCIE`, and `RREG32_SOC15`.
- SMU common helpers in `smu_cmn` and display VBIOS SMC message protocols.

The header uses the older `mm` naming convention. Later MP 13 headers may use `reg...` names, so cross-generation code must respect the expected helper macro family.

## Risks and Edge Cases

- The MP1 mailbox range stops at C2PMSG 103. Reusing 11.5.0 code that expects C2PMSG 104-127 would fail at compile time or require a different offset header.
- All base indexes are `0`; if an ASIC base table changes, this generated map must change with it.
- Display mailbox code relies on hard-coded semantic indices, especially response `91`, parameter `83`, and trigger `67`. Any offset error can create silent SMU command loss or long busy waits.
- Offset headers do not encode access width, read/write side effects, or firmware protocol restrictions. Call sites must know whether a register is safe to poll, write, clear, or acknowledge.
- Mixing this MP 12.0.0 offset header with MP 11.x or 13.x field headers can compile in limited cases but target incorrect hardware semantics.

## Test Signals

Useful validation signals include:

- Build `smu_v12_0.o`, `psp_v12_0.o`, and `rn_clk_mgr_vbios_smu.o`.
- Exercise Renoir display clock programming paths that call the VBIOS SMU message helpers.
- Confirm firmware-status checks in `smu_v12_0_check_fw_status()` return success when MP1 firmware has enabled interrupts.
- Runtime signs of bad offsets include `-EIO` from firmware-status checks, failed PSP initialization, repeated SMU busy responses, display clock failures, and rejected or unknown VBIOS SMC messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_offset.h -->
