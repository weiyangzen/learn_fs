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
