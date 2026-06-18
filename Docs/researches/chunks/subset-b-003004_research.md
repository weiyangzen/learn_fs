# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h lines 2482-3651

## Scope And Purpose

This chunk is the final portion of the generated NBIO 6.1 register offset header. It contains preprocessor constants for AMDGPU NBIO/BIF, GDC, RCC/MSI-X, SR-IOV virtual-function, and Syshub indirect register addresses. The file does not implement executable logic; it gives driver code stable symbolic names for hardware register offsets and base-index selectors.

The chunk defines 536 register-name constants and 477 `_BASE_IDX` constants. Most direct MMIO-style names use the `mm` prefix, while the tail Syshub entries use `ix` names for indexed indirect registers. Runtime code combines these offsets with matching shift/mask headers and AMDGPU register access helpers to read, write, poll, and update NBIO state.

## Register Families Covered

The opening block continues NBIF BIF offsets from the previous chunk. It covers BACO exit timing registers, memory type control, SMU/BIF VDDGFX power-status and per-GFX power-window registers, VDDGFX reserved window pairs, VDDGFX framebuffer compare, doorbell global aperture pairs, HDP flush remap controls, a BIF ring-buffer control/base/read/write-pointer group, mailbox index, GPU IOV config-size registers for UVD/VCE/GFX/SDMA, and PCIe pad-control registers for reset, power-enable, reference clock, and clock-request pins.

`nbio_nbif_bif_bx_pf_BIFPFVFDEC1` defines physical-function BIF/PF-visible offsets for bus-master-enable status, atomic error logging, doorbell self-ring GPA aperture base/control, HDP register and memory coherency flush controls, GPU HDP flush request/done registers, BIF transaction-pending status, four transmit and four receive mailbox dwords, mailbox control, mailbox interrupt control, and the VM/HV mailbox.

`nbio_nbif_gdc_GDCDEC[14976..15487]` defines GDC and doorbell-related offsets. The named registers include NGDC SDP port controls, SHUB register interface control, reserved NGDC slots, SDMA0/SDMA1/IH/MMSCH0 doorbell ranges, doorbell fence control, and S2A miscellaneous control.

`nbio_nbif_rcc_pf_0_BIFDEC2` defines the physical-function RCC MSI-X table offsets for graphics vectors 0 through 2. Each vector has low/high address, message data, and control offsets, followed by the graphics MSI-X pending-bit array. These offsets use base index 3 rather than the common NBIF base index 2.

The generated `nbio_nbif_bif_bx_pf_SYSPFVFDEC[0..255]` block is present only as commented-out PF index/data/index-high names. The active equivalents in this chunk are the per-VF `SYSPFVFDEC` blocks for VF0 through VF15, each with `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` at base index 0.

For each VF0 through VF15, the chunk then repeats the same `BIFPFVFDEC1` register pattern: BME status, atomic error log, doorbell self-ring GPA aperture high/low/control, HDP register and memory coherency flush controls, GPU HDP flush request/done, BIF transaction-pending status, mailbox transmit and receive dwords, mailbox control, mailbox interrupt control, and VM/HV mailbox. The register offsets are the same across VFs; the macro name encodes the function instance.

The final `syshub_mmreg_ind_syshubind` block defines indirect Syshub offsets for SOC clock and SHUB clock domains. It includes deep-sleep control, enhancement bypass/immediate enable controls, DMA and host clock QoS/class controls, Syshub clock-gating and transaction-idle status, high-priority timer, MGCG controls, scratch/class-mask registers, and NIC400 ASIB/AMIB function-modifier offsets.

## APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. Its exported interface is the set of generated `#define` names:

- `mm...` register-offset macros for NBIO direct register access.
- Matching `mm..._BASE_IDX` macros that select the AMDGPU register base array entry used by SOC15 register helpers.
- `ixSYSHUB_MMREG_IND_...` indirect-register offset macros for Syshub indexed access.

Important consumers are expected to be AMDGPU NBIO, PCIe, SR-IOV, interrupt, mailbox, power-management, HDP flush, and doorbell code paths that include this header through the ASIC-specific register set. Typical access patterns in AMDGPU code combine the offset with helper macros or functions such as SOC15 register-offset construction, indexed MMIO helpers, and register-field helpers from the corresponding shift/mask header.

## Control Flow

This header has no control flow. It influences runtime behavior only by resolving symbolic register names at compile time.

The runtime control flow lives in the consuming driver code. For example, a mailbox or HDP flush path may write a request register, poll a done/status register, and then clear or acknowledge state. A SR-IOV management path may select a VF-specific `MM_INDEX`/`MM_DATA` aperture and then operate on the matching VF BIF registers. A Syshub clock or QoS path may use the `ixSYSHUB_MMREG_IND_*` offsets through an indirect register interface. Those sequences are not encoded here; this chunk only supplies the addresses.

## State And Persistence Behavior

The persistent state represented by this chunk is hardware state in the NBIO, BIF, GDC, RCC, virtual-function, and Syshub blocks. The header itself stores no software state and performs no persistence.

Notable hardware state categories include BACO exit timers, VDDGFX power-window ranges, memory-type and pad controls, doorbell aperture and per-engine doorbell range state, HDP coherency flush request/done state, BIF transaction-pending status, mailbox payload/control/interrupt state, MSI-X vector address/data/control state, per-VF MMIO index/data aperture state, and Syshub QoS, clock-gating, idle, scratch, and interconnect function-modifier state.

Several registers are naturally sequencing-sensitive even though the header does not express the sequencing. Flush request/done pairs, transaction-pending status, mailbox transmit/receive dwords, MSI-X vector controls, BACO timing registers, and per-VF indirect index/data registers require consumer code to respect hardware ordering, timeout, and privilege rules.

## Dependencies And Integration Points

This chunk depends on the rest of the generated NBIO 6.1 register package:

- Earlier portions of `nbio_6_1_offset.h`, which define adjacent NBIO offsets not visible in this chunk.
- The matching `nbio_6_1_sh_mask.h` file, which provides field shifts and masks for many of these registers.
- Any matching default-value header for reset/default metadata where generated.
- AMDGPU SOC15 register-base metadata, which interprets `_BASE_IDX` values such as 0, 2, and 3.
- AMDGPU register access helpers for direct MMIO, PCIe/NBIO access, indexed Syshub access, polling, and field packing/extraction.

Integration points are hardware-facing rather than source-level call sites. The BIF and PF/VF blocks integrate with PCIe/NBIO initialization, SR-IOV virtualization, PF/VF mailbox communication, HDP flush handling, doorbell routing, GPU IOV config sizing, BACO/power management, and interrupt/MSI-X programming. The GDC block integrates with engine doorbell range assignment and SHUB register access. The Syshub indirect block integrates with clock-gating, QoS/class-limiter, idle detection, and NIC400 interconnect configuration.

## Risks And Edge Cases

Generated offset headers are easy to treat as inert data, but mistakes here have high blast radius. A wrong offset or base index can redirect a write to an unrelated hardware register, break boot-time initialization, wedge a flush or mailbox protocol, or corrupt privilege-sensitive SR-IOV state.

The repeated VF0 through VF15 blocks are especially sensitive. Their offsets intentionally match across virtual functions while the macro names distinguish the VF instance. Consumers must use the correct VF-specific symbol or an equivalent generated lookup pattern; mixing PF and VF names can break isolation, mailbox routing, or HDP flush ownership.

The `_BASE_IDX` values are part of the address contract. Most NBIF/GDC/PF/VF BIF registers in this chunk use base index 2, VF `MM_INDEX`/`MM_DATA` apertures use base index 0, and RCC MSI-X registers use base index 3. Treating all offsets as belonging to one base would produce incorrect MMIO addresses.

The PF `SYSPFVFDEC[0..255]` symbols are commented out while the VF-specific `SYSPFVFDEC` symbols are active. Code expecting generic `mmBIF_BX_PF_MM_INDEX` names from another generation would not compile against this header and should use the generation-appropriate names.

The Syshub block uses `ix` indirect offsets, not `mm` direct offsets with `_BASE_IDX` companions. Consuming code must use the correct indirect access mechanism and should not treat those numeric values as ordinary direct MMIO offsets.

## Test Signals

The header itself is normally validated through build coverage and hardware or simulator execution rather than unit tests. Useful signals include:

- Successful compilation of NBIO 6.1 AMDGPU code that references the `mm...`, `_BASE_IDX`, and `ix...` names.
- Register access traces showing expected base-index expansion for base indices 0, 2, and 3.
- BACO and power-management tests that exercise BACO exit timing and VDDGFX status/window registers without timeout regressions.
- Doorbell and HDP flush tests that verify doorbell ranges, aperture programming, flush request/done handshakes, and transaction-pending polling.
- SR-IOV validation with VF0 through VF15 covering per-VF MMIO index/data access, mailbox transmit/receive paths, VM/HV mailbox signaling, and isolation from PF state.
- Interrupt tests that program RCC graphics MSI-X vector address/data/control registers and observe expected interrupt delivery and pending-bit behavior.
- Syshub clock-gating/QoS/idle tests or hardware bring-up logs that confirm indirect Syshub offsets are reached through the right access path.

Because this chunk ends the header, merged research should connect it with earlier chunks for the full NBIO 6.1 register map and with the matching shift/mask file for bit-level semantics.
