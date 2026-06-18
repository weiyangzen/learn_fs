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
