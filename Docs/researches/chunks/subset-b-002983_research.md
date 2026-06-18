# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 54382-56932

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,128 preprocessor `#define` entries across 2,551 source lines. It has no C functions, structs, enums, variables, allocation, locking, or executable statements.

The range starts inside the global `PCIEMSIX_VECT230_ADDR_HI` register family, after the `MSG_ADDR_HI` shift from the previous chunk. It then completes the MSI-X vector table from the tail of vector 230 through vector 255, defines the eight MSI-X pending-bit-array registers, covers the `nbio_nbif0_rcc_strap_rcc_strap_internal` strap block, covers `nbio_nbif0_bif_rst_bif_rst_regblk` reset and lifecycle interrupt masks, and enters `nbio_nbif0_bif_misc_bif_misc_regblk`. The chunk ends inside `BIF_ATOMIC_ERR_LOG_DEV0_F1`; the remaining mask for `UR_ATOMIC_NR_DEV0_F1` and the clear masks continue after this range.

The source is declarative hardware metadata. It defines field bit positions and masks used by AMDGPU register access code in combination with `nbio_4_3_0_offset.h` and the common AMD register helper macros.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 register interface. For each hardware register field, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to extract or pack the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or compose the field.

This chunk describes several NBIO/BIF/RCC hardware surfaces:

- MSI-X message table and pending-bit-array layout for high vector numbers.
- Strap-derived PCIe/NBIF capability, identity, power-management, reset, SR-IOV, PASID/ATS/ACS/AER, MSI/MSI-X, BAR, and class-code exposure.
- Reset-control and reset-status/interrupt state for endpoint, downstream-port, PF FLR, D3hot-to-D0, power, and PF D-state transitions.
- BIF miscellaneous controls for BIOS strap override, interrupt-line state, outstanding virtual-channel allocation, DMA/GMI/HST/GSI/SDP behavior, bus-master and atomic error logs, PASID checks, performance counters, NBIF power gating, SMN master behavior, doorbell monitor vector routing, INTx/PMI behavior in low-power states, GMI WRR weights, and power-break requests.

The repository path is under a `ceph-client` mirror, but this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The first part of the range is the tail of the global `PCIEMSIX` block:

- `PCIEMSIX_VECT230_*` starts as a boundary fragment with only `ADDR_HI` mask, then `MSG_DATA` and `CONTROL`.
- `PCIEMSIX_VECT231_*` through `PCIEMSIX_VECT255_*` repeat the standard MSI-X vector pattern: `ADDR_LO__MSG_ADDR_LO` shifted by 2 and masked with `0xFFFFFFFC`, `ADDR_HI__MSG_ADDR_HI` full-width, `MSG_DATA__MSG_DATA` full-width, and `CONTROL__MASK_BIT` at bit 0.
- `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` expose full-width `MSIX_PENDING_BITS` fields. Together they represent 256 pending MSI-X bits.

The `rcc_strap_internal` block is strap-oriented configuration metadata:

- `RCC_STRAP1_RCC_DEV0_PORT_STRAP0` through `STRAP14` define device-0 downstream-port identity and PCIe capability exposure. Fields cover device/vendor/subsystem IDs, ARI/ACS/AER, completion-abort handling, interrupt pin, E2E prefix handling, payload/link-width support, ECRC generation/checking, error reporting, Gen2/Gen3/Gen4/Gen5 capability and compliance, L0s/L1 latency, LTR, MSI, timeout behavior, OBFF, lane-equalization presets, PM support, atomics, power budget data, virtual channel and TPH support, 10-bit tags, no-command-completed support, target link speed, port and bus/device/function numbers, modified TS metadata, reset timing, alternate protocol details, CTO logging, DOE, and correctable-error subclass capability.
- `RCC_DEV1_PORT_STRAP*` and `RCC_DEV2_PORT_STRAP*` appear as register-family comments only in this chunk. Their field definitions are absent from the visible range.
- `RCC_STRAP1_RCC_BIF_STRAP0` through `STRAP6` define global BIF/NBIF strap controls, including Gen3/Gen4/Gen5 disable/kill bits, ROM validation, VGA and memory aperture pins, BIOS ROM enable, PX capability, MSI first-BE behavior, error-ignore policy, local-prefix behavior, VF bus-number check, Big APU mode, link-down reset, ROM strap validity, SWUS aperture sizing/prefetchability, hardware/software revision bits, link-reset policy, IOV link-reset disable, DLF, PHY 16GT/32GT enablement, margining controls, S5 access behavior, posted writes, LTR mode, GSI SMN post-write behavior, indirect access disables, link-down DMA-drop policy, power-break deglitching, ASPM/PM/L0s/L1 timers, SMN error data behavior, emergency power reduction, and power-break status timing.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*`, `RCC_STRAP1_RCC_DEV0_EPF1_STRAP*`, and `RCC_DEV0_EPF2/EPF3_STRAP*` provide endpoint-function strap fields. They cover function enablement, legacy-device type, D1/D2 support, SR-IOV VF device ID and supported page size, SR-IOV enable, 64-bit BAR disable, soft-reset behavior, resizable BAR, PASID width and permissions, MSI per-vector masking and multi-message capability, ARI/AER/ACS/ATS, completion-abort handling, DPA/DSN/VC/page request/PASID features, subsystem ID/vendor ID, poisoned advisory nonfatal behavior, power enablement, MSI/MSI-X enablement, MSI clear-pending, SMN error mask enablement, clock PM, true PM status, reset-time reporting, atomic 64-bit and atomic enablement, FLR enablement, PME support, interrupt pin, auxiliary power/current, aperture enablement, class code, and vendor ID.
- Many later endpoint-function families for `DEV0_EPF4` through `DEV2_EPF2` are present only as comments in this slice, which signals generated register names but not visible field definitions.

The `bif_rst_regblk` block defines reset and lifecycle interrupt controls:

- `HARD_RST_CTRL` and `SELF_SOFT_RST` expose reset enables and active reset bits for DSPT, endpoint, SDP port, SION always-on, strap, SWUS shadow, core, and sticky reset domains.
- `BIF_GFX_DRV_VPU_RST`, `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3` define graphics-driver/VPU reset state, reset timer and abort behavior, FLR and D3hot timing, power-gating bypass behavior, spare fields, reset interrupt enables, and reset pending masks.
- `DEV0_PF0_FLR_RST_CTRL` through `DEV0_PF3_FLR_RST_CTRL` define per-PF FLR reset participation for configuration and private reset domains, including sticky reset enablement.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` expose reset, FLR, D3hot/D0, power, and D-state interrupt status bits.
- The matching `*_INTR_MASK` registers control masking for those interrupt sources.
- `BIF_PF_FLR_RST` provides per-PF FLR reset request/state bits.
- `BIF_DEV0_PF[0-3]_DSTATE_VALUE` and `BIF_PORT0_DSTATE_VALUE` expose target and acknowledged D-state values.
- `DEV0_PF[0-3]_D3HOTD0_RST_CTRL` defines per-PF reset handling for D3hot-to-D0 transitions.

The `bif_misc_regblk` portion supplies BIF/NBIF behavior and diagnostics:

- `REGS_ROM_OFFSET_CTRL`, `NBIF_STRAP_BIOS_CNTL`, and `MISC_SCRATCH` define ROM offset, BIOS-driven strap overrides, and scratch storage.
- `INTR_LINE_POLARITY` and `INTR_LINE_ENABLE` describe legacy interrupt-line behavior for device 0.
- `OUTSTANDING_VC_ALLOC` allocates DMA and HST outstanding transaction slots across virtual channels and threshold fields.
- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` cover DMA/GMI/HST/GSI/SDP behavior, including VC4 non-DVM status, chain-lock/chain-break controls, split read stall behavior, atomic length checking, forcing VF-as-PF semantics when SR-IOV enable is low, HDP P2P direct address adjustment, SWUS selection, poison and ACS violation reporting, unsupported SDP command status, response ordering controls, BME-drop disables, request-attribute masks, and message block-level selection.
- `BIFC_BME_ERR_LOG_LB` and `BIFC_RCCBIH_BME_ERR_LOG0` log DMA or RCCBIH activity while bus master enable is low for `DEV0_F0` through `DEV0_F3`, with clear fields at bits 16-19.
- `BIFC_LC_TIMER_CTRL` defines ASPM idle and L1 exit timer scales.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `_F6_F7` define ID-based ordering, relaxed ordering, snoop/no-snoop, and block-level override fields for pairs of functions.
- `BIFC_DMA_ATTR_CNTL2_DEV0`, `BME_DUMMY_CNTL_0`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, `BIFC_PASID_STS`, `BIFC_ATHUB_ACT_CNTL`, `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the `BIFC_PERF_CNT_*_L32BIT` registers define DMA attribute policy, dummy BME behavior, host arbitration, GSI read/write selection and PIO handling, function-level PCIe controls, PASID checking and status, SDP arbitration/disconnect behavior, ATHUB activity controls, and performance counter selection/values.
- `NBIF_REGIF_ERRSET_CTRL`, `BIFC_SDP_CNTL_2`, `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` define register-interface error set behavior, disconnect hysteresis, NBIF master/slave power-gating hysteresis/enables, idleness counting, firmware power-gating exit behavior, SHUBCLK idle hysteresis, D3-only power gating, clock permissions, refclk timing, load masking, and power-gating exit override.
- `SMN_MST_EP_CNTL3`, `SMN_MST_EP_CNTL4`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL5` control zero-byte-enable write/read behavior and all-ones error-response data behavior for endpoint PFs.
- `BIF_SELFRING_BUFFER_VID` and `BIF_SELFRING_VECTOR_CNTL` select doorbell-monitor and RAS interrupt client IDs and control doorbell-monitor interrupt/timestamp behavior.
- `NBIF_STRAP_WRITE_CTRL`, `NBIF_INTX_DSTATE_MISC_CNTL`, and `NBIF_PENDING_MISC_CNTL` control one-time strap writes, INTx/PMI behavior in D-states and non-D0 states, and pending-check bypasses for FLR master/slave paths.
- `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3` define GMI weighted-round-robin modes and weights for entries 0-7.
- `NBIF_PWRBRK_REQUEST` exposes a one-bit NBIF power-break request.
- `BIF_ATOMIC_ERR_LOG_DEV0_F0` and the beginning of `BIF_ATOMIC_ERR_LOG_DEV0_F1` expose unsupported-request atomic error causes for opcode, request-enable-low, length, and non-relaxed-request conditions, with clear fields for the complete F0 block.

## APIs, Types, And Functions

There are no runtime APIs, type declarations, or functions in this chunk. The public interface is the generated macro namespace. These constants are normally consumed with the companion offset header and helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

The macros are untyped integer constants with an `L` suffix. They encode field layout only. They do not encode read/write permissions, write-one-to-clear behavior, sticky status semantics, reset defaults, polling requirements, register access ordering, or privilege rules.

## Control Flow

This header has no local control flow. Runtime flow is external to the file:

1. AMDGPU code selects a register address from `nbio_4_3_0_offset.h`.
2. The caller reads, writes, polls, or composes the register value using the `__SHIFT` and `_MASK` constants from this header.
3. NBIO/BIF/RCC hardware implements the side effect, such as interrupt routing, pending-bit updates, strap-derived capability exposure, reset assertion/deassertion, D-state transition acknowledgement, power-gating entry/exit, error logging, PASID checking, or GMI arbitration.

Important represented flows include MSI-X setup and masking, PF/port strap interpretation during initialization, SR-IOV capability exposure, PF FLR and D3hot-to-D0 reset sequencing, reset interrupt masking/status handling, bus-master and atomic error diagnosis, power management and power-gating policy, SMN master error response behavior, doorbell-monitor/RAS interrupt routing, and performance-counter sampling.

## State And Persistence Behavior

The header stores no software state. It describes hardware state held in NBIO/BIF/RCC registers. Persistence and reset behavior depend on the GPU reset domain, strap load/reload, firmware initialization, platform policy, suspend/resume save-restore, PF/VF lifecycle, FLR, D-state transitions, and explicit AMDGPU writes.

The MSI-X vector address/data/control and PBA fields affect interrupt delivery until reprogrammed or reset. The vector mask bit suppresses delivery for one vector, while the PBA fields represent pending interrupt state.

Strap fields are generally derived from hardware straps, fuses, firmware, or BIOS override mechanisms and become the basis for PCIe capability and identity presentation. In this chunk, strap state influences device IDs, vendor/subsystem IDs, link capability, power-management support, reset timing, MSI/MSI-X capability, SR-IOV/PASID/ATS/ACS/AER exposure, BAR behavior, aperture support, and class codes.

Reset and D-state registers represent transition state. Some bits enable participation of reset domains; status/mask registers report or suppress reset-related interrupts; target/acknowledge D-state fields reflect ongoing device and port power-state transitions.

Miscellaneous BIF controls are a mix of persistent configuration, live policy, counters, and sticky diagnostic state. Error-log registers such as `BIFC_BME_ERR_LOG_LB`, `BIFC_RCCBIH_BME_ERR_LOG0`, and `BIF_ATOMIC_ERR_LOG_DEV0_F0/F1` contain status bits paired with clear bits. Performance-counter registers expose sampled low 32-bit counter values. Power-gating controls, GMI weights, and outstanding VC allocation fields can affect live traffic behavior until changed or reset.

## Dependencies And Integration Points

This chunk depends on the generated AMD NBIO 4.3.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies matching register offsets and base indices.
- Other generated NBIO headers, including default/reset-value metadata where present.
- AMDGPU register helper macros that assume the generated `__SHIFT` and `_MASK` naming convention.

Observed include-level integration for the NBIO 4.3.0 header set in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, SMU 13.0.0/13.0.7 power-management files, and DCN 3.2 display resource files. Semantically, these masks integrate with Linux PCI/PCIe, MSI/MSI-X, SR-IOV, AER, ACS, ATS, PASID/IOMMU, power-management, reset, and interrupt-handling paths.

## Risks And Edge Cases

- The chunk starts inside `PCIEMSIX_VECT230_ADDR_HI`; the paired shift for `MSG_ADDR_HI` is outside this range. The final merge lane must not treat vector 230 as a complete vector definition from this chunk alone.
- The chunk ends inside `BIF_ATOMIC_ERR_LOG_DEV0_F1`; the `UR_ATOMIC_NR_DEV0_F1` mask and clear masks continue in the next chunk. Consumers and final research must reconcile that boundary.
- Generated strap definitions are broad and high-impact. A wrong mask can misrepresent PCIe identity, SR-IOV, PASID/ATS, AER/ACS, MSI/MSI-X, BAR sizing, or link capability without causing a compile failure.
- Many reset and interrupt fields differ only by PF index or event type. Mixing FLR, D3hot/D0, power, PF D-state, and instance-reset fields can cause missed interrupts, stuck reset state, or reset of the wrong domain.
- Status/clear pairs in BME and atomic error logs use low bits for status and bits 16-19 for clear requests. Treating them as ordinary read-modify-write storage can accidentally clear diagnostic evidence.
- MSI-X address low fields intentionally mask off low alignment bits. Treating the field as a raw byte address can corrupt vector programming.
- Strap comments for many devices/functions appear without field definitions in this slice. A report or tooling pass should distinguish present macros from comment-only register names.
- Power-gating, D-state, and link-management bits can affect device reachability and timing. Incorrect writes may surface as hangs, lost interrupts, or resume/reset regressions rather than immediate register-access faults.
- Performance-counter and arbitration fields influence observation and traffic scheduling; bad masks can lead to misleading diagnostics or unfair/incorrect traffic weighting.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage of AMDGPU code that includes the NBIO 4.3.0 headers. Missing or malformed generated macros should fail compilation in direct consumers.
- Generated-header consistency checks against the authoritative NBIO 4.3.0 register database, including offset-to-mask pairing with `nbio_4_3_0_offset.h`.
- Pattern checks that complete MSI-X vector definitions from `PCIEMSIX_VECT231` through `PCIEMSIX_VECT255` all have the expected four-register field pattern and masks.
- Boundary checks that vector 230 is completed by the previous chunk and `BIF_ATOMIC_ERR_LOG_DEV0_F1` is completed by the next chunk.
- Strap decode validation against expected PCIe configuration space: vendor/device/subsystem IDs, class codes, link capabilities, MSI/MSI-X, SR-IOV, PASID, ATS, ACS, AER, BAR, and power-management capability exposure.
- Runtime reset tests that exercise PF FLR, D3hot-to-D0, power, and PF D-state transitions while checking status and mask behavior.
- MSI-X tests that program high-numbered vectors 231-255, toggle per-vector masks, inspect PBA bits, and confirm interrupt delivery and quiescing.
- Error-path tests that force or observe bus-master-low and unsupported atomic conditions, then verify status and clear bits for `BIFC_BME_ERR_LOG_LB`, `BIFC_RCCBIH_BME_ERR_LOG0`, and `BIF_ATOMIC_ERR_LOG_DEV0_F0/F1`.
- Power-management and resume tests that cover NBIF power-gating hysteresis, clock permission, refclk cycle, power-break, INTx/PMI-in-D-state, and pending-check controls.
- Performance-counter and arbitration diagnostics that verify BIFC counter selection/value fields and GMI WRR weight fields decode as expected on supported hardware.
