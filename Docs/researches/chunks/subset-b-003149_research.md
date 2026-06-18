# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 7355-9783

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment. It contains 2,401 `#define` macros over 2,429 source lines, all in the `reg*` namespace. The macros alternate between register offset constants and their matching `<REGISTER>_BASE_IDX` selector constants, with the base index fixed to `5` throughout this range.

The range starts inside the `nbio_nbif0_bif_misc_bif_misc_regblk` block at `regBIFC_HSTARB_CNTL_BASE_IDX`, then covers complete NBIF reset, RAS, SION, and PCIe endpoint-function configuration blocks for device 0 functions EPF0 through the beginning of EPF3. It ends at `regBIF_CFG_DEV0_EPF3_0_MSI_PENDING_64_BASE_IDX`, so the EPF3 PCIe configuration block continues in the following chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct Ceph or distributed-filesystem logic.

## Purpose

`nbio_7_2_0_offset.h` provides symbolic register offsets for the NBIO 7.2.0 ASIC register map. Driver code uses these constants with AMDGPU register-access helpers and companion shift/mask/default headers so call sites can name hardware registers instead of embedding raw offsets.

This chunk maps NBIO/BIF control registers, reset controls, RAS reporting registers, SION buffer/credit controls, and PCIe configuration-space windows for several GPU endpoint functions. The constants are address metadata only: they do not define bitfields, reset values, access permissions, side effects, or register sequencing.

## Important Macro Families

The opening partial `nbio_nbif0_bif_misc_bif_misc_regblk` tail covers BIF/NBIF miscellaneous control and status offsets around `0xe829`-`0xe8d2`. Important groups include BIFC GSI and PCIe function controls, PASID check/status controls, SDP controls, ATHUB activation, MMIO/DMA performance counters, NBIF register-interface error-set control, NBIF power-gating master/slave/misc controls, host miscellaneous controls, SMN master endpoint controls, strap write control, INTx D-state and pending controls, GMI weighted round-robin controls, power-break request, atomic/PASID/DMA error logs, OBFF emulation, endpoint urgent interrupt capabilities, pending block masks, virtual-wire controls, LCLK clock/deep-sleep controls, SHUB timeout detector registers, SDP/SST pool-credit allocation, BDF controls, and early wakeup control.

The complete `nbio_nbif0_bif_rst_bif_rst_regblk` block starts at line 7522 and contributes 186 macros. It maps hard and self soft reset controls, VPU/GFX driver reset controls, BIF reset miscellaneous controls, per-device and per-function FLR reset controls for device 0 functions 0-7, device 1 functions 0-7, and device 2 functions 0-7, FLR power-state-change request/status/enable registers, FLR request disable registers, reset request disable registers, reset sticky/status registers, host reset straps, software scratch reset cleanup controls, reset monitoring controls, per-function reset pulse counters, bus and device reset controls, hot reset controls, and per-port D-state value registers.

The complete `nbio_nbif0_bif_ras_bif_ras_regblk` block contributes 24 macros. It maps BIFL RAS central control, error status, BIFL-to-host and BIFL-to-IOHUB virtual-wire control/status registers, and virtual-wire source registers. These offsets integrate NBIO error reporting with broader RAS and sideband notification paths.

The complete `nbio_nbif0_nbif_sion_SIONDEC` block contributes 124 macros. It maps SION client read-response, write-response, request, and data buffer target registers for clients CL0 through CL8, per-client buffer status registers, read/write buffer-credit registers, accumulated credit counters, and global SION control registers. These offsets describe NBIF/SION buffering and flow-control state rather than software queues.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` blocks each contribute 702 macros. They provide PCI-compatible configuration registers for device 0 endpoint functions 0 and 1, including vendor/device identity, command/status, class/revision, BARs, ROM BAR, interrupt metadata, vendor capability, power-management capability, PCIe capability, device/link capability and control/status pairs, MSI registers, subsystem ID, MSI mapping, PCIe vendor-specific, VC, serial number, AER, secondary PCIe, ACS, data-link feature, 16 GT/s PHY, lane margining, physical-layer, latency tolerance reporting, link declaration, multicast, atomic-op routing, PASID, LTR, and TPH requestor/ST table registers. They also include large AMD GPU-IOV vendor-specific scheduling/header register windows for SDMA, VCE, UVD, and related engine scheduling controls.

The `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` block contributes 378 macros. It mirrors the standard PCIe endpoint configuration structure for device 0 function 2 through TPH requestor and TPH steering-table entries, but this range does not include the larger GPU-IOV scheduling windows present for EPF0 and EPF1.

The final `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block starts at line 9662 and contributes 120 macros in this chunk. It covers the early PCIe configuration-space portion of device 0 function 3: identity, command/status, class/header, BARs, ROM BAR, interrupts, vendor and power-management capabilities, PCIe device/link capability and control/status pairs, second-generation device/link capability and control/status pairs, and MSI address/data/mask/pending registers. The rest of EPF3 follows after line 9783.

## APIs, Types, And Functions

There are no callable APIs, C types, functions, variables, allocations, locks, or executable statements in this chunk. The public interface is the preprocessor macro namespace:

- `reg<NAME>` macros encode NBIO register offsets, usually in dword-indexed SOC15-style form.
- `reg<NAME>_BASE_IDX` macros encode the base-instance selector used by AMDGPU register helpers; all values in this range are `5`.

Consumers are expected to combine these macros with sibling generated headers such as `nbio_7_2_0_sh_mask.h` for field layout and any default-value metadata for reset values. The header itself cannot tell a caller whether a register is read-only, write-one-to-clear, sticky across reset, firmware-owned, or safe to touch during power transitions.

## Control Flow

This header has no local runtime control flow. Runtime flow is external and typically follows this pattern:

1. AMDGPU code selects the NBIO 7.2.0 register symbol matching the active ASIC and hardware block.
2. Register helper macros use the `reg*` offset plus the `_BASE_IDX` selector to compute the target MMIO or indexed-register address.
3. Driver code reads, writes, or read-modify-writes the hardware register using companion shift/mask macros to isolate fields.
4. Hardware then performs the configured operation, such as changing PCIe configuration state, reporting an error, gating a link/control path, initiating or observing reset state, or exposing SION credit/status information.

The implied hardware flows include PCIe enumeration and capability walking, MSI programming, function-level reset handling, hot reset and D-state transitions, PASID and atomic-operation error logging, NBIF power/clock gating, RAS virtual-wire signaling, SION buffer-credit accounting, PCIe advanced error reporting, lane margining, LTR/TPH configuration, and GPU-IOV engine scheduling configuration.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes offsets for hardware-visible state inside NBIO/BIF registers and PCIe configuration windows.

State represented by this chunk includes reset request/status/sticky bits, FLR controls, D-state values, strap and virtual-wire settings, PASID/atomic/DMA error logs, performance counters, power-gating and clock-gating controls, timeout-detector state, SION buffer occupancy and credits, PCI configuration identity/control/status registers, BAR and ROM aperture registers, MSI address/data/mask/pending state, PCIe capability and AER status, lane margining controls, LTR and TPH policy, and GPU-IOV scheduler/vendor-specific state for selected endpoint functions.

Persistence depends on the hardware reset domain, PCIe reset type, FLR, hot reset, power gating, firmware/BIOS initialization, PSP/SMU ownership, suspend/resume restore, and explicit driver writes. Several names in this range indicate sticky or latched state (`*_STATUS`, `*_STS`, `*_ERR_LOG`, `*_ERR_CLR`, `*_RST_STICKY`, MSI pending/mask registers), but the offset header does not define clear behavior or read side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must stay synchronized with sibling offset, shift/mask, and default headers for the same IP version. It is included through AMDGPU ASIC register include paths under `drivers/gpu/drm/amd/include/asic_reg/nbio`.

Primary integration points are AMDGPU NBIO initialization, PCIe configuration and capability handling, GPU reset and FLR paths, runtime power management, interrupt/MSI setup, RAS/error handling, virtualization/GPU-IOV configuration, SION/NBIF flow-control diagnostics, SMN/ATHUB interaction, and suspend/resume or hotplug recovery paths.

The PCIe endpoint-function blocks align closely with standard PCI configuration-space concepts. They are integration points between Linux PCI core expectations, AMDGPU ASIC-specific register access, firmware-populated strap/default state, and virtualized function exposure. The reset and RAS blocks integrate with recovery paths that must coordinate host-visible PCIe state, internal NBIO state, SMU/PSP handling, and user-visible GPU reset behavior.

## Risks And Edge Cases

- Generated-offset drift can compile cleanly but direct reads or writes to the wrong NBIO register, causing PCIe enumeration failures, broken MSI setup, missed errors, unstable reset recovery, or incorrect virtualization state.
- This chunk starts and ends mid-block. The preceding chunk is needed for the beginning of `nbio_nbif0_bif_misc_bif_misc_regblk`, and the following chunk is needed to complete `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`.
- All macros use base index `5`. A consumer that assumes a different SOC15 base instance for NBIO 7.2.0 will access the wrong register aperture even if the offset constant is correct.
- Many PCIe configuration fields share the same dword offset, for example status/control pairs or MSI address/data aliases. Callers must use proper field masks and access widths to avoid clobbering adjacent fields.
- Reset and FLR registers are sequencing-sensitive. Writing disable, request, pulse-count, hot-reset, or sticky-status registers without the required waits can leave functions partially reset or make recovery failures intermittent.
- Error-log and status-clear registers may have latched or write-one-to-clear semantics not represented here. Generic read-modify-write patterns can lose diagnostic evidence or clear unrelated status.
- PASID, atomic operation, LTR, TPH, ACS, AER, and MSI registers affect PCIe protocol behavior. Bad values can appear as device-specific performance issues, DMA faults, interrupt loss, or upstream PCIe errors.
- GPU-IOV vendor-specific scheduling registers are repeated and mechanically named. A single EPF0/EPF1 offset mismatch could break only one engine scheduler or virtual-function exposure path, making failures topology- or workload-specific.
- SION credit/status registers expose live hardware flow-control state. Polling or diagnostics must tolerate asynchronous changes and avoid treating sampled counters as persistent software-owned state.

## Test Signals

- Build AMDGPU code paths that include NBIO 7.2.0 headers; compile coverage catches renamed, removed, or malformed symbols used by consumers.
- Run generated-header consistency checks: every register offset in this range should have a matching `_BASE_IDX`, all `_BASE_IDX` values should be expected for NBIO 7.2.0, and repeated EPF0/EPF1/EPF2/EPF3 standard PCIe register patterns should align.
- Cross-check this offset header against `nbio_7_2_0_sh_mask.h` and default/reset metadata so field layouts and offsets refer to the same register names.
- On supported hardware, validate PCIe enumeration, BAR sizing, MSI delivery and masking, AER reporting, LTR/TPH negotiation, PASID/ATS-related behavior where applicable, and suspend/resume register restoration.
- Exercise GPU reset paths: FLR, hot reset, function reset pulse counters, sticky reset status, D-state transitions, and full GPU reset recovery should leave PCIe configuration and NBIO status coherent.
- Exercise RAS and diagnostic paths where available: parity/error logging, virtual-wire notification, PASID/atomic/DMA error logs, and status clear paths should preserve unrelated latched state.
- For virtualization-enabled configurations, validate GPU-IOV scheduling/vendor-specific registers for EPF0 and EPF1 under virtual-function creation, reset, engine scheduling, and teardown.
- For NBIF/SION diagnostics, sample buffer status and credit registers under MMIO/DMA load and confirm counters/statuses remain plausible across power-management transitions.
