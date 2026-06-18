# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 59411-61872

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header range. It contains C preprocessor constants, not executable functions. Each hardware field is represented as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro; consumers combine these with register offsets from `nbio_4_3_0_offset.h` and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

The range starts at the tail of the PF1 HDP flush-done register masks, then covers PF1 BIF transaction/mailbox registers, the `nbio_nbif0_rcc_strap_BIFDEC1` strap block, GDC DMA/HST SION scheduling blocks, S2A doorbell routing entries, GDC clock/reset/RAS controls, and the beginning of the `PSWUSCFG0_1` PCIe configuration-space mirror through `LINK_STATUS`.

## Purpose

These macros define the bit-level ABI between NBIO v4.3.0 driver code, firmware-owned policy, and NBIO/PCIe hardware. The fields in this chunk support:

- Per-engine HDP flush completion status for PF1, covering CP0-CP9, SDMA0-1, and reserved engine bits.
- PF1 BIF transaction pending status, address-LUT bypass, and mailbox transmit/receive handshakes.
- Strap-derived PCIe/NBIF behavior including link-generation disable/kill bits, ASPM/LTR timers, power break timing, error ignore policy, ARI/ACS/AER/ATS/PASID/SR-IOV capabilities, BAR sizing, GPUIOV VSEC sizing/revision, reset timing, and endpoint/root-port identity fields.
- GDC DMA and host SION arbitration tables for request/data/read-response/write-response burst targets, time slots, and pool-credit allocation.
- S2A doorbell entry routing for ports 0-15, including enable, AWID, range offset/size, and high address nibble selection.
- GDC clock gating, power-gating, reset, SDP port reset, ATDMA, and RAS leaf controls/status.
- PCIe type-1 configuration registers for PSWUSCFG0, including command/status, bridge bus/window registers, PM capability, PCIe device/link capability/control/status fields.

Because this is generated hardware metadata, correctness is mostly about exact macro names, masks, shifts, generation pairing, and register ownership. Many fields represent straps or firmware-programmed state and should not be treated as ordinary scratch registers.

## Important Macro Families

PF1 BIF status and mailbox:

- Lines 59411-59452 finish `BIF_BX_PF1_GPU_HDP_FLUSH_DONE`; masks map flush completion bits for CP0-CP9, SDMA0-1, and reserved engines 0-19. This mirrors the PF0 flush-done family used by `nbio_v4_3_hdp_flush_reg`, but this chunk is specifically the PF1 register family.
- `BIF_BX_PF1_BIF_TRANS_PENDING` exposes master and slave transaction-pending bits.
- `BIF_BX_PF1_NBIF_GFX_ADDR_LUT_BYPASS` exposes a one-bit LUT bypass control.
- `BIF_BX_PF1_MAILBOX_MSGBUF_TRN_DW0..3` and `RCV_DW0..3` are full 32-bit message buffer words.
- `BIF_BX_PF1_MAILBOX_CONTROL` provides transmit valid/ack and receive valid/ack bits; `BIF_BX_PF1_MAILBOX_INT_CNTL` enables valid/ack interrupts.
- `BIF_BX_PF1_BIF_VMHV_MAILBOX` is a compact VM/HV mailbox with transmit/receive 4-bit data fields plus valid, ack, and interrupt enable bits.

RCC BIF strap block:

- `RCC_STRAP2_RCC_BIF_STRAP0..6` describe NBIF/PCIe strap policy for Gen3/Gen4/Gen5 disable and kill bits, ROM/VGA/audio presence, PX capability, PME compliance, MSI payload behavior, error-ignore controls, local prefix handling, big-APU mode, link-down reset, ECRC, margining, SWUS aperture settings, DLF, 16 GT/s and 32 GT/s PHY enablement, power-break deglitch timing, VLINK L0s/L1/LDN timers, emergency power reduction, and ASPM/LTR interlocks.
- Multi-bit timer fields such as `STRAP_VLINK_ASPM_IDLE_TIMER`, `STRAP_VLINK_PM_L1_ENTRY_TIMER`, `STRAP_VLINK_L0S_EXIT_TIMER`, `STRAP_VLINK_L1_EXIT_TIMER`, and `STRAP_VLINK_LDN_ENTRY_TIMER` are programming surfaces for link power-management policy.
- `nbio_v4_3_program_aspm()` in the implementation actively programs the related `RCC_STRAP0` generation of these BIF strap timers; this `RCC_STRAP2` family is a parallel strap address block with the same class of semantics.

Device 0 port straps:

- `RCC_STRAP2_RCC_DEV0_PORT_STRAP0..14` encode downstream/root-port identity and PCIe capability advertisement: device/vendor/subsystem IDs, ARI/ACS/AER, completion abort behavior, interrupt pin, max payload, max link width, modified TS support, RTR timing, alternate protocol details, class of timeout/logging support, ECRC generation/checking, extended tags, virtual channels, L0s/L1 acceptable/exit latency, LTR/OBFF/power-management support, atomic support, power-budget table bytes, ACS capability bits, 10-bit tag support, 16 GT/s and 32 GT/s equalization presets, target link speed, port number, bus/device/function numbers, and revision IDs.
- These strap fields are source-of-truth inputs for how hardware exposes PCIe bridge/root-port capability, so changing them can alter OS-visible PCI configuration behavior.

Device 0 endpoint function straps:

- `RCC_STRAP2_RCC_DEV0_EPF0_STRAP*` defines endpoint function 0 identity, SR-IOV, ATS/PASID/page-request, BAR, MSI/MSI-X, DPA/DSN/VC, FLR, PME, resize BAR, GPUIOV, and reset timing fields.
- Notable virtualization fields include `STRAP_SRIOV_EN_DEV0_F0`, `STRAP_SRIOV_VF_DEVICE_ID_DEV0_F0`, `STRAP_SRIOV_SUPPORTED_PAGE_SIZE_DEV0_F0`, `STRAP_SRIOV_TOTAL_VFS_DEV0_F0`, `STRAP_VF_DOORBELL_APER_SIZE_DEV0_F0`, `STRAP_VF_MEM_AP_SIZE_DEV0_F0`, `STRAP_VF_REG_AP_SIZE_DEV0_F0`, `STRAP_SRIOV_VF_MAPPING_MODE_DEV0_F0`, and `STRAP_VF_REG_PROT_DIS_DEV0_F0`.
- Address-translation fields include ATS enable, ATS invalidate queue depth, ATS page-aligned request, PASID enable, maximum PASID width, page request enable, and PASID permission/global-invalidate/private-mode support.
- `RCC_STRAP2_RCC_DEV0_EPF1_STRAP*` provides a smaller endpoint function 1 family with identity, capability, MSI/MSI-X, AER/ACS/ATS/PASID, and BAR/cacheline/class-code style fields. Empty comment-only placeholders for EPF1 straps 20-25 indicate generated register headings without bit definitions in this chunk.

GDC DMA/HST SION scheduling:

- `GDC_DMA_SION_CL0..CL3_*` and `GDC_HST_SION_CL0..CL2_*` define repeated 64-bit register pairs for `RdRsp_BurstTarget`, `RdRsp_TimeSlot`, `WrRsp_BurstTarget`, `WrRsp_TimeSlot`, `Req_BurstTarget`, `Req_TimeSlot`, and pool-credit allocation.
- Each low/high pair exposes a full 32-bit field at shift 0. Together they represent 64-bit scheduling, credit, or time-slot bitmaps/values for client classes.
- `GDC_DMA_SION_CNTL_REG0/1` and `GDC_HST_SION_CNTL_REG0/1` expose SION glue clock soft-overrides and control fields for the DMA and host paths.

Doorbell, GDC control, and reset/RAS:

- `S2A_DOORBELL_ENTRY_0_CTRL` through `S2A_DOORBELL_ENTRY_15_CTRL` repeat the same five fields per port: enable, AWID, range offset, range size, and high address bits. `nbio_v4_3.c` programs entries 0, 1, 2, 3, 4, and 5 for graphics, IH, SDMA, and VCN doorbell routing.
- `S2A_DOORBELL_COMMON_CTRL_REG` provides common S2A doorbell policy outside the per-entry routing fields.
- `GDC1_SHUB_REGS_IF_CTL`, `GDC1_NGDC_MGCG_CTRL`, `GDC1_NBIF_GFX_DOORBELL_STATUS`, `GDC1_ATDMA_MISC_CNTL`, `GDC1_S2A_MISC_CNTL`, `GDC1_NGDC_EARLY_WAKEUP_CTRL`, `GDC1_NGDC_PG_MISC_CTRL`, `GDC1_NGDC_PGMST_CTRL`, and `GDC1_NGDC_PGSLV_CTRL` cover GDC register-interface, medium-grain clock gating, doorbell status, ATDMA, S2A, early wakeup, and power-gating controls.
- `GDCSOC_ERR_RSP_CNTL`, `GDCSOC_RAS_CENTRAL_STATUS`, `GDCSOC_RAS_LEAF*_CTRL`, `GDCSOC_RAS_LEAF*_STATUS`, and leaf-2 misc controls define RAS/error-response enable, injection, interrupt, and status surfaces for GDC SOC leaves.
- `SHUB_PF_FLR_RST`, `SHUB_GFX_DRV_VPU_RST`, `SHUB_LINK_RESET`, `SHUB_HARD_RST_CTRL`, `SHUB_SOFT_RST_CTRL`, and `SHUB_SDP_PORT_RST` define reset controls for PF FLR, graphics-driver/VPU reset, link reset, hard/soft reset, and SDP port reset.
- `HST_CLK0_SW0_CL0_CNTL` and `HST_CLK0_SW1_CL0_CNTL` are system-hub direct clock controls.

PSWUSCFG0_1 PCIe configuration-space mirror:

- `PSWUSCFG0_1_VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, class-code, cache-line, latency, header, and BIST macros define standard PCI identity/header fields.
- `PSWUSCFG0_1_COMMAND` and `STATUS` define I/O, memory, bus-master, parity, SERR, interrupt disable, capability-list, interrupt, error, and devsel status bits.
- Bridge-window registers include primary/secondary/subordinate bus numbers, I/O base/limit, memory base/limit, prefetchable base/limit upper/lower fields, ROM base address, and interrupt line/pin.
- Capability-list macros include a vendor capability list, adapter ID, PM capability/list/status-control, and PCIe capability/list registers.
- `PSWUSCFG0_1_DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` expose max payload/read request, relaxed ordering, extended tag, phantom functions, no-snoop, AUX power, error-reporting enables/status, FLR capability, slot power fields, and transaction-pending status.
- `PSWUSCFG0_1_LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` define link speed/width, ASPM/power-management support, common clock, retrain/link disable, bandwidth interrupt enables/status, DL active, slot clock, and current negotiated link state.

## Control Flow and Runtime Use

There is no local control flow in this header. Runtime behavior comes from NBIO v4.3.0 code and firmware paths that include this mask header with the matching offset header.

Key in-tree flows connected to this chunk:

1. `amdgpu_discovery.c` selects `nbio_v4_3_funcs` or `nbio_v4_3_sriov_funcs` for NBIO IP 4.3 devices and installs `nbio_v4_3_hdp_flush_reg`.
2. `nbio_v4_3_hdp_flush_reg` uses the generated HDP flush-done masks for CP and SDMA engines. That object currently references the PF family, while this chunk exposes the PF1-specific equivalent at the start of the range.
3. `nbio_v4_3_sdma_doorbell_range()`, `nbio_v4_3_vcn_doorbell_range()`, `nbio_v4_3_gc_doorbell_init()`, and `nbio_v4_3_ih_doorbell_range()` read/modify/write `S2A_DOORBELL_ENTRY_*_CTRL` registers using the per-port fields defined in this chunk.
4. `nbio_v4_3_update_medium_grain_clock_gating()` and `nbio_v4_3_update_medium_grain_light_sleep()` use other NBIO v4.3 masks for BIF clock/light-sleep controls; the GDC clock-gating and SION soft-override fields in this chunk are adjacent integration surfaces for lower-level GDC/SION power behavior.
5. `nbio_v4_3_program_aspm()` programs related BIF strap and PCIe link control registers to configure ASPM/LTR behavior. The `RCC_STRAP2` BIF/port strap families in this chunk describe the same PCIe capability and timing domain for another address block.
6. `nbio_v4_3_init_registers()` clears a no-soft-reset strap bit for IP 4.3.0 using generated RCC strap macros; the EPF strap families in this chunk contain parallel no-soft-reset, FLR, VF reset, D3hot-to-D0, and RTR timing fields.
7. `nbio_v4_3_set_reg_remap()` and the doorbell functions distinguish bare-metal and SR-IOV behavior. That lines up with the SR-IOV, VF BAR, VF mapping, VF protection, and GPUIOV strap fields in this range.
8. `nbio_v4_3_set_ras_err_event_athub_irq_state()` and related RAS hooks manage NBIO RAS interrupt routing using generated masks outside this exact chunk; this chunk contributes GDC SOC RAS leaf control/status fields for the GDC-side error-reporting surface.
9. SMU13 power-management code includes `nbio_4_3_0_offset.h` and this mask header, so power/ASPM/PPT paths may rely on the same generated bitfields even when they are not touched by `nbio_v4_3.c` directly.

Many fields in this chunk are not directly manipulated by the searched in-tree C implementation. The strap, SION scheduling, PF1 mailbox, PSWUSCFG0 bridge config, and several GDC reset/RAS fields are likely consumed by firmware, silicon initialization scripts, debug tooling, or future driver paths. They still form ABI documentation for those MMIO/config registers.

## State and Persistence Behavior

The header stores no software state. It describes hardware MMIO, strap, and PCIe configuration state that persists until reset, power-domain loss, firmware reprogramming, suspend/resume reinitialization, FLR, or explicit driver writes.

Important persistent state represented here:

- HDP flush-done bits are live completion state used to determine whether CPU-visible memory flushes for CP/SDMA clients have completed.
- PF1 transaction-pending and mailbox control bits are synchronization state; valid/ack and interrupt-enable fields can be edge/level sensitive depending on hardware behavior and should be updated with handshake discipline.
- Strap registers encode boot/firmware policy for PCIe capability exposure. Mutating strap-derived fields at runtime can change advertised capability, reset timing, BAR sizing, SR-IOV exposure, ATS/PASID support, or link power behavior.
- SION scheduling registers hold arbitration/credit policy for GDC DMA and host paths. Bad values can throttle or starve request/response classes.
- Doorbell entry controls define which doorbell ranges reach which hardware clients. These values must match `adev->doorbell` allocation and client ring setup.
- GDC reset controls and SDP port reset fields represent destructive state transitions; writes can reset SHUB/GDC paths, links, or ports.
- GDC RAS controls/status registers are error-detection, interrupt, and status state. Status bits may be sticky until explicitly cleared by the appropriate RAS flow.
- PSWUSCFG0_1 fields mirror PCIe config-space state that the OS, PCI core, firmware, and device hardware may all observe. Command, bridge-window, PM, PCIe capability, device control/status, and link control/status fields can affect enumeration, routing, power management, and error reporting.

## Dependencies and Integration Points

Generated-register dependencies:

- `nbio_4_3_0_offset.h` supplies register addresses and base indices matching these masks. The same symbolic field names must be paired with NBIO 4.3.0 offsets, not copied across NBIO/PCIE generations.
- Earlier chunks of `nbio_4_3_0_sh_mask.h` define the PF0 HDP flush, BIF interrupt, doorbell aperture, PCIe link, CPM, and RCC strap families that `nbio_v4_3.c` actively uses with the same helper style.
- Later chunks continue the PSWUSCFG0_1 PCIe capability space beyond `LINK_STATUS`, including higher-speed link and lane-equalization fields.

Driver integration:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` is the principal NBIO v4.3.0 implementation consumer. It uses generated NBIO masks for HDP flush offsets, memory controller access, doorbell routing, interrupt control, ASPM/LTR, clock gating, ROM offset, register remap, SR-IOV function selection, and RAS interrupt setup.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c` binds NBIO v4.3.0 function tables and HDP flush descriptors during IP discovery.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c` include the NBIO v4.3.0 offset and mask headers, connecting these fields to SMU13 platform power-management decisions.
- Display resource code includes the NBIO v4.3.0 offset header, so display/IP discovery code can share the same generated register namespace even when it does not include this mask header directly.
- SR-IOV integration is explicit: bare-metal and SR-IOV NBIO function tables differ for doorbell setup, while the strap fields in this chunk define SR-IOV/VF identity and mapping policy.

## Risks and Edge Cases

- Generation mismatch is the primary risk. NBIO, NBIF, and PCIe headers contain many similarly named register families. Using NBIO 4.3.0 masks with a different offset header can silently program wrong bits.
- The chunk starts in the middle of `BIF_BX_PF1_GPU_HDP_FLUSH_DONE`. The register heading and earlier shift definitions are outside this chunk, so whole-register analysis needs adjacent lines.
- PF0 and PF1 HDP/mailbox fields are easy to confuse. Current `nbio_v4_3_hdp_flush_reg` uses PF-family flush masks; PF1-specific use must select the matching PF1 offset and mask set.
- Strap fields often reflect firmware/boot-time policy. Runtime writes can conflict with firmware ownership, PCI core expectations, or silicon validation assumptions.
- SR-IOV, ATS, PASID, page request, GPUIOV, and VF BAR fields affect isolation and IOMMU behavior. Incorrect advertisement or enablement can expose host/VF access bugs.
- Doorbell range offset and size fields must be consistent with allocated doorbell index space. Overlap or incorrect AWID/high-address settings can route ring writes to the wrong client.
- SION burst/time-slot/pool-credit registers are wide and repeated. Partial low/high updates can create transient inconsistent arbitration policy if hardware observes them between writes.
- Reset-control fields can be destructive and may require sequencing with clock/power gating, firmware ownership, and outstanding transactions.
- RAS leaf status/control bits may have write-one-to-clear, sticky, or interrupt side effects not visible from the macro names. Generic read/modify/write helpers must respect hardware-clearing rules.
- PSWUSCFG0_1 PCIe config fields overlap with OS PCI configuration management. Driver writes must coordinate with the PCI core and avoid changing bridge apertures, link control, or command bits behind the OS's back.

## Test and Verification Signals

Useful validation for this chunk is mostly compile coverage, register readback, and platform smoke testing:

- Build AMDGPU configurations that include `nbio_v4_3.c`, SMU13 PPT files, and the NBIO 4.3.0 generated headers; this catches missing or renamed generated macros.
- On NBIO 4.3.0 hardware, verify `nbio_v4_3_hdp_flush_reg` masks still match CP/SDMA flush completion behavior, and use PF1-specific masks only with PF1 offsets.
- Exercise SDMA, IH, GC, and VCN doorbell setup and read back `S2A_DOORBELL_ENTRY_0/1/2/3/4/5_CTRL` to confirm enable, AWID, range offset, range size, and high address fields match the programmed ring topology.
- Run SR-IOV VF smoke tests to ensure VF doorbell setup remains skipped by the SR-IOV function table while VF capability/mapping straps match expected virtualization policy.
- Validate ASPM/LTR changes with link-state telemetry and PCIe config-space reads, especially when strap timers or LTR enablement are touched.
- Check PCI enumeration and `lspci -vv` output against PSWUSCFG0_1 identity, PM, PCIe device, and link capability fields after firmware/driver initialization.
- For RAS work, inject or observe GDC/NBIO RAS events and confirm leaf status/control bits, interrupt status, and global RAS ISR behavior are consistent.
- For SION scheduling changes, use traffic stress on DMA/host paths and compare performance counters or timeout/error signals before and after programming burst target, time slot, or credit allocation fields.
- For reset-control changes, verify suspend/resume, FLR, link reset, and GPU reset paths on both bare-metal and SR-IOV configurations.
