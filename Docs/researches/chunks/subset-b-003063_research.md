# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 8712-11690

## Scope

This chunk is part of AMDGPU's generated NBIO 7.0 register default-value header. It contains C preprocessor constants ending in `_DEFAULT`, not executable code. The covered range starts in the tail of the `nbio_pcie0_bifp3_pciedir_p` PCIe-port default block, then covers `BIFP4`, `BIFP5`, `BIFP6`, the shared `PCIE` directory block, multiple IOHUB/NB/IOMMU/RAS/IOAPIC/SST blocks, and complete `BIFPLR0_2` through `BIFPLR2_2` PCIe root-port config-space default blocks. It ends in the beginning of `BIFPLR3_2`, so that final root-port block is split across the next chunk.

The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` alongside the matching `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h` headers. Runtime code uses the address and mask headers for reads/writes; this header records hardware reset or generated default values for the same register names.

## Purpose

The chunk gives the driver and validation code symbolic defaults for NBIO 7.0 PCIe, IOHUB, IOMMU, RAS, and root-port configuration registers. These defaults document expected reset state for link controller registers, PCIe flow-control and replay registers, clock/power/reset controls, performance counters, error-reporting registers, IOMMU L1/L2 configuration/shadow windows, IOAPIC routing, and PCIe capability structures.

Because this is generated hardware metadata, it has no algorithms of its own. Its value is alignment: a macro such as `smnPCIE_CNTL2_DEFAULT`, `smnCPM_CONTROL_DEFAULT`, `smnPARITY_CONTROL_0_DEFAULT`, `smnIOMMU_L1_PCIE0_L1_CNTRL_0_DEFAULT`, or `smnBIFPLR0_2_LINK_CAP_DEFAULT` lets NBIO users refer to the intended default without duplicating numeric literals outside the generated register tree.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this chunk. The public interface is a set of generated macros:

- `smn..._DEFAULT` constants describe SMN-addressed NBIO register reset/default values.
- `mm..._DEFAULT` constants appear for memory-mapped IOMMU/SMMU-style register defaults in the chunk.
- Each value is a literal 32-bit default value, usually `0x00000000` for status, scratch, counter, or software-programmed registers, with nonzero values for capability advertisement, link-control policy, power gating, error masks, and fixed hardware IDs.

Important block families in the range:

- `BIFP3` tail plus complete `BIFP4`, `BIFP5`, and `BIFP6` PCIe port defaults. These include TX/RX control, replay and credit registers, flow-control defaults, link-controller training/width/speed registers, link-management masks, L1 PM substate defaults, strap defaults, BCH ECC, HPGI, and per-port TXCLK performance counter defaults. The repeated `BIFP4`-`BIFP6` blocks mirror the `BIFP3` tail pattern.
- Shared `nbio_pcie0_pciedir` defaults. This block covers PCIe controller control/status (`smnPCIE_CNTL`, `smnPCIE_CONFIG_CNTL`, `smnPCIE_CNTL2`), link-controller state/status registers, write-protect, last-TLP logs, I2C access registers, lane/port ordering, PCIe performance counter banks, PRBS test status/counters, software reset controls, CPM/RSMU controls, LNC counters, SMU interrupt handoff, and PCIe power-gating master/slave controls.
- NB config, shadow, device-indirect, root-bridge-indirect, dummy, fastreg, and miscellaneous IOHUB/NB defaults. These include NB IDs and SMN index/data apertures, PCIe/IOMMU/IOAPIC shadow windows, IOHC reference clock and AER control, DRAM/MMIO aperture registers, device remapping, interrupt controls, CAM registers, dropped-DMA logs, VDM controls, stall controls, PSP/SMU/IOAPIC/FASTREG/SMMU base addresses, scratch registers, SMU CPU-block controls, and trap request/response register banks.
- RAS and PSP-RAS defaults. These include parity control/severity/status/counter groups, global RAS status, miscellaneous RAS control, per-event action-control registers for PCIe0 ports A-G and NBIF1 ports A-B, poison/sync-flood/NMI/APML state, and PSP-specific parity and poison registers.
- IOMMU and SMMU defaults. The range covers L2 PCI config/capability/MSI defaults, L2 controls and memory power gating, L2 shadow/PSP/MMIO views, L1 PCIE0 and IOAGR controls, L1 shadow device-table/exclusion/counter/PASID/domain/device-ID match banks, L1 PSP windows, L2A and L2A shadow controls, SMMU MMIO ID/control defaults, and a large L2 MMIO capability/control/status bank.
- IOAPIC and IOAGR defaults. These include IOAPIC bridge interrupt routing, serial IRQ status, scratch/perf/power-gating controls, IOAPIC shadow remap registers, and IOAGR configuration, security, interrupt, scratch, and trap-like controls.
- `SST0` and `SST1` core defaults. These provide status/control and per-sensor or per-threshold defaults for the NBIO SST core blocks.
- `BIFPLR0_2`, `BIFPLR1_2`, and `BIFPLR2_2` PCIe root-port config defaults, plus the first part of `BIFPLR3_2`. Each complete root-port block includes standard PCI/PCIe config defaults, PM/MSI/SSID/MSI-map capability defaults, PCIe vendor-specific and VC enhanced capability defaults, device serial number, AER masks/severity/logging, secondary PCIe capability, lane equalization controls for lanes 0-15, ACS and multicast capability defaults, L1 PM substate controls, DPC/PIO error-reporting defaults, and ESM capability placeholders.

Representative nonzero defaults are meaningful hardware policy markers: port control defaults such as `0x00010009`, link-controller training/width/speed defaults such as `0x94009880`, `0xda800006`, and `0x04400100`, shared `smnPCIE_CNTL2_DEFAULT` `0x0e000109`, software-reset controls such as `smnSWRST_CONTROL_0_DEFAULT` `0x5600ff00`, RAS parity control `0x00010001`, root-port PCIe capability and link defaults such as `PCIE_CAP` `0x00000002`, `DEVICE_CNTL` `0x00002810`, `LINK_CAP` `0x00011c03`, `LINK_STATUS` `0x00000001`, `LINK_CAP2` `0x0000000e`, and lane equalization defaults of `0x00007f7f`.

## Control Flow

There is no local control flow in this header. The effective runtime flow is in NBIO 7.0 users:

1. ASIC-specific code includes this default header with the matching offset, SMN, and shift/mask headers.
2. Driver paths read or write NBIO registers through helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `REG_SET_FIELD`.
3. The default constants can be used as reference values for initialization, reset handling, generated-table checks, documentation, or comparisons against hardware readback.
4. Link training, power gating, RAS handling, IOMMU setup, IOAPIC routing, and PCIe capability exposure are then controlled by the active driver logic and hardware state, not by this header directly.

In-tree examples show the integration pattern. `nbio_v7_0.c` includes this file and then manipulates NBIO registers such as `smnPCIE_CNTL2`, `smnCPM_CONTROL`, doorbell ranges, SMN apertures, and Syshub indirect registers using the companion offset and mask definitions. `soc15.c` includes the same header as part of SOC15 ASIC bring-up, while `smu10_inc.h` makes NBIO 7.0 defaults visible to SMU10 power-management code.

## State And Persistence

The macros are compile-time constants and own no runtime state. They do not allocate memory, perform I/O, lock anything, or persist data.

The state described by the constants is hardware state in NBIO and adjacent IOHUB/IOMMU blocks:

- PCIe transient/status state: link-controller states, last-TLP capture registers, PRBS counters, replay/NAK counters, root-port AER/DPC/PIO status, and ESM status.
- PCIe configuration state: port controls, link width/speed/training defaults, L1 PM substate defaults, capability-list values, MSI and VC capability structures, ACS/multicast capability defaults, and lane equalization defaults.
- Power/reset/clock state: SWRST controls, CPM/RSMU controls, IOHC/IOAPIC clock-gating controls, IOMMU/L2 memory power-gating controls, and PCIe power-gating master/slave defaults.
- Addressing and routing state: NB MMIO/DRAM aperture defaults, device-remap windows, PSP/SMU/IOAPIC/FASTREG/SMMU base address registers, shadow windows, IOMMU device-table/exclusion/shadow registers, and IOAPIC bridge routing defaults.
- Error and recovery state: RAS parity/poison/sync-flood/NMI/APML defaults, event action-control defaults for each PCIe/NBIF port, and IOMMU/PSP error-reporting defaults.

Persistence across boot, reset, BACO, suspend/resume, or GPU reset depends on the hardware reset domain and the AMDGPU initialization/resume paths. This header records the intended reset/default values; it does not itself restore them.

## Dependencies And Integration Points

Direct dependencies are only the C preprocessor and AMD's generated register-header naming scheme. Functional dependencies are the companion NBIO 7.0 headers:

- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` provide register addresses and address-space selection.
- `nbio_7_0_sh_mask.h` provides bitfield masks/shifts for fields inside these registers.
- `nbio_7_0_default.h` supplies the reset/default value layer covered here.

Main integration points are:

- AMDGPU NBIO 7.0 ASIC code for PCIe doorbells, memory-controller access, clock gating, light sleep, SMN/Syshub access, reset handling, and link-related state.
- SOC15 common initialization, which includes NBIO 7.0 generated definitions along with GC, SDMA, MP, HDP, and other IP block headers.
- SMU10 power-management include plumbing, where NBIO register defaults and masks are available with MP and thermal register definitions.
- PCIe and platform-facing behavior: root-port configuration defaults, advertised capabilities, AER/DPC/PIO reporting, MSI capability defaults, and IOMMU/IOAPIC mappings affect what firmware, the kernel PCI core, and diagnostics expect from the hardware.

The final per-file research document should merge this chunk with adjacent chunks of the same generated header because this range begins after the start of `BIFP3` and ends before the end of `BIFPLR3_2`.

## Risks

- Generated default drift from the ASIC register database can create misleading reset expectations. A wrong default may not break compilation, but it can hide real hardware changes or cause initialization code to preserve an unintended value.
- Repeated blocks are easy to desynchronize. `BIFP4`, `BIFP5`, and `BIFP6` should remain structurally aligned unless the hardware spec says otherwise; `BIFPLR0_2`, `BIFPLR1_2`, and `BIFPLR2_2` are also highly repetitive root-port capability blocks.
- Nonzero defaults in link-control, SWRST, CPM/RSMU, IOMMU power-gating, RAS mask/severity, and PCIe capability registers are sensitive. Treating them as arbitrary constants can affect link stability, reset behavior, power management, error handling, or advertised PCIe features.
- Status, log, and clear-style registers default to zero in many places. Runtime code must still honor hardware semantics; using default values as writable initialization values without checking write-one-to-clear or sticky-status behavior can lose diagnostics or perturb error state.
- Root-port defaults expose PCI/PCIe capability policy. Incorrect `LINK_CAP`, `LINK_CAP2`, AER severity/mask, ACS, L1 PM substate, DPC, or lane equalization defaults can mismatch the kernel PCI core's expectations or reduce interoperability.
- IOMMU shadow/counter/PASID/domain/device-ID defaults are security-sensitive when used by runtime setup code. Incorrect assumptions about zeroed base, limit, or match registers can affect DMA isolation and address translation behavior.
- This chunk has artificial boundaries. The first lines are only the tail of `BIFP3`, and the final `BIFPLR3_2` block is incomplete. Whole-block conclusions must be made after merging adjacent chunk research.

## Test And Validation Signals

Useful validation is mostly generated-header consistency plus hardware-oriented smoke testing:

- Build AMDGPU with NBIO 7.0/SOC15/SMU10 users enabled to catch syntax errors, renamed macros, missing includes, or incompatible generated-header updates.
- Cross-check every `_DEFAULT` name in this range against the corresponding address names in `nbio_7_0_offset.h`/`nbio_7_0_smn.h` and field names in `nbio_7_0_sh_mask.h`.
- Compare the generated defaults against the authoritative NBIO 7.0 register database, paying special attention to nonzero link, reset, power, RAS, IOMMU, and root-port capability values.
- Run mechanical symmetry checks for repeated blocks: `BIFP4`/`BIFP5`/`BIFP6`, PCIe shadow/devind/rcbdg sequences, L1 PCIE0 versus IOAGR IOMMU families where applicable, `SST0` versus `SST1`, and `BIFPLR0_2`/`BIFPLR1_2`/`BIFPLR2_2`.
- On NBIO 7.0 hardware, exercise PCIe link bring-up, link speed/width reporting, ASPM/L1 substates, suspend/resume, GPU reset, BACO or power-gating transitions, and doorbell operation.
- Validate RAS and PCIe error paths by checking AER/DPC/PIO logs, parity counters, poison/sync-flood/NMI/APML status, and kernel logs for unexpected AMDGPU reset storms or PCIe AER noise.
- Validate IOMMU-visible behavior with DMA, ATS/PASID-capable clients where available, IOAPIC routing, and device-remap/shadow state after initialization and resume.

## Chunk Boundary Notes

Lines 8712-8745 are the tail of `nbio_pcie0_bifp3_pciedir_p`; earlier `BIFP3` defaults are outside this chunk. Lines 11654-11690 begin `nbio_pcie0_bifplr3_cfgdecp` and stop after early standard PCIe config defaults through `LINK_STATUS`. The next chunk should complete `BIFPLR3_2`; the final per-file report should avoid treating this chunk alone as full coverage of either boundary block.
