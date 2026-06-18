# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 20321-22702

## Scope

This chunk covers lines 20321-22702 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage, allocation, locking, or direct register accesses.

The range begins at the tail of the `BIF_BX1_NBIF_GFX_ADDR_LUT_*` group, continues through BIF/PF virtualization and mailbox fields, RCC strap fields, SION/GDC doorbell and arbitration controls, SHUB reset controls, SysHub/NIC400 QoS fields, and ends inside the `NB_SPARE2` register of the NB misc block. The requested slice defines 2,167 macros, almost evenly split between `__SHIFT` constants and `_MASK` constants.

Although this repository path is under a `ceph-client` source-tree mirror, this file is AMD GPU NBIO register metadata. It does not implement distributed-filesystem behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-layout companion for the NBIO 7.9.0 register map. Each generated macro describes where a named hardware field lives inside a 32-bit register:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the raw unshifted mask for that field.

Driver code combines these constants with the matching NBIO 7.9.0 register-offset header and AMDGPU register helpers to extract status bits, compose read/modify/write values, and decode debug dumps. This chunk is centered on NBIF/BIF virtualization surfaces, PCIe/function straps, GPU doorbell routing, GDC/SION traffic controls, SHUB reset domains, SysHub/NIC400 QoS controls, and a small NB misc tail.

## Register Families

The opening `BIF_BX1` section finishes graphics address LUT entries 13-15, then defines virtual-function gating and status bitmaps:

- `BIF_BX1_VF_REGWR_EN`, `BIF_BX1_VF_DOORBELL_EN`, and `BIF_BX1_VF_FB_EN` expose per-VF enables for register writes, doorbells, and framebuffer access across VF0-VF30.
- Matching `BIF_BX1_VF_REGWR_STATUS`, `BIF_BX1_VF_DOORBELL_STATUS`, and `BIF_BX1_VF_FB_STATUS` expose per-VF status bits.
- `BIF_BX1_REMAP_HDP_*_FLUSH_CNTL`, `BIF_BX1_BIF_RB_*`, `BIF_BX1_MAILBOX_INDEX`, `BIF_BX1_BIF_MP1_INTR_CTRL`, pad controls, and VCN GPUIOV config-size fields support BIF ring-buffer, mailbox, interrupt, pad, and virtualization configuration plumbing.

The `addressBlock: aid_nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` section defines PF1-oriented control/status fields:

- BME and atomic error log fields, including clear bits for DMA-on-BME-low and unsupported atomic request conditions.
- Doorbell self-ring GPA aperture base and control fields.
- HDP register/memory coherency flush and invalidate controls.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bitmaps for CP0-CP9, SDMA0-1, and reserved engine bits.
- Transaction-pending, address-LUT bypass, transmit/receive mailbox data words, mailbox valid/ack controls, mailbox interrupt enables, and VM/HV mailbox fields.
- Compute and memory partition capability/status fields, including SPX/DPX/TPX/QPX/CPX support and NPS1/NPS2/NPS3/NPS4/NPS6/NPS8 support.

The `addressBlock: aid_nbio_nbif0_rcc_strap_BIFDEC1:1` section is a large strap decode block:

- `RCC_BIF_STRAP0-6` describe global BIF/PCIe feature straps: Gen3/Gen4/Gen5 disable/kill controls, VGA/BIOS ROM/memory aperture pins, error-ignore policy, margining, DLF/16GT, SWUS aperture behavior, power/link timers, power-brake behavior, emergency power reduction, and link-down reset behavior.
- `RCC_DEV0_PORT_STRAP*` describes device-0 port capabilities and policy such as port presence, bifurcation or link sizing, ASPM/LTR/PM behavior, reset behavior, MSI/MSI-X or AER-related capabilities, peer-to-peer/security policy, and link/power-management knobs.
- `RCC_DEV0_EPF0_STRAP*` and `RCC_DEV0_EPF1_STRAP*` describe endpoint function straps for function 0 and function 1: device/revision IDs, function enablement, D-state support, PASID capability, AER/ACS/VC/DPA/FLR/atomic/PME support, MSI/MSI-X capabilities, subsystem IDs, aperture sizes, SR-IOV VF mapping and aperture sizing, BAR/ROM/VGA controls, resize-BAR, clock/power management, and GPUIOV VSEC revision.
- Several empty strap comments, such as `EPF1_STRAP20-25` and `EPF1_STRAP7`, mark generated register names that have no fields in this slice.

The SION/GDC sections describe doorbell routing and NBIF-to-GDC traffic behavior:

- `S2A_DOORBELL_ENTRY_0_CTRL` through `_15_CTRL` repeat a per-port layout: enable, AWID, fence enable, range offset, range size, 64-bit support disable, range-offset deduction, and AWADDR high nibble value.
- `S2A_DOORBELL_COMMON_CTRL_REG` provides a common doorbell control bit for the SION block.
- `GDC1_A2S_CNTL_CL0/CL1`, `GDC1_A2S_CNTL3_CL0/CL1`, and `GDC1_A2S_CNTL_SW0/SW1/SW2` define A2S client arbitration, outstanding-request, QoS, ordering, and reset-related controls.
- `GDC1_A2S_TAG_ALLOC_*`, `GDC1_A2S_MISC_CNTL`, `GDC1_SHUB_REGS_IF_CTL`, `GDC1_NGDC_MGCG_CTRL`, `GDC1_ATDMA_MISC_CNTL`, and `GDC1_S2A_MISC_CNTL` describe tag allocation, miscellaneous ordering/arbitration, SHUB register-interface behavior, clock gating, ATDMA WRR weights, and S2A response behavior.
- `GDC1_NBIF_GFX_DOORBELL_STATUS` and `XCC_DOORBELL_FENCE` expose doorbell-sent/fence state for graphics, XCCs, CP engines, and remote clients.
- `GDC1_NGDC_EARLY_WAKEUP_CTRL`, `GDC1_NGDC_PG_MISC_CTRL`, `GDC1_NGDC_PGMST_CTRL`, and `GDC1_NGDC_PGSLV_CTRL` describe early-wakeup and power-gating hysteresis/enable behavior.

The reset and SysHub/NIC400 tail provides reset-domain and interconnect QoS fields:

- `SHUB_PF_FLR_RST`, `SHUB_GFX_DRV_VPU_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, `SHUB_SOFT_RST_CTRL`, and `SHUB_SDP_PORT_RST` expose PF FLR, link, hard/soft, NIC400, SION, and SDP-port reset bits.
- `HST_CLK0_*_CNTL` and `DMA_CLK0_*_CNTL` configure FLR/link-reset response and, for DMA clients, static QoS override and read/write WRR weights.
- `NIC400_*_FN_MOD`, `NIC400_2_ASIB_*_QOS_CNTL`, `MAX_OT`, `MAX_COMB_OT`, AW/AR rate parameters, target latency, KI flow-control latency, and QoS range fields expose ARM NIC400 interconnect read/write override, outstanding transaction, rate/flow-control, latency, and QoS tuning.
- `NB_NBCFG0_NBCFG_SCRATCH_4`, `NB_CNTL`, `NB_SPARE1`, and the first part of `NB_SPARE2` provide NB scratch, hardware-initialization write-lock, spare RW, and spare RW1C bit definitions. The chunk ends before all `NB_SPARE2` mask lines are included.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace, and each symbol is meaningful only when paired with the matching NBIO 7.9.0 register address definitions.

Important macro categories are:

- Per-field geometry macros for register helpers: `*_SHIFT` and `*_MASK`.
- Per-VF bitmaps for VF0-VF30 enable/status controls.
- Per-engine bitmaps for CP, SDMA, reserved engines, XCCs, remote clients, and SHUB reset ports.
- Per-doorbell-port definitions repeated for 16 S2A doorbell entries.
- Strap fields that describe hardware fuse/ROM strap inputs, policy overrides, and capability exposure.
- QoS and arbitration fields for GDC, ATDMA, SysHub, DMA clients, and NIC400 interfaces.

Typical consumers use these macros through AMDGPU helpers such as field extract/set macros and SOC15/NBIO register accessors. The companion address/default headers provide offsets and reset values; this file only supplies bit positions and masks.

## Control Flow and Data Flow

This header has no local control flow. Runtime use is indirect:

1. AMDGPU code chooses an NBIO 7.9.0 register offset from the generated address header.
2. The driver reads or constructs a 32-bit register value.
3. A field helper uses the `__SHIFT` and `_MASK` macro for the named field.
4. The driver decodes hardware state or writes a preserved read/modify/write value.
5. Hardware applies the field semantics in the relevant BIF, PF/VF, GDC, SION, SHUB, SysHub, NIC400, or NB domain.

The ordering in the header follows the generated register database, not an execution sequence. For example, a reset flow might use SHUB reset bits before polling transaction-pending or HDP flush-done status, but this file only declares the bit layouts. Similarly, mailbox message buffers and valid/ack bits imply a producer/consumer handshake, but the handshake policy is implemented by external driver and firmware code.

## State and Persistence Behavior

The chunk stores no software state and persists nothing in files or memory. The represented state lives in hardware registers:

- Virtualization state: VF register-write, doorbell, and framebuffer enable/status bitmaps; SR-IOV and VF aperture/mapping strap fields; GPUIOV config-size and VSEC strap fields.
- Addressing and aperture state: graphics address LUT entries, doorbell self-ring GPA aperture base/control, BAR/ROM/memory/register aperture strap sizing, SWUS aperture fields, and NB scratch/spare registers.
- Flush and coherency state: HDP flush request/done bits, coherency flush/invalidate controls, and transaction-pending bits.
- Mailbox state: transmit/receive message buffers, valid/ack bits, interrupt enables, VM/HV mailbox data and valid/ack flags.
- Capability and policy state: fuse/ROM strap validity, PCIe generation disable/kill straps, AER/ACS/VC/DPA/PASID/FLR/atomic/PME/MSI/MSI-X/resize-BAR/DOE support straps, D-state support, LTR/ASPM behavior, and error-ignore policy.
- Doorbell and fence state: S2A per-port range routing, fence enables, XCC/CP/remote-client fence state, and NBIF graphics doorbell sent status.
- Interconnect and QoS state: GDC A2S/S2A arbitration, tag allocation, outstanding transaction controls, WRR weights, QoS ranges, target latencies, and NIC400 rate/flow-control settings.
- Reset and power state: PF FLR, link resets, SHUB hard/soft reset enables, SDP port resets, early wakeup controls, clock gating, and NGDC power-gating hysteresis/enable bits.

Persistence follows hardware reset and power-domain rules. Some strap-derived values are sampled from fuse/ROM/pins and should be treated as firmware or hardware-owned. Some status and spare bits are write-one-to-clear or sticky. Reset bits can immediately affect live hardware state and may clear or reinitialize other registers in this same slice.

## Dependencies and Integration Points

This chunk depends on the generated AMDGPU NBIO 7.9.0 register header set staying synchronized:

- The matching `nbio_7_9_0_d.h` or offset/address header supplies register addresses.
- Optional generated default headers supply reset/default values where available.
- AMDGPU register helpers require the generated naming convention to stay stable.
- ASIC/IP-version selection code must include this header only for hardware whose NBIO layout matches version 7.9.0.

Practical integration points include:

- AMDGPU NBIO initialization and reset paths.
- PCIe/BIF link and endpoint policy derived from RCC straps.
- SR-IOV/GPUIOV virtualization setup, VF aperture programming, and VF access gating.
- Doorbell routing for graphics, CP, SDMA, XCC, remote clients, and S2A ports.
- HDP flush/coherency paths used before CPU/GPU-visible memory synchronization.
- Firmware or hypervisor mailbox flows using PF1 and VM/HV mailbox registers.
- GPU partition discovery for compute partition modes and memory/NPS modes.
- GDC/SION arbitration, power gating, clock gating, and early-wakeup tuning.
- SHUB reset recovery, FLR handling, link reset handling, and SDP port reset flows.
- SysHub/NIC400 QoS and outstanding-transaction tuning for host and DMA traffic.
- Register dump and diagnostics code that decodes NBIO 7.9.0 fields for supportability.

## Risks and Edge Cases

- This chunk starts and ends mid-family. LUT entry 12 begins before the range, and `NB_SPARE2` masks continue after the range. The final per-file reconciliation should merge adjacent chunks before making whole-register claims.
- Generated mask/shift drift can compile cleanly while changing hardware behavior. High-impact fields include VF access gating, doorbell aperture/range programming, HDP flush bits, mailbox valid/ack bits, reset enables, strap-derived capability exposure, and NIC400 QoS controls.
- Per-VF and per-engine bitmaps are repetitive. A single misplaced bit can affect only one VF, CP engine, XCC, SDMA path, or SDP port, making failures dependent on partitioning, virtualization, or traffic pattern.
- Doorbell ranges and fence controls are security-sensitive in virtualized environments. Wrong ranges, sizes, AWIDs, or address high bits can route doorbells to the wrong client or expose VF/PF interactions.
- HDP flush request/done fields require ordering and polling discipline outside this header. Treating request/done masks as ordinary writable state can cause stale CPU/GPU memory visibility or false completion.
- Mailbox valid/ack fields imply handshakes with firmware or a hypervisor. Incorrect clear/set ordering can lose messages, wedge notification state, or generate interrupt storms.
- Strap fields describe sampled hardware policy, not necessarily writable runtime configuration. Driver code should not assume a strap mask is safe to change after initialization.
- Reset controls can affect broad domains such as SHUB, NIC400, SION, SDP ports, and links. Incorrect read/modify/write behavior can reset active paths or leave dependent state inconsistent.
- Several fields appear to be sticky, clear-on-write, or write-one-to-clear by name, such as clear bits and `RW1C` spare bits. Generic writes may destroy diagnostic evidence.
- NIC400 and GDC QoS tuning can produce performance or deadlock-like symptoms without obvious correctness failures if outstanding-transaction, latency, WRR, or QoS-range masks are wrong.
- Empty generated strap comments should not be mistaken for missing implementation bugs in this chunk; they may represent reserved registers or fields defined outside the requested range.

## Test and Validation Signals

Validation is indirect because this file is compile-time metadata:

- Build AMDGPU configurations that include NBIO 7.9.0 support. Missing, renamed, or malformed field symbols should fail at consumer call sites.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift and mask, and every field-bearing register should have a matching address definition.
- Compare NBIO 7.9.0 register dumps from matching hardware against decoded VF enable/status, BIF ring-buffer, mailbox, partition, doorbell, GDC, SHUB, SysHub, NIC400, and NB misc fields.
- Exercise SR-IOV/GPUIOV scenarios with multiple VFs: VF register-write, doorbell, framebuffer, VF aperture size, VF mapping mode, and VF MSI capability bits should decode and behave as expected.
- Test doorbell delivery and fencing for CP/SDMA/XCC/remote clients and S2A ports, including 64-bit doorbells, range-offset deduction, range sizing, and fence-sent/clear-pending state.
- Exercise HDP flush/coherency paths under CPU/GPU memory synchronization workloads and confirm request/done bits progress for CP and SDMA engines.
- Validate PF1 and VM/HV mailbox handshakes under firmware/hypervisor interactions: message data, valid/ack bits, and interrupt enables should transition coherently.
- Test GPU reset, FLR, link reset, suspend/resume, and power-gating transitions while checking SHUB reset bits, transaction-pending status, GDC early wakeup, NGDC power-gating controls, and restored QoS settings.
- Cross-check strap-derived capability reporting against PCI config-space observations: AER, ACS, VC, PASID, MSI/MSI-X, FLR, atomic ops, resize-BAR, D-states, PME, Gen3/Gen4/Gen5, DLF, and 16GT support should match platform expectations.
- Run performance or stress tests that exercise host and DMA traffic while observing NIC400/GDC QoS, outstanding transaction, WRR weight, and latency fields for unexpected throttling or starvation.
