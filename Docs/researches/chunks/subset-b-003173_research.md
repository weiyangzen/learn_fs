# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 31793-34270

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It covers 2,478 source lines and 2,129 `#define` macros. The macros expose bit positions (`__SHIFT`) and bit masks (`_MASK`) for NBIO/BIF PCIe, RCC, strap, endpoint, downstream, GPU-IOV, doorbell, interrupt, scratch, and control registers.

The chunk starts in the middle of `BIFPLR6_PCIE_ESM_CAP_5` after earlier shift definitions for 19.0 GT/s through 20.5 GT/s were emitted in the previous chunk. It ends in the middle of `BIF_BX0_BIF_DOORBELL_INT_CNTL`, before the final mask for `SET_ATH_RAS_INTR_STATUS_WHEN_RB_ENABLE` and subsequent BIF_BX0 registers. Merge/reconciliation must therefore join this document with neighboring chunks for a complete per-file report.

Although the source path is under a `ceph-client` mirror, this file is AMDGPU hardware register metadata. It contains no Ceph, filesystem, networking, or distributed-storage behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` provides symbolic field extraction and field construction constants for AMD NBIO 7.2.0 registers. Driver code combines these macros with sibling offset definitions from `nbio_7_2_0_offset.h` and AMDGPU register-access helpers to read, update, or program hardware registers without embedding numeric bit positions in call sites.

This specific chunk describes several related hardware surfaces:

- PCIe physical-layer enhanced capability fields for 16 GT/s, margining, CCIX extended speed mode, and data-link features.
- BIF indexed access windows, BIOS/SBIOS scratch registers, MMIO remap CAM fields, and engine interrupt status/control bits.
- RCC strap fields that define hardware-default PCIe, BAR, SR-IOV/GPU-IOV, PASID, ATS, ACS, MSI/MSI-X, FLR, DPA, LTR, ASPM, link speed, aperture, and function-exposure policy.
- RCC endpoint/downstream/root/common control fields for PCIe error handling, LTR/DPA, requester IDs, link-speed controls, VDM, margining, peer apertures, host bus numbering, xDMA, and GPU virtualization.
- BIF_BX0 bus, reset, interrupt, CLKREQ pad, feature, and doorbell control fields.

The header does not describe reset values, legal value ranges beyond mask width, read/write permissions, side effects, or required hardware sequencing.

## Important Macro Families

The opening `BIFPLR6_PCIE_ESM_CAP_5`, `BIFPLR6_PCIE_ESM_CAP_6`, and `BIFPLR6_PCIE_ESM_CAP_7` families define one-bit ESM capability positions for extended speed steps from 19.0 GT/s through 28.0 GT/s. Each capability bit has a matching shift and mask, except that this chunk begins after some `BIFPLR6_PCIE_ESM_CAP_5` shifts from the prior chunk. These fields are capability bitmap metadata, not a runtime speed-selection API by themselves.

The `BIFPLR6_PCIE_DLF_ENH_CAP_LIST`, `BIFPLR6_DATA_LINK_FEATURE_CAP`, and `BIFPLR6_DATA_LINK_FEATURE_STATUS` families define enhanced capability-list IDs/version/next-pointers and local/remote data-link feature negotiation fields. They include scaled-flow-control support, data-link feature support bitmaps, exchange enable, remote support, and validity.

The `BIFPLR6_PCIE_PHY_16GT_ENH_CAP_LIST`, `BIFPLR6_LINK_*_16GT`, parity mismatch, and `BIFPLR6_LANE_0` through `BIFPLR6_LANE_15_EQUALIZATION_CNTL_16GT` families describe PCIe 4.0-style 16 GT/s capability, status, parity, and per-lane equalization preset fields. Link status exposes equalization completion, phase success, and link equalization request bits. Per-lane equalization controls repeat the same downstream/upstream transmit preset layout across 16 lanes.

The `BIFPLR6_PCIE_MARGINING_ENH_CAP_LIST`, `BIFPLR6_MARGINING_PORT_*`, and per-lane `BIFPLR6_LANE_<n>_MARGINING_LANE_CNTL/STATUS` families expose PCIe lane margining support. Each lane has receiver number, margin type, usage model, and payload fields for control and corresponding status. These fields are replicated mechanically for lanes 0 through 15.

The `BIFPLR6_PCIE_CCIX_*` families describe CCIX/ESM capability headers, capability flags, required speed support, status, control, and transaction-format enablement. Key fields include alternate protocol negotiation, extended format support, ESM required capability bits for 2.5/5/8/16/20/25 GT/s, ESM current data rate, calibration complete, perform calibration, ESM enable, equalization timeout selectors, link reach target, retimer present, and optimized TLP format enablement.

The `BIFPLR6_ESM_LANE_<n>_EQUALIZATION_CNTL_20GT` and `_25GT` families repeat per-lane downstream/upstream transmit-preset fields for higher extended data rates. The identical two-field layout across 16 lanes makes generated-name consistency important: a lane-number or speed suffix error could silently program the wrong link training field.

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_SYSDEC` address blocks define fields for PF MMIO/RSMU indexed access windows, two PCIE indexed access windows, SBIOS scratch dwords, BIOS scratch dwords, RLC/VCE/UVD interrupt controls, and eight GFX MMIO register CAM/remap pairs. These fields allow indexed register access, firmware/BIOS communication, engine interrupt classification, and GFX MMIO remapping.

The `nbio_nbif0_rcc_strap_BIFDEC1` block is the largest configuration-policy region in this chunk. `RCC_STRAP0_RCC_BIF_STRAP0` through `STRAP5`, device port straps, and endpoint-function straps for EPF0/EPF1 encode link-generation disable/kill bits, VGA/ROM/aperture settings, PX and big-APU mode, error-ignore behavior, PME compliance, DLF/16GT/margining enablement, ASPM/L0s/L1/LDN timing, link reset policy, power-break/emergency power behavior, AER/ACS/ARI capability exposure, max payload/link-width support, subsystem IDs, BAR sizing, class/vendor/device IDs, PASID/ATS/atomic/DPA/DSN/VC capability bits, MSI/MSI-X capability policy, FLR and power-management support, SR-IOV VF aperture sizing, VF MSI capability, GPU-IOV VSEC revision, and BAR compliance behavior.

The `nbio_nbif0_rcc_ep_dev0_BIFDEC1`, `rcc_dwn_dev0`, and `rcc_dwnp_dev0` blocks define endpoint and downstream PCIe control fields. They include error interrupt enable/status bits, unsupported-request and malformed atomic operation handling, invalid PASID handling, hidden configuration decoding, LTR transmit controls, F0/F1 DPA capability/control/substate allocations, PME service timing, transmit ordering/non-snoop/TPH controls, requester ID fields, AER header log timeout/status bits for functions 0 through 7, RX error masking, link speed controls, downstream bus/config controls, lane-speed/link-control fields, and LTR message capture from the endpoint.

The `nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1` block exposes per-function RCC error logs, doorbell aperture enables, config memory-size dwords, reserved config storage, and GPU-IOV function identifiers. These fields are relevant to SR-IOV/GPU-IOV virtualization, error diagnosis, and per-function aperture setup.

The `nbio_nbif0_rcc_dev0_BIFDEC1` block covers common RCC device control. Important fields include interrupt control, BACO miscellaneous control, reset enable, VDM support and request/response data fields, margining parameter controls, GPU-IOV region selection, GPU host-VM enable, console IOV mode and VF numbering, peer register ranges, broad RCC bus controls, config aperture sizing and base, xDMA base address low/high parts, feature-control knobs, bus number and device/function number lists, host bus capture, peer framebuffer offsets, common link controls, endpoint requester ID restore, LTR switch latency, and memory-hub arbitration mode/priority.

The final `nbio_nbif0_bif_bx_BIFDEC1` section in this chunk defines BIF_BX0 strap, indirect-access disable, bus coherency, traffic class, zero-byte-enable, HDP flush, reset, MM config, interrupt, CLKREQ pad, feature, doorbell control, and partial doorbell interrupt-control fields. These are integration fields between NBIO, host doorbells, HDP flushing, interrupt handling, VGA compatibility, and RAS doorbell notification.

## APIs, Types, And Functions

There are no callable APIs, structs, enums, variables, locks, allocations, or functions in this chunk. The public interface is the generated preprocessor namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a named field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted mask for the same field.

Consumers typically use these macros with AMDGPU bitfield helpers, register offsets from `nbio_7_2_0_offset.h`, and register I/O helpers such as SOC15-style read/modify/write paths. The macros are meaningful only when paired with the matching register offset, correct NBIO IP version, correct hardware instance, and the relevant access path, such as direct MMIO or indexed PCIE/RSMU access.

## Control Flow

This header has no local runtime control flow. Runtime flow is external and generally follows this pattern:

1. AMDGPU detects an ASIC/IP block that uses NBIO 7.2.0 metadata.
2. Driver code chooses a register offset from the matching offset header.
3. The code reads or writes the register through direct or indexed register helpers.
4. The code uses the shift/mask macros in this header to isolate status bits, compose field values, or preserve unrelated bits during read-modify-write.
5. Hardware applies the requested configuration or reports live status, such as link training, margining, interrupts, doorbell activity, RAS events, error logs, or virtualization aperture state.

The implied hardware flows include PCIe capability enumeration and negotiation, link equalization, lane margining, ESM calibration, CCIX/optimized TLP feature enablement, BIOS-to-driver scratch handoff, RLC/VCE/UVD hang/FLR signaling, GFX MMIO remapping, strap-driven function and capability exposure, endpoint/downstream PCIe error reporting, DPA/LTR power policy, peer aperture and host bus-number handling, xDMA address programming, doorbell routing, and RAS/ATHUB interrupt propagation.

## State And Persistence Behavior

The header itself owns no memory, persists no state, and performs no I/O. It describes fields in hardware registers whose persistence is determined by firmware initialization, straps, reset domains, PCIe reset type, function-level reset, hot reset, BACO/power-gating state, suspend/resume restore, and explicit driver writes.

Several fields represent strap-derived or firmware-populated policy and may be effectively static after boot unless the hardware supports software overrides. Examples include link speed capability exposure, BAR and aperture sizing, class/vendor/device identity, MSI/MSI-X capability bits, PASID/ATS/atomic/ACS/AER/FLR support, DPA/LTR support, SR-IOV/GPU-IOV VF aperture sizing, and power-management support.

Other fields represent live or latched state. Examples include link equalization status, remote data-link feature status, lane margining status, ESM calibration/current-rate status, PCIe error interrupt status, AER header-log timeout bits, RLC/VCE/UVD interrupt classifications, doorbell interrupt status/clear/disable bits, RAS controller and ATHUB error-event status, host bus number capture, error logs, and pending transaction/doorbell behavior. The header does not indicate which status bits are read-only, write-one-to-clear, sticky until reset, sticky until explicit clear, or sampled asynchronously.

Scratch registers are intentionally state-bearing handoff locations between BIOS/SBIOS, firmware, and driver code. Because their semantics are outside this generated mask header, consumers must rely on platform/driver conventions before treating a scratch bit as persistent or authoritative.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must stay synchronized with the companion offset and default/reset-value headers for the same IP version. A field mask that is valid for NBIO 7.2.0 is not automatically valid for another NBIO revision even when register names look similar.

Primary integration points include:

- AMDGPU NBIO, PCIe, reset, RAS, power-management, virtualization, and interrupt code paths.
- Linux PCI behavior that observes PCIe capabilities, AER/ACS/ARI/ATS/PASID/MSI/MSI-X/FLR/DPA/LTR exposure through configuration space.
- Firmware/BIOS initialization that sets strap-derived hardware policy and scratch registers.
- SMU/PSP and power-management flows that own BACO, reset, DPA, LTR, link, and power-state behavior.
- GPU-IOV/SR-IOV paths that configure VF apertures, function IDs, doorbells, memory sizes, and per-function capabilities.
- Doorbell and HDP integration where self-ring, translation checks, interrupt generation, flush stalls, and outstanding NP limits affect command submission and interrupt delivery.
- RAS and ATHUB event handling where BIF doorbell interrupt status, RAS controller status, and ATHUB error-event status feed higher-level error recovery.

The generated names also integrate with source generation and review tooling. Mechanical repetition across lanes, speeds, functions, and straps makes consistency checks more valuable than manual inspection of individual macro values.

## Risks And Edge Cases

- This chunk starts and ends mid-family. A standalone analysis of only this range lacks the first `BIFPLR6_PCIE_ESM_CAP_5` shift definitions and the tail of `BIF_BX0_BIF_DOORBELL_INT_CNTL`.
- Shift/mask drift can compile successfully but program the wrong hardware bits, causing link-training failures, incorrect capability exposure, broken error handling, bad doorbell routing, or virtualization-specific failures.
- Many fields are capability or strap fields rather than ordinary software controls. Treating strap-derived bits as freely mutable can desynchronize driver assumptions from firmware and hardware policy.
- PCIe link, ESM, equalization, and margining fields are timing-sensitive. Updating fields outside the expected training, calibration, or diagnostic window can produce intermittent link instability.
- Error status and clear bits may have write-one-to-clear or latch semantics not represented in the macro names. Generic read-modify-write code can accidentally clear evidence or mask unrelated events.
- Doorbell and HDP flush controls affect command submission visibility and interrupt generation. Incorrect settings can appear as lost interrupts, stale memory visibility, or hangs under load.
- GPU-IOV/SR-IOV fields are repeated across functions and aperture types. A single function suffix, BAR-size, VF-stride, or aperture mask mismatch can fail only in virtualized configurations.
- Scratch registers are shared convention surfaces. Reusing a full-width scratch mask without respecting BIOS/firmware ownership can corrupt platform handoff state.
- Several full-width `0xFFFFFFFFL` masks describe opaque dwords rather than validated software fields. Callers still need register-specific rules for valid values and side effects.
- Some names refer to legacy engines such as VCE/UVD while modern ASIC software may map them into newer engine abstractions. Tests must verify the active driver path for the target ASIC rather than assuming all named engines are present.

## Test Signals

- Build AMDGPU code paths that include NBIO 7.2.0 headers; compile coverage catches malformed macro names and missing symbols used by consumers.
- Run generated-header consistency checks: every field should have a matching shift/mask pair, masks should correspond to their shifts and widths, lane families should be complete for lanes 0-15, and repeated 20 GT/s/25 GT/s ESM layouts should match.
- Cross-check this shift/mask chunk against `nbio_7_2_0_offset.h` so every register family used here has a matching offset symbol in the same IP version.
- Validate PCIe enumeration on supported hardware: link speed/width, AER/ACS/ARI/ATS/PASID/MSI/MSI-X/FLR/DPA/LTR capability exposure, BAR sizing, ROM/doorbell aperture behavior, and class/vendor/device IDs should match expected strap policy.
- Exercise link and PHY diagnostics where supported: 16 GT/s equalization status, lane margining readiness/control/status, ESM calibration/current-rate reporting, and CCIX/optimized TLP capability fields.
- Exercise interrupt and error paths: corrected/non-fatal/fatal/user/misc/power-state interrupts, AER header log timeout bits, RLC/VCE/UVD interrupt classes, RAS controller interrupt status, ATHUB error-event status, and doorbell interrupt clear/disable behavior.
- Validate reset and power transitions: FLR, hot reset, link reset, BACO, suspend/resume, D-state transitions, LTR/DPA changes, and host bus-number restoration should leave NBIO/RCC fields coherent.
- Under GPU-IOV/SR-IOV configurations, validate VF aperture sizing, function identifiers, doorbell aperture enables, config memory-size fields, peer offsets, console IOV mode, and VF reset behavior.
- Under command-submission and memory-pressure workloads, watch for HDP flush, doorbell, outstanding-request, non-snoop, relaxed-ordering, and xDMA-related regressions.
