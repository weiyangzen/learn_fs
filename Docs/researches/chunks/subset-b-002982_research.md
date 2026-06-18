# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 51418-54381

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,002 preprocessor `#define` entries across 2,964 source lines. There are no C functions, structs, enums, variables, allocation sites, locks, branches, loops, or executable statements in this range.

The range starts inside an endpoint DPA power-allocation register definition: line 51418 is only the mask for `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_2`, while its comment and shift definition are in the previous chunk. It then covers endpoint PCIe control/status field maps, two RCC downstream/downstream-port address blocks, and a large MSI-X table sequence. The range ends inside `PCIEMSIX_VECT230_ADDR_HI`: the `_SHIFT` is present at line 54381, while the matching `_MASK` is on line 54382 in the next chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 hardware interface. For each named hardware register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to extract or pack the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or compose the field.

The companion `nbio_4_3_0_offset.h` header supplies the matching register offsets and base indices. Runtime driver code combines the offsets and masks through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

This particular chunk describes PCIe endpoint behavior for NBIO/RCC device 0 function group `DEV0_1`, downstream port decode fields, downstream-port PCIe error/link/power-management fields, and the start of a large MSI-X vector table. It is hardware metadata rather than policy code.

## Important Macro Families

The `RCC_EP_DEV0_1_*` endpoint families at the start of the chunk expose PCIe endpoint capability and control fields:

- `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_[2-7]` defines 8-bit dynamic power allocation substate power values. The chunk contains only the mask for substate 2, then complete shift/mask pairs for substates 3 through 7.
- `RCC_EP_DEV0_1_EP_PCIE_PME_CONTROL` defines the `PME_SERVICE_TIMER` field.
- `RCC_EP_DEV0_1_EP_PCIEP_RESERVED` maps a full-width reserved value.
- `RCC_EP_DEV0_1_EP_PCIE_TX_CNTL` defines transmit-side override and TPH-disable bits: `TX_SNR_OVERRIDE`, `TX_RO_OVERRIDE`, and `TX_F[0-2]_TPH_DIS`.
- `RCC_EP_DEV0_1_EP_PCIE_TX_REQUESTER_ID` splits requester ID into function, device, and bus fields.
- `RCC_EP_DEV0_1_EP_PCIE_ERR_CNTL` defines error-reporting control, AER header-log timeout, immediate error-message send, poisoned advisory nonfatal behavior, and AER header-log timer-expired bits for functions 0 through 7.
- `RCC_EP_DEV0_1_EP_PCIE_RX_CNTL` defines receive-side ignore/disable controls for max-payload, traffic-class, completion-timeout, prefix, PASID, not-PASID unsupported-request, and TPH behavior.
- `RCC_EP_DEV0_1_EP_PCIE_LC_SPEED_CNTL` defines link-speed strap enables for Gen2, Gen3, Gen4, and Gen5.

The `nbio_nbif0_rcc_dwn_dev0_RCCPORTDEC` address block maps downstream decode registers:

- `RCC_DWN_DEV0_1_DN_PCIE_RESERVED` and `RCC_DWN_DEV0_1_DN_PCIE_SCRATCH` expose full 32-bit reserved/scratch fields.
- `RCC_DWN_DEV0_1_DN_PCIE_CNTL` includes `HWINIT_WR_LOCK`, downstream unsupported-request error-report disable, and `RX_IGNORE_LTR_MSG_UR`.
- `RCC_DWN_DEV0_1_DN_PCIE_CONFIG_CNTL` exposes the `CI_EXTENDED_TAG_EN_OVERRIDE` field.
- `RCC_DWN_DEV0_1_DN_PCIE_RX_CNTL2` exposes `FLR_EXTEND_MODE`.
- `RCC_DWN_DEV0_1_DN_PCIE_BUS_CNTL` includes immediate-PMI disable and AER completion-timeout relaxed-ordering disable.
- `RCC_DWN_DEV0_1_DN_PCIE_CFG_CNTL` controls decode to hidden registers for baseline and Gen2 through Gen5 capability spaces.
- `RCC_DWN_DEV0_1_DN_PCIE_STRAP_F0`, `STRAP_MISC`, and `STRAP_MISC2` map downstream strap state including function enable, memory-controller enable, MSI multi-message capability, clock power management, 64-bit master address support, and master completion-timeout enable.

The `nbio_nbif0_rcc_dwnp_dev0_RCCPORTDEC` address block maps downstream-port PCIe-facing fields:

- `RCC_DWNP_DEV0_1_PCIE_ERR_CNTL` provides error-reporting disable, AER header-log timeout, function-0 timer-expired, immediate error-message send, and clear bits for received correctable, nonfatal, and fatal errors.
- `RCC_DWNP_DEV0_1_PCIE_RX_CNTL` defines downstream receive ignore/disable controls for max-payload errors, traffic-class errors, completion timeout, short-prefix errors, and RCB FLR timeout.
- `RCC_DWNP_DEV0_1_PCIE_LC_SPEED_CNTL` defines Gen2 through Gen5 link-speed strap enables.
- `RCC_DWNP_DEV0_1_PCIE_LC_CNTL2` controls link-state and link-bandwidth notification disable bits.
- `RCC_DWNP_DEV0_1_PCIEP_STRAP_MISC` exposes downstream-port multi-function strap enable.
- `RCC_DWNP_DEV0_1_LTR_MSG_INFO_FROM_EP` maps a full 32-bit LTR message-info value received from the endpoint.

The `PCIEMSIX_VECT*` families dominate the chunk. Vectors 0 through 229 are complete; vector 230 is partial because of the chunk boundary. For each complete vector:

- `PCIEMSIX_VECT<n>_ADDR_LO__MSG_ADDR_LO` starts at bit 2 and masks with `0xFFFFFFFC`, reflecting the alignment of MSI/MSI-X message addresses.
- `PCIEMSIX_VECT<n>_ADDR_HI__MSG_ADDR_HI` is a full 32-bit high-address field.
- `PCIEMSIX_VECT<n>_MSG_DATA__MSG_DATA` is a full 32-bit message data field.
- `PCIEMSIX_VECT<n>_CONTROL__MASK_BIT` is bit 0, the per-vector mask control.

## APIs, Types, And Functions

There are no runtime APIs, C types, or functions in this chunk. The public interface is the generated macro namespace. The macros are untyped integer constants, mostly with an `L` suffix, and are intended for compile-time use by register access helpers.

The field macros do not encode access semantics. They identify bit positions and masks only. They do not specify whether a register is read-only, write-only, sticky, write-one-to-clear, reset-sensitive, privilege-gated, posted, side-effecting, or safe to modify while hardware is active. Those properties come from the hardware register specification and from driver code that sequences reads and writes.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. Driver code selects a register offset from `nbio_4_3_0_offset.h`.
2. The caller reads, writes, modifies, polls, or decodes the register through AMDGPU SOC15 access helpers.
3. The caller uses the `__SHIFT` and `_MASK` constants from this header to isolate or compose fields.
4. Hardware implements the resulting state transition, such as PCIe link capability exposure, AER status updates, DPA/PME behavior, downstream hidden-register decode, LTR propagation, or MSI-X interrupt routing.

Important external flows represented by this chunk include PCIe endpoint bring-up, link-speed capability strap handling, PCIe error-reporting and AER timer handling, receive/transmit policy overrides, downstream port configuration, latency tolerance reporting propagation, dynamic power allocation reporting, and MSI-X vector table programming/masking.

## State And Persistence Behavior

The header stores no software state. It names hardware-visible state in NBIO/RCC/PCIe registers. Persistence is controlled by GPU reset domains, PCIe function-level reset, suspend/resume handling, firmware initialization, strap sampling, and explicit driver writes.

Represented hardware state includes:

- DPA substate power allocation values and endpoint PME service timer configuration.
- PCIe requester ID bus/device/function fields.
- Transmit and receive policy bits for relaxed ordering, snoop behavior, TPH, PASID-related receive handling, prefix handling, completion timeout, and traffic-class errors.
- AER/error-reporting control and timer-expired/received-error status or clear bits.
- Link-speed strap enables for Gen2 through Gen5 and link notification disable controls.
- Downstream hidden-register decode enables and downstream-port strap fields.
- LTR message information received from an endpoint.
- MSI-X per-vector message address, message data, and vector mask bits.

Several fields are not ordinary retained storage. Error status and clear bits may be sticky or write-one-to-clear depending on the register contract. Strap-derived fields may be sampled at hardware initialization and may not be freely mutable later. MSI-X vector address/data/control fields directly affect interrupt delivery. Link and receive/transmit policy bits can alter PCIe protocol behavior while traffic is active.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register set:

- `nbio_4_3_0_offset.h` supplies matching register addresses and base indices, including RCC downstream registers and `PCIEMSIX_VECT*` table offsets.
- `nbio_4_3_0_sh_mask.h` supplies the field layout documented here.
- Other generated NBIO/RCC/PCIe headers provide adjacent chunks and other IP-generation layouts.

Observed include-level integration in this repository includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`

The exact macros in this chunk were not found as direct references in those implementation files during this pass, but the include relationship matters: the header is part of the shared generated register contract for NBIO 4.3.0. Nearby NBIO code in `nbio_v4_3.c` uses the same pattern of generated register offsets plus generated shift/mask macros through `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while causing the driver to touch the wrong hardware bits. Highest-risk fields in this chunk include MSI-X address/data/control, AER status/clear bits, PCIe receive/transmit policy bits, link-speed straps, hidden-register decode enables, and LTR/DPA power-management fields.
- The chunk boundaries split real register definitions. The merge lane must not interpret the lone `RCC_EP_DEV0_1_PCIE_F0_DPA_SUBSTATE_PWR_ALLOC_2` mask at the start or the missing `PCIEMSIX_VECT230_ADDR_HI` mask at the end as whole-file omissions.
- The MSI-X sequence is intentionally repetitive. A missing vector, incorrect low-address alignment mask, or changed control bit position would be easy to miss in review but could cause lost, misdirected, or permanently masked interrupts.
- Error-control fields include both disable bits and clear/status bits. Confusing these semantics can either suppress real PCIe errors or clear diagnostic evidence before software observes it.
- Link-speed strap and hidden-register decode bits can affect enumeration, capability exposure, and access to generation-specific PCIe configuration space. Incorrect masks can make device behavior differ from hardware straps or firmware expectations.
- Receive/transmit policy bits change how the endpoint handles completion timeouts, prefixes, PASID-related requests, TPH, relaxed ordering, and snoop behavior. Incorrect updates may create subtle I/O correctness or interoperability failures.
- Full-width reserved/scratch fields are still register-addressable; treating reserved fields as safe general storage can conflict with undocumented hardware behavior.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Missing or misspelled generated macros should be caught by consumers that include the NBIO 4.3.0 header pair.
- Run runtime probe on affected AMD GPUs and verify stable NBIO initialization, PCIe enumeration, suspend/resume, and reset behavior.
- Exercise MSI-X setup and teardown for high vector counts. Verify vector address/data programming, per-vector masking, interrupt delivery, and absence of vector aliasing across vectors 0 through at least 229.
- Exercise PCIe AER/error paths where possible. Verify correct logging, clear behavior, and no unintended suppression when error-reporting disable fields are toggled by firmware or driver code.
- Validate link capability exposure and negotiated speed for Gen2 through Gen5-capable platforms, especially after resume and reset.
- Exercise power-management paths that depend on PME, LTR, and DPA state and verify no regressions in low-power entry/exit or wake behavior.
- Use register-dump or debugfs tooling to compare `nbio_4_3_0_offset.h` addresses with these shift/mask definitions for the downstream RCC blocks and MSI-X table layout.
- For generated-header maintenance, diff this chunk against the authoritative hardware register database and adjacent NBIO generations to catch accidental vector-count, field-width, or bit-position drift.
