# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 19895-22340

## Scope

This chunk is the 2,446-line tail of the generated AMDGPU NBIO 6.1 default-value header. It contains C preprocessor constants and the file-closing `#endif` for `_nbio_6_1_DEFAULT_HEADER`. There are no C functions, structs, enums, global variables, allocations, locks, loops, branches, or direct I/O operations in this range.

The range starts in the middle of a DesignWare E12MP PHY x4 default block for `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANE1`, continues through lane 2, lane 3, shared `SUPX`, `LANEX`, and `RAWLANEX` PHY defaults, then covers the `KPFIFO3` and `KPNP3` link/PHY directory defaults, per-VF NBIF/BIF defaults for virtual functions 0 through 15, final SYSHUB indirect defaults, and the closing include guard.

Although this repository path is under a `ceph-client` source tree, this file is AMD GPU register metadata for DRM/AMDGPU. It does not implement Ceph distributed-filesystem behavior.

## Purpose

`nbio_6_1_default.h` publishes generated reset/default values for registers in the NBIO 6.1 IP block. Runtime code combines these `_DEFAULT` macros with sibling offset and shift/mask headers when it needs generated hardware metadata for initialization, diagnostics, register programming, or generated-table consistency.

This chunk supplies defaults for several hardware areas:

- `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANE1` tail and `RAWLANE2`/`RAWLANE3` full lane defaults: PCS/PMA transfer overrides, RX/TX override inputs and outputs, receive adaptation state, AON calibration offsets, DFE tap defaults, IRQ status/clear/mask defaults, PMA lane override defaults, TX/RX finite-state-machine controls, loss-of-signal masking, and RX data-enable override defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_3_SUPX`: shared PHY/supervisor defaults such as ID code values, reference-clock overrides, MPLLA/MPLLB override inputs, PLL power-control timing thresholds, spread-spectrum clocking defaults, analog override/status defaults, and RTUNE control/status defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_3_LANEX`: generic per-lane defaults for ASIC lane override inputs, TX/RX power states, power-up timings, LBERT controls, RX VCO calibration, CDR controls, adaptation configuration/status, DFE/slicer offsets, RX statistic counters, and link counters.
- `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANEX`: generic raw-lane defaults mirroring the concrete raw-lane register families for PCS transfer, FSM, AON adaptation, IRQ, PMA transfer, and TX/RX control defaults.
- `nbio_lcu_kpfifo_kpfifo3_kpfifo_dir`: `KPFIFO3` primary TX FIFO and PCS/PMA soft-reset defaults.
- `nbio_lcu_kpnp_kpnp3_kpnp_dir`: `KPNP_SNPS3` PHY information, lane request/status, PMA control, PHY/lane soft-reset, and reset-control defaults.
- `nbio_nbif_bif_bx_dev0_epf0_vf{0..15}_SYSPFVFDEC`: per-virtual-function indirect MMIO index/data register defaults.
- `nbio_nbif_bif_bx_dev0_epf0_vf{0..15}_BIFPFVFDEC1`: per-virtual-function BIF defaults for BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP coherency flush controls, GPU HDP flush request/done, transaction-pending status, transmit/receive mailbox buffers, mailbox control/interrupt control, and VM/HV mailbox state.
- `syshub_mmreg_ind_syshubind`: SYSHUB deep-sleep and clock-domain defaults, DMA/HST QoS and client-control defaults, clock-gating controls, scratch/default mask values, and NIC400 function-modifier defaults.

Most values are zero reset/defaults. Non-zero defaults in this range are the important review anchors: lane/PHY tuning values such as `0x80` DFE/AON offsets, RX/TX control values, PLL timing thresholds, KPNP PMA and lane reset defaults, VF doorbell aperture control `0x00000100`, SYSHUB QoS `0x0000001e`, SYSHUB DMA client control `0x20200000`, clock-gating/deep-sleep timer values, and the PHY/shared ID defaults.

## Important APIs, Types, And Functions

This chunk defines no callable APIs or C types. The public interface is the generated macro namespace. The macros are compile-time constants named after hardware registers with a `_DEFAULT` suffix.

The matching register addresses live in `nbio_6_1_offset.h`, and field layouts live in `nbio_6_1_sh_mask.h`. Consumers normally use the offset and field headers with AMDGPU helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `WREG32_FIELD15`, and `REG_SET_FIELD`. This default header is included directly by `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` and by Vega power-management include bundles such as `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`.

Relevant integration examples in the source tree include:

- `nbio_v6_1.c` includes `nbio_6_1_default.h`, `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`, then programs NBIO doorbell apertures, HDP flush remapping, interrupt control, PCIe ASPM/LTR, and clock-gating behavior.
- `nbio_v6_1_set_reg_remap()` uses the VF0 HDP memory coherency flush register offset as the SR-IOV VF/MMIO remap fallback, tying the per-VF register family in this chunk to KFD/MMIO remapping behavior.
- `mxgpu_ai.c` uses NBIO 6.1 offset and mask metadata for host/VF mailbox handling in SR-IOV paths. This chunk supplies the reset/default values for the analogous per-VF mailbox buffer/control registers.
- `psp_v3_1.c`, `vega10_inc.h`, and `vega12_inc.h` include NBIO 6.1 register headers as part of the Vega ASIC register contract used by firmware, PSP, and power-management paths.

## Control Flow

There is no local control flow in the header. The effective runtime flow is external:

1. ASIC-specific AMDGPU, PSP, virtualization, or power-management code includes the generated NBIO 6.1 headers.
2. The caller selects a register through the offset header, optionally compares or documents the reset value through this default header, and composes fields with the shift/mask header.
3. Driver code reads or writes the hardware through SOC15, PCIe, SMN, or MMIO helper paths.
4. Hardware, firmware, PCIe link-training logic, SR-IOV virtualization, HDP cache-coherency flush machinery, or SYSHUB fabric state observes the register value.

The PHY-related defaults affect link bring-up indirectly: firmware and low-level hardware sequencing can use reset values for PLLs, lane power states, CDR, RX adaptation, DFE offsets, PMA/PCS transfer, soft reset, and IRQ signaling. The VF BIF defaults affect the initial state seen by PF/VF mailbox and HDP flush paths. SYSHUB defaults affect fabric clocking, QoS, idle/deep-sleep, and NIC400 behavior before any explicit driver override.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It names hardware reset/default state. Persistence is therefore governed by GPU reset domains, power gating, firmware initialization, PCI function-level reset, hot reset, suspend/resume, SR-IOV PF/VF lifecycle, and explicit driver or firmware writes.

The state represented by this chunk includes:

- PCIe/PHY lane electrical and protocol state: CDR, VCO calibration, DFE offsets, slicer controls, RX adaptation, lane power states, loopback/BERT controls, IRQ status/clear/mask bits, and PCS/PMA override wiring.
- Shared PHY and PLL state: reference-clock selection, MPLLA/MPLLB override inputs, power-up/down timing thresholds, spread-spectrum clocking, RTUNE controls, and analog status/override defaults.
- Link-controller sideband state: KPFIFO3 FIFO/lane control and KPNP3 lane request/status, PMA control, soft-reset, and reset-control defaults.
- Per-VF BIF state: VF-local indirect MMIO selector/data registers, doorbell self-ring GPA aperture programming, HDP coherency flush request/done state, transaction-pending state, and PF/VF mailbox buffers/control.
- SYSHUB fabric state: deep-sleep controls, QoS/client-control defaults for DMA/HST clocks, clock-gating controls, scratch/mask defaults, and NIC400 function modifiers.

The `_DEFAULT` constants do not identify which registers are read-only, write-one-to-clear, sticky, firmware-owned, volatile status, or driver-programmable. That information must come from field masks, hardware documentation, and the consuming code paths.

## Dependencies And Integration Points

Direct dependencies are the generated NBIO 6.1 sibling headers:

- `nbio_6_1_offset.h` provides addresses/base indices for the same register names without `_DEFAULT`.
- `nbio_6_1_sh_mask.h` provides field shifts and masks, including the field definitions for KPFIFO, KPNP, mailbox/control, HDP flush, SYSHUB clock-gating, and PHY control/status registers.
- `nbio_6_1_smn.h` provides SMN address constants used by PCIe/NBIO paths in the same IP generation.

Broader integration points are:

- AMDGPU NBIO 6.1 initialization and function table plumbing through `nbio_v6_1_funcs`.
- PCIe link management, ASPM/LTR programming, and clock-gating behavior in `nbio_v6_1.c`.
- Doorbell aperture setup, self-ring doorbell aperture programming, and interrupt-ring doorbell range setup.
- HDP coherency flushing and KFD MMIO remapping, including SR-IOV-specific VF register remap behavior.
- SR-IOV/MxGPU mailbox communication between guest VF and host/PF firmware or hypervisor components.
- PSP and power-management include bundles for Vega-generation ASICs.
- Low-level firmware or bring-up tooling that validates generated PHY reset values against the hardware register database.
- SYSHUB fabric clock/QoS/idle behavior and NIC400 interconnect integration.

## Risks And Edge Cases

- Generated default drift can be hard to catch in ordinary C builds. Macro names may remain valid while default values silently change, leaving hardware bring-up, diagnostics, or generated-register validation inconsistent with the ASIC database.
- This chunk starts mid-block. The final per-file report should merge adjacent chunks to describe the complete `DWC_E12MP_PHY_X4_NS_X4_3` PHY default set rather than treating line 19895 as a natural hardware boundary.
- The DWC PHY defaults include sensitive analog/PHY tuning values. Incorrect PLL timing, RX adaptation, CDR, VCO calibration, DFE, slicer, LOS mask, PMA/PCS override, or lane power-state defaults can affect PCIe link training, stability, speed negotiation, error rate, low-power transitions, and resume behavior.
- Many PHY status and IRQ defaults are zero, while `RESET_RTN_REQ` defaults to one in the raw-lane IRQ block. Consumers must not assume every zero-valued default means "safe to write zero"; status/clear and request semantics may be write-sensitive.
- Per-VF blocks are highly repetitive from VF0 through VF15. Mechanical generation or manual edits can accidentally change one VF while leaving the others unchanged. VF0 is especially important because current NBIO/KFD remap logic references VF0 HDP coherency flush offsets.
- VF mailbox defaults are all zero, which is a sane reset state, but mailbox runtime protocols rely on strict valid/ack ownership and interrupt-control semantics. Treating default values as protocol state after reset can race with host firmware or hypervisor updates.
- `DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT` is `0x00000100` for every VF. Any incorrect interpretation of that non-zero reset/default can affect doorbell aperture enable/mode/size programming, guest isolation, or self-ring notification behavior.
- HDP flush request/done and transaction-pending defaults are stateful hardware synchronization points. Polling code must handle reset, VF lifecycle, and timeout cases rather than relying only on the default constants.
- SYSHUB defaults such as DMA QoS `0x1e`, client control `0x20200000`, clock-gating `0x00082000`, and MGCG `0x80` can influence fabric latency, power, and idle detection. Misaligned defaults can cause performance, power, or suspend/resume regressions.
- The closing `#endif` is part of this chunk. Any truncation before it breaks the include guard and should fail compilation; duplicate or misplaced definitions around the tail can create subtle macro redefinition or stale-metadata hazards.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with NBIO 6.1/Vega support enabled. Syntax errors, missing include guard closure, or macro redefinition issues should surface at compile time.
- Run generated-register consistency checks against the authoritative NBIO 6.1 register database, specifically covering the `DWC_E12MP_PHY_X4_NS_X4_3` lane/shared/generic defaults, `KPFIFO3`, `KPNP3`, VF0-VF15 BIF defaults, and final SYSHUB indirect defaults.
- Boot affected Vega/NBIO 6.1 hardware and confirm PCIe link training, negotiated width/speed, ASPM/LTR behavior, suspend/resume, and warm-reset behavior remain stable.
- Exercise SR-IOV/MxGPU flows with multiple VFs. Check PF/VF mailbox valid/ack behavior, mailbox interrupts, guest reset, VF teardown/recreate, and host-driven messages.
- Validate KFD/MMIO remapping and HDP coherency flush behavior, including the VF path that uses `BIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` as the remap fallback.
- Run graphics, compute, and DMA workloads that stress doorbells, interrupt rings, SDMA, and HDP flushes while monitoring for hangs, stale cache/coherency symptoms, and timeout diagnostics.
- Check power-management and fabric behavior through clock-gating, deep-sleep, and SYSHUB idle paths, especially after runtime suspend/resume and under mixed DMA/display/compute load.
- For PHY-specific modifications, use hardware link diagnostics and error counters to verify CDR/VCO/adaptation behavior, link error rate, retraining frequency, and low-power lane transitions.

## Chunk-Specific Notes For Merge

This is the final chunk of `nbio_6_1_default.h` and includes the closing `#endif`. It should be merged with preceding chunks before producing the final per-file research document because the first lines here continue an existing DWC E12MP PHY raw-lane block. Preserve that this slice covers the tail of the generated NBIO 6.1 default-value ABI: DWC PHY x4 instance 3 lane/shared/generic defaults, KPFIFO3/KPNP3 defaults, all `BIF_BX_DEV0_EPF0_VF0` through `VF15` per-VF defaults, and final SYSHUB indirect defaults.
