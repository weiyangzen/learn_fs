# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003060`: lines 1-2880, `Docs/researches/chunks/subset-b-003060_research.md`
- `subset-b-003061`: lines 2881-5824, `Docs/researches/chunks/subset-b-003061_research.md`
- `subset-b-003062`: lines 5825-8711, `Docs/researches/chunks/subset-b-003062_research.md`
- `subset-b-003063`: lines 8712-11690, `Docs/researches/chunks/subset-b-003063_research.md`
- `subset-b-003064`: lines 11691-14586, `Docs/researches/chunks/subset-b-003064_research.md`
- `subset-b-003065`: lines 14587-14865, `Docs/researches/chunks/subset-b-003065_research.md`

## Chunk Research

### subset-b-003060: lines 1-2880

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 1-2880

## Scope

This chunk covers the first 2,880 lines of the generated AMD NBIO 7.0 default-register header. The full source file is much larger; this chunk contains the license and include guard plus the initial NBIO/IOMMU/PCIe configuration-space default-value macros. It defines 2,793 preprocessor constants in the assigned range and no functions, structs, enums, or executable statements.

## Purpose

The header provides hardware reset/default values for NBIO 7.0 register and PCI configuration-space fields used by AMDGPU and related SMU/power-management code. In this chunk, the constants describe:

- Northbridge configuration defaults for `nbio_iohub_nb_nbcfg_nb_cfgdec`.
- IOMMU L2 configuration defaults for `nbio_iohub_iommu_l2_iommul2cfg`.
- NBIF root-complex PCIe config defaults for device 0 and device 1.
- Dummy PCIe function headers.
- Endpoint-function PCIe config defaults for several `DEV0_EPF*` and `DEV1_EPF*` functions.
- PCIe physical/root-port-like `BIFPLR0` through the start of `BIFPLR4`.

The values are intended to be consumed with companion generated headers such as `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h`, giving driver code symbolic names for reset values when initializing, comparing, restoring, or documenting register programming.

## Important APIs, Types, And Macros

There are no C APIs or types in this chunk. The public surface is entirely C preprocessor macros with names ending in `_DEFAULT`.

The top-level guard is `_nbio_7_0_DEFAULT_HEADER`. Its casing differs from typical all-caps guard style but matches generated AMD register headers.

Important macro groups include:

- `cfgNB_NBCFG0_*_DEFAULT`: northbridge PCI config defaults. Notable non-zero defaults include `cfgNB_NBCFG0_NB_HEADER_DEFAULT` and `_HEADER_W_DEFAULT` at `0x00000080`, adapter IDs at `0x15d01022`, `NB_PCI_ARB_DEFAULT` at `0x00000108`, and `NB_PERF_CNT_CTRL_DEFAULT` at `0x00808000`.
- `cfgIOMMU_L2_0_*_DEFAULT`: AMD IOMMU/SMMU defaults. Vendor/device IDs are `0x1022`/`0x15d1`, interrupt pin defaults to `1`, and several SMMU ID/control values are non-zero, including `IOMMU_CONTROL_W_DEFAULT`, `IOMMU_MMIO_CONTROL0_W_DEFAULT`, `IOMMU_MMIO_CONTROL1_W_DEFAULT`, `SMMU_MMIO_IDR0_W_DEFAULT`, `SMMU_MMIO_IDR1_W_DEFAULT`, and `SMMU_MMIO_IDR5_W_DEFAULT`.
- `cfgBIF_CFG_DEV{0,1}_RC0_*_DEFAULT`: root-complex config-space defaults. They model PCI/PCIe capability chains, MSI capability defaults, virtual channel defaults, AER defaults, link capability/status defaults, lane-equalization defaults, and ACS defaults for two root-complex devices.
- `cfgNB_PCIEDUMMY{0,1}_0_*_DEFAULT`: compact dummy PCIe config headers with non-zero header type defaults.
- Unprefixed `cfg*` macros for `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`: endpoint function 0 has generic names such as `cfgVENDOR_ID_DEFAULT`, `cfgLINK_CAP_DEFAULT`, and `cfgPCIE_SRIOV_SYSTEM_PAGE_SIZE_DEFAULT`. These are more collision-prone than the later prefixed endpoint groups and depend on include ordering/namespace discipline across generated headers.
- `cfgBIF_CFG_DEV0_EPF{1..7}_0_*_DEFAULT` and `cfgBIF_CFG_DEV1_EPF{0..2}_0_*_DEFAULT`: repeated endpoint-function templates for PCIe capability, MSI/MSI-X, AER, BAR enhanced capability, power budget, DPA, ACS, ARI, and in some functions ATS/PASID/page request/TPH/multicast/LTR/SR-IOV or SATA/USB-like capability placeholders.
- `cfgBIFPLR{0..4}_0_*_DEFAULT`: physical/root-port configuration defaults. This chunk fully covers `BIFPLR0` through `BIFPLR3` and begins `BIFPLR4`.

## Address-Block Layout

The assigned range is organized by generated comments of the form `// addressBlock: ...`. The visible blocks are:

- Lines 25-74: `nbio_iohub_nb_nbcfg_nb_cfgdec`.
- Lines 75-122: `nbio_iohub_iommu_l2_iommul2cfg`.
- Lines 123-247: `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`.
- Lines 248-372: `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`.
- Lines 373-380: `nbio_iohub_nb_pciedummy0_pciedummy_cfgdec`.
- Lines 381-388: `nbio_iohub_nb_pciedummy1_pciedummy_cfgdec`.
- Lines 389-642: `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`.
- Lines 643-896: `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`.
- Lines 897-1022: `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`.
- Lines 1023-1148: `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`.
- Lines 1149-1274: `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`.
- Lines 1275-1400: `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`.
- Lines 1401-1526: `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`.
- Lines 1527-1652: `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`.
- Lines 1653-1807: `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`.
- Lines 1808-1933: `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`.
- Lines 1934-2059: `nbio_nbif0_bif_cfg_dev1_epf2_bifcfgdecp`.
- Lines 2060-2231: `nbio_pcie0_bifplr0_cfgdecp`.
- Lines 2232-2403: `nbio_pcie0_bifplr1_cfgdecp`.
- Lines 2404-2575: `nbio_pcie0_bifplr2_cfgdecp`.
- Lines 2576-2747: `nbio_pcie0_bifplr3_cfgdecp`.
- Lines 2748-2880: the beginning of `nbio_pcie0_bifplr4_cfgdecp`.

## Control Flow

This chunk has no runtime control flow. It influences control flow indirectly when included driver code uses these macros as literal values in register programming, reset comparison, or default initialization paths.

The main integration path is compile-time inclusion:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` includes this header with the matching offset, mask, and SMN headers. That source implements NBIO operations such as HDP remap, memory controller access enablement, doorbell aperture programming, interrupt doorbell ranges, and syshub indirect access.
- `drivers/gpu/drm/amd/amdgpu/soc15.c` includes this header alongside many SOC15 IP headers. That source selects and initializes SOC15-family AMDGPU IP blocks.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` includes this header as part of the SMU10 hardware manager register include bundle.

No direct uses of the specific chunk macros were found in the nearby include sites during this pass; many generated default headers are included as shared symbolic catalogs even when only a subset of constants is referenced by handwritten code.

## State And Persistence Behavior

The header stores no mutable state and has no persistence behavior of its own. The macro values represent hardware-visible default/reset state for NBIO-related PCI config and MMIO-visible register blocks. Persistence concerns are therefore external:

- If driver suspend/resume, reset, or firmware handoff code uses these defaults as canonical values, a wrong macro can cause incorrect restore or validation behavior.
- Constants such as PCIe link capability, device control, AER masks/severity, VC resource control/status, and MSI capability defaults describe observable PCI configuration state and may affect enumeration, diagnostics, or error handling if programmed from these values.
- The IOMMU/SMMU ID and control defaults are especially sensitive because they describe translation capability and MMIO behavior exposed to system-level IOMMU paths.

## Dependencies

This chunk depends only on the C preprocessor. It does not include other headers, but it is semantically coupled to generated AMD register metadata:

- `nbio_7_0_offset.h` supplies register offsets and index names.
- `nbio_7_0_sh_mask.h` supplies field masks and shifts.
- `nbio_7_0_smn.h` supplies SMN addressing constants.
- AMDGPU helper macros such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `SOC15_REG_OFFSET` in consumer code perform actual register access; this header only supplies literal defaults.

The file is part of an AMDGPU source tree under a larger `sources/distributed-fs/ceph-client` import. Nothing in this chunk is specific to Ceph; it is Linux DRM/AMDGPU hardware-description material.

## Integration Points

The visible hardware integration points are NBIO, PCIe/NBIF, IOMMU L2/SMMU, and SMU10 include aggregation.

Notable register families in this chunk:

- PCI identity/config header fields: vendor ID, device ID, command, status, revision, class code, BARs, ROM base, interrupt line/pin.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, device/link capabilities and controls, link status, link capability 2/control 2/status 2.
- MSI/MSI-X capability defaults: capability list pointers, message control/address/data, masks, pending bits.
- PCIe enhanced capabilities: vendor-specific, VC, serial number, AER, TLP prefix logs, secondary PCIe, BAR, power budget, dynamic power allocation, ACS, ATS, page request, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, DPC, RP PIO, and ESM.
- IOMMU/SMMU configuration and identification defaults.
- PCIe lane equalization defaults. Root-complex blocks use `0x00007f0f`; endpoint extended-capability blocks use `0x00007f00`; BIFPLR blocks use `0x00007f7f`.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. These constants must match the silicon register database for NBIO 7.0. Manual edits are risky because a single hex literal can change PCIe/IOMMU capability exposure or reset behavior.
- The unprefixed `cfg*` endpoint-function-0 macro block can collide with other generated config headers if multiple similar headers are included into the same translation unit. The include guard prevents duplicate inclusion of this header, but not macro-name conflicts with other headers.
- Capability-chain values encode offsets and next-capability links. Values such as `0x11000000`, `0x14000000`, `0x20020000`, `0x2a010019`, `0x2b000000`, `0x32800000`, and `0x33000000` are opaque without the paired register layout; accidentally changing them can silently break PCIe enhanced capability traversal.
- Most macros default to `0x00000000`, so meaningful review should focus on non-zero defaults and on block-to-block differences rather than raw macro count.
- The chunk ends in the middle of the `BIFPLR4` address block. Whole-file analysis must merge later chunks to understand the complete `BIFPLR4` block and subsequent NBIO register families.
- Some fields represent writable defaults (`*_W_DEFAULT`) while others represent read-only identification-like values. Consumer code must respect hardware access semantics from the paired mask/offset docs and not infer writability from this file alone.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/driver integration signals:

- Compile AMDGPU/SOC15 code with this header included; macro-name collisions or malformed generated lines should fail compilation.
- Compare generated constants against the authoritative AMD register database or a known-good upstream import for the same ASIC generation.
- Boot/probe AMDGPU hardware using NBIO 7.0/SOC15-era devices and watch for PCIe enumeration, IOMMU, MSI/MSI-X, AER, link-training, and doorbell-related regressions.
- Exercise suspend/resume and GPU reset paths to catch incorrect assumptions about reset/default values.
- Inspect kernel logs for AMDGPU NBIO, PCIe AER, IOMMU/SMMU, and SMU initialization warnings.
- Because this chunk contains no executable code, unit-test coverage is not expected; compile coverage and hardware smoke tests are the relevant checks.

## Cross-Chunk Notes

This is an oversized-file chunk report, not the final per-file research document. Later reconciliation should merge this with reports for the remaining line ranges of `nbio_7_0_default.h`, preserving the complete source path and summarizing all address blocks in the full generated header.

### subset-b-003061: lines 2881-5824

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

### subset-b-003062: lines 5825-8711

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 5825-8711

## Scope

This chunk is part of AMDGPU's generated NBIO 7.0 default-register header. It contains C preprocessor constants only: every exported item in the range is a `#define` ending in `_DEFAULT`, and there are no functions, structs, enums, variables, branches, locks, allocations, or direct MMIO operations.

The range starts inside `addressBlock: nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, whose header is on line 5764 before this chunk. It then covers complete NBIF PCI configuration blocks for `DEV1_EPF0`, `DEV1_EPF1`, and `DEV1_EPF2`; MSI-X table and pending-bit-array default blocks for AMDGFX, PSP, USB3, MP2, and GBE functions; PCIe physical root-port configuration defaults for BIFPLR0 through BIFPLR6; and per-port PCIe direction defaults for BIFP0, BIFP1, BIFP2, plus the beginning of BIFP3.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMD GPU hardware register metadata, not Ceph or filesystem logic.

## Purpose

`nbio_7_0_default.h` publishes reset/default values for NBIO 7.0 registers. This chunk describes the default configuration image for PCIe/NBIF endpoint functions, MSI-X table apertures, PCIe bridge/root-port configuration spaces, and low-level PCIe port/link-controller registers. Driver code can include these constants alongside the matching offset and shift/mask headers to compare hardware state against expected reset values, initialize registers, preserve documented defaults, or generate ASIC-specific register tables.

The chunk is hardware-description data. Its correctness is tied to AMD's NBIO 7.0 register specification and to the generated sibling headers that assign addresses and bitfields for the same register names.

## Important APIs, Types, Functions, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the macro namespace:

- `smnBIF_CFG_DEV0_EPF7_1_*_DEFAULT`: tail of a device 0, embedded physical function 7 PCIe configuration block. The visible part covers MSI/MSI-X capability defaults, SATA capability placeholders, vendor-specific enhanced capability defaults, AER defaults, BAR capability/control defaults, power-budget/DPA defaults, ACS defaults, and ARI defaults.
- `smnBIF_CFG_DEV1_EPF0_1_*_DEFAULT`, `smnBIF_CFG_DEV1_EPF1_1_*_DEFAULT`, and `smnBIF_CFG_DEV1_EPF2_1_*_DEFAULT`: default PCI configuration-space values for device 1 functions. EPF0 is the most complete block in this range, including normal PCI header registers, PCIe capability, MSI/MSI-X, virtual channel, AER, BAR, power-budget, DPA, secondary PCIe, lane equalization, ACS, LTR, ARI, SR-IOV, PASID, resizable BAR, and TPH requester defaults. EPF1 and EPF2 carry a smaller but similar function capability/default surface.
- `smnPCIEMSIX_*_MSIX_TABLE_*_DEFAULT`: 128 default table entries each for `AMDGFX`, `PSP`, `USB3_0`, `USB3_1`, `MP2`, `GBE0`, and `GBE1`. The entries are all zero in this chunk, meaning message address/data/vector-control table storage has no nonzero generated reset value here.
- `smnPCIEMSIX_*_MSIX_PBA_DEFAULT`: one pending-bit-array default for each of the same MSI-X functions, also zero.
- `smnBIFPLR0_1_*_DEFAULT` through `smnBIFPLR6_1_*_DEFAULT`: repeated PCIe physical root-port configuration defaults. Each complete BIFPLR block has 169 definitions, with nonzero capability-chain, PCIe capability, link, MSI, SSID, vendor-specific, VC, AER, BAR, power-budget, DPA, secondary PCIe, lane equalization, ACS, LTR, ARI, SR-IOV, PASID, resizable BAR, and TPH defaults.
- `smnBIFP0_*_DEFAULT`, `smnBIFP1_*_DEFAULT`, `smnBIFP2_*_DEFAULT`, and partial `smnBIFP3_*_DEFAULT`: PCIe port/direct-register defaults for transaction-layer, data-link, flow-control, error, RX/TX, link-control, lane-control, clock/data recovery, equalization, link-management, strap, L1 PM substate, BCH ECC, HPGI, descriptor, and TX clock performance-counter registers.

The full range contains 2,803 `#define` rows. The address-block counts are useful validation anchors: seven 128-entry MSI-X table blocks, seven single-entry MSI-X PBA blocks, seven 169-definition BIFPLR blocks, three complete 72-definition BIFP port-direct blocks, and a partial BIFP3 block ending at `smnBIFP3_PCIE_LC_SPEED_CNTL_DEFAULT`.

## Control Flow And Runtime Behavior

This header has no executable control flow. It affects runtime only when included by code that uses these constants while programming or checking NBIO 7.0 hardware.

The implied runtime pattern is:

1. Caller code selects a register address from `nbio_7_0_offset.h` or `nbio_7_0_smn.h`.
2. It uses field geometry from `nbio_7_0_sh_mask.h` when only part of a register should change.
3. It may compare against, preserve, or write the `_DEFAULT` value from this header.
4. The actual read/write happens through AMDGPU accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD` in the including driver code.

The hardware behavior represented by this chunk is PCIe/NBIF enumeration and link behavior rather than software branching: PCI config capability chains, MSI/MSI-X interrupt-vector storage, AER reporting defaults, BAR sizing/control defaults, root-port bridge capabilities, link speed/width/training defaults, lane equalization defaults, ASPM/L1-substate-related defaults, and port flow-control/error/link-management defaults.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. Its constants describe hardware reset/default state.

State classes represented in the chunk include:

- PCI configuration-space defaults for endpoint and root-port functions: vendor/device/header registers, BARs, capability pointers, command/status words, PCIe device/link capability/control/status registers, MSI/MSI-X, SSID, SR-IOV, PASID, resizable BAR, TPH, ACS, ARI, LTR, DPA, and power-budget capability blocks.
- MSI-X table/PBA state for function-specific interrupt delivery. The generated default table entries and PBA values are zero, so runtime vector programming must come from OS/driver interrupt setup.
- Link and port controller state in `BIFP*` blocks: TX/RX control, replay and credit controls, flow-control advertised/allocation state, error controls, link-control/training registers, lane controls, equalization forcing/best-settings registers, link-management status/masks, straps, L1 PM substates, BCH ECC, HPGI, and performance-counter defaults.
- Hardware-updated status fields are represented as default values only. For example, link status, AER status, MSI-X pending bits, lane status, link-management status, and RX captured LTR status can change at runtime after hardware initialization, firmware programming, PCI enumeration, link training, interrupt delivery, or error handling.

Persistence across warm reset, GPU reset, suspend/resume, BACO, PCIe retraining, or function-level reset is not defined here. AMDGPU reset/resume code and platform firmware decide when hardware is reinitialized and whether these defaults are restored, overridden, or merely used as reference values.

## Dependencies And Integration Points

The direct dependencies are the C preprocessor and the generated AMD register naming scheme. Functional use depends on sibling generated headers:

- `nbio_7_0_offset.h` for register offsets and base indices.
- `nbio_7_0_sh_mask.h` for field masks and shifts.
- `nbio_7_0_smn.h` for SMN-addressed register definitions.

In-tree include sites for `nbio_7_0_default.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`

Those consumers integrate NBIO 7.0 data with ASIC initialization, PCIe register access, memory-controller access enablement, doorbell ranges, interrupt handling, HDP flush offsets, clock gating, light sleep, power-management headers, and common SOC15 device setup. The exact macros in this chunk may not all be referenced by normal C code paths, but they are part of the generated ASIC register ABI and can be used by bring-up code, diagnostics, debug tooling, future driver paths, or generated register-table checks.

## Risks And Edge Cases

- The chunk boundaries are artificial. Line 5825 begins mid-`DEV0_EPF7` block, and line 8711 ends inside the `BIFP3` port-direct block. Whole-block conclusions must be merged with adjacent chunks.
- Generated default drift can compile cleanly while changing hardware behavior. A wrong nonzero default for PCIe capability, AER severity/mask, BAR control, link speed/width, lane equalization, or L1 substate register can affect enumeration, link training, power management, or error reporting.
- Many blocks are dense repetitions with only suffix changes. MSI-X tables repeat 128 zero entries per function, BIFPLR root ports repeat the same 169-definition pattern, and BIFP ports repeat the same 72-definition pattern. Off-by-one suffix or missing-row errors are easy to miss in review.
- Zero defaults are not proof that a register is unused. MSI-X table entries, PBA bits, BARs, AER status, lane status, and link-management status are normally programmed or updated dynamically after reset.
- PCIe capability-chain defaults encode offsets between capabilities and enhanced capabilities. Bad values can break OS PCI capability traversal or hide advertised features such as MSI, AER, ACS, ARI, SR-IOV, PASID, resizable BAR, LTR, or TPH.
- Status, clear, and mask registers often have side effects or hardware-updated semantics. Treating a `_DEFAULT` value as a safe writeback value without preserving live status can clear events, drop interrupts, or mask errors.
- Port/link-control defaults such as `PCIE_LC_CNTL*`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_CDR_CNTL`, equalization controls, and L1 PM substate values are link-stability sensitive and may vary by board, straps, firmware, or ASIC revision.

## Test And Validation Signals

Useful validation is mostly generated-header consistency plus hardware smoke testing:

- Build AMDGPU configurations that include NBIO 7.0 headers to catch missing, malformed, or renamed macros.
- Compare each macro name in this chunk against `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h` so defaults, addresses, and field definitions stay aligned.
- Run generation checks for the repeated structures: seven 128-entry MSI-X table blocks should remain all-zero unless the hardware spec changes; seven PBA blocks should remain present; BIFPLR0-6 should retain aligned register lists and defaults; BIFP0-2 should match each other for the complete port-direct subset.
- Validate nonzero PCIe capability defaults against the hardware specification, especially capability-list pointers, `PCIE_CAP`, `DEVICE_CNTL`, `LINK_CAP`, `LINK_STATUS`, `LINK_CAP2`, `LINK_CNTL2`, AER severity/mask, BAR controls, DPA status, secondary PCIe lane equalization, LTR, ARI, SR-IOV, PASID, resizable BAR, and TPH fields.
- On NBIO 7.0 hardware, exercise PCI enumeration, MSI/MSI-X interrupt setup, AER reporting, suspend/resume, GPU reset, ASPM/L1 substates, link retraining, and link speed/width reporting while watching kernel logs for PCIe errors, AMDGPU reset storms, interrupt failures, or unexpected bandwidth drops.
- For low-level debug paths, read back representative `BIFPLR*` and `BIFP*` registers after reset and after driver initialization to distinguish hardware reset defaults from firmware or driver overrides.

## Chunk Boundary Notes

The previous chunk owns the start of `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`; this chunk begins at its MSI-X and enhanced-capability tail. The next chunk owns the remainder of `nbio_pcie0_bifp3_pciedir_p`, starting after `smnBIFP3_PCIE_LC_SPEED_CNTL_DEFAULT`, and then any later BIFP port-direct blocks. The final per-file research document should reconcile these boundaries before making whole-file statements about all NBIO 7.0 defaults.

### subset-b-003063: lines 8712-11690

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

### subset-b-003064: lines 11691-14586

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 11691-14586

## Scope

This chunk is a generated AMDGPU NBIO 7.0 register-default header slice. It contains C preprocessor constants only: `#define` names ending in `_DEFAULT` mapped to reset/default register values. There are no functions, structs, enums, branches, allocation sites, or runtime side effects in the covered lines.

The requested range begins inside the tail of the `BIFPLR3_2` PCIe root-port config-space defaults, then covers complete `BIFPLR4_2`, `BIFPLR5_2`, and `BIFPLR6_2` root-port config blocks. It continues through NBIF PCIe dummy/config blocks for RC and endpoint functions, then into NBIF/BIF MMIO defaults for system indexed access, RCC strap/endpoint/downstream registers, BIF PF virtualization/doorbell/power/reset registers, and GDC doorbell/SDP controls. The range ends in a repeated `mm`-prefixed `nbio_nbif0_rcc_ep_dev0_BIFDEC1` block.

The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`. Companion headers in the same directory provide register offsets/SMN addresses and bit masks (`nbio_7_0_offset.h`, `nbio_7_0_smn.h`, `nbio_7_0_sh_mask.h`); this file supplies the reset/default values used by ASIC-specific code and generated register knowledge.

## Purpose

The chunk documents default values for NBIO 7.0 PCIe/NBIF hardware blocks. These defaults define the expected initial programming for PCIe configuration-space capabilities and NBIF control registers before the driver applies runtime policy. The values are useful for reset programming, comparing observed hardware state against generated ASIC data, initializing saved register images, and avoiding magic constants in AMDGPU ASIC code.

Major responsibilities represented here:

- PCIe root-port config-space templates for `BIFPLR3_2` through `BIFPLR6_2`.
- Root-complex config templates for `BIF_CFG_DEV0_RC2` and `BIF_CFG_DEV1_RC2`.
- Endpoint-function config templates for `DEV0_EPF0_3`, `DEV0_EPF1_2`, `DEV0_EPF2_2` through `DEV0_EPF7_2`, and `DEV1_EPF0_2` through `DEV1_EPF2_2`.
- PCIe capability chain defaults: standard PCIe capability, MSI, SSID, vendor-specific enhanced capability, VC, device serial number, AER, secondary PCIe, ACS, multicast, BAR, power budget, DPA, ATS, PRI/page request, PASID, TPH requester, LTR, ARI, and SR-IOV-related defaults where present.
- NBIF/BIF control defaults for indexed MMIO, BIOS scratch registers, strap revision ID, endpoint LTR/DPA controls, downstream port controls, reset/interrupt/pad controls, BACO timers, VDDGFX aperture windows, doorbell apertures, HDP flush remaps, GPU IOV configuration sizes, mailbox registers, and GDC doorbell/SDP controls.

## Important Definitions

The generated names encode the access window, instance, register, and default value:

- `smnBIFPLR*_2_*_DEFAULT` names are SMN-accessible PCIe root-port defaults. The chunk starts with the remainder of `smnBIFPLR3_2` and fully covers `smnBIFPLR4_2`, `smnBIFPLR5_2`, and `smnBIFPLR6_2`.
- `smnBIF_CFG_DEV*_RC2_*_DEFAULT` names describe NBIF root-complex PCIe config defaults.
- `smnBIF_CFG_DEV*_EPF*_2_*_DEFAULT` and `smnBIF_CFG_DEV0_EPF0_3_*_DEFAULT` describe endpoint-function config-space defaults.
- `smnRCC_*` names describe root-complex controller strap, endpoint, downstream, and downstream-port defaults.
- `smnBIF_BX_PF1_*` names describe BIF PF1 MMIO/control defaults, including reset, interrupts, doorbells, BACO, VDDGFX apertures, HDP flush controls, ring buffer/mailbox state, and GPU IOV sizing.
- `smnGDC1_*` names describe GDC1 SDP, SHUB, doorbell-range, ATDMA, fence, S2A, and power-gating defaults.
- `mm*` names at the end mirror indexed/MMIO register defaults for system, syshub, strap, and endpoint blocks.

Notable non-zero defaults and patterns:

- Root-port `BIFPLR*_2` blocks use common PCIe defaults: `INTERRUPT_LINE_DEFAULT` is `0xff`, `PCIE_CAP_LIST_DEFAULT` is `0x0000a000`, `PCIE_CAP_DEFAULT` is `0x00000002`, `DEVICE_CNTL_DEFAULT` is `0x00002810`, `LINK_CAP_DEFAULT` is `0x00011c03`, `LINK_STATUS_DEFAULT` is `0x00000001`, `LINK_CAP2_DEFAULT` is `0x0000000e`, and `LINK_CNTL2_DEFAULT` is `0x00000003`.
- Root-complex `BIF_CFG_DEV*_RC2` blocks differ from endpoint/root-port templates by setting `INTERRUPT_PIN_DEFAULT` to `1`, `PCIE_CAP_DEFAULT` to `0x42`, `LINK_STATUS_DEFAULT` to `0x2001`, and lane equalization defaults to `0x00007f0f`.
- Endpoint function blocks use `PCIE_CAP_DEFAULT` `0x2`, `DEVICE_CAP_DEFAULT` `0x10000000`, `DEVICE_CNTL_DEFAULT` `0x2810`, `LINK_CAP_DEFAULT` `0x11c03`, `LINK_STATUS_DEFAULT` `1`, MSI message control `0x80`, and AER severity/masks. Full EPF0/EPF1-style functions include VC, serial number, secondary PCIe, lane equalization, ACS/ATS/PRI/PASID/TPH/MC/LTR/ARI, and SR-IOV page-size defaults; smaller EPF2-EPF7-style blocks include `FLADJ_DEFAULT` `0x20`, BAR, power-budget, DPA, ACS, and ARI defaults.
- DPA-related defaults appear in endpoint config and endpoint RCC/MMIO blocks: `PCIE_DPA_STATUS_DEFAULT` `0x100`, `EP_PCIE_F0_DPA_CAP_DEFAULT` `0x190a1000`, latency indicator `0xf0`, control `0x100`, and substate power allocations descending from `0xfa` to `0x0a`.
- Strap defaults include `RCC_DEV0_EPF0_STRAP0_DEFAULT`/`RCC_STRAP2_RCC_DEV0_EPF0_STRAP0_DEFAULT` at `0x300015dd`, the register used by NBIO code to derive the device revision ID through the corresponding mask/shift header.
- BIF PF1 has hardware-control defaults such as `BX_RESET_EN_DEFAULT` `0x00010003`, `BIF_BUSY_DELAY_CNTR_DEFAULT` `0x3f`, BACO exit timers `0x100` through `0x500`, VDDGFX aperture lower/upper pairs, doorbell global aperture lower/upper pairs, HDP flush remaps `0x385c`/`0x3858`, GPU IOV config sizes `8`, pad controls, and `DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT` `0x100`.
- GDC1 non-zero defaults include `NGDC_SDP_PORT_CTRL_DEFAULT` and `NGDC_SDP_PORT_CTRL_SOCCLK_DEFAULT` at `0xf`, plus `ATDMA_MISC_CNTL_DEFAULT` `0x04040001`.

## Control Flow

There is no direct control flow in this header. Runtime control flow belongs to AMDGPU NBIO and PCIe code that includes this generated data:

1. ASIC-specific code includes the default, offset, SMN, and mask headers for NBIO 7.0.
2. Driver paths read or write NBIO registers through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`.
3. Field helpers and mask constants from `nbio_7_0_sh_mask.h` interpret values whose defaults are defined here.
4. Reset, initialization, suspend/resume, BACO, PCIe link-management, virtualization, and diagnostics paths compare against or program hardware using the generated constants.

Concrete integration observed nearby: `nbio_v7_0.c` includes this header and reads `mmRCC_DEV0_EPF0_STRAP0` to derive `STRAP_ATI_REV_ID_DEV0_F0`. Related NBIO versions use endpoint LTR control (`EP_PCIE_TX_LTR_CNTL`) to adjust LTR behavior and use the same register-access helper families. This chunk therefore participates in the data side of those flows even though it does not execute code itself.

## State And Persistence

The macros are compile-time constants and do not store state. The state they describe lives in hardware registers and PCIe configuration-space images:

- PCIe capability state: link capability/status, link-control target speed, MSI/SSID capability-list placement, AER masks/severity/log registers, VC resources, ACS/ATS/PASID/PRI/TPH/LTR/ARI/MC/secondary capability metadata, and DPA power-allocation state.
- Endpoint and root-complex state: command/status, BAR controls, bus/window registers, interrupt line/pin, link training status, and error reporting defaults.
- NBIF MMIO state: indexed access registers, BIOS scratch registers, interrupt controls, CAM remap defaults, syshub access windows, endpoint LTR/DPA controls, downstream controls, reset enables, BACO timers, VDDGFX/doorbell apertures, HDP flush remap addresses, mailbox buffers, ring-buffer pointers, and GDC doorbell/ATDMA controls.

Persistence across GPU reset, runtime suspend, BACO, hot reset, and system sleep depends on the hardware power domain and the AMDGPU reset/resume sequence that reprograms or restores registers. This header has no persistence mechanism; it supplies the expected reset/reference values used by code that manages persistence.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and include ordering. Functional dependencies include:

- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` for the actual register addresses corresponding to these defaults.
- `nbio_7_0_sh_mask.h` for masks/shifts used to interpret or modify fields in registers with these defaults.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, which includes this header and uses NBIO register definitions in ASIC-specific callbacks.
- Common AMDGPU register helpers (`RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`) and field macros (`REG_GET_FIELD`, `REG_SET_FIELD` style patterns).
- PCIe, AER, ASPM, DPA/LTR, GPU reset, BACO, virtualization/IOV, doorbell, HDP flush, and SMU/PM integration paths that rely on NBIF/NBIO state being correctly described.

The document should be merged later with adjacent chunks of the same source file. This range starts mid-block (`BIFPLR3_2`) and repeats some `mm` address blocks after SMN-prefixed equivalents, so the final per-file research should reconcile duplicate address-block names and line-boundary splits rather than treating this chunk as a complete standalone register map.

## Risks

- Generated default drift can be hard to detect. A single incorrect default in PCIe link, AER, LTR, DPA, BACO, or doorbell programming can produce link-training failures, power-management regressions, lost interrupts, or inaccessible MMIO/doorbell ranges.
- Repeated templates invite inconsistent edits. `BIFPLR4_2`, `BIFPLR5_2`, and `BIFPLR6_2` are structurally aligned; root-complex and endpoint-function families also repeat. Any intentional exception should be traceable to the ASIC register specification.
- Capability-list default values encode PCIe config-space layout. Incorrect next-capability pointers or enhanced-capability headers can confuse config-space traversal, AER setup, SR-IOV/ARI handling, or OS PCI core behavior.
- Error mask/severity defaults are security and reliability sensitive. AER masks such as uncorrectable/correctable masks and severity values determine which errors are reported, suppressed, or treated as fatal.
- Doorbell and VDDGFX aperture defaults are address-window data. Incorrect lower/upper bounds can misroute doorbells, expose unintended ranges, or break GPU/CPU synchronization.
- Reset, BACO, and pad-control defaults are platform-sensitive. Incorrect values can leave hardware stuck across reset, break wake/link behavior, or require a full power cycle.
- Manual edits to generated headers are high risk. These files should normally be regenerated from the authoritative register database and reviewed with generated diff tooling rather than changed by hand.

## Test Signals

Useful validation signals for changes touching this chunk:

- Build AMDGPU with NBIO 7.0 support enabled to catch missing or renamed macros and include-order problems.
- Compare this header against the authoritative AMD register database or regeneration output for NBIO 7.0.
- Run static symmetry checks across repeated root-port and endpoint-function blocks: identical blocks should keep matching defaults except where the ASIC spec intentionally differs.
- Boot NBIO 7.0 hardware and verify AMDGPU probe, PCIe config-space enumeration, BAR setup, AER capability reporting, and link speed/width reporting.
- Exercise suspend/resume, GPU reset, BACO entry/exit, hot reset if supported, and PCIe link retraining; watch for AMDGPU timeout/reset messages and PCIe AER logs.
- Validate LTR/DPA behavior with runtime power management enabled, especially around `EP_PCIE_TX_LTR_CNTL` and DPA substate power-allocation defaults.
- Validate doorbell/HDP paths under graphics, SDMA, UVD/VCE or video, and KFD workloads; failures here may show as queue stalls, missing interrupts, or cache/coherency flush timeouts.
- For virtualization or SR-IOV/GPU IOV configurations, verify mailbox, GPUIOV config-size, ARI/SR-IOV-related defaults, and BIF PF/VF transaction-pending registers behave as expected.

### subset-b-003065: lines 14587-14865

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 14587-14865

## Scope

This chunk is the final section of the generated AMD NBIO 7.0 default-register header. It contains `#define` constants for reset/default values, not executable code. The covered range spans the tail of the `nbio_nbif0_rcc_ep_dev0_BIFDEC1` block and then complete default sets for downstream PCIe, RCC, BIF/BX PF, GDC, GFX MSI-X, and Syshub indirect MMIO blocks before the file's include guard closes.

The companion headers `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h` provide the register offsets and bit masks that make these defaults usable. Active NBIO v7.0 driver code includes this file from `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`.

## Purpose

The constants document hardware reset expectations for NBIO 7.0 registers. Driver code mostly uses the offset and mask headers for live register programming, while this default header supplies authoritative reset values for generated register metadata, diagnostics, initialization comparisons, and ASIC-specific bring-up references.

The chunk covers several functional areas:

- PCIe endpoint/downstream capability defaults, including Dynamic Power Allocation and link-control defaults.
- RCC register-configuration and reset defaults for config windows, peer ranges, BACO control, requester ID restore, and bus-number tracking.
- BIF/BX PF defaults for framebuffer enable, doorbell apertures, HDP remap/coherency flush registers, mailbox registers, interrupt controls, reset controls, and BACO timers.
- GDC defaults for SDP ports, SDMA/IH/MMSCH doorbell ranges, ATDMA, and doorbell fencing.
- GFX MSI-X vector table defaults with vectors initially masked.
- Syshub indirect MMIO defaults for clock gating, QoS, client controls, scratch registers, and NIC400 fabric function-modifier registers.

## Important Macros and Register Groups

There are no functions, structs, enums, or typedefs in this range. The important API surface is the macro namespace:

- `mmEP_PCIE_*_DEFAULT` and `mmPCIE_F0_DPA_*_DEFAULT`: endpoint PCIe defaults for DPA capability, latency, substate power allocation, PME, TX/RX control, error control, and link speed.
- `mmDN_PCIE_*_DEFAULT` and `mmPCIE_*_DEFAULT`: downstream/downstream-port PCIe defaults. Notable defaults are `mmDN_PCIE_BUS_CNTL_DEFAULT == 0x00000080`, `mmPCIE_ERR_CNTL_DEFAULT == 0x00000500`, and zeroed link-control defaults.
- `mmRCC_*_DEFAULT`: RCC defaults. `mmRCC_RESET_EN_DEFAULT == 0x00008000`, `mmRCC_PEER_REG_RANGE0_DEFAULT` and `mmRCC_PEER_REG_RANGE1_DEFAULT` are `0xffff0000`, and most configuration, peer offset, and bus-number registers reset to zero.
- `mmBIF_*_DEFAULT`, `mmBUS_CNTL_DEFAULT`, `mmBX_*_DEFAULT`, and related PF constants: BIF/BX PF reset defaults. Nonzero defaults include `mmBX_RESET_EN_DEFAULT == 0x00010003`, `mmBIF_BUSY_DELAY_CNTR_DEFAULT == 0x0000003f`, the BACO exit timers, VDDGFX lower/upper windows, doorbell global apertures, HDP remap controls, GPUIOV config sizes, and pad controls.
- `mmBIF_DOORBELL_GBLAPER*_DEFAULT`: default global doorbell aperture windows. Aperture 1 starts with `0x80000780`/`0x000007fc`, and aperture 2 starts with `0x80000800`/`0x0000087c`.
- `mmREMAP_HDP_MEM_FLUSH_CNTL_DEFAULT` and `mmREMAP_HDP_REG_FLUSH_CNTL_DEFAULT`: default remap targets for HDP memory and register flush controls. `nbio_v7_0_remap_hdp_registers()` overwrites the live registers during driver initialization based on `adev->rmmio_remap`.
- `mmGPU_HDP_FLUSH_REQ_DEFAULT` and `mmGPU_HDP_FLUSH_DONE_DEFAULT`: default zeroed flush request/done state. `nbio_v7_0_hdp_flush_reg` maps the done bits for CP0-CP9 and SDMA0/1 in the live driver.
- `mmBIF_SDMA0_DOORBELL_RANGE_DEFAULT`, `mmBIF_SDMA1_DOORBELL_RANGE_DEFAULT`, `mmBIF_IH_DOORBELL_RANGE_DEFAULT`, and `mmBIF_MMSCH0_DOORBELL_RANGE_DEFAULT`: all reset to zero. `nbio_v7_0_sdma_doorbell_range()`, `nbio_v7_0_ih_doorbell_range()`, and `nbio_v7_0_vcn_doorbell_range()` program their `OFFSET` and `SIZE` fields at runtime.
- `mmGFXMSIX_VECT{0,1,2}_*_DEFAULT` and `mmGFXMSIX_PBA_DEFAULT`: MSI-X vector address/data defaults are zero, while each vector control default is `0x00000001`, consistent with a masked vector at reset.
- `ixSYSHUB_MMREG_IND_*_DEFAULT`: defaults for indirect Syshub registers. Notable values include QoS controls at `0x0000001e`, DMA client controls at `0x20200000`, `ixSYSHUB_MMREG_IND_SYSHUB_CG_CNTL_DEFAULT == 0x00082000`, `ixSYSHUB_MMREG_IND_SYSHUB_HP_TIMER_DEFAULT == 0x00000100`, and MGCG controls at `0x00000080`.

## Control Flow and Runtime Use

This header has compile-time-only behavior:

1. The include guard `_nbio_7_0_DEFAULT_HEADER` prevents duplicate macro definitions.
2. Preprocessor definitions bind register default names to literal 32-bit values.
3. Consumers include this header alongside `nbio_7_0_offset.h` and `nbio_7_0_sh_mask.h`.
4. Runtime code uses the matching `mm*` or `ix*` register names with `RREG32_*`, `WREG32_*`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` helpers.

The chunk itself has no branches, loops, side effects, or direct control transfer. Runtime control flow appears in consumers:

- `nbio_v7_0_remap_hdp_registers()` writes `mmREMAP_HDP_MEM_FLUSH_CNTL` and `mmREMAP_HDP_REG_FLUSH_CNTL`.
- `nbio_v7_0_mc_access_enable()` writes `mmBIF_FB_EN` using `BIF_FB_EN__FB_READ_EN_MASK` and `BIF_FB_EN__FB_WRITE_EN_MASK`.
- Doorbell setup functions program `mmBIF_SDMA0_DOORBELL_RANGE`, `mmBIF_SDMA1_DOORBELL_RANGE`, `mmBIF_IH_DOORBELL_RANGE`, and `mmBIF_MMSCH0_DOORBELL_RANGE`.
- `nbio_v7_0_ih_control()` programs `mmINTERRUPT_CNTL2` and fields in `mmINTERRUPT_CNTL`.
- `nbio_7_0_read_syshub_ind_mmr()` and `nbio_7_0_write_syshub_ind_mmr()` access the `ixSYSHUB_MMREG_IND_*` namespace through `mmSYSHUB_INDEX` and `mmSYSHUB_DATA`.
- `nbio_v7_0_update_medium_grain_clock_gating()` toggles Syshub MGCG enable bits at `ixSYSHUB_MMREG_IND_SYSHUB_MGCG_CTRL_SOCCLK` and `ixSYSHUB_MMREG_IND_SYSHUB_MGCG_CTRL_SHUBCLK`.

## State and Persistence Behavior

The macros are immutable compile-time constants. They do not persist state themselves. The state they describe is hardware register state after reset or default strap/configuration loading.

Live persistent effects occur only when consumers write the associated registers:

- HDP remap registers persist the selected MMIO remap offsets until reset or reprogramming.
- Doorbell range registers persist queue/interrupt aperture routing for SDMA, IH, and VCN/MMSCH blocks.
- `mmBIF_FB_EN` controls whether NBIO permits framebuffer reads and writes.
- MSI-X vector registers hold interrupt target addresses, data, and mask state.
- Syshub indirect registers hold clock-gating, QoS, and interconnect control state.
- Scratch and mailbox registers are default-zero storage/control windows; their content can be used by firmware, virtualization, or driver paths outside this chunk.

Because these values are defaults, driver code must not assume they remain unchanged after firmware, bootloader, SR-IOV PF/VF management, suspend/resume, runtime power management, or previous driver initialization has touched the hardware.

## Dependencies

Direct dependencies are minimal:

- C preprocessor support for include guards and `#define`.
- Register naming conventions shared with generated AMD ASIC headers.
- Companion NBIO 7.0 offset and mask headers for usable addresses and field layout.

Runtime consumers depend on the amdgpu SOC15 register access layer:

- `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET` for NBIO MMIO access.
- `RREG32_PCIE`, `WREG32_PCIE` for PCIe/SMN-style register access where applicable.
- `REG_SET_FIELD` and generated `__SHIFT`/`__MASK` constants from `nbio_7_0_sh_mask.h`.
- `struct amdgpu_device` fields such as `rmmio_remap`, `rmmio_base`, `cg_flags`, `dummy_page_addr`, and SR-IOV state helpers in `amdgpu/nbio_v7_0.c`.

## Integration Points

Key integration points visible from this chunk and its consumers:

- NBIO IP block selection: `nbio_v7_0_funcs` exposes NBIO operations to the broader amdgpu driver and relies on registers whose defaults are listed here.
- KFD/HSA integration: HDP flush remap constants are rewritten using `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` and `KFD_MMIO_REMAP_HDP_REG_FLUSH_CNTL`, allowing user queues and compute paths to reach flush controls through a remapped MMIO page.
- Interrupt handling: `mmINTERRUPT_CNTL`, `mmINTERRUPT_CNTL2`, IH doorbell range defaults, and GFX MSI-X defaults connect NBIO reset state to amdgpu interrupt setup.
- Doorbell routing: zero default ranges mean SDMA, IH, and MMSCH doorbells are disabled until the driver assigns aperture offsets and sizes.
- Power management: BACO timers, VDDGFX windows, CLKREQ/PERST/PX pad controls, Syshub MGCG defaults, and light-sleep related Syshub controls integrate with power-gating, clock-gating, and platform link-management paths.
- Virtualization/SR-IOV: PF/VF decode blocks, GPUIOV config sizes, BIF transaction-pending registers, mailbox message buffers, VMHV mailbox, and doorbell self-ring aperture controls are the default substrate for PF/VF isolation and communication.
- Fabric/interconnect tuning: Syshub QoS, CL control, and NIC400 function-modifier defaults describe baseline data-movement behavior between DMA/HST clients and the system fabric.

## Risks and Edge Cases

- Generated-header drift: default values must match the ASIC register database. A stale value can mislead diagnostics or bring-up code even if runtime code mostly writes explicit field values.
- Duplicate register names across address blocks and ASIC generations can cause accidental inclusion or macro collision problems. The include guard prevents duplicate inclusion of this file, but it does not protect against selecting the wrong NBIO generation header.
- Default-zero doorbell and mailbox registers are safe reset values, but treating zero as an initialized runtime configuration would disable doorbells or leave firmware/virtualization mailboxes unusable.
- HDP remap defaults (`0x385c` and `0x3858`) are overwritten by runtime remap setup. Tests or diagnostics that compare against defaults after initialization need to account for that intentional mutation.
- MSI-X vector control defaults are masked (`0x1`). Interrupt tests must program and unmask vectors before expecting delivery.
- Syshub indirect registers require index/data sequencing. Incorrect access ordering or concurrent index/data users can read or write the wrong Syshub register.
- Several defaults encode platform-sensitive timing or electrical behavior, such as BACO exit timers, pad controls, and clock-gating hysteresis. Small changes can cause resume, link training, or low-power-state failures that only appear on specific boards.
- Some live register state can be modified before the kernel driver by firmware or by an SR-IOV PF. The driver should read-modify-write fields where appropriate instead of blindly restoring reset defaults.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage: compile amdgpu paths that include `nbio_7_0_default.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `smu10_inc.h`, with no macro redefinition or missing-symbol failures.
- Register table consistency: generated default names in this file should align one-to-one with matching `mm*`/`ix*` offsets in `nbio_7_0_offset.h` and matching field masks in `nbio_7_0_sh_mask.h` where fields exist.
- Boot/probe on NBIO 7.0 hardware: amdgpu should initialize NBIO, enable framebuffer access, configure IH and SDMA/VCN doorbells, and expose expected PCIe/interrupt behavior.
- HDP flush tests: CP and SDMA flush request/done paths should observe the `GPU_HDP_FLUSH_DONE` masks used by `nbio_v7_0_hdp_flush_reg`.
- Interrupt tests: MSI/MSI-X and IH handling should work after `nbio_v7_0_ih_control()` and doorbell range setup; vectors should not be assumed active at reset because vector control defaults are masked.
- Power-management tests: suspend/resume, BACO entry/exit, clock gating, and light sleep should be exercised because this chunk contains defaults for BACO timers, VDDGFX windows, Syshub MGCG, and pad controls.
- SR-IOV/virtualization tests: PF/VF mailbox, GPUIOV config-size, transaction-pending, and doorbell aperture behavior should be checked on virtualized configurations.
