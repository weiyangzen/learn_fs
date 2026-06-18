<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_offset.h

## Purpose

`mp_15_0_8_offset.h` is a generated AMDGPU register-offset contract for the MP 15.0.8 block. It gives symbolic names and SOC15 base-index selectors for MP1, MPASP, MPRAS, MPIFOE, and MPIO mailbox, interrupt, scratch, public-control, and firmware-flag registers. The file contains no executable code; its job is to let PSP/SMU driver code address hardware registers through `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and PCIe/SMN access paths without embedding raw offsets at each call site.

## Important APIs, Types, And Macros

The file exports preprocessor constants only. There are no functions, structs, enums, or data objects.

Important macro groups:

- `regMP1_SMN_C2PMSG_0` through `regMP1_SMN_C2PMSG_175`, all in the `mp_SmuMp1_SmnDec` address block, with `_BASE_IDX` value `2`. These are the command/message mailbox registers used by host-to-MP1 and firmware-to-host protocols.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_PUB_CTRL`, also under MP1 SMN decode with base index `2`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31`, a contiguous external scratch range at offsets `0x01c0` through `0x01df`.
- `regMPASP_SMN_C2PMSG_0` through `regMPASP_SMN_C2PMSG_175`, plus MPASP interrupt-credit and software-interrupt registers, in the `mp_SmuMpASP_SmnDec` address block with `_BASE_IDX` value `1`.
- Firmware-flag aliases for CRU0 public decode: `regMPRAS_CRU0_MPRAS_FIRMWARE_FLAGS`, `regMPIFOE_CRU0_MPIFOE_FIRMWARE_FLAGS`, `regMP1_CRU0_MP1_FIRMWARE_FLAGS`, and `regMPIO_CRU0_MPIO_FIRMWARE_FLAGS`, all offset `0xbeb009` with `_BASE_IDX` `3`.
- Firmware-flag aliases for MMIO public decode: `regMPRAS_CRU1_MPRAS_FIRMWARE_FLAGS`, `regMPIFOE_CRU1_MPIFOE_FIRMWARE_FLAGS`, `regMP1_CRU1_MP1_FIRMWARE_FLAGS`, and `regMPIO_CRU1_MPIO_FIRMWARE_FLAGS`, all offset `0x4009` but with block-specific base indices `9`, `26`, `6`, and `23`.

The header uses the `reg...` naming convention common to newer generated AMD register headers, unlike older MP 9.0 headers that use many `mm...` names.

## Control Flow

There is no local control flow. Runtime flow is supplied by consumers. In this tree, `pm/swsmu/smu15/smu_v15_0_8_ppt.c` includes this header and uses `regMP1_SMN_IH_SW_INT_CTRL` and `regMP1_SMN_IH_SW_INT` when processing, masking, unmasking, and acknowledging MP1 software interrupts. That flow reads a register with `RREG32_SOC15(MP1, 0, reg...)`, updates fields with masks from `mp_15_0_8_sh_mask.h`, and writes the value back with `WREG32_SOC15`.

`amdgpu/psp_v15_0_8.c` also includes this header so PSP code can use the same generated MP 15.0.8 register names. SMU firmware-status checks combine a hard-coded MP1 public base with an SMN firmware-flag offset and decode the result using the companion mask header.

## State And Persistence Behavior

The header itself is stateless and compile-time only. The named registers represent live hardware state:

- C2PMSG registers carry mailbox commands, parameters, responses, status flags, ring addresses, and firmware protocol values. Their contents persist in hardware registers until overwritten, reset, or changed by firmware.
- IH software-interrupt registers store interrupt IDs, validity bits, mask state, acknowledgement state, and credit values.
- External scratch registers provide firmware/driver scratch state whose lifetime is tied to the MP block and GPU reset/power state.
- Public firmware flag registers expose whether firmware has enabled interrupts and may be read during PSP/SMU bring-up, resume, reset, and reload paths.

The driver, not this header, is responsible for ordering, polling, and ownership rules around these registers.

## Dependencies

Consumers depend on:

- `mp_15_0_8_sh_mask.h` for field layouts inside the registers named here.
- SOC15 register-access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.
- PCIe/SMN register access helpers such as `RREG32_PCIE` where code builds absolute public-register addresses.
- The generated AMD register convention that `<register>_BASE_IDX` selects the register base segment used by SOC15 helpers.

The include guard is `_mp_15_0_8_OFFSET_HEADER`.

## Integration Points

Direct integration found in this source tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c` includes this file for MP1 interrupt-control register access and MP1 firmware-status checks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.c` includes this file for PSP-side MP 15.0.8 register access.
- The offsets mirror nearby generation families such as `mp_15_0_0_offset.h`, but MP 15.0.8 has its own base-index assignments and MPASP/RAS/IFOE/IO public flag layout.

## Risks

- Register-map drift is high impact. A wrong offset or `_BASE_IDX` can route reads/writes to another hardware block or to the wrong instance of an MP public window.
- Version confusion is likely because many MP generations expose similarly named C2PMSG and interrupt registers with different prefixes, offsets, or base indices. MP 15.0.8 consumers must not silently substitute MP 15.0.0, 14.x, 13.x, or 9.0 constants.
- Mailbox registers are protocol registers. Incorrect writes can wedge PSP/SMU boot, command submission, interrupt routing, or reset/unload flows.
- The CRU0 and CRU1 firmware-flag macros deliberately reuse the same offsets across multiple public blocks with different base indices. Callers must use the correct block name and access path.
- The header gives no locking, bounds, or sequencing rules. Callers must coordinate with firmware and higher-level SMU/PSP state machines before changing interrupt masks, acknowledgements, or mailbox contents.

## Test Signals

- Compile coverage of `smu_v15_0_8_ppt.c` and `psp_v15_0_8.c` catches missing or renamed macros.
- Hardware bring-up should verify that `smu_v15_0_8_check_fw_status()` reads the expected MP1 firmware flag and that interrupt enablement is detected.
- SMU interrupt tests should exercise enable, disable, and ACK paths for `regMP1_SMN_IH_SW_INT` and `regMP1_SMN_IH_SW_INT_CTRL`.
- PSP/SMU mailbox tests should confirm C2PMSG command/response polling reaches expected completion bits and does not time out after reset or resume.
- Register traces can validate the computed SOC15 addresses for base indices `1`, `2`, `3`, `6`, `9`, `23`, and `26`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_offset.h -->
