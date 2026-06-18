# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_7_1_0_offset.h

## Purpose

`osssys_7_1_0_offset.h` is the generated register offset map for OSSSYS 7.1.0. Like the 7.0.0 offset header, it describes the `osssys_osssysdec` address block with base address `0x4280` and exports `reg...` plus `..._BASE_IDX` macros for use with SOC15 AMDGPU register helpers.

The file preserves most of the OSSSYS 7.0.0 interrupt-handler register map but introduces a version-specific `regIH_VMID_LUT_INDEX` register and moves the SEM/client/virtualization tail window down from the `0x0180` range to the `0x0120` range. It is therefore a hardware-version ABI map, not a general replacement for the 7.0.0 header.

## Important APIs, Types, And Macros

This header exports only preprocessor macros. Important groups include:

- `regIH_VMID_0_LUT` through `regIH_VMID_15_LUT` and `regIH_VMID_0_LUT_MM` through `regIH_VMID_15_LUT_MM`, still contiguous at `0x0000`-`0x001f`.
- `regIH_COOKIE_0` through `regIH_COOKIE_7` at `0x0020`-`0x0027`.
- `regIH_VMID_LUT_INDEX` at `0x0028`, new relative to 7.0.0. This register selects which VMID LUT slice/instance subsequent LUT accesses address on 7.1 hardware.
- Ring 0 and ring 1 IH registers at the same offsets as 7.0.0 for `RB_CNTL`, `RPTR`, `WPTR`, base address, writeback address, doorbell, retry CAM, status, control, rate-limit, memory power, performance, DSM match, VF status, flood/drop, MSI storm, and last interrupt info.
- SEM mailbox registers at `regSEM_MAILBOX` `0x010a` and `regSEM_MAILBOX_CLEAR` `0x010b`, with `regSEM_REGISTER_LAST_PART2` reduced to `0x011f`.
- The virtualization/client tail window beginning at `regIH_VIRT_RESET_REQ` `0x0120`, followed by `regIH_CLIENT_CFG`, indexed ring1/client configuration, CID remap, `regIH_CHICKEN`, interrupt drop match/mask registers, and `regIH_MMHUB_CNTL` at `0x0147`.
- `regIH_REGISTER_LAST_PART1` at `0x019f`, marking the tail of this generated register partition.

All `*_BASE_IDX` macros are `0`.

## Control Flow And Runtime Use

The header contains no executable control flow. Consumers use it to compute register addresses. Direct consumer evidence in this tree includes:

- `amdgpu/gmc_v12_1.c`, which includes `osssys_7_1_0_offset.h` and `osssys_7_1_0_sh_mask.h`. Its VMID/PASID lookup helper computes an index from the hub instance, writes that value to `SOC15_REG_OFFSET(OSSSYS, 0, regIH_VMID_LUT_INDEX)`, then reads `SOC15_REG_OFFSET(OSSSYS, 0, regIH_VMID_0_LUT) + vmid` and masks the low 16 bits.
- `amdgpu/ih_v7_0.c`, which is shared across OSSSYS 7.x interrupt handling. That file currently includes the 7.0.0 offset/mask headers and carries local `regIH_RING1_CLIENT_CFG_INDEX_V7_1`, `regIH_RING1_CLIENT_CFG_DATA_V7_1`, and `regIH_CHICKEN_V7_1` constants matching this 7.1 offset map. It chooses those constants when `amdgpu_ip_version(adev, OSSSYS_HWIP, 0) == IP_VERSION(7, 1, 0)`.

The runtime flow for 7.1 VMID lookup is version-specific: select a LUT index first, then access the same contiguous LUT offsets used by earlier hardware. This is the key behavioral addition represented by the offset header.

## State And Persistence Behavior

The header is stateless. The hardware registers it names hold the same categories of live state as 7.0.0: IH ring configuration and pointers, VMID/PASID mappings, interrupt cookies, storm/drop/flood diagnostics, SR-IOV status and reset requests, SEM mailbox data, client remapping, and MMHUB control.

The new `regIH_VMID_LUT_INDEX` has important state behavior: it is a selector that affects which VMID LUT instance is addressed by later LUT reads or writes. Callers must treat it as mutable global hardware selector state. Code that writes it should restore or intentionally leave it in a known state if later operations could assume a different LUT slice. The observed `gmc_v12_1_get_vmid_pasid_mapping_info()` flow writes the selector immediately before reading the LUT, reducing but not eliminating interleaving risk if other contexts access the same selector without serialization.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- SOC15 register-address helpers, which combine `OSSSYS`, instance `0`, and the generated register offsets.
- `gmc_v12_1.c`, where the new LUT selector is part of VMID/PASID lookup for multi-instance/hub-aware TLB invalidation.
- The 7.1 shift/mask header for field encoding. This work item did not require researching that file, but `gmc_v12_1.c` includes it alongside this offset header.
- Shared IH initialization in `ih_v7_0.c`, which must account for moved 7.1 offsets when programming ring1 client configuration and the `IH_CHICKEN` register.
- The older 7.0.0 offset map, which is mostly compatible for the front part of the register block but differs in the tail window.

## Risks

The largest risk is treating the 7.0.0 and 7.1.0 offset maps as interchangeable. The early IH ring and status windows are stable, but the tail region changed: 7.0.0 has `regIH_ACTIVE_FCN_ID` at `0x0180` and subsequent client/virtualization registers through `0x01a8`; 7.1.0 removes that active-function offset from this header and places `regIH_VIRT_RESET_REQ` at `0x0120`, `regIH_CHICKEN` at `0x0129`, and `regIH_MMHUB_CNTL` at `0x0147`. Using 7.0 addresses on 7.1 hardware can write to the wrong register window.

`regIH_VMID_LUT_INDEX` introduces selector state. Missing selector writes can read the wrong PASID mapping; unsynchronized selector use can produce wrong results if multiple paths access the selector/LUT pair concurrently. Tests should look for locking or hardware access serialization around selector-dependent reads and writes.

Local hard-coded 7.1 constants in `ih_v7_0.c` are a maintenance risk because they duplicate values already present in this header. If the generated header changes, those local constants can drift unless updated together.

## Test Signals

Useful validation signals include:

- Build coverage for `gmc_v12_1.c` with the 7.1 offset and mask headers.
- VMID/PASID lookup tests across multiple `inst` values that verify the index calculation writes the expected selector values and reads the correct PASID from VMIDs 1-15.
- TLB invalidation-by-PASID tests on 7.1 hardware, especially with multiple hub/instance combinations, because stale or wrong LUT selector state would flush the wrong VMID.
- IH bring-up on OSSSYS 7.1.0 hardware verifying the moved `IH_CHICKEN` and ring1 client config offsets are programmed correctly by the version checks in `ih_v7_0.c`.
- Suspend/resume, reset, and SR-IOV tests checking that selector state and moved tail-window registers are restored or reprogrammed reliably.
- Register readback or hardware trace checks comparing `regIH_VMID_LUT_INDEX`, `regIH_RING1_CLIENT_CFG_INDEX`, `regIH_RING1_CLIENT_CFG_DATA`, and `regIH_CHICKEN` addresses against the generated 7.1 spec.
