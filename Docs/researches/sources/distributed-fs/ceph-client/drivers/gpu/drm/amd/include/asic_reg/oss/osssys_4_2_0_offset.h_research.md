# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_2_0_offset.h

## Purpose

`osssys_4_2_0_offset.h` is the OSSSYS 4.2.0 register offset table for AMDGPU SOC15-style register access. It maps symbolic `mm...` register names to offsets within the `osssys_osssysdec` address block, whose documented base address is `0x4280`, and defines a corresponding `*_BASE_IDX` for each register. It contains no executable logic; its job is to provide the address half of the register ABI, while the companion `osssys_4_2_0_sh_mask.h` supplies field masks and shifts.

The table spans IH VMID/PASID LUTs, IH cookie registers, semaphore request inputs, primary and secondary IH ring-buffer registers, retry CAM/version/control/status/performance registers, DSM match controls, interrupt flood/status/diagnostic registers, SEM UTC/MCIF/performance/status/mailbox registers, virtualization function/reset controls, client configuration/remap registers, interrupt drop match registers, SEM response address registers, atomic operation LUT, EDC/chicken controls, and MMHUB integration registers.

## Important APIs, Types, And Macros

This header exports only macros:

- `mmREG` constants define word offsets used by SOC15 register address helpers, for example `mmIH_RB_CNTL 0x0080`, `mmSEM_STATUS 0x0108`, and `mmSEM_ATOMIC_OP_LUT 0x01b2`.
- `mmREG_BASE_IDX` constants are all `0` in this file and identify the base-index slot used by generated SOC15 access machinery.
- IH ring offsets are grouped as ring 0 at `0x0080` onward, ring 1 at `0x008c` onward, and ring 2 at `0x0098` onward, with each ring exposing base, high-base, read pointer, write pointer, and doorbell read pointer registers.
- OSSSYS 4.2.0 adds or exposes offsets not present in older 4.0-style tables, including `mmIH_DOORBELL_RETRY_CAM`, `mmIH_RETRY_CAM_ACK`, `mmIH_RETRY_INT_CAM_CNTL`, `mmIH_MEM_POWER_CTRL`, `mmSEM_MEM_POWER_CTRL`, `mmIH_INT_DROP_CNTL`, `mmIH_INT_DROP_MATCH_VALUE{0,1}`, `mmIH_INT_DROP_MATCH_MASK{0,1}`, and `mmSEM_RESP_UVD_1`.

There are no functions, structs, enums, variables, or inline accessors.

## Control Flow

The header itself has no control flow. Runtime use is visible in `amdgpu/vega20_ih.c`, which includes `oss/osssys_4_2_0_offset.h` and `oss/osssys_4_2_0_sh_mask.h`. That driver:

- Converts offsets such as `mmIH_RB_BASE`, `mmIH_RB_CNTL`, and `mmIH_DOORBELL_RPTR` into concrete register addresses with `SOC15_REG_OFFSET(OSSSYS, 0, ...)`.
- Initializes `amdgpu_ih_regs` for ring 0, ring 1, and ring 2 only when each software ring has a nonzero `ring_size`.
- Reads and writes the computed control register addresses with `RREG32`, `WREG32`, `WREG32_NO_KIQ`, or PSP indirect programming when SR-IOV requires it.
- Uses companion `IH_RB_CNTL` masks/shifts to toggle ring enable, timestamp enable, interrupt enable, and overflow-clear handling.

Thus this offset file participates in runtime control flow by selecting which hardware addresses those consumers touch, but it does not implement the sequencing itself.

## State And Persistence Behavior

The header stores no software state and has no persistence. The offsets name hardware state:

- IH ring base/read/write/doorbell registers point to memory-backed interrupt rings and doorbell update paths.
- IH control/status/flood/drop/last-interrupt registers represent live interrupt handler state, some of which may be sticky until explicitly cleared.
- SEM mailbox/status/UTC/MCIF/response registers represent semaphore subsystem routing, pending requests, and mailbox state.
- Virtualization registers such as active function ID, virtual reset request, client config, and client ID remap affect PF/VF behavior.
- Power/clock control registers can change hardware block power behavior when programmed by consumers.

All persistence semantics are hardware-defined and external to this header.

## Dependencies And Integration Points

The file is coupled to:

- `osssys_4_2_0_sh_mask.h`, which defines field layout for the registers named here.
- SOC15 access helpers (`SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and direct `RREG32`/`WREG32` through precomputed addresses).
- AMDGPU IH implementations, especially `vega20_ih.c`; other ASIC generations have parallel offset files such as `osssys_4_0_offset.h`, `osssys_4_0_1_offset.h`, and `osssys_5_0_0_offset.h`.
- PSP and SR-IOV paths when IH control registers are programmed indirectly rather than through normal MMIO.

The symbolic names and base indexes are part of the generated AMDGPU register namespace. Renaming or relocating macros breaks compile-time consumers even when the numeric offsets are unchanged.

## Risks

- Offset drift is severe: an incorrect numeric offset directs register reads or writes to the wrong hardware register.
- Revision confusion can compile successfully because same-named registers exist in nearby OSSSYS versions but have different offsets or extra registers.
- Ring spacing differences matter: OSSSYS 4.2.0 places ring 1 at `0x008c` and ring 2 at `0x0098`, unlike some 4.0 offset variants where secondary rings start earlier. Copying older assumptions can misprogram retry CAM or ring controls.
- Base-index errors would affect SOC15 address calculation even if offsets are correct.
- The file has no self-checking logic; generated constants require external comparison or hardware tests.

## Test Signals

Relevant signals include:

- Successful build of ASIC code that includes `osssys_4_2_0_offset.h`, particularly `vega20_ih.c`.
- Device probe on OSSSYS 4.2.0-family GPUs reaches IH initialization without MMIO faults or PSP register-programming errors.
- Interrupt ring tests verify ring 0, ring 1, and ring 2 addresses are configured correctly and produce interrupts on the expected ring.
- Overflow and flood handling tests exercise `mmIH_RB_WPTR*`, `mmIH_STATUS`, `mmIH_INT_FLOOD_*`, and `mmIH_INT_DROP_*` paths.
- SR-IOV testing checks PSP indirect programming, active-function state, virtual reset request offsets, and client remap/configuration registers.
- Diffing against AMD generated register headers or upstream Linux AMDGPU headers is the strongest static validation for the numeric table.
