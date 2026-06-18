# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 12731-14663

## Scope

This chunk is the final large slice of the generated AMD NBIO 2.3 register offset header. It contains C preprocessor address constants only: no functions, structs, variables, allocation, locking, branching, loops, or direct MMIO access. The range starts inside the virtual-function 12 PCIe config-space block, covers full VF13 through VF30 config-space blocks, then defines later NBIF/RCC/BIF/GDC config and MMIO blocks through the file end and closing include guard.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The range contains 1803 `#define` offset constants. Major address blocks in scope are:

- Tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`: 53 PCIe capability and extended-capability config-space offsets.
- Full `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp` through `vf30_bifcfgdecp`: 18 complete virtual-function PCIe config-space windows, 79 constants each.
- `nbio_nbif0_rcc_shadow_reg_shadowdec`: bridge shadow command/base/limit/IRQ and SUC index/data offsets.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`, `nbio_nbif0_bif_bx_SYSDEC`, and `nbio_nbif0_syshub_mmreg_syshubdec`: PF MMIO index/data windows, PCIe/SYSHUB indirect windows, BIOS/SBIOS scratch registers, interrupt controls, and GFX MMIO CAM remap offsets.
- RCC strap, endpoint, downstream, downstream-port, and PF/VF blocks: strap registers, endpoint PCIe controls, downstream link control, root-complex config, doorbell aperture, memory size, and IOV function identifier offsets.
- `nbio_nbif0_rcc_dev0_BIFDEC1`: RCC error, reset, VDM, margining, GPUIOV, peer, bus-number, XDMA, requester-ID, LTR, and arbitration offsets.
- `nbio_nbif0_bif_bx_BIFDEC1` and `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`: BIF reset/interrupt/doorbell/framebuffer/BACO/LUT/HDP flush/ring/mailbox/pad offsets and PF-specific coherency, HDP flush, atomic, BME, self-ring, and mailbox offsets.
- `nbio_nbif0_gdc_GDCDEC`: A2S/S2A, SDP, SHUB, clock/power, and doorbell range offsets for SDMA, IH, MMSCH0, and ACV.
- `nbio_nbif0_rcc_dev0_epf0_BIFDEC2`: four GFX MSI-X vector table entries and PBA offsets.

## Purpose

The purpose of this header section is to publish the NBIO 2.3 address ABI used by AMDGPU code when it programs or reads GPU northbridge I/O, PCIe, root-complex, doorbell, HDP flush, SR-IOV, mailbox, and GDC registers. Each macro names a hardware register or PCI config-space location and expands to the numeric address used by the driver-side access helpers.

This is the companion to generated field/default headers:

- `nbio_2_3_sh_mask.h` supplies the bit masks and shifts for fields inside these registers.
- `nbio_2_3_default.h` supplies generated default values where available.
- This `nbio_2_3_offset.h` file supplies `mm*`, `smn*`, and `cfg*` addresses/base indices. The assigned range is almost entirely `cfg*` addresses, with full physical-looking config addresses such as `0xfffe1030d000` for VF13 config space and `0x30303870` for `cfgBIF_DOORBELL_CNTL`.

Because the file is generated register metadata, exact numeric values are the main contract. A wrong constant often still compiles but points the driver or diagnostic tooling at the wrong hardware register.

## Important Macro Families

### VF PCIe Config-Space Windows

The first line is already inside VF12 and begins at `cfgBIF_CFG_DEV0_EPF0_VF12_1_PCIE_CAP_LIST`. The remainder of VF12 in this chunk covers standard PCIe capability offsets, MSI/MSI-X offsets, vendor-specific enhanced capability offsets, AER status/mask/severity/header-log/TLP-prefix-log offsets, ATS capability/control offsets, and ARI capability/control offsets.

VF13 through VF30 are complete repeated blocks. Each block starts on a 0x1000 boundary:

- VF13 base: `0xfffe1030d000`
- VF14 base: `0xfffe1030e000`
- VF15 base: `0xfffe1030f000`
- VF16 base: `0xfffe10310000`
- ...
- VF30 base: `0xfffe1031e000`

Every full VF block includes the Type 0 config header fields (`VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class/cache/latency/header/BIST, BARs 1-6, CIS pointer, adapter ID, ROM base, capability pointer, interrupt line/pin, and min/max latency), PCIe capability registers (`DEVICE_CAP`, `DEVICE_CNTL`, `LINK_CAP`, `LINK_CNTL`, `DEVICE_CAP2`, `LINK_CNTL2`, etc.), MSI/MSI-X layout, vendor-specific enhanced capability, AER logging/masks, ATS, and ARI. The repeated layout is part of the SR-IOV VF presentation for device 0 endpoint function 0.

The repeated MSI offsets intentionally contain aliases reflecting 32-bit versus 64-bit MSI layouts. For example, within each VF block `MSI_MSG_ADDR_HI` and `MSI_MSG_DATA` share the same numeric address, `MSI_MASK` and `MSI_MSG_DATA_64` share the next address, and `MSI_MASK_64` and `MSI_PENDING` share the following address. Consumers must interpret these according to the MSI capability format, not as independent storage.

### Shadow, Indirect Access, Scratch, and CAM Registers

`nbio_nbif0_rcc_shadow_reg_shadowdec` exposes bridge-shadow config state: command, base address, bus/latency, I/O and memory limit windows, prefetchable limit windows, IRQ bridge control, and SUC index/data. These are shadowed configuration surfaces rather than ordinary C state.

`nbio_nbif0_bif_bx_pf_SYSPFVFDEC` exposes PF MMIO index/data registers (`cfgBIF_BX_PF1_MM_INDEX`, `cfgBIF_BX_PF1_MM_DATA`, and high index). `nbio_nbif0_bif_bx_SYSDEC` exposes indirect SYSHUB and PCIe index/data windows, BIOS/SBIOS scratch registers 0-15, BIF interrupt control registers, and eight GFX MMIO register CAM address/remap pairs plus CAM control/completion registers. `nbio_nbif0_syshub_mmreg_syshubdec` aliases the SYSHUB index/data window.

These constants integrate with indirect register access and firmware/BIOS/driver coordination. Scratch registers and CAM remap registers can carry persistent coordination or address translation state until reset or reprogramming.

### RCC Strap, Endpoint, Downstream, and PF/VF Blocks

The RCC strap block defines `cfgRCC_BIF_STRAP0..6`, several `cfgRCC_BIF_STRAP_F0_*` registers, EOI/interrupt strap state, and sideband/CC register state. Endpoint and downstream blocks define endpoint PCIe controls, debug/status, DPA, LTR, replay/transaction control, unsupported-request response, error-reporting control, link speed, link bandwidth, bus/device/function, and port controls.

The `nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]` block supplies PF/VF-facing root-complex endpoint function 0 offsets:

- `cfgRCC_DEV0_EPF0_RCC_DOORBELL_APER_EN`
- `cfgRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`
- `cfgRCC_DEV0_EPF0_RCC_CONFIG_RESERVED`
- `cfgRCC_DEV0_EPF0_RCC_IOV_FUNC_IDENTIFIER`

`nbio_v2_3.c` directly reads `mmRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE` for memory-size reporting and writes the doorbell aperture enable field through the corresponding register-field helper. The `cfg*` aliases in this chunk are the config-address form of the same generated register database.

### RCC Device 0 Runtime Control

`nbio_nbif0_rcc_dev0_BIFDEC1` contains offsets for root-complex error interrupt control, BACO miscellaneous control, reset enable, VDM support, margining parameters, GPUIOV region, peer register ranges, bus control, config aperture sizing, XDMA lower/upper apertures, feature controls, bus-number capture/list registers, host bus-number registers, peer framebuffer offsets 0-3, device/function number lists, link controls, requester-ID restore, LTR switch control, and multi-host arbitration.

These addresses are relevant to PCIe/root-complex bring-up, virtualization, peer aperture programming, XDMA exposure, reset sequencing, and link management. The header does not encode which values are safe; it only exposes where those values live.

### BIF BX, Doorbells, HDP Flush, BACO, Mailbox, and Pads

`nbio_nbif0_bif_bx_BIFDEC1` defines BIF-side control and status offsets: straps, indirect MM access, bus control, scratch registers, reset control, interrupt control, CLKREQ pad control, feature control, doorbell control/interrupt control, framebuffer enable, BIF interrupt control, VF master/slave transaction pending status, BACO control and exit timers, memory type control, NBIF GFX address LUT control and 16 LUT entries, HDP remap flush controls, BIF ring-buffer controls/pointers/writeback address, mailbox index, MP1 interrupt control, GPU IOV config sizes for UVD/VCE/GFX SDMA, and PCIe pad controls for PERST, PX enable, reference clock, CLKREQ, PWRBRK, WAKE, and VAUX.

`nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` provides PF-specific offsets for BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP register/memory coherency flush, GPU HDP flush request/done, BIF transaction pending, LUT bypass, mailbox transmit/receive dwords, mailbox control, mailbox interrupt control, and VM/hypervisor mailbox.

These constants are directly aligned with `nbio_v2_3.c` behavior. That file writes remap HDP flush registers, enables/disables framebuffer access through `mmBIF_FB_EN`, programs SDMA/VCN/IH doorbell ranges, enables doorbell and self-ring apertures, writes `mmINTERRUPT_CNTL2` and fields in `mmINTERRUPT_CNTL`, returns HDP flush request/done offsets, clears doorbell interrupt status, and sets register remap addresses through versioned NBIO helpers.

### GDC and GFX MSI-X Blocks

The GDC block defines A2S control registers for client and switch paths, completion-buffer and tag allocation, A2S/S2A miscellaneous controls, NGDC SDP port and clock/power controls, SHUB register interface control, doorbell ranges for SDMA0, SDMA1, IH, MMSCH0, and ACV, doorbell fence control, and NGDC power-gating master/slave controls. The SDMA/IH/MMSCH doorbell range addresses are integration points for engine doorbell setup.

The final BIFDEC2 block defines four GFX MSI-X vector entries, each with address low, address high, message data, and control, plus `cfgRCC_DEV0_EPF0_GFXMSIX_PBA`. These offsets describe the GPU-facing MSI-X table/PBA storage for graphics interrupts.

## Control Flow

There is no executable control flow in this chunk. Runtime sequencing is supplied by AMDGPU code that includes this generated header:

1. Versioned NBIO, SMU, MXGPU, or display code selects a generated offset macro.
2. SOC15 or PCIe access helpers combine the offset with IP-instance/base information, or access an SMN/config-space address directly.
3. Generated field macros from `nbio_2_3_sh_mask.h` are used through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, or `WREG32_FIELD15` when only part of a register changes.
4. The driver writes, reads, polls, or returns the offset as part of hardware setup, power management, interrupt setup, doorbell setup, virtualization, or diagnostics.

Observed local include points for `nbio_2_3_offset.h` include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, SMU11 PPT files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`, and display resource files for DCN20/DCN303. The most direct runtime consumer is `nbio_v2_3.c`.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It names hardware-backed register state whose lifetime is controlled by GPU reset, PCIe reset/FLR, BACO, suspend/resume, firmware initialization, SR-IOV PF/VF policy, and driver programming.

The represented hardware state includes:

- PCIe VF config headers and capabilities, including BARs, command/status, MSI/MSI-X, AER, ATS, and ARI state.
- Shadow bridge config, indirect access windows, BIOS/SBIOS scratch state, and GFX MMIO CAM remap state.
- RCC straps, endpoint/downstream/root-complex configuration, bus numbering, peer apertures, XDMA aperture state, requester ID restore, and LTR/link controls.
- Doorbell aperture enablement, doorbell range assignments, self-ring aperture base/control, doorbell interrupt state, and doorbell fence control.
- Framebuffer access enablement, transaction-pending status, HDP coherency and flush request/done state, and remap flush controls.
- BACO/power/clock/pad state, NGDC power controls, BIF ring-buffer pointers/writeback address, and PF/VF mailbox buffers/control.
- GFX MSI-X vector table and pending-bit array state.

Some of these registers are persistent configuration until reset or reprogramming; others are status, command, interrupt-clear, pending, table, pointer, or log locations with hardware side effects. The header itself does not mark access width or side effects, so callers must rely on the ASIC register specification and existing AMDGPU access patterns.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`
- AMDGPU SOC15 and PCIe register helpers, including `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.

Concrete integration points visible in this source tree include:

- `nbio_v2_3_remap_hdp_registers()`, which writes remapped HDP memory/register flush controls.
- `nbio_v2_3_mc_access_enable()`, which toggles BIF framebuffer read/write enablement.
- `nbio_v2_3_get_memsize()`, which reads the RCC config memory-size register.
- `nbio_v2_3_sdma_doorbell_range()`, `nbio_v2_3_vcn_doorbell_range()`, and `nbio_v2_3_ih_doorbell_range()`, which program engine doorbell range registers.
- `nbio_v2_3_enable_doorbell_aperture()` and `nbio_v2_3_enable_doorbell_selfring_aperture()`, which program root-complex and PF self-ring doorbell aperture registers.
- `nbio_v2_3_ih_control()`, which writes interrupt control and dummy-read behavior.
- `nbio_v2_3_get_hdp_flush_req_offset()` and `nbio_v2_3_get_hdp_flush_done_offset()`, which provide higher-level HDP flush code with the relevant BIF PF flush request/done offsets.
- Clock-gating, ASPM, LTR, link-width workaround, and PCIe programming paths in `nbio_v2_3.c`, which use adjacent NBIO 2.3 PCIe/strap/link macros from the same generated header set.
- SMU and display resource code that includes this offset header for ASIC-specific register naming.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line starts midway through VF12, while the file-level report must merge adjacent chunks to describe the full VF12 block.
- The generated `cfg*` constants are untyped numeric addresses. A wrong value can compile cleanly and only fail as hardware misprogramming, bad diagnostics, timeouts, or missing interrupts.
- VF config blocks are highly repetitive. Off-by-one VF numbering or 0x1000-base drift can target the wrong virtual function, which is especially risky for SR-IOV isolation, MSI/MSI-X programming, AER status, ATS, and ARI controls.
- MSI 32-bit/64-bit alias offsets reuse numeric addresses by design. Code must interpret them based on capability mode rather than treating every macro as unique storage.
- Doorbell and self-ring aperture offsets are security- and isolation-sensitive. Incorrect aperture enable/base/size programming can expose the wrong doorbell range or break engine notification.
- HDP flush and coherency offsets are ordering-sensitive. Wrong request/done/remap addresses can leave CPU-visible GPU memory stale or cause waits for acknowledgments that never arrive.
- Scratch, mailbox, and CAM registers may be shared with firmware, BIOS, PSP/SMU, hypervisor, or PF/VF coordination paths. Writing the wrong full-width offset can corrupt coordination state without a type-system warning.
- Power, BACO, pad, reset, link, and clock-related offsets can affect register accessibility and PCIe stability. Register writes around these areas need hardware-sequenced ordering and ASIC-specific guards.

## Test Signals

Useful validation for this chunk is mostly build-time plus hardware integration:

- Build AMDGPU for ASICs using NBIO 2.3 headers; missing or renamed macros should fail in `nbio_v2_3.c`, SMU PPT, MXGPU, or display resource include paths.
- Exercise NBIO bring-up, reset, suspend/resume, BACO, ASPM/LTR, and clock-gating flows; link drops, register-access failures, or power-management regressions can indicate offset/header drift.
- Run doorbell-backed workloads for SDMA, IH interrupt handling, VCN/MMSCH, and ACV where applicable; missed interrupts or engines not waking point at doorbell range/aperture issues.
- Exercise HDP flush paths through graphics and SDMA workloads; stale CPU-visible memory, coherency failures, or timeout waiting for flush done are strong signals for BIF/HDP offset problems.
- In SR-IOV configurations, validate PF and VF isolation, VF config-space enumeration, MSI/MSI-X delivery, ATS/ARI behavior, and AER reporting across VFs near the covered VF12-VF30 range.
- Validate mailbox and MXGPU paths under virtualization; lost PF/VF messages, interrupt storms, or stale message buffers can indicate mailbox or interrupt-control drift.
- Use PCIe error-injection or diagnostics where available to confirm AER status/mask/log offsets and root-complex error controls behave as expected.
