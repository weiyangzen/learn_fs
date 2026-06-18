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
