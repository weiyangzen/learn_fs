# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 17467-19906

## Scope

This chunk is a generated AMD NBIO 4.3.0 shift/mask header segment. It contains 2,163 `#define` entries across 261 register-comment blocks. The range starts in the middle of `BIF_BACO_EXIT_TIMER1`, continues through BACO timers, memory type control, graphics address LUTs, SR-IOV virtual-function enable/status bitmaps, reset/remap/ring-buffer/mailbox/pad/power/GPIO controls, RCC decode and strap fields, PF mailbox and HDP coherency controls, GDC clock/power controls, shadowed PCI bridge configuration registers, PF1 MM-index registers, and ends after the first `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL__PM_CONTROL__SHIFT` line.

The content is C preprocessor data only. It defines no functions, structs, variables, local state, allocation, locking, branching, or direct MMIO operations. Its public interface is the generated register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by AMDGPU register helpers.

## Purpose

`nbio_4_3_0_sh_mask.h` supplies the bitfield half of the NBIO 4.3.0 hardware ABI. Driver code pairs these macros with addresses from `nbio_4_3_0_offset.h`, then uses helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 field helpers to compose or decode register values without hard-coding bit positions.

This chunk specifically describes fields used for:

- BACO exit timing and S5/power-transition support.
- Graphics address lookup-table configuration for NBIF routing and MSI address behavior.
- SR-IOV VF register-write, doorbell, and framebuffer access gates and their matching status bitmaps for VF0 through VF30.
- Reset, HDP flush remapping, BIF ring buffer, mailbox, pad, GPIO, CLDO, and SMN clock-select control.
- RCC register decode, peer range, bus-number, requester ID, link, margining, GPU IOV, host VM, and console IOV behavior.
- RCC straps that describe PCIe/NBIO advertised capabilities, including link speeds, power-management support, ACS, ATS, PASID, ARI, AER, SR-IOV, MSI/MSI-X, BAR sizing, device IDs, class codes, reset timing, and vendor-specific capability sizing.
- PF-side HDP coherency flush request/done bits, PF mailbox words, VMHV mailbox, GDC clock/power controls, SWUS/SUC indexed access, PCI bridge shadow registers, and the beginning of VF0 PCIe config-space decoding.

## Important Macro Families

### BACO, Memory, LUT, and VF Gates

The range begins with the tail of `BIF_BACO_EXIT_TIMER1`, defining hardware auto-flush, hardware exit disable, PX_EN output-enable behavior, BACO mode select, and automatic exit-clear disable masks. `BIF_BACO_EXIT_TIMER2`, `BIF_BACO_EXIT_TIMER3`, and `BIF_BACO_EXIT_TIMER4` add 20-bit timer fields for LCLK backup, dummy-enable clear, and BACO-enable clear timing. `MEM_TYPE_CNTL` exposes a single `BF_MEM_PHY_G5_G3` bit.

`NBIF_GFX_ADDR_LUT_CNTL` controls LUT enable, MSI address mode, and broadcast mode. `NBIF_GFX_ADDR_LUT_0` through `_15` each expose a 24-bit `ADDR` field, giving a compact table-like mapping area for NBIF graphics address routing.

`VF_REGWR_EN`, `VF_DOORBELL_EN`, and `VF_FB_EN` are 31-bit per-VF enable bitmaps for VF0 through VF30. Their matching `VF_REGWR_STATUS`, `VF_DOORBELL_STATUS`, and `VF_FB_STATUS` families expose per-VF status bits. `VF_DOORBELL_EN` also includes `VF_DOORBELL_RD_LOG_DIS` at bit 31. These families are central SR-IOV controls: a single wrong bit selects a different virtual function.

### Reset, Remap, Ring Buffer, Mailbox, Pad, and S5 Controls

`GFX_RST_CNTL` exposes graphics reset control. `REMAP_HDP_MEM_FLUSH_CNTL` and `REMAP_HDP_REG_FLUSH_CNTL` hold remapped HDP flush control values used by runtime code that maps KFD/amdgpu-visible flush registers into a remap aperture.

`BIF_RB_CNTL`, `BIF_RB_BASE`, `BIF_RB_RPTR`, `BIF_RB_WPTR`, `BIF_RB_WPTR_ADDR_HI`, and `BIF_RB_WPTR_ADDR_LO` describe BIF ring-buffer enable, size, base, read/write pointers, and write-pointer address fields. `MAILBOX_INDEX`, `BACO_AZ_ENHANCE_CTRL`, `BIF_MP1_INTR_CTRL`, and the `BIF_*_GPUIOV_CFG_SIZE` registers describe mailbox indexing, audio/BACO request handling, MP1 interrupt routing, and GPU IOV config sizing for VCN and GFX/SDMA.

`BIF_PERSTB_PAD_CNTL`, `BIF_PX_EN_PAD_CNTL`, `BIF_REFPADKIN_PAD_CNTL`, `BIF_CLKREQB_PAD_CNTL`, `BIF_PWRBRK_PAD_CNTL`, `BIF_WAKEB_PAD_CNTL`, and `BIF_VAUX_PRESENT_PAD_CNTL` define pad pull-up/pull-down, input receive, impedance, output-enable, and signal-specific GPIO settings. `GPIO_CNTL_0_REG` through `GPIO_CNTL_4_REG` repeat a broader GPIO control pattern with input, output-enable, and output value fields.

`PCIE_PAR_SAVE_RESTORE_CNTL`, `BIF_S5_MEM_POWER_CTRL0`, `BIF_S5_MEM_POWER_CTRL1`, `BIF_S5_DUMMY_REGS`, `CLDO_075_S5_CTRL`, `CLDO_12_PCIE_CTRL`, and `SMNCLK_SEL` describe PCIe parameter save/restore state, S5 memory-power control words, S5 dummy storage, LDO voltage/config enable fields, and S5 SMN clock selection.

### RCC Decode, Peer, Bus, Link, and Strap Controls

The `nbio_nbif0_rcc_dev0_BIFDEC1` address block starts at `RCC_ERR_INT_CNTL`. It defines SR-IOV invalid-register-access interrupt enable, BACO request-disables, doorbell aperture reset enable, vendor-defined-message support, margining parameter fields, GPU IOV region and host VM enable fields, console IOV mode and VF spacing, peer register ranges, bus-control policy, config aperture sizing, XDMA bounds, and miscellaneous feature controls for unsupported-request handling, MSI/MSI-X pending behavior, ECRC error policy, and poison-flag handling.

`RCC_BUSNUM_*`, `RCC_CAPTURE_HOST_BUSNUM`, `RCC_HOST_BUSNUM`, `RCC_PEER*_FB_OFFSET_*`, `RCC_DEVFUNCNUM_LIST*`, `RCC_DEV0_LINK_CNTL`, `RCC_CMN_LINK_CNTL`, `RCC_EP_REQUESTERID_RESTORE`, `RCC_LTR_LSWITCH_CNTL`, and `RCC_MH_ARB_CNTL` define bus-number filters, captured host bus numbers, peer framebuffer offsets, device/function number lists, link control behavior, requester-ID restore, LTR local switch behavior, and multi-host arbitration.

The `nbio_nbif0_rcc_strap_BIFDEC1` block dominates the middle of the chunk. `RCC_BIF_STRAP0` through `RCC_BIF_STRAP6` describe broad BIF/PCIe strap state such as bus/device/function IDs, link width and port presence, L1/LTR/OBFF behavior, completion timeout policy, maximum payload/read-request sizes, lane/equalization presets, Gen2/Gen3/Gen4/Gen5 capability, ten-bit tags, hotplug-style presence bits, error reporting, clock power management, local DLF support, ACS-related capability, downstream port settings, and vendor/device identity fields.

`RCC_DEV0_PORT_STRAP0` through `RCC_DEV0_PORT_STRAP14` define device-port advertised behavior: device/function numbers, link width/speed, reset and power timing, link power-management latencies, MSI/downstream support, ECRC, DSN, VC, atomic operations, ACS, power budget tables, port numbers, revision IDs, target link speed, Gen5 and 32 GT/s lane-equalization presets, TPH, and downstream-specific error reporting.

`RCC_DEV0_EPF0_STRAP*` and `RCC_DEV0_EPF1_STRAP*` define endpoint function straps. EPF0 receives the richest set here: device/vendor/subsystem IDs, SR-IOV VF device ID and page size, class code and total VFs, RTR reset/DLUP/FLR/D3 timings, SR-IOV enable, BAR sizing/disables, PASID width and capability bits, ARI/AER/ACS/ATS enables, MSI/MSI-X and interrupt pin behavior, FLR/PME/atomic support, doorbell and VF aperture sizes, VGA disable, VF mapping mode, GPUIOV VSEC length, extended capability pointers, and interrupt routing behavior. EPF1 repeats many of the same identity, SR-IOV, BAR, MSI/MSI-X, PM, and capability fields, with numerous empty strap placeholders also present.

### PF, GDC, Shadow, and VF0 PCI Config

The `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` block covers PF-visible behavior. `BIF_BX_PF_BIF_BME_STATUS` exposes bus-master status, `BIF_BX_PF_BIF_ATOMIC_ERR_LOG` captures atomic error metadata, and `BIF_BX_PF_DOORBELL_SELFRING_GPA_APER_*` defines the self-ring doorbell GPA aperture. HDP coherency controls include register/memory flush, memory-flush-only, invalidate-only, and 31 client-style `BIF_BX_PF_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF_GPU_HDP_FLUSH_DONE` bitmaps. `BIF_BX_PF_BIF_TRANS_PENDING`, address-LUT bypass, transmit/receive mailbox dwords, mailbox control, mailbox interrupt control, and VMHV mailbox fields round out the PF virtualization/coordination surface.

The `nbio_nbif0_gdc_GDCDEC` block includes SHUB non-PF drop behavior, `NGDC_MGCG_CTRL` medium-grain clock-gating fields, reserved dwords, graphics doorbell sent status, ATDMA/S2A arbitration weights and modes, early wakeup controls, MCA SMN posted behavior, and NGDC power-gating master/slave controls.

`SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI` plus `SUC_INDEX` and `SUC_DATA` expose indexed access windows. The shadow block describes upstream PCI bridge shadow state: command IO/memory enables, BAR1/BAR2, secondary/subordinate bus numbers, IO base/limit, memory base/limit, prefetchable memory windows, and upper 32-bit window halves. `BIF_BX_PF1_MM_INDEX`, `BIF_BX_PF1_MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI` provide an indexed PF1 MMIO access path.

The final address block begins `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`. This chunk covers VF0 config-space fields from vendor/device ID through the first `LINK_CNTL` shift: command/status, revision/class fields, BARs, ROM BAR, capability pointer, interrupt line/pin, PCIe capability header, device capability/control/status, and link capability. The matching `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL` masks and later VF0 PCIe capability fields continue in the next chunk.

## Control Flow

There is no executable control flow in this header. The operational flow is external:

1. NBIO 4.3, SMU13, virtualization, power-management, or platform code includes `nbio_4_3_0_offset.h` and this shift/mask header.
2. The caller selects an address macro such as `cfgBIF_BX_PF_GPU_HDP_FLUSH_REQ`, `cfgRCC_BUS_CNTL`, `cfgNGDC_MGCG_CTRL`, or `cfgBIF_CFG_DEV0_EPF0_VF0_0_COMMAND`.
3. Register helper macros combine the selected register name, field name, shift, and mask to update or extract a field.
4. Hardware, firmware, the PF driver, a VF guest, or a hypervisor observes the result according to the selected access path and permissions.

Because the chunk includes PCIe config-space, SR-IOV, indexed MMIO, mailbox, HDP flush, and power-management fields, the real ordering and polling rules live in the driver logic and hardware specification, not in this generated header.

## State and Persistence Behavior

The header itself has no runtime state. It names hardware-visible fields whose values can persist across ordinary software calls until overwritten or until a reset/power/firmware/hypervisor event changes them.

Important represented state includes:

- BACO and S5 transition timers and power-control settings.
- Address LUT entries and address-LUT bypass state.
- Per-VF enable/status state for register writes, doorbells, and framebuffer access.
- Ring-buffer pointers, remap registers, mailbox valid/ack/data bits, and VMHV mailbox interrupt enables.
- Pad, GPIO, CLDO, and SMN clock selection state used around board signaling and low-power modes.
- RCC decode policy, peer ranges, host/peer bus numbers, requester-ID restore, XDMA bounds, link controls, and feature-policy bits.
- Strap-derived capability state that determines what PCIe/SR-IOV/ATS/PASID/ARI/AER/MSI/MSI-X/ACS/link/power behavior the device advertises.
- PF HDP flush request/done bitmaps and PF mailbox transport state.
- GDC clock-gating, arbitration, wakeup, MCA SMN, and power-gating controls.
- Shadowed upstream PCI bridge aperture and command state.
- VF0 PCI config-space identity, command/status, BAR, ROM BAR, device capability/control/status, and link capability fields.

Many fields are not ordinary read/write storage. Status latches, HDP flush request/done bits, mailbox valid/ack bits, reset controls, FLR-capable fields, PCIe status/error fields, link controls, and power-gating controls can have side effects, clear-on-write behavior, hardware ownership, firmware ownership, or ordering requirements.

## Dependencies and Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the addresses for these field names. Examples from the same tree include `cfgBIF_BACO_EXIT_TIMER2` at `0x302038b8`, `cfgRCC_BUS_CNTL` at `0x30203784`, `cfgBIF_BX_PF_GPU_HDP_FLUSH_REQ` at `0x30203898`, `cfgNGDC_MGCG_CTRL` at `0x30203ba8`, `cfgBIF_CFG_DEV0_EPF0_VF0_0_VENDOR_ID` at `0xfffe10300000`, and `cfgBIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL` at `0xfffe10300074`. The same offset header also contains SMN/register-space aliases such as `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP2` and later instance-specific forms.

Observed local consumers of `nbio_4_3_0_sh_mask.h` are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which includes this header with the matching offset header and uses generated NBIO field macros in register reads/writes and `REG_SET_FIELD`/mask operations.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`, which includes the NBIO 4.3.0 offset and mask headers alongside SMU13 headers.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, which includes the same NBIO 4.3.0 generated headers for SMU13 platform behavior.

The field vocabulary also lines up with generated NBIO/NBIF headers for other ASIC revisions. That makes it useful for cross-version comparison, but it also means callers must use the NBIO 4.3.0 address and mask files as a matched pair.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can enable the wrong VF, mis-size a BAR, corrupt a mailbox handshake, break HDP flush signaling, alter PCIe advertised capabilities, or change power/reset behavior.
- The per-VF bitmaps are dense and repetitive. VF0 through VF30 use one bit each; off-by-one mistakes compile cleanly while affecting a different virtual function.
- Strap fields are capability-defining. Incorrect SR-IOV, ACS, ATS, PASID, ARI, AER, MSI/MSI-X, BAR, link-speed, or power-management bits can cause enumeration failures, isolation bugs, or host/device protocol errors.
- PF mailbox and VMHV mailbox fields mix data, valid, ack, and interrupt-enable bits. Incorrect sequencing can lose notifications or leave one side waiting for an acknowledgment.
- HDP flush request/done bits must match the hardware client convention expected by the runtime flush path. Mis-decoding these bits can produce stale CPU/GPU memory visibility.
- PCIe config-space fields have standard side effects and access policies. Command/status, BAR, ROM BAR, link, device-control, and error-status fields should not be treated as inert storage.
- Power, BACO, S5, GDC MGCG, and power-gating controls are timing-sensitive. Changing timer or gating masks without matching firmware/hardware sequencing can lead to resume, reset, or low-power failures.
- This chunk has two incomplete boundaries: it starts after earlier `BIF_BACO_EXIT_TIMER1` shift definitions and ends after only the first VF0 `LINK_CNTL` shift line. The final per-file report must reconcile adjacent chunks before claiming complete coverage of those registers.

## Test and Validation Signals

Useful validation is mostly build, generated-header consistency, hardware enumeration, power-management, and SR-IOV behavior:

- Build AMDGPU paths that include `nbio_4_3_0_sh_mask.h`, especially `nbio_v4_3.c` and SMU13 platform files.
- Check that every field family in this chunk has a matching address in `nbio_4_3_0_offset.h` where applicable, and that generated mask widths match the intended field widths.
- Exercise SR-IOV flows that enable and disable VF register-write, doorbell, and framebuffer access, then verify the expected VF0 through VF30 status bits change.
- Validate VF0 PCI config-space enumeration: vendor/device ID, command/status, BAR sizing, ROM BAR, capability list, device capability/control/status, and link capability should decode as expected.
- Run doorbell and self-ring aperture tests that cover PF doorbell aperture base/cntl fields and doorbell status reporting.
- Exercise HDP memory/register flush paths and confirm request/done bits transition correctly under GPU memory coherency tests.
- Test BACO/S5 suspend-resume and reset paths for timer, CLDO, GPIO/pad, and SMN clock-selection regressions.
- Validate GDC clock-gating and power-gating controls under runtime power-management and idle/resume workloads.
- Use PCIe/AER/ATS/PASID/ARI capability and error-injection tests where platform support exists, especially around strap-derived capability fields and RCC bus/error policy bits.
- Static review should compare repeated strap, VF bitmap, and PCI config-space families against neighboring NBIO 4.3.0 chunks and other ASIC versions to detect generator or copy drift.

## Unresolved Cross-Chunk References

This range begins with `BIF_BACO_EXIT_TIMER1` fields whose earlier shift definitions are in the previous chunk. It ends immediately after `BIF_CFG_DEV0_EPF0_VF0_0_LINK_CNTL__PM_CONTROL__SHIFT`; the rest of `LINK_CNTL` and later VF0 PCIe config-space fields continue in the next chunk. The merge/reconciliation lane should stitch those boundaries before producing the final source-tree-aligned per-file report.
