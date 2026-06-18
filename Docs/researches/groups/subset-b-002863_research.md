# Research: subset-b-002863

Grouped research report for AMD GPU MP 13.0.x register definition headers. Each section is delimited for reconciliation into the mapped source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_2_sh_mask.h

## Purpose

This generated AMD register header describes bit shifts and masks for the MP 13.0.2 management processor register interface. It is the field-definition companion to the MP 13.0.2 offset header and is consumed by PSP and display/SMU code that needs symbolic access to MP0 and MP1 mailbox registers. The file does not implement executable logic. Its purpose is to make register field extraction and construction stable across driver code by naming each field as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

The file is organized by hardware address block. `mp_SmuMp0_SmnDec` covers MP0 SMN client-to-processor message (`C2PMSG`) registers and interrupt helper registers. `mp_SmuMp1Pub_CruDec` contributes `MP1_FIRMWARE_FLAGS`. `mp_SmuMp1_SmnDec` covers MP1 SMN `C2PMSG` registers, interrupt helper registers, FPS counter, and a small scratch register range.

## Important APIs, Types, And Macros

The public surface is entirely C preprocessor macros guarded by `_mp_13_0_2_SH_MASK_HEADER`. There are no functions, structs, enums, or data objects.

The bulk of the file maps `C2PMSG` payload registers to one full-width `CONTENT` field with shift `0x0` and mask `0xFFFFFFFFL`. MP0 defines `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`, plus `MP0_SMN_C2PMSG_109` and a specialized `MP0_SMN_C2PMSG_126`. MP1 defines `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_127`.

The most semantically rich register in this file is `MP0_SMN_C2PMSG_126`. Unlike the surrounding full-width mailbox payload fields, it exposes decoded boot/error fields: `GPU_ERR_MEM_TRAINING`, `GPU_ERR_FW_LOAD`, WAFL/XGMI/USR CP/USR DP link-training errors, HBM test/BIST errors, `SOCKET_ID`, `AID_ID`, `HBM_ID`, and the top-bit `BOOT_STATUS`. These masks allow diagnostic code to classify MP0 boot status instead of treating the register as an opaque 32-bit value.

Interrupt helper fields are defined for both MP0 and MP1. `*_SMN_IH_CREDIT` has `CREDIT_VALUE` in bits 1:0 and `CLIENT_ID` at bits 23:16. `*_SMN_IH_SW_INT` exposes interrupt `ID` and `VALID`. `*_SMN_IH_SW_INT_CTRL` exposes `INT_MASK` and `INT_ACK`. `MP1_FIRMWARE_FLAGS` defines `INTERRUPTS_ENABLED` bit 0 and a reserved remainder. `MP1_SMN_FPS_CNT` and `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH7` are full-width data fields.

Inventory signals: the header has 204 `__SHIFT` definitions and 206 `_MASK` definitions. The mismatch is expected because `MP1_FIRMWARE_FLAGS__RESERVED_MASK` and similar fields are not paired with executable code, only macro definitions.

## Control Flow

There is no runtime control flow. The only compile-time control flow is the include guard. At runtime, control flow lives in consumers such as `amdgpu/psp_v13_0.c` and `display/dc/clk_mgr/dcn31/dcn31_smu.c`, where the macros are used with register access helpers. For example, PSP code polls or writes `regMP0_SMN_C2PMSG_35`, `regMP0_SMN_C2PMSG_36`, `regMP0_SMN_C2PMSG_64`, `regMP0_SMN_C2PMSG_67`, `regMP0_SMN_C2PMSG_81`, and related registers during bootloader handshakes, firmware component loading, ring setup, USB-PD access, SPI ROM operations, and GBR interrupt handling. DCN 3.1 display SMU code uses MP1 `C2PMSG` registers as a command mailbox: wait on a response register, clear it to busy, write a parameter, write a message id, and then poll for completion.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. The macros describe hardware-backed state. Reads from the described registers reflect PSP/SMU firmware state, bootloader status, mailbox command/response state, interrupt credit state, and scratch/FPS values. Writes performed by consumers are persistent only in the hardware register sense until firmware or hardware overwrites them. The risk profile is therefore hardware-state oriented: incorrect masks or shifts can make the driver misread boot status, acknowledge/mask interrupts incorrectly, or send malformed mailbox payloads.

## Dependencies

The file depends only on the C preprocessor. It is intended to be included with the matching MP 13.0.2 offset header so register addresses and field masks are available together. Consumers rely on AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_READ`, `REG_WRITE`, and field helpers such as `FD`/`FN` in display code. It is also tightly coupled to generated ASIC register naming conventions under `drivers/gpu/drm/amd/include/asic_reg/mp/`.

## Integration Points

Direct include sites include `amdgpu/psp_v13_0.c` and `display/dc/clk_mgr/dcn31/dcn31_smu.c`; `pm/swsmu/smu13/aldebaran_ppt.c` includes the matching MP 13.0.2 offset header. The PSP path uses the MP0 mailbox definitions for security processor firmware loading, bootloader readiness, ring creation/destruction, firmware version queries, and update/status commands. The display clock manager uses the MP1 mailbox definitions for VBIOS SMU messages such as clock changes, table transfers, and power-management requests.

## Risks

The central risk is silent hardware misprogramming. These macros compile to constants, so mistakes usually appear only as boot failures, firmware timeouts, missing interrupts, incorrect diagnostics, or display clock/SMU command failures on affected ASICs. `MP0_SMN_C2PMSG_126` is especially sensitive because it decodes multiple boot error causes. Any drift between this generated header and the hardware specification can produce misleading RAS or boot status information. Another risk is cross-version reuse: MP 13.0.2 shares many macro names with other MP versions, but exact register availability and base indices can differ.

## Test Signals

Useful validation signals include successful AMDGPU build coverage for include compatibility, PSP boot without `psp_wait_for` timeout messages, correct firmware load and ring creation on MP 13.0.2 hardware, and successful DCN 3.1 SMU message exchange for display clock operations. Runtime logs around PSP bootloader readiness, SOS sign-of-life, memory-training or firmware-load errors, SMU timeout callbacks, and interrupt enablement are the practical tests. Static tests should compare the generated shifts/masks against AMD register XML/spec output and verify that consumer code includes the version-matched offset and mask headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_offset.h

## Purpose

This generated header provides the MP 13.0.4 register offsets and base-index selectors for the AMD management processor register interface. It is the address companion to `mp_13_0_4_sh_mask.h`. Consumers use its `reg...` macros to build MMIO/SMN addresses through SOC15 AMDGPU helpers, while the matching mask header describes bit-level layout.

The file covers two address blocks: `mp_SmuMp0_SmnDec` and `mp_SmuMp1_SmnDec`. The MP0 block exposes C2PMSG mailboxes 32 through 127 plus MP0 interrupt helper registers. The MP1 block exposes C2PMSG mailboxes 32 through 103, MP1 interrupt helper registers, `MP1_SMN_FPS_CNT`, and `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH7`.

## Important APIs, Types, And Macros

The public surface is C preprocessor register-address macros guarded by `_mp_13_0_4_OFFSET_HEADER`. Each register has two definitions: `reg<NAME>` for the block-relative register offset and `reg<NAME>_BASE_IDX` for the base segment index. There are no functions, types, enums, or variables.

Important MP0 offsets include `regMP0_SMN_C2PMSG_32` at `0x0060`, continuing sequentially through `regMP0_SMN_C2PMSG_127` at `0x00bf`, with interrupt helper registers at `0x00c1` through `0x00c3`. Important MP1 offsets include `regMP1_SMN_C2PMSG_32` at `0x0260`, continuing through `regMP1_SMN_C2PMSG_103` at `0x02a7`, then MP1 interrupt helper registers at `0x02c1` through `0x02c3`, `regMP1_SMN_FPS_CNT` at `0x02c4`, and MP1 scratch registers `0x0340` through `0x0347`.

All base indices in this file are `1`. That is a key integration detail: display and SOC15 helpers use the index to choose the correct segment from an IP base table. A consumer using an MP 13.0.5-style base table or base index would address the wrong segment for this ASIC revision.

Inventory signal: the header contains 366 register/base-index macro definitions.

## Control Flow

There is no executable control flow. The include guard is the only compile-time gate. Runtime control flow appears in consumers that combine these constants with AMDGPU register helpers. The primary direct consumer is `amdgpu/psp_v13_0_4.c`, which includes both this offset header and `mp_13_0_4_sh_mask.h`. It waits for the bootloader on `MP0_SMN_C2PMSG_35`, writes firmware buffer addresses to `MP0_SMN_C2PMSG_36`, checks SOS sign-of-life through `MP0_SMN_C2PMSG_81`, and uses mailbox registers such as `MP0_SMN_C2PMSG_64`, `67`, `69`, `70`, `71`, `101`, `102`, and `103` for ring and command traffic.

## State And Persistence Behavior

The header stores no state. It describes the address map for hardware state owned by MP0/MP1 firmware and the GPU register fabric. Consumer reads and writes alter or observe firmware mailboxes, bootloader state, command responses, interrupt helper registers, and scratch data. Persistence is limited to hardware register lifetime. A bad offset can persistently disrupt a boot sequence during a driver session because every subsequent poll or write targets the wrong register.

## Dependencies

The file depends only on the C preprocessor, but it is meaningful only with the AMDGPU register access framework. Consumer code usually passes these `reg...` macros to `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, or local display `REG()` macros that add a base segment selected by `reg..._BASE_IDX`. It is generated in the same style as neighboring `mp_13_0_x_offset.h` files and should be treated as ASIC specification data rather than hand-maintained logic.

## Integration Points

The direct include site found for this exact file is `drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.c`. That PSP implementation declares firmware modules for PSP 13.0.4 and uses MP0 mailbox addresses for TOC/TA initialization, bootloader component loading, ring stop/create, register programming, and command response handling. The matching mask header is included in the same file, though most PSP accesses use full-register command values and response masks from broader PSP definitions rather than field extraction from this header.

## Risks

The base index of `1` is the highest-value risk. It differs from MP 13.0.5, where equivalent registers use base index `0`. Any copy/paste or include mismatch between ASIC revisions can compile cleanly but address the wrong register segment. Another risk is mailbox range mismatch: this header provides MP0 C2PMSG 32-127 but MP1 C2PMSG only 32-103, so consumers must not assume identical MP0/MP1 ranges. Because these constants are generated, manual edits risk diverging from AMD hardware definitions.

## Test Signals

Compile-time tests should verify the PSP 13.0.4 translation unit builds with this header and the matching mask header. Runtime validation requires PSP 13.0.4 hardware or emulation: bootloader wait should complete, SOS sign-of-life should become nonzero, firmware component loading should succeed, and ring setup/teardown should avoid mailbox timeouts. Static comparison against the source register database should confirm sequential MP0/MP1 C2PMSG offsets and base index `1` for every register in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_sh_mask.h

## Purpose

This generated header defines bit shifts and masks for MP 13.0.4 register fields. It pairs with `mp_13_0_4_offset.h`: the offset header tells consumers where each register is, while this header tells them how to interpret or compose values inside those registers. It is part of AMDGPU's ASIC register-definition layer and contains no executable implementation.

The file is organized into `mp_SmuMp0_SmnDec` and `mp_SmuMp1_SmnDec`. MP0 field macros cover C2PMSG 32-103 and MP0 interrupt helper registers. MP1 field macros cover C2PMSG 32-127, MP1 interrupt helper registers, FPS count, and MP1 external scratch registers 0-7.

## Important APIs, Types, And Macros

The public API is a set of macros guarded by `_mp_13_0_4_SH_MASK_HEADER`. There are no C types or functions. Most `C2PMSG` registers are represented as a single full-width `CONTENT` field at shift `0x0` with mask `0xFFFFFFFFL`. This matches their mailbox role: command IDs, parameters, responses, ring addresses, and firmware-defined payloads are usually treated as opaque 32-bit words by the PSP or SMU firmware protocol.

The interrupt helper fields mirror the MP 13.0.2 shape. `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT` expose `CREDIT_VALUE` and `CLIENT_ID`. `*_IH_SW_INT` exposes `ID` and `VALID`; `*_IH_SW_INT_CTRL` exposes `INT_MASK` and `INT_ACK`. `MP1_SMN_FPS_CNT__COUNT` and `MP1_SMN_EXT_SCRATCH0..7__DATA` are full-width fields.

Compared with MP 13.0.2, this header lacks the specialized MP0 `C2PMSG_126` boot/error subfields and lacks `MP1_FIRMWARE_FLAGS`. Compared with MP 13.0.5, it has only scratch registers 0-7 and no MP1 public firmware-flags block.

Inventory signal: the header contains 189 shift definitions and 191 mask definitions.

## Control Flow

There is no runtime control flow. The include guard prevents multiple definition. Runtime control flow belongs to consumers such as `amdgpu/psp_v13_0_4.c`. That code uses the matching offset header heavily for mailbox polling and writes. It includes this mask header to keep version-specific field definitions available for any field-based register operations and to match the standard PSP include pattern used by other PSP versions.

The relevant consumer control pattern is mailbox-oriented: wait for a bootloader-ready bit in an MP0 C2PMSG register, write a firmware memory address to another C2PMSG register, write a command value, delay or poll, then read a response or sign-of-life register. The field macros here are the symbolic bridge if code needs to mask or shift one of those response values.

## State And Persistence Behavior

This file has no internal state. The state it describes is hardware state inside MP0/MP1 mailbox and interrupt registers. Consumers may observe command responses, interrupt state, scratch data, and firmware counters. Writes are hardware side effects, not software persistence. Since most C2PMSG fields are full-width content, consumers are responsible for protocol-specific interpretation outside this header.

## Dependencies

The file depends only on the preprocessor but should be used with `mp_13_0_4_offset.h` and AMDGPU register access helpers. Consumers often use offsets with `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and PSP wait helpers. If field helper macros such as `FD`/`FN` are used, they depend on the naming convention provided here.

## Integration Points

The direct exact include site is `amdgpu/psp_v13_0_4.c`, which implements PSP 13.0.4 microcode loading and ring command handling. Although the visible register operations in that file primarily use register offsets and broader PSP response masks, this header supplies the version-matched field view for MP0/MP1 mailbox and interrupt registers. It is also part of the larger generated MP register header family, so tooling or driver additions can include it when adding field-based access for 13.0.4.

## Risks

The main risk is version skew with the offset header or hardware specification. Since the masks are mostly full-width, many mistakes would not be caught by build tests. Missing specialized fields are also a risk for maintainers: code ported from MP 13.0.2 must not assume `MP0_SMN_C2PMSG_126__GPU_ERR_*` definitions exist here. Code ported from MP 13.0.5 must not assume `MP1_FIRMWARE_FLAGS` or scratch registers beyond 7 exist here. Incorrect interrupt masks could cause lost, stuck, or falsely acknowledged firmware interrupts.

## Test Signals

Build coverage confirms macro availability and include compatibility. Runtime PSP 13.0.4 smoke tests should show firmware load, bootloader wait, SOS sign-of-life, and ring operations succeeding without C2PMSG timeouts. Static tests should compare the generated field list against the MP 13.0.4 register database, especially the absence of `MP1_FIRMWARE_FLAGS`, the MP1 scratch range, and the interrupt helper bit definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_5_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_5_offset.h

## Purpose

This generated header provides MP 13.0.5 register offsets and base-index selectors for AMDGPU MP0/MP1 register access. It is an address map, not executable code. Consumers use `reg...` constants and `reg..._BASE_IDX` selectors with AMDGPU register-access helpers to talk to PSP/SMU firmware through mailbox registers and related MP1 status/scratch registers.

The header covers `mp_SmuMp0_SmnDec`, `mp_SmuMp1_SmnDec`, and `mp_SmuMp1Pub_CruDec`. MP0 includes C2PMSG 32-103 and MP0 interrupt helper registers. MP1 includes C2PMSG 32-127, MP1 interrupt helper registers, `MP1_SMN_FPS_CNT`, an extended scratch range, and `MP1_FIRMWARE_FLAGS`.

## Important APIs, Types, And Macros

The public surface is a set of preprocessor macros guarded by `_mp_13_0_5_OFFSET_HEADER`. Every register macro has an offset and base-index macro. There are no functions, structs, enums, or stateful definitions.

MP0 offsets start at `regMP0_SMN_C2PMSG_32` `0x0060` and continue sequentially through `regMP0_SMN_C2PMSG_103` `0x00a7`, followed by `regMP0_SMN_IH_CREDIT` `0x00c1`, `regMP0_SMN_IH_SW_INT` `0x00c2`, and `regMP0_SMN_IH_SW_INT_CTRL` `0x00c3`. MP1 offsets start at `regMP1_SMN_C2PMSG_32` `0x0260` and continue through `regMP1_SMN_C2PMSG_127` `0x02bf`; MP1 interrupt helpers are at `0x02c1` through `0x02c3`; `regMP1_SMN_FPS_CNT` is `0x02c4`.

The scratch range is larger than MP 13.0.4: it includes `regMP1_SMN_EXT_SCRATCH0` through `8`, skips `9`, then includes `10` through `31`, with offsets `0x0340` through `0x035f` except the missing `0x0349` entry. `regMP1_FIRMWARE_FLAGS` is in the MP1 public block at `0xbee009`.

All base indices in this file are `0`. This is a critical distinction from MP 13.0.4, where analogous offsets use base index `1`.

Inventory signal: the header contains 414 register/base-index macro definitions.

## Control Flow

There is no runtime control flow. Runtime behavior appears in display/SMU consumers that include this file. `display/dc/clk_mgr/dcn314/dcn314_smu.c` includes it and defines local MP1 base segment constants with a `REG(reg_name)` macro that selects `BASE(reg..._BASE_IDX) + reg...`. It uses MP1 C2PMSG registers 67, 83, and 91 to send VBIOS SMU messages and poll responses. `display/dc/clk_mgr/dcn315/dcn315_smu.c` also includes it and uses a local `MP0_BASE` segment table, then performs a different mailbox flow through MP1 C2PMSG 37 and 38 plus an indexed write to `mmMP1_C2PMSG_3`.

## State And Persistence Behavior

The file itself is stateless. The described registers are hardware/firmware state: command mailboxes, response mailboxes, interrupt helper state, scratch registers, firmware flags, and counters. Consumer writes change hardware register contents and can trigger firmware actions. Consumer reads observe firmware state that may change asynchronously. Persistence is limited to the active device/firmware session.

## Dependencies

This header depends on the preprocessor and on consumer-side AMDGPU register access infrastructure. Direct consumers provide base tables or SOC15 helpers that understand `reg..._BASE_IDX`. It is conventionally paired with `mp_13_0_5_sh_mask.h`, although current direct display consumers found in this tree include only the offset header and mostly treat mailbox values as full-width protocol words.

## Integration Points

Direct include sites are `display/dc/clk_mgr/dcn314/dcn314_smu.c` and `display/dc/clk_mgr/dcn315/dcn315_smu.c`. These files use MP 13.0.5 mailbox offsets for display clock and power-management communication with PMFW/SMU. The command flows include SMU version queries, display clock and DPP clock frequency changes, DCFCLK limits, deep-sleep clock settings, watermark table transfers, display idle optimizations, and DP reference clock queries. The larger scratch and firmware-flags coverage aligns MP 13.0.5 with other 13.0.x generated headers that expose firmware diagnostics/status registers.

## Risks

The primary risk is wrong base-index interpretation. Because every base index is `0`, a consumer that assumes MP 13.0.4's base index `1` will compute a different physical address even when the register offset number is identical. Another risk is the non-contiguous scratch register list: there is no `regMP1_SMN_EXT_SCRATCH9`, so generated-code or loop-based assumptions over 0-31 can fail at compile time or accidentally target an undefined register. Header mismatch can cause display SMU mailbox timeouts, wrong returned clock values, or firmware commands going to the wrong register.

## Test Signals

Compile-time tests should cover DCN 3.1.4 and DCN 3.1.5 display SMU translation units. Runtime tests should verify SMU message response polling exits busy state, `GetSmuVersion`/`GetPmfwVersion` returns sane data, display clock changes return expected MHz values, and watermark/table transfer paths do not trigger SMU timeouts. Static checks should compare offset sequences, base index `0`, the missing scratch 9, and `MP1_FIRMWARE_FLAGS` address `0xbee009` against the authoritative register database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_5_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_5_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_5_sh_mask.h

## Purpose

This generated header defines field shifts and masks for MP 13.0.5 MP0/MP1 registers. It complements `mp_13_0_5_offset.h` by describing how to extract or build bitfields once a consumer has addressed the correct register. The file is part of AMDGPU's generated ASIC register headers and contains no runtime implementation.

The address-block organization matches the offset header: `mp_SmuMp0_SmnDec`, `mp_SmuMp1_SmnDec`, and `mp_SmuMp1Pub_CruDec`. MP0 covers C2PMSG 32-103 and interrupt helper registers. MP1 covers C2PMSG 32-127, interrupt helpers, FPS count, extended scratch registers, and MP1 firmware flags.

## Important APIs, Types, And Macros

The public API is purely preprocessor macros guarded by `_mp_13_0_5_SH_MASK_HEADER`. There are no functions, types, or stored values.

Most C2PMSG and scratch fields are full-width values: `<REGISTER>__CONTENT__SHIFT` or `<REGISTER>__DATA__SHIFT` is `0x0`, and the corresponding mask is `0xFFFFFFFFL`. This indicates that the firmware mailbox protocol interprets the full 32-bit register payload. MP0 C2PMSG 32-103 are represented this way. MP1 C2PMSG 32-127 are also represented this way.

Interrupt helper fields are explicitly decoded. `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT` use `CREDIT_VALUE` bits 1:0 and `CLIENT_ID` bits 23:16. `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT` expose an 8-bit interrupt `ID` and `VALID` bit 8. `MP0_SMN_IH_SW_INT_CTRL` and `MP1_SMN_IH_SW_INT_CTRL` expose `INT_MASK` bit 0 and `INT_ACK` bit 8. `MP1_FIRMWARE_FLAGS` exposes `INTERRUPTS_ENABLED` bit 0 and `RESERVED` bits 31:1.

The MP1 scratch range mirrors the offset header and includes `EXT_SCRATCH0` through `8`, then `10` through `31`; there is no scratch 9 macro. Each scratch register exposes a full-width `DATA` field.

Inventory signal: the header contains 214 shift definitions and 216 mask definitions.

## Control Flow

There is no runtime control flow. Consumers control firmware communication by combining offset and mask definitions with register helpers. The exact direct consumers found for MP 13.0.5 currently include the offset header in DCN 3.1.4 and DCN 3.1.5 SMU code, but not this mask header. This mask file is still the version-matched field authority for future or indirect code that needs MP 13.0.5 field extraction, especially interrupt and firmware-flag handling.

When used, expected control patterns are mailbox polling and command dispatch: clear a response register, write a parameter to a C2PMSG register, write a command id, wait until the response register is no longer busy, then decode the result or returned payload. Interrupt-control code would use the `IH_*` masks to set/clear valid, ack, mask, credit, and client-id fields.

## State And Persistence Behavior

The header has no software state and no persistence. It describes hardware register state. Full-width mailbox content represents command, response, parameter, and scratch values controlled by firmware protocols. Interrupt helper bits represent active hardware/firmware interrupt state. `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED` reflects firmware interrupt readiness. Any writes done by consumers are hardware side effects and may be overwritten by firmware.

## Dependencies

This file depends only on the preprocessor but is designed to be used with `mp_13_0_5_offset.h` and AMDGPU register/field helper conventions. Code using `FD`, `FN`, or register field macros depends on the exact naming scheme in this file. It is also coupled to the generated ASIC register database that determines which scratch registers and firmware flag fields exist for this ASIC revision.

## Integration Points

The immediate source-tree integration point is the MP 13.0.5 register family used by `dcn314_smu.c` and `dcn315_smu.c` through the matching offset header. This mask header can support field-aware access for those display SMU paths if they later need to decode interrupt helpers, firmware flags, FPS counters, or scratch register data. It also aligns with neighboring MP 13.0.x headers used by PSP and SMU code, so consistency across generated files matters for shared AMDGPU register helper macros.

## Risks

The most important risk is assuming this file has the same semantic field set as other 13.0.x versions. It does not contain MP 13.0.2's specialized `MP0_SMN_C2PMSG_126__GPU_ERR_*` boot-status decode, but it does include MP1 firmware flags and an expanded non-contiguous scratch range absent from MP 13.0.4. The missing scratch 9 can break naive loops or generated references. Because most fields are full-width, field macro mistakes may not be detected by unit tests unless hardware mailbox behavior is exercised.

## Test Signals

Build tests should include any translation unit that adds this header and verify no macro-name collisions occur. Runtime validation should focus on hardware paths that would use these fields: SMU command response polling, interrupt enablement and acknowledgment, scratch-register diagnostics, and firmware-flag reads. Static tests should compare all shift/mask pairs against the MP 13.0.5 register source, including interrupt bit positions, `MP1_FIRMWARE_FLAGS`, full-width C2PMSG content fields, and the non-contiguous scratch list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_5_sh_mask.h -->
