# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 19668-22147

## Purpose

This chunk is a generated AMD NBIO 6.1 register field header. It defines `__SHIFT` and `_MASK` constants for bit fields in several NBIO/NBIF PCIe, BIF, RCC, virtualization, doorbell, power-management, and fabric-control registers. The source has no executable functions or data objects; its purpose is to make register programming in AMDGPU code type-checked by the C preprocessor and consistent with the matching address definitions in `nbio_6_1_offset.h`.

The range starts in the middle of the `BIF_CFG_DEV0_SWDS1_LINK_CNTL` field list, then covers the rest of the SWDS1 PCI configuration capability space, several PF1 BIF/SYSHUB/MMIO and GPU virtualization registers, RCC endpoint/downstream port controls, PCI shadow registers, and NBIF miscellaneous/fabric controls through the beginning of `BIFC_PERF_CNTL_0`.

## Major Register Families

- `BIF_CFG_DEV0_SWDS1_*`: PCIe switch/downstream port configuration space for link, slot, MSI, subsystem ID, vendor-specific enhanced capability, virtual-channel capability, device serial number, AER, secondary PCIe capability, lane equalization, and ACS. These fields mirror standard PCIe capability layouts such as link speed/width, hotplug, completion timeout, LTR/OBFF, MSI addressing/data, uncorrectable/correctable AER status and masks, header logs, TLP prefix logs, per-lane equalization presets, and ACS source validation/translation/blocking controls.
- `BIF_BX_PF3_MM_*` and `BIF_BX_PF1_*_INDEX/DATA*`: indirect MMIO/SYSHUB/PCIe aperture index/data pairs. These are register-window selectors, so incorrect use can redirect later reads or writes.
- `BIF_BX_PF1_SBIOS_SCRATCH_*`, `BIF_BX_PF1_BIOS_SCRATCH_*`, and `MISC_SCRATCH`: firmware/driver scratch state registers. They are persistent hardware-visible communication storage across some boot, reset, and power-management paths.
- `BIF_BX_PF1_BIF_RLC_INTR_CNTL`, `BIF_VCE_INTR_CNTL`, `BIF_UVD_INTR_CNTL`, `INTERRUPT_CNTL`, `INTERRUPT_CNTL2`, mailbox interrupt controls, and RCC PCIe interrupt controls/status: routing and masking for graphics/video/virtualization/PCIe events.
- `BIF_BX_PF1_GFX_MMIOREG_CAM_*`: graphics MMIO register CAM and remap controls, including remap addresses and completion behavior.
- `RCC_STRAP1/2_RCC_DEV0_EPF0_STRAP0`, `RCC_PF_0_1_RCC_*`, and `RCC_*_PCIE_*`: strap, endpoint, downstream, and downstream-port RCC controls. Fields include revision/SSID/multifunction straps, doorbell aperture enable, memory size, IOV function identity, FLR behavior, unsupported request policy, LTR, DPA, PME, TX/RX behavior, link speed, lane reversal, and posted/non-posted request attributes.
- `BIF_BX_PF1_BUS_CNTL`, `BIF_FEATURES_CONTROL_MISC`, `BIF_DOORBELL_CNTL`, `BIF_FB_EN`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, and `BIF_TRANS_PENDING`: core BIF control/status fields for bus behavior, feature gates, doorbell monitoring, frame-buffer read/write enable, bus-master status, atomic error logging, and pending master/slave traffic.
- `BIF_BX_PF1_BACO_*`, `SMU_BIF_VDDGFX_PWR_STATUS`, and `BIF_VDDGFX_*`: BACO and VDDGFX power-state/power-timing registers used by runtime power-management flows.
- `BIF_BX_PF1_DOORBELL_SELFRING_GPA_APER_*`: self-ring doorbell GPA aperture base and enable/mode/size controls. Later NBIO generations use equivalent PF1 masks directly in `nbio_v7_11.c`; NBIO 6.1 uses the PF0 variant in its runtime file.
- `BIF_BX_PF1_REMAP_HDP_*`, `HDP_*_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, and `GPU_HDP_FLUSH_DONE`: HDP flush register remap and per-engine flush request/done bits for CP0-CP9, SDMA0/1, and reserved engines.
- `BIF_BX_PF1_BIF_RB_*`: register-ring/ring-buffer base, read pointer, write pointer, and write-pointer address fields.
- `BIF_BX_PF1_MAILBOX_*` and `BIF_VMHV_MAILBOX`: transmit/receive message buffers, mailbox control flags, interrupt enables, and VM/hypervisor mailbox fields for SR-IOV/MxGPU communication.
- `SHADOW_*`, `SUC_INDEX/DATA`, and `SUM_INDEX/DATA`: shadowed PCI configuration and indexed configuration/data access windows.
- `OUTSTANDING_VC_ALLOC`, `BIFC_MISC_CTRL0/1`, `BIFC_BME_ERR_LOG`, `BIFC_RCCBIH_BME_ERR_LOG`, `BIFC_DMA_ATTR_OVERRIDE_DEV0_F*_F*`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, `BIFC_SDP_CNTL_*`: NBIF fabric arbitration, outstanding allocation, DMA attribute override, BME error logging, GSI/SDP behavior, and function identity controls.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_*`, `NBIF_SDP_VWR_*`, `SMN_MST_CNTL0`, `SMN_MST_EP_CNTL1/2`: virtual-wire and SMN master controls, including per-PF endpoint masks, write-trigger/voltage-change triggers, reset override values, and multi-SMN transaction ID behavior.
- `NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK`: medium-grain clock gating and deep-sleep control on LCLK. `nbio_v6_1.c` programs the `NBIF_MGCG_REG_DIS_LCLK` bit by SMN address during ASPM setup.
- `BME_DUMMY_CNTL_0` and the beginning of `BIFC_PERF_CNTL_0`: dummy BME response controls and MMIO performance counter enables/resets/selectors.

## Important APIs, Types, and Functions

This header contributes macros, not callable APIs. The important consumer API is the AMDGPU register-access layer:

- `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` combine offsets from `nbio_6_1_offset.h` with these masks to read/write MMIO registers.
- `RREG32_PCIE` and `WREG32_PCIE` access SMN/PCIe-addressed registers such as `NBIF_MGCG_CTRL_LCLK` and RCC/PCIe link-control registers.
- `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15` depend on the exact `<register>__<field>__SHIFT` and `<register>__<field>_MASK` naming convention used here.
- `struct nbio_hdp_flush_reg` instances in NBIO implementation files store per-engine HDP flush mask constants from these generated headers. The NBIO 6.1 runtime file uses PF0 names; later related files such as `nbio_v7_11.c` use the same PF1 family represented in this chunk.

Key direct and adjacent users include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `mxgpu_ai.c`, `psp_v3_1.c`, `display/dc/resource/dce120/dce120_resource.c`, and the Vega PowerPlay include files. Cross-generation users (`nbio_v7_0.c`, `nbio_v7_11.c`, `nbio_v7_4.c`) show the same control patterns for equivalent fields.

## Control Flow and Runtime Behavior

There is no local control flow in this file. Runtime behavior appears when the masks are used by AMDGPU initialization, power, interrupt, and virtualization paths:

- NBIO initialization reads and writes PCIe/BIF control fields to set request-size policy, slave ordering, memory-controller access, doorbell apertures, interrupt behavior, and HDP flush register locations.
- ASPM/LTR setup in `nbio_v6_1.c` programs PCIe link controls, RCC LTR controls, strap timers, and `NBIF_MGCG_CTRL_LCLK`. The masks in this chunk identify the comparable NBIF and RCC fields for this generation and neighboring PF/downstream instances.
- HDP flush flows write `GPU_HDP_FLUSH_REQ` bits and wait for matching `GPU_HDP_FLUSH_DONE` bits. The masks define which CP/SDMA engine a bit corresponds to, so mask drift can break cache/coherency flush acknowledgement.
- SR-IOV/MxGPU flows in `mxgpu_ai.c` use mailbox registers to send requests, poll acknowledgement bits, receive PF messages, and enable mailbox interrupts. This chunk contains the PF1 version of the same mailbox layout: transmit/receive dwords, valid/ack control, and interrupt enable fields.
- BACO and VDDGFX fields participate in power-state transitions where firmware or PowerPlay tables issue read/modify/write and wait-for operations against NBIF registers.
- AER, ACS, equalization, virtual-channel, and MSI fields are exposed as PCI configuration-space capability behavior. They influence enumeration, error reporting, hotplug, link retraining, lane equalization, interrupt delivery, and isolation semantics.

## State and Persistence

Most macros describe hardware register state rather than software-owned memory. State is persistent at the hardware register level until reset, power transition, firmware reprogramming, or another driver path overwrites it.

- Scratch and BIOS/SBIOS scratch registers are explicit low-level persistence/communication points between firmware and driver.
- Mailbox transmit/receive buffers and control bits are transient but externally synchronized with PF/VF or hypervisor peers; valid/ack bit ordering matters.
- Doorbell aperture, HDP flush remap, MMIO CAM, FB enable, and bus control registers define live address-routing and coherency behavior.
- PCIe configuration capability registers can be visible to the PCI core or host, so masks here are part of the device ABI exposed during enumeration and error handling.
- Strap fields reflect boot-time or firmware-programmed configuration; modifying writable strap-like mirrors at runtime can affect reset, link, power, or virtualization behavior.

## Dependencies and Integration Points

- Must stay synchronized with `nbio_6_1_offset.h`, which gives the corresponding MMIO/config/SMN addresses and base indices.
- Depends on AMDGPU SOC15 register macros and field helpers in the driver tree. The macro names are generated to match helper expectations.
- Integrates with Linux PCIe concepts: MSI/MSI64, AER, ACS, VC, LTR, OBFF, hotplug, link speed/width, slot control/status, and completion timeout.
- Integrates with AMDGPU virtualization: doorbell apertures, function identifiers, mailbox protocol, VM/hypervisor messages, VF pending transaction status, and per-PF virtual-wire/SMN controls.
- Integrates with power management: BACO controls, VDDGFX status/ranges, ASPM/LTR, LCLK clock gating/deep sleep, and PME/D-state controls.
- Integrates with display and KFD indirectly through HDP flush remap, doorbells, and NBIF base registration.

## Risks and Edge Cases

- Bit mask or shift errors are high impact because helpers silently program the wrong bits. Symptoms can look like PCIe link instability, lost interrupts, failed mailbox handshakes, broken doorbells, missing HDP flush completion, bad power transitions, or SR-IOV isolation failures.
- The chunk includes many repeated layouts for PF/downstream/endpoint instances. Copying a PF1 mask into a PF0 register, or pairing these masks with the wrong offset namespace, can compile but target the wrong hardware field.
- Several registers are indexed access windows (`*_INDEX`, `*_DATA`, `SUC_*`, `SUM_*`). Concurrent or unordered use can corrupt the selected target register.
- AER status registers often require write-one-to-clear semantics at the hardware/PCI layer; generic read/modify/write code can accidentally clear or preserve error state incorrectly if it treats status bits as ordinary control bits.
- Doorbell, HDP flush, and mailbox registers are synchronization points. Reordering, missing barriers, or stale valid/ack bits can deadlock GPU initialization or reset paths.
- Power and clock-gating bits can be platform-sensitive. Enabling LCLK gating, BACO, ASPM, or LTR without checking capability flags and firmware expectations can cause hangs on specific ASIC steppings or boards.
- Scratch and shadow registers may be firmware-owned at particular times. Driver writes must account for bootloader/SMU/PSP ownership and reset domains.

## Test Signals

- Build coverage: compile AMDGPU with this header included by `nbio_v6_1.c`, `mxgpu_ai.c`, Vega PowerPlay headers, display resource code, and PSP code. Macro name mismatches surface as build failures.
- Boot/init logs: successful NBIO initialization should report sane revision and memory size, enable memory-controller access, initialize interrupts, and avoid PCIe/AER fatal errors.
- PCIe validation: `lspci -vv` should show expected link speed/width, MSI/MSI-X/MSI64 behavior, AER/ACS capabilities, LTR/ASPM state, and no unexpected correctable/uncorrectable error growth under load.
- Doorbell and HDP validation: graphics, SDMA, KFD, and interrupt rings should submit work and flush coherently without timeouts in `GPU_HDP_FLUSH_DONE`.
- Virtualization validation: SR-IOV guests should complete PF/VF mailbox handshakes, receive `READY_TO_ACCESS_GPU`, program doorbells, and reset without mailbox timeout messages.
- Power validation: BACO entry/exit, runtime suspend/resume, ASPM/LTR operation, and clock-gating state queries should complete without link retraining loops, D3/D0 failures, or device disappearance.
- Error-path validation: injected or natural PCIe AER events should set the intended status bits, respect masks/severity, log header/TLP prefix data, and route interrupts according to the RCC and BIF interrupt controls.
