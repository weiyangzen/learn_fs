# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 2881-5824

## Scope

This chunk is part of AMDGPU's generated NBIO 7.0 register-default header. It contains C preprocessor constants only: each `*_DEFAULT` macro records the reset/default value for a PCIe/NBIO/SMN register described by companion address and shift/mask headers. The requested range covers 2,788 `#define` entries and starts at the tail of the `cfgBIFPLR4_0` PCIe root-port default block, then spans `cfgBIFPLR5_0`, `cfgBIFPLR6_0`, debug MM ports, GDC, SYSHUB, SION, GDC reset/RAS, IOMMU L2 MMIO, IOAPIC MMIO, root-complex config spaces, BIF/BX PF/VF system registers, RCC endpoint/downstream controls, BIF misc/reset/RAS registers, power-function-controller blocks, and endpoint-function config-space defaults for `DEV0_EPF0` through the start of `DEV0_EPF7`.

The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. The practical consumers are the SOC15/NBIO v7.0 register access paths and power-management tables that need a hardware reset baseline alongside `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h`.

## Purpose

The chunk documents the hardware reset state for a large part of NBIO 7.0. It is not executable driver logic; it is a compile-time register ABI used for comparison, initialization tables, diagnostics, and generated-header consistency. The constants describe the values hardware should expose before software reprograms registers for PCIe enumeration, doorbell aperture setup, HDP flush remapping, SYSHUB indirect access, clock gating, reset handling, RAS, virtualization, and PCIe endpoint/root-complex capability surfaces.

Most defaults are `0x00000000`, which means disabled, unprogrammed, or hardware-owned state. The nonzero defaults are the important operational anchors: PCIe capability-list pointers and link defaults, AER masks/severity, lane equalization defaults, SYSHUB QoS/deep-sleep/clock-gating timers, reset control timing, doorbell/global aperture defaults, BACO exit timers, VDDGFX comparator windows, D3hot/D0 and FLR reset timing, PCIe DPA power allocations, and endpoint/root-complex capability list chaining.

## Important Macro Families

### PCIe Root-Port Defaults

The chunk begins with the tail of `cfgBIFPLR4_0` and fully covers `cfgBIFPLR5_0` and `cfgBIFPLR6_0`. These are config-space default values for PCIe root-port-like blocks under `nbio_pcie0_bifplr*_cfgdecp`. They include standard PCI config registers, bridge bus/window registers, interrupt and PM capability registers, PCIe device/link/slot/root capability and control registers, MSI and SSID capabilities, vendor-specific and VC extended capabilities, device serial number, AER registers, lane equalization controls, ACS, multicast, L1 PM substate, DPC, root-port PIO, and ESM fields.

Notable defaults include `PCIE_CAP_LIST` at `0x0000a000`, `PCIE_CAP` as `0x00000002` for root-port style capability identity in the `cfgBIFPLR` blocks, `DEVICE_CNTL` as `0x00002810`, `LINK_CAP` as `0x00011c03`, `LINK_STATUS` as `0x00000001`, `LINK_CAP2` as `0x0000000e`, `LINK_CNTL2` as `0x00000003`, AER uncorrectable severity as `0x00440010`, correctable-error masks as `0x00006000`, and 16 lane equalization defaults of `0x00007f7f`. These values define the config-space baseline later visible to PCIe setup and error-reporting logic.

### Debug, GDC, SYSHUB, and SION

The `nbio_dbgu0_dbgudec` block defines default-zero `mmport_{a,b,c,d}_{addr,data_lo,data_hi}` debug MM-port values. These are raw access windows, not policy state.

`nbio_nbif0_gdc_GDCDEC` defines GDC defaults: SDP port control defaults of `0x0000000f`, per-engine doorbell ranges for SDMA0, SDMA1, IH, and MMSCH0 defaulting disabled, `ATDMA_MISC_CNTL` defaulting to `0x04040001`, and doorbell fence/S2A/power-gating misc defaults. These constants pair with `nbio_v7_0.c` functions that program SDMA, VCN/MMSCH, and IH doorbell ranges after device initialization decides whether each engine uses doorbells.

`nbio_nbif0_syshub_mmreg_direct_syshubdirect` covers direct SYSHUB policy defaults. It includes deep-sleep controls and timers for SOCCLK and SHUBCLK, BGEN enhancement controls, DMA QoS controls defaulting to `0x0000001e`, DMA client controls defaulting to `0x20200000`, host client reset controls, clock-gating controls such as `SYSHUB_CG_CNTL` defaulting to `0x00082000`, high-priority timer `0x00000100`, MGCG controls defaulting to `0x00000080`, scratch/mask registers, and NIC400 outstanding-issue override defaults. `nbio_v7_0_update_medium_grain_clock_gating()` uses the corresponding SYSHUB shift/mask names through indirect `SYSHUB_INDEX`/`SYSHUB_DATA` accesses; these defaults are the reset-side baseline for those toggles.

`nbio_nbif0_nbif_sion_SIONDEC` contains per-client SION credit and timing defaults. Clients CL0 through CL3 appear in this chunk, each with read-response, write-response, request burst target and timeslot registers plus request/data/read-response/write-response pool-credit allocation registers. Defaults are zero, indicating no software override from the generated reset table. `SION_CNTL_REG0` and `SION_CNTL_REG1` also default zero.

### Reset, RAS, IOMMU, and IOAPIC Defaults

`nbio_nbif0_gdc_rst_GDCRST_DEC` supplies reset defaults for SHUB PF/VF FLR reset, GFX driver/VPU reset, link reset, hard/soft reset controls, SDP port reset, and reset misc timing. `SHUB_HARD_RST_CTRL` defaults to `0x0000001b`, `SHUB_SOFT_RST_CTRL` to `0x00000009`, and `SHUB_RST_MISC_TRL` to `0x00100001`. These values matter because reset registers often combine enable bits and timing fields; blindly restoring an incorrect default can alter reset propagation across the NBIO fabric.

`nbio_nbif0_gdc_ras_gdc_ras_regblk` defines six GDC RAS leaf control defaults, each `0x00000080`. `nbio_nbif0_bif_ras_bif_ras_regblk` later defines BIF RAS leaf controls with the same `0x00000080` baseline plus BIF RAS miscellaneous and IOHUB interrupt controls defaulting zero. These are RAS policy/status registers, so the default values must be interpreted with the companion shift/mask header before any writes.

`nbio_iohub_iommu_l2mmio_l2mmiocfg` is a dense IOMMU L2 MMIO default block. It covers device table bases, command/event/PPR/GA log bases, IOMMU control words, exclusion ranges, EFR, hardware error addresses/status, SMI filters, additional device table bases, MSI capability/address/data/mapping registers, MARC base/relocation/length windows, command/event/PPR/GA ring head/tail pointers, status, autoreply/overflow controls, and performance counter configuration and match registers. Several high dword base defaults are `0x08000000`, while most address/control/status defaults are zero; `IOMMU_MMIO_CNTRL_0` defaults to `0x00000400` and `CNTRL_1` to `0x00002200`.

The IOAPIC blocks define default-zero index/data plus 64 redirection entries and EOI/IRQ/misc registers. These constants document IOHUB interrupt-controller reset state; they are sensitive because redirection-table defaults control whether interrupts are initially masked/routed.

### Root Complex, BIF/BX, RCC, and Power Blocks

`nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` define root-complex config-space defaults for two devices. Their PCIe capability defaults identify root-complex/root-port style functions: `PCIE_CAP` is `0x00000042`, `LINK_STATUS` is `0x00002001`, MSI message control is `0x00000080`, VC0 control is `0x000000fe`, AER capability list is `0x20020000`, AER severity is `0x00440010`, correctable-error mask is `0x00002000`, secondary capability list is `0x2a000000`, lane equalization defaults are `0x00007f0f`, and ACS defaults are zero. These blocks form the root-complex baseline distinct from endpoint-function defaults.

The BIF/BX PF/VF and system blocks define indirect MM access registers, SYSHUB and PCIe index/data windows, SBIOS/BIOS scratch defaults, interrupt controls for RLC/VCE/UVD, GFX MMIO CAM windows, BIF reset enables, pad controls, doorbell controls, framebuffer enable, busy delay, BACO timers, VDDGFX comparator windows, global doorbell apertures, HDP flush remap defaults, ring-buffer registers, mailbox registers, BME/atomic logs, coherency flush request/done, transaction-pending status, and VM/HV mailbox defaults. Nonzero examples include `BX_RESET_EN` `0x00010003`, `CLKREQB_PAD_CNTL` `0x000008e0` in the system block, BIFDEC1 `BIF_BUSY_DELAY_CNTR` `0x0000003f`, BACO exit timers from `0x00000100` through `0x00000500`, VDDGFX GFX comparator lower/upper windows, global doorbell aperture windows, and HDP remap defaults `0x0000385c`/`0x00003858`.

`nbio_nbif0_rcc_*` blocks describe PCIe endpoint and downstream RCC defaults. The RCC strap default `smnRCC_STRAP0_RCC_DEV0_EPF0_STRAP0_DEFAULT` is `0x300015dd`. Endpoint defaults include PCIe scratch/control/interrupt/RX/bus/config/TX LTR control, DPA substate power allocations, PME, TX requester ID, error control, RX control, and link speed control. Downstream and downstream-port blocks cover reserved/scratch/control/config/RX/bus defaults, error control, LC speed/control, strap misc, and LTR message fields. These pair with NBIO PCIe/LTR setup code that reads or writes SMN/PCIE registers through `RREG32_PCIE` and `WREG32_PCIE`.

The BIF miscellaneous block contains NBIF fabric-level defaults: system ROM aperture, BIFC miscellaneous controls, DMA attribute overrides, virtual-wire controls, MGCG/deep-sleep controls, SMN master endpoint controls, dummy control, throttle/GSI/PCIE function controls, SDP controls, performance counters, register-interface error controls, power-gating controls, self-ring vector controls, and GMI completion-buffer controls. Important nonzero defaults include `OUTSTANDING_VC_ALLOC` `0x6f06c0cf`, `BIFC_MISC_CTRL0` `0x08000004`, `BIFC_MISC_CTRL1` `0xa0108c04`, `NBIF_MGCG_CTRL_LCLK` `0x00000080`, `NBIF_DS_CTRL_LCLK` `0x01000000`, `SMN_MST_CNTL0` `0x00000001`, `BME_DUMMY_CNTL_0` `0xaaaaaaaa`, `BIFC_THT_CNTL` `0x00000222`, `BIFC_GSI_CNTL` `0x000017c0`, `BIFC_SDP_CNTL_0` `0x3f3f3f3f`, `NBIF_PGSLV_CTRL` `0x00000004`, `NBIF_PG_MISC_CTRL` `0x14006084`, `BIF_SELFRING_BUFFER_VID` `0x0000605f`, `BIF_GMI_WRR_WEIGHT` `0x00040404`, and GMI completion-buffer controls.

The repeated `nbio_nbif0_rcc_pfc_*_RCCPFCDEC` blocks cover power-function-controller defaults for amdgfx, amdgfxaz, PSP, USB3 ports, ACP, AZ, MP2, SATA, and GBE ports. Each block defaults LTR control, PME restore, sticky restore registers, and AUX power control to zero. This is a platform-wide table of per-function power-management restore surfaces.

### BIF Reset and Endpoint Function Config Spaces

`nbio_nbif0_bif_rst_bif_rst_regblk` defines BIF reset and interrupt reset defaults. `HARD_RST_CTRL` defaults to `0xb0000055`, `RSMU_SOFT_RST_CTRL` to `0x90000000`, `BIF_RST_MISC_CTRL` to `0x000e0648`, `BIF_RST_MISC_CTRL3` to `0x00104900`, `DEV0_PF0_FLR_RST_CTRL` to `0x8206a0a9`, other PF FLR controls to `0x02060009`, D3HOTD0 reset controls to `0x0000001b`, and `BIF_D3HOTD0_INTR_MASK` to `0x0000ffff`. These defaults are high-risk because they encode reset timing, interrupt mask, and PF/VF behavior across both device 0 and device 1.

The chunk then covers `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` through part of `epf7`. `EPF0_2` is the largest endpoint-function config-space block in this range. It includes standard config, BARs, interrupt, PM, PCIe, MSI/MSI-X, vendor-specific, VC, AER, BAR capability, power-budgeting, DPA, secondary capability, lane equalization, ACS, ATS, Page Request, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, and GPUIOV vendor-specific mailbox/scheduler/FB defaults. Most SR-IOV and GPUIOV values are zero except `PCIE_SRIOV_SYSTEM_PAGE_SIZE_DEFAULT` at `0x00000001`, showing a reset baseline without enabled VFs.

`EPF1_1` through `EPF7_1` repeat a smaller endpoint-function pattern. They include standard config, PM, USB/SATA-related capability placeholders where applicable, PCIe capability (`PCIE_CAP` `0x00000002`), device capability (`0x10000000`), device control (`0x00002810`), link capability/status/control defaults, MSI control (`0x00000080`), AER severity (`0x00440010`), correctable-error mask (`0x00002000`), BAR capability/control defaults with BAR1 control `0x00000020`, power-budgeting, DPA status (`0x00000100`), ACS, and ARI. `EPF6_1` and `EPF7_1` begin near the end of the chunk, so the final per-file report must merge the next chunk to complete the `EPF7_1` block.

## APIs, Types, and Functions

There are no C functions, structs, enums, or variables declared in this chunk. The public interface is the generated macro namespace:

- `cfgBIFPLR*_0_<REGISTER>_DEFAULT` for PCIe root-port config defaults.
- `smn<REGISTER>_DEFAULT` for SMN-addressed NBIO, GDC, SYSHUB, SION, IOMMU, RCC, BIF, reset, RAS, and endpoint config defaults.
- `mmport_*_DEFAULT` for debug MM-port defaults.

These macros are meaningful only when paired with address macros from `nbio_7_0_offset.h`/`nbio_7_0_smn.h` and field definitions from `nbio_7_0_sh_mask.h`. Driver code such as `nbio_v7_0.c` does not generally call these names as functions; it uses the same generated register namespace to read, write, compare, or script the corresponding hardware registers through `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `WREG32_FIELD15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

## Control Flow and Hardware Protocols

This header has no runtime control flow. The effective control flow lives in AMDGPU initialization, reset, suspend/resume, virtualization, and power-management code:

1. Hardware resets into the values represented by these `*_DEFAULT` macros.
2. SOC15/NBIO setup code reads registers through SOC15 or SMN/PCIE access helpers.
3. Driver helpers use shift/mask macros to modify fields such as doorbell range offset/size, framebuffer read/write enable, HDP flush remaps, SYSHUB clock-gating enables, or PCIe LTR controls.
4. Power and reset paths may compare against or reapply default-like values while moving through BACO, D3hot/D0, FLR, link reset, soft reset, or runtime suspend/resume.
5. Status-style registers, such as RAS leaves, mailbox valid/ack, transaction pending, HDP flush done, IOMMU ring pointers, and PCIe AER status, are hardware-updated after reset and are not stable constants in normal operation.

Important protocols encoded by these defaults include PCIe capability-chain layout, MSI/MSI-X setup baseline, AER severity/mask policy, doorbell aperture programming, HDP coherency flush remapping, PF/VF mailbox handshakes, IOMMU command/event/PPR/GA rings, FLR/D3hot reset timing, SYSHUB deep-sleep/MGCG policy, and BACO/VDDGFX low-power transitions.

## State and Persistence Behavior

The macros themselves have no memory, locking, allocation, or persistence. They compile into integer constants. The state they describe lives in hardware registers and has mixed persistence:

- PCIe config-space defaults persist only until firmware, the PCI core, or AMDGPU programs command bits, BARs, MSI/MSI-X, link controls, and advanced capabilities.
- Doorbell ranges, global apertures, self-ring aperture controls, HDP flush remaps, framebuffer enable, and SYSHUB policy registers are driver-owned after initialization and usually need reprogramming after GPU reset, FLR, BACO exit, or suspend/resume.
- Mailbox valid/ack bits, HDP flush request/done, RAS status, IOMMU head/tail pointers, event logs, AER status, and transaction-pending registers are hardware-owned or handshake state; reset defaults are useful only as an initial baseline.
- Reset-control defaults encode timing and enable policy across power/reset domains. Some fields may be sticky or strap-influenced, and not every software reset returns all NBIO blocks to these values.
- Endpoint-function GPUIOV/SR-IOV defaults are security-sensitive because they describe PF/VF exposure, mailbox, BAR, page-size, and VF resource baselines before virtualization code enables any feature.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header ecosystem. The `_DEFAULT` names must remain aligned with:

- `nbio_7_0_offset.h` for MMIO/config register offsets.
- `nbio_7_0_smn.h` for SMN/PCIE addresses.
- `nbio_7_0_sh_mask.h` for field extraction and update.
- SOC15 register helpers used by `amdgpu/nbio_v7_0.c` and `amdgpu/soc15.c`.
- SMU10/PowerPlay includes that may need NBIO defaults for power-management tables.

The main integration points are AMDGPU PCIe/NBIO initialization, doorbell management for SDMA/IH/MMSCH, HDP flush mapping for KFD and command submission coherency, memory-controller access enable, SYSHUB indirect MM register access, clock-gating and light-sleep policy, PCIe LTR/DPA/power management, RAS setup, reset/FLR handling, IOMMU/IOAPIC interrupt routing, and SR-IOV/GPUIOV virtualization plumbing.

## Risks

- Generated-header drift is silent and high impact. A wrong default can mislead initialization tables, diagnostics, or reset-restore logic even when code still compiles.
- Registers in this chunk include command/status mixtures. Treating a reset default as a safe read-modify-write base can accidentally clear sticky status, acknowledge mailboxes, request resets, or alter interrupt masks.
- PCIe capability-list defaults must remain consistent with offset and shift/mask headers. Broken capability pointers can affect enumeration, AER, ACS, ATS/PASID/PRI, SR-IOV, and power-management discovery.
- Doorbell and aperture defaults touch engine submission and interrupt delivery. Incorrect range or global aperture programming can break SDMA/IH/MMSCH doorbells or expose the wrong GPU page.
- Reset defaults are especially risky: PF/VF FLR, D3hot/D0, hard reset, soft reset, and link reset timing affect recovery and virtualization isolation.
- RAS and AER defaults affect error containment. Mask/severity mistakes can hide errors, over-report correctable events, or turn recoverable PCIe errors into fatal paths.
- IOMMU defaults cover table bases, command/event/PPR/GA rings, MSI, and counters. Wrong assumptions here can affect DMA translation, interrupt remapping, fault reporting, or performance counters.
- SYSHUB QoS, clock-gating, and deep-sleep defaults interact with outstanding fabric traffic. Reprogramming them without idle/pending checks can cause fabric timeouts or hangs.
- This chunk ends inside the `EPF7_1` endpoint-function block. Final per-file reconciliation must merge the next chunk before making whole-file claims about all endpoint-function defaults.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware smoke testing:

- Build AMDGPU with SOC15/NBIO v7.0 and SMU10/PowerPlay paths enabled; missing or renamed defaults should fail includes or register-table compilation.
- Compare this generated header against the authoritative NBIO 7.0 register database, especially nonzero reset defaults and capability-list chains.
- Cross-check `_DEFAULT` macro names against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_sh_mask.h`; every default should have a coherent address/register definition.
- Boot NBIO 7.0 hardware and verify PCIe enumeration, link width/speed, MSI/MSI-X, AER/ACS capability visibility, and config-space defaults with `lspci` and kernel logs before/after AMDGPU binds.
- Exercise SDMA, IH, VCN/MMSCH, KFD, and command submission to validate doorbell ranges and HDP flush remaps.
- Run suspend/resume, GPU reset, FLR, BACO/runtime power-management, and D3hot/D0 paths while watching for AMDGPU timeouts, PCIe AER storms, or failed link retraining.
- In SR-IOV/GPUIOV environments, test PF/VF reset isolation, mailbox valid/ack handling, VF resource defaults, and doorbell/self-ring aperture isolation.
- For RAS and IOMMU paths, validate fault injection or error-reporting tests where available, checking that status/mask/severity defaults do not suppress expected events or generate spurious interrupts.
