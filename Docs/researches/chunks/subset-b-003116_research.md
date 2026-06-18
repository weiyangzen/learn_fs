# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 117357-118975

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 1,364 `#define` field-layout macros, 229 register comments, and 8 address-block comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the tail of a downstream PCIe-control group, covering `DN_PCIE_CNTL` leftovers plus `DN_PCIE_CONFIG_CNTL`, `DN_PCIE_RX_CNTL2`, `DN_PCIE_BUS_CNTL`, and `DN_PCIE_CFG_CNTL`. It then covers RCC downstream/PF/VF decode fields, BIF PF and PF/VF decode fields, GDC fields, a small GFX MSI-X table block, and the end of the `syshub_mmreg_ind_syshubind` field definitions. The chunk ends at the file trailer `#endif`, so this is the final slice of `nbio_7_0_sh_mask.h`.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMDGPU's generated NBIO 7.0 register interface. For each hardware register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

This slice describes NBIO, BIF, RCC, GDC, MSI-X, doorbell, mailbox, HDP coherency, GPU virtualization, and system-hub clock/QoS/register-interconnect fields. Despite the repository path being under a Ceph client source mirror, this chunk is GPU PCIe/NBIO register metadata and has no filesystem behavior.

## Important Macro Families

The opening downstream PCIe and `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1` groups define fields for PCIe error reporting, receiver error-ignore policy, link-speed strap enables, link-bandwidth notification disable, multifunction strap state, LTR message capture, hidden config-register decode enables, FLR extension mode, immediate PMI disable, and AER completion-timeout reporting controls. These are low-level PCIe policy knobs used by code that configures or diagnoses downstream/root-complex behavior.

The `nbio_nbif0_rcc_dev0_BIFPFVFDEC1` group covers RCC per-function or SR-IOV-visible state: invalid SR-IOV register access and doorbell-read access status, doorbell aperture enable, configuration memory size/reserved fields, and `RCC_IOV_FUNC_IDENTIFIER` fields for function identity and IOV enable state.

The main `nbio_nbif0_rcc_dev0_BIFDEC1` group describes RCC control-plane state. It includes invalid-SRIOV-access interrupt enable, BACO ROM/AZ request disables, DB aperture reset enable, vendor-defined message support, peer-register ranges, bus-control bits for PMI, root error logging, poisoned completion logging, downstream completion error handling, privileged max payload and max read request size, VGA/config aperture controls, F0/config aperture bases and sizes, XDMA aperture bounds, feature-control knobs for unsupported-request, poison, PASID, page request, invalid completion, MSI pending clearing, BME checks, ECRC, and host-poison behavior. It also defines bus-number list/capture fields, host bus number, peer frame-buffer offsets, common link control, endpoint requester-ID restore, LTR local-switch latency, and multi-host arbitration controls.

The `nbio_nbif0_bif_bx_pf_BIFDEC1` group is the largest BIF PF register block in this slice. It defines MM indirect-access disable, BIF bus controls for PMI interrupts, VGA coherency, traffic class selection, zero-byte-enable accesses, interrupt deassertion behavior, ECRC/UR handling, read/write stall and HDP flush policies, scratch registers, reset enables, MM-to-config access selection, link-training enable, IH interrupt dummy-read and delay controls, CLKREQB pad controls, BIF feature-control bits, doorbell controls and interrupts, frame-buffer enable, busy-delay counter, VF master/slave transaction-pending status, BACO controls and exit timers, memory type control, VDDGFX range and compare registers, global doorbell aperture bounds, remapped HDP flush controls, BIF ring-buffer control/base/read/write pointer fields, mailbox index, GPUIOV config sizes for UVD/VCE/GFX/SDMA, PERSTB/PX/REFPAD/CLKREQB pad controls.

The `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` group adds status and virtualization-facing controls. It includes bus-master-enable violation status/clear, atomic unsupported-request error logs and clears, self-ring GPA doorbell aperture base/control fields, HDP register and memory coherency flush controls, per-engine `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bits for CP0 through CP9 and SDMA0/SDMA1, BIF master/slave transaction-pending state, 4-dword transmit and receive mailbox message buffers, mailbox valid/ack handshakes, mailbox interrupt enables, and compact VM/HV mailbox data/valid/ack/intr fields.

The `nbio_nbif0_gdc_GDCDEC` group defines GDC and doorbell routing metadata. It includes SDP disconnect hysteresis, SHUB MMREG request error behavior for non-PF requests, reserved registers, SOCCLK-specific SDP hysteresis, doorbell ranges for SDMA0, SDMA1, IH, and MMSCH0, ATDMA arbitration and VC weights, doorbell-fence enable, 64-bit doorbell support disables for SDMA and CP, AXI host completion disable, and GDC power-gating reset selection.

The `nbio_nbif0_rcc_dev0_BIFDEC2` group defines three GFX MSI-X vector table entries: low/high message address, message data, per-vector mask bit, and pending bits in the MSI-X pending bit array. These fields model hardware-backed interrupt vector storage rather than Linux-side MSI descriptor objects.

The final `syshub_mmreg_ind_syshubind` group describes system-hub indirect MMREG fields. It defines SOCCLK and SHUBCLK deep-sleep allow enables for host and DMA client lanes, deep-sleep timers, bgen enhancement bypass/immediate enables, per-switch DMA QoS min/max controls, repeated per-client reset/QoS/static override/read-weight/write-weight controls, host client reset behavior, clock-gating controls, transaction-idle status, HP timer, MGCG controls, CPF doorbell reset behavior, scratch and client-mask fields, and NIC400 ASIB/AMIB read/write issuing-override fields across several fabric instances.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated C preprocessor macro namespace.

Consumers combine these constants with sibling NBIO 7.0 register address/default/access headers and AMDGPU register helpers. Typical use is to read a register, extract a field with `*_MASK` and `*_SHIFT`, or compose a read/modify/write value by clearing the mask and ORing `(value << shift) & mask`. The macros do not encode register addresses, access permissions, reset values, reserved-bit policy, write-one-to-clear semantics, required polling intervals, or firmware ownership.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a BIF/RCC/GDC/SYSHUB register address from companion generated metadata.
2. It accesses that register through MMIO, config-space, SMN, or an indirect MMREG path appropriate to the block.
3. It uses the shift/mask macros in this chunk to decode status or build a read/modify/write update.
4. Hardware state machines then carry out PCIe error handling, FLR/reset sequencing, doorbell routing, HDP flush handshakes, mailbox valid/ack exchanges, MSI-X delivery, BACO entry/exit timing, power/clock gating, QoS arbitration, or system-fabric transaction control.

Several represented flows are asynchronous and require sequencing by consumers: `GPU_HDP_FLUSH_REQ` must be matched against `GPU_HDP_FLUSH_DONE`; mailbox transmit/receive buffers require valid/ack transitions; BIF ring-buffer pointers and overflow status require ownership discipline; reset and FLR fields interact with transaction-pending status; BACO timer/control fields affect power-state transitions; and SYSHUB deep-sleep/MGCG/QoS controls interact with fabric idleness.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state in NBIO 7.0 registers.

Represented state includes writable configuration bits, strap-derived state, interrupt status and clear bits, error logs, transaction-pending status, scratch registers, reset enables, timer values, address aperture bases/ranges, mailbox payload dwords, valid/ack handshakes, ring-buffer read/write pointers, per-engine HDP flush request/done flags, MSI-X address/data/mask/pending fields, power-gating/clock-gating controls, QoS weights and static overrides, and NIC400 issuing behavior.

Persistence is determined by the hardware reset and power domains, not by this file. Some fields likely reset on cold reset, hot reset, FLR, BACO, link reset, or GDC/SYSHUB power gating; others may be firmware-initialized, sticky until explicitly cleared, or live status. The shift/mask macros do not reveal which fields are sticky, clear-on-write, clear-on-read, shadowed, virtualized per function, or preserved across suspend/resume.

## Dependencies And Integration Points

This generated file depends on AMD's NBIO 7.0 register database and must stay synchronized with sibling offset, default-value, and access metadata. Address comments group related registers, but this file itself only provides bit positions and masks.

AMDGPU integration points include NBIO/BIF initialization, PCIe bring-up and policy setup, SR-IOV/GPUIOV virtualization, VF/PF register decode and invalid-access handling, doorbell aperture programming, HDP coherency flush paths, interrupt handler ring-buffer setup, MSI/MSI-X programming, VM/HV mailbox protocols, BACO and runtime power management, GPU reset/FLR/link reset handling, and system-hub clock, deep-sleep, QoS, and fabric issuing configuration.

Linux integration is indirect but important. MSI-X fields correspond to interrupt delivery state coordinated with the PCI/MSI core. Doorbell, HDP flush, and mailbox fields are used by command submission, interrupt, virtualization, and reset paths. PCIe error reporting, AER, LTR, FLR, BME, and max-payload/max-read-request fields intersect with Linux PCI core assumptions and platform firmware setup.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while programming the wrong bit, causing broken PCIe error policy, invalid SR-IOV isolation, failed doorbells, lost interrupts, stale HDP data, reset hangs, or bad power-gating behavior.
- This chunk starts in the middle of a downstream PCIe control group. Whole-file research must reconcile the previous chunk before treating the opening `DN_PCIE_CNTL` context as complete.
- Status and clear fields share registers in several places, including BIF doorbell interrupts, BME status, atomic error logs, and ring-buffer overflow. Consumers must know access semantics before writing masks.
- Full-width masks such as mailbox payloads, scratch registers, aperture high/low values, MSI-X message data, and reserved fields are not blanket permission to overwrite all bits. Ownership, alignment, firmware programming, and reserved-bit preservation still matter.
- Doorbell aperture, range, and self-ring GPA fields affect CPU/GPU notification paths. Incorrect base, size, 48-bit checking, or translation policy can misroute writes or expose isolation bugs under SR-IOV.
- HDP flush request/done fields are synchronization points. Missing polling, wrong engine bit selection, or timeout mistakes can leave CPU-visible memory stale or stall command submission/reset paths.
- Mailbox valid/ack fields can deadlock if either side reuses buffers before acknowledgements or enables interrupts without clearing stale state.
- MSI-X address/data/mask/pending fields must remain consistent with PCI/MSI core ownership; direct hardware programming that races Linux vector setup can drop or misdirect interrupts.
- Reset, FLR, transaction-pending, and BACO fields are order-sensitive and can race with runtime PM, suspend/resume, firmware ownership, and in-flight DMA.
- SYSHUB deep-sleep, MGCG, QoS, and NIC400 issuing overrides can affect fabric ordering and latency. Aggressive power or QoS settings need validation under graphics, DMA, display, interrupt, and virtualization loads.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time references catch missing, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every field should have a coherent `__SHIFT`/`_MASK` pair, masks should fit the intended register width, repeated CP/SDMA/QoS/client-lane patterns should be complete, and register comments should map to sibling address metadata.
- Cross-check this final header chunk against NBIO 7.0 offset/default/access headers so PF, PF/VF, GDC, MSI-X, and SYSHUB registers have matching addresses and reset values.
- On supported hardware, validate cold boot, warm reboot, suspend/resume, BACO entry/exit, FLR, GPU reset, link reset, SR-IOV VF enable/disable, and transaction-pending drain behavior.
- Exercise doorbell paths for CP, SDMA, IH, MMSCH, self-ring GPA apertures, and 64-bit doorbell support; verify invalid or non-PF accesses are logged or blocked as expected.
- Validate HDP coherency by issuing per-engine flush requests and checking `GPU_HDP_FLUSH_DONE` bits before reading CPU-visible data.
- Exercise mailbox transmit/receive paths, valid/ack interrupts, and VM/HV mailbox fields under normal operation and reset recovery.
- Validate MSI-X vector programming and pending/mask behavior through Linux interrupt tests, including masking, unmasking, and pending-bit observation.
- Stress SYSHUB power/QoS settings with concurrent graphics, SDMA, interrupts, virtualization, and power-management transitions while watching for hangs, latency spikes, or fabric idle-status mismatches.
