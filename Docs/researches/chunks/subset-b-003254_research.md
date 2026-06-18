# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 19480-21933

## Scope

This chunk is a generated AMDGPU NBIO 7.7 register-offset header segment. It contains 2,362 `#define` lines: 1,181 register-address macros and 1,181 matching `_BASE_IDX` macros. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the tail of a `BIFP5` PCIe port block, then covers several NBIO/IOHUB address blocks, NBIF0 BIF/RCC/GDC register windows, and ends in `BIFPLR0_2` PCIe capability/config-space aliases through lane 15 equalization control. Adjacent chunks are required for the beginning of the `BIFP5` block before line 19480 and any `BIFPLR0_2` registers that follow line 21933.

## Purpose

`nbio_7_7_0_offset.h` is the address half of AMD's generated NBIO 7.7 register interface. Each `reg*` macro gives a hardware register offset or encoded address, and each `<register>_BASE_IDX` macro tells AMDGPU's SOC15 register helpers which NBIO base index to use. In this chunk every visible `_BASE_IDX` value is `5`.

This segment maps low-level PCIe, NBIO, IOMMU L2A, BIF, RCC, GDC, RAS, trap, doorbell, mailbox, MSI-X, and PCIe config/capability registers. The constants let runtime driver code use named hardware registers through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT` instead of hard-coded offsets.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Register Families

The opening `BIFP5` tail covers PCIe protocol/link registers for an existing port block: TX skid, lane status, error control, RX sequence/vendor/credit state, physical and transaction error injection, NAK/LTR/AER controls, link-control state registers, link-width/speed/equalization controls, L1 PM substate registers, BCH ECC/HPGI/performance controls, save/restore slots, TX sequence/replay/credit/flow-control registers, and VC0/VC1 flow-control counters.

The `nbio_pcie1_pciedir` block starts `BIF1` PCIe port registers at base address `0x11280000`. It includes common PCIe control/status, RX last-TLP capture, I2C expansion/data access, link power-management controls, physical-port status, SDP and CLKREQ mapping, performance counters, strap registers, PRBS clear/status/free-run/pattern/error counters for lanes 0 through 15, software reset command/control registers, power-gating master/slave controls, RX margining, presence detect, LC debug, TX last-TLP capture, tracking registers, TX status/attribute controls, bandwidth and master controls, and HIP registers.

The `nbio_iohub_nb_nbcfg_nb_cfgdec`, `fastreg`, `misc`, and `rascfg` blocks expose IOHUB/NB configuration space. They include NB vendor/device/command/status/class/cache/header/capability aliases, SMN index/data windows, scratch registers, DRAM aperture and top-of-memory registers, interrupt-routing and parity controls, MMIO CAM target/remap entries, dropped DMA logs, VDM controls, xbar stall controls, SMU and fastreg base addresses, trap request/response registers, 16 repeated trap match units, RAS action-control registers for PCIE0 ports A-F and NBIF1 ports A-C, sync flood/NMI/poison status and masks, and APML status/control/trigger registers.

The IOMMU `l2acfg` block maps L2A performance counters, status/control registers, DTC/ITC/PTC hash and way controls, credit controls, update filters, error-rule controls, clock/power/page-size controls, memory power gates, power-gate control, and ECO control. The adjacent `l2ashdw` block is present as an address-block marker in this range but has no register macros inside the chunk.

The NBIF0 BIF/RCC/GDC portion maps indirect MMIO and PCIe index/data windows, SBIOS/BIOS scratch registers, BIF interrupt controls, GFX MMIO CAM remaps, RCC strap registers, RCC endpoint/downstream/downstream-port registers, EPF0 VF/PF aperture controls, MSI/MSI-X table entries, requester/device/function restore, LTR and arbitration controls, BIF bus/reset/doorbell/FB enable controls, GPU-I/O virtualization aperture sizes, HDP coherency flush/invalidate controls, transaction-pending status, VM/HV mailbox buffers, GDC SDP/clock/power controls, and doorbell ranges for SDMA, IH, VCN, RLC, CSDMA, and related clients.

The final high-address `nbio_iohub_nb_nbcfg_nb_cfgdec` and `nbio_pcie0_bifplr0_cfgdecp` blocks expose large encoded config-space aliases. `NB_NBCFG1` repeats northbridge PCI configuration/header, SMN index/data, scratch, DRAM, and mutex registers. `BIFPLR0_2` maps PCI header fields, PM/PCIe/MSI/SSID/MSI-map capabilities, PCIe vendor-specific and virtual-channel enhanced capabilities, device serial number, AER status/masks/severity/header/TLP-prefix logs, root error command/status/source ID, secondary PCIe capability, link control 3, lane error status, and lane 0-15 equalization controls.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace:

- `reg<name>` macros are integer constants used as register selectors.
- `reg<name>_BASE_IDX` macros select the SOC15 base index for those registers.

The offsets do not encode bit fields, reset values, access permissions, write-one-to-clear behavior, ordering requirements, ownership, or side effects. Consumers must pair these macros with `nbio_7_7_0_sh_mask.h` for field layout, any generated default metadata for reset values, and AMDGPU's register access helpers for the correct access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. NBIO 7.7 driver code includes `nbio_7_7_0_offset.h` and the matching shift/mask header.
2. Code passes a `reg*` macro through `SOC15_REG_OFFSET(NBIO, instance, reg)` or a PCIe-port accessor helper.
3. The read or write reaches the selected NBIO, PCIe, RCC, GDC, RAS, IOMMU, or config-space register.
4. Field operations use the companion shift/mask macros to preserve unrelated bits while programming the register.

The main visible consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this header and uses this generated register namespace for NBIO 7.7 operations such as HDP flush register remapping, PCIe index/data offset reporting, doorbell aperture setup, interrupt handler dummy-read control, memory controller access enablement, clock gating/light sleep, and initialization workarounds.

## State And Persistence Behavior

The header owns no software state and persists nothing. It describes hardware-visible register locations whose state lives in GPU/NBIO reset and power domains.

Represented state includes PCIe link/protocol state, AER and RAS status/action controls, PRBS diagnostic counters, RX margining controls, software reset controls, interrupt routing, memory aperture and remap registers, HDP flush/invalidate requests and completion status, doorbell aperture/range programming, GPU virtualization and mailbox registers, trap comparators, poison/NMI/sync-flood status, IOMMU L2A performance and power controls, PCIe capability/configuration aliases, and MSI/MSI-X table entries.

Persistence depends on the specific register's reset domain, PCIe reset, GPU reset, BACO/power-gating state, firmware/BIOS programming, SR-IOV PF/VF ownership, suspend/resume restore, and explicit driver writes. Register-address macros alone must not be treated as evidence that a value survives reset or is safe to cache.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.7 register database and must remain synchronized with sibling generated headers:

- `nbio_7_7_0_sh_mask.h` provides bit shifts and masks for the same register names.
- Other generated NBIO 7.7 metadata provides defaults or additional address views where present.
- AMDGPU SOC15 and PCIe-port accessors interpret the offset and base-index macros.

Important integration points include:

- `amdgpu/nbio_v7_7.c`, which binds these constants into `nbio_v7_7_funcs` and `nbio_v7_7_hdp_flush_reg`.
- `amdgpu_discovery.c`, which selects NBIO 7.7 functions for discovered hardware.
- Doorbell, HDP, IH, SDMA, VCN, RLC, KFD, SR-IOV, PCIe link-management, RAS, and power-management paths that rely on correct NBIO register addresses.

## Risks And Edge Cases

- Generated offset drift can compile cleanly while redirecting reads or writes to the wrong hardware register, causing PCIe link failures, broken doorbells, missed interrupts, invalid HDP flush completion checks, RAS misrouting, or GPU reset/resume regressions.
- The chunk starts mid-`BIFP5` block and ends in the `BIFPLR0_2` capability block. Whole-file research must reconcile neighboring chunks before treating either family as complete.
- Several address blocks share the same base address `0xd0000000` but represent different decoders. Consumers must use the intended macro namespace and access path, not just compare raw values.
- The high encoded addresses such as `0x3fff7bfc...` are config-space aliases, not ordinary small MMIO offsets. Truncation, sign extension, or using a 32-bit-only path incorrectly would be dangerous.
- Trap, reset, poison, RAS action-control, AER, error-injection, and PRBS registers have diagnostic or fault-routing side effects. Accidental writes can mask hardware errors, inject faults, reset blocks, or perturb link diagnostics.
- Doorbell aperture/range and mailbox registers interact with queue submission, virtualization, KFD, and host memory visibility. Incorrect programming can break command submission or isolate the wrong client.
- Scratch, strap, BIOS/SBIOS, requester-ID restore, and PCIe capability aliases may be firmware-owned or boot-time sampled. Runtime writes need hardware documentation and sequencing.
- Repeated lane, port, trap, and action-control macro families are mechanically generated; lane or port off-by-one mistakes are plausible at call sites because many names and offsets differ only by a number.

## Test Signals

- Build AMDGPU with NBIO 7.7 support enabled. Compile-time coverage catches missing or renamed generated symbols used by `nbio_v7_7.c` and related code.
- Run generated-header consistency checks: every `reg*` macro in this chunk should have a matching `_BASE_IDX`, base-index values should match the SOC15 NBIO instance mapping, and duplicated config aliases should intentionally share offsets.
- Cross-check `nbio_7_7_0_offset.h` against `nbio_7_7_0_sh_mask.h` so field macros exist for registers that runtime code reads or writes.
- On supported hardware, validate PCIe link bring-up/retraining, link-speed/width reporting, RX margining visibility, PRBS diagnostics, suspend/resume, BACO or GPU reset recovery, and clock-gating/light-sleep transitions.
- Exercise HDP flush/invalidate paths, doorbell ranges for SDMA/IH/VCN/RLC/CSDMA, interrupt handling, KFD remapped HDP registers, and SR-IOV PF/VF register access where applicable.
- Validate RAS and AER behavior by checking that correct status, mask, severity, root error, poison, NMI, sync-flood, and action-control registers are read or written for each port.
- Review register traces for writes to reset, trap, error-injection, PRBS, RAS, and strap/config aliases to ensure they are intentional, sequenced, and use read-modify-write with the companion masks where fields share registers.
