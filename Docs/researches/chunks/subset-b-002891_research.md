# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 1-2947

## Scope

This chunk is the first 2,947 lines of AMDGPU's generated NBIO 2.3 register-default header. It contains a license banner, the `_nbio_2_3_DEFAULT_HEADER` include guard, and 2,782 C preprocessor constants ending in `_DEFAULT`. There are no functions, structs, enums, executable branches, allocations, locks, or direct register reads/writes in this range.

The constants are grouped by generated `addressBlock:` comments. Names beginning with `mm` describe memory-mapped register defaults, names beginning with `cfg` describe PCI configuration-space defaults, and names beginning with `smn` describe SMN-accessible register/config defaults. In this chunk, 315 macros are `mm*`, 1,327 are `cfg*`, and 1,139 are `smn*`; 858 constants have nonzero defaults. The chunk ends mid-block at `smnBIF_CFG_DEV0_EPF0_PCIE_ACS_CAP_DEFAULT`, so later chunks are required for the remainder of the SMN `BIF_CFG_DEV0_EPF0` configuration-space defaults and for the file-level synthesis.

Although the repository path is under `distributed-fs/ceph-client`, this source is Linux AMD GPU driver hardware-description data under `drivers/gpu/drm/amd/include/asic_reg/nbio`; it is not Ceph client filesystem logic.

## Purpose

The header provides reset/default values for NBIO 2.3 registers and PCIe configuration registers. Driver code can include this generated file with companion offset and bitfield headers to compare observed hardware state, initialize register blocks, document expected reset state, or build generated tables without embedding raw reset constants in C logic.

This line range covers the NBIF/BIF front-end, RCC endpoint/downstream control, GDC and System Hub defaults, PCIe root/downstream and endpoint function configuration spaces, virtualization-oriented GPU I/O vendor-specific defaults, reset/RAS blocks, function-control restore defaults, and the start of the SMN-visible endpoint-function defaults.

## Important Macro Families

`mmBIF_BX_PF_MM_INDEX_DEFAULT`, `mmBIF_BX_PF_MM_DATA_DEFAULT`, and `mmBIF_BX_PF_MM_INDEX_HI_DEFAULT` are PF MMIO indirect-access defaults. The nearby `mmSYSHUB_*`, `mmPCIE_INDEX*`, `mmPCIE_DATA*`, `mmSBIOS_SCRATCH_*`, and `mmBIOS_SCRATCH_*` families default System Hub/PCIe indirect windows and BIOS scratch registers to zero.

`mmRCC_BIF_STRAP*`, `mmRCC_DEV0_PORT_STRAP*`, and `mmRCC_DEV0_EPF[01]_STRAP*` carry nonzero reset strap defaults for the Root Complex Controller and endpoint functions. Notable values include AMD vendor ID material (`0x1002` embedded in strap and config defaults), device IDs for EPF0/EPF1, port strap values, capability layout defaults, and feature straps such as MSI/MSI-X, class/device behavior, and function capability exposure.

`mmEP_PCIE_*`, `mmDN_PCIE_*`, and `mmPCIE_*` define endpoint, downstream, and downstream-port PCIe control defaults. The nonzero values set bus control defaults, low-power latency reporting (`EP_PCIE_TX_LTR_CNTL`), dynamic power allocation substate budgets, DPA capability/status defaults, error-control defaults, and RX behavior.

`mmRCC_*` under `nbio_nbif0_rcc_dev0_BIFDEC1` captures RCC-level reset, margining, peer aperture, bus-number, requester-ID restore, LTR, and arbitration defaults. Nonzero defaults include reset enable, margin parameters, peer register ranges, and common link control.

`mmBIF_*`, `mmNBIF_GFX_ADDR_LUT_*`, `mmREMAP_HDP_*`, pad-control, BACO, doorbell, mailbox, and transaction-pending defaults describe the BIF block. The LUT defaults map entries 0-15 to their matching indices; HDP flush remap registers default to fixed MMIO offsets; pad-control defaults cover PERST, PX_EN, REFCLK, CLKREQ, PWRBRK, WAKE, and VAUX signals. BACO exit timers and GPUIOV config sizes are also represented.

`mmBIF_BX_PF_*` defines PF-only BIF state such as BME status, atomic error logging, doorbell self-ring GPA aperture defaults, HDP coherency flush controls, PF mailbox transmit/receive dwords, mailbox interrupt control, and VM/HV mailbox state. Most default to zero, with the doorbell self-ring aperture control defaulting to `0x00000100`.

`mmA2S_*`, `mmNGDC_*`, `mmSHUB_REGS_IF_CTL_DEFAULT`, and GDC doorbell range defaults describe GDC/NBIO data-path and power controls. Nonzero values cover A2S client and switch control, completion-buffer allocation, SDP port enables, medium-grain clock gating, and page-gating controls.

`mmRCC_DEV0_EPF0_GFXMSIX_VECT*` and `mmRCC_DEV0_EPF0_GFXMSIX_PBA_DEFAULT` define the graphics MSI-X vector table defaults for four vectors. Address and data fields default to zero, while each vector-control default is `0x00000001`, meaning the default state is masked/disabled until software programs it.

`cfgPSWUSCFG0_0_*` describes a PCIe switch/upstream-style configuration space. It includes standard header fields, bridge bus/memory/prefetch windows, power-management capability, PCIe capability, MSI, SSID, vendor-specific capability, VC, serial number, AER, secondary PCIe, ACS, multicast, LTR, ARI, L1 PM substate, ESM, data-link feature, 16GT PHY, margining, CCIX, and ESM 20GT/25GT equalization defaults. Capability-list pointer defaults encode the generated PCI capability chain.

`cfgBIF_CFG_DEV0_EPF0_0_*` and `cfgBIF_CFG_DEV0_EPF1_0_*` are full endpoint-function configuration-space defaults for two major functions. They repeat standard PCI header, BAR, adapter ID, power-management, PCIe capability, MSI/MSI-X, vendor-specific, VC, serial number, AER, BAR resize, power budget, DPA, secondary PCIe, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16GT PHY, margining, VF resize BAR, and GPU IOV vendor-specific mailbox/scheduler/VF framebuffer fields. EPF0 uses device ID `0x7310`; EPF1 uses device ID `0xab38`.

`cfgBIF_CFG_DEV0_EPF2_0_*` and `cfgBIF_CFG_DEV0_EPF3_0_*` are shorter endpoint-function defaults for additional functions. EPF2 advertises a USB-like class tuple through nonzero programming interface, subclass, and base-class defaults and device ID `0x7316`; EPF3 uses device ID `0x731a` with a shorter PCIe/AER/BAR/DPA/ACS/PASID/ARI/TPH-style capability set. These blocks lack the large GPUIOV VF framebuffer and scheduler payload present on EPF0/EPF1.

`smnA2S_*`, `smnSYSHUB_*`, `smnNIC400_*`, and `smnSION_*` provide SMN-visible GDC/System Hub/NIC/SION defaults. They include clock-domain-specific deep-sleep and scratch registers, transaction-idle controls, BGEN enhancement controls, NIC400 QoS/outstanding/fabric controls, and SION credit/time-slot/burst-target defaults for client lanes CL0-CL3.

`smnSHUB_*` reset and `smnGDCSOC_RAS_*` defaults cover GDC/System Hub reset and RAS. Nonzero reset defaults include hard/soft reset control and reset miscellaneous timing, while RAS leaf controls default to enabled-looking nonzero bit patterns for several leaves and zero status registers.

`smnBIF_CFG_DEV0_SWDS_*` describes an SMN-visible switch/downstream configuration space, including bridge class defaults, interrupt line, PMI, PCIe, VC, AER, secondary, ACS, data-link feature, 16GT PHY, and margining defaults.

The repeated `smnMM_*`, `smnSYSHUB_*`, `smnRCC_STRAP0_*`, `smnRCC_EP_DEV0_*`, `smnRCC_DWN_DEV0_*`, `smnRCC_DWNP_DEV0_*`, and `smnRCC_DEV0_*` families mirror many earlier `mm*` defaults through SMN naming. These aliases let code using SMN register addressing see the same default-value contract as MMIO-oriented code.

`smnBIFC_*`, `smnNBIF_*`, `smnBIF_GMI_*`, `smnSMN_MST_*`, and `smnBIFC_A2S_*` under `nbio_nbif0_bif_misc_bif_misc_regblk` define miscellaneous BIF policy defaults: interrupt line enable, outstanding VC allocation, DMA attribute overrides for pairs of functions, dummy BME behavior, throttling, GSI behavior, PASID check disable/status, ATHUB activity control, NBIF page-gating and clock-gating defaults, self-ring buffer ID, GMI weighted round-robin weights, SMN master behavior, and A2S SDP/client control.

`smnRCC_PFC_*` blocks for AMDGFX, AMDGFXAZ, USB, and PD controller functions define function-control restore defaults. They cover LTR control/status restore, PME message restore, sticky AER-style status/header/prefix restore dwords, and auxiliary power control defaults.

`smnHARD_RST_CTRL`, `smnBIF_RST_MISC_CTRL*`, `smnDEV0_PF*_FLR_RST_CTRL`, `smnBIF_*_INTR_*`, `smnBIF_PF*_RST`, `smnBIF_DEV0_PF*_DSTATE_VALUE`, and `smnDEV0_PF*_D3HOTD0_RST_CTRL` define BIF reset, FLR, D3hot-to-D0, interrupt mask/status, and D-state defaults. PF0 has a broader FLR reset default (`0x8206a0a9`) than PF1-PF7 (`0x02060009`), and all D3hot-D0 reset controls default to `0x0000001b`.

`smnBIFL_RAS_*` defines BIF RAS central, leaf control/status, IOHub interrupt, and virtual-wire defaults. Leaf controls use nonzero defaults (`0x00000f61`), while status and central registers default to zero.

The final section in this chunk starts `smnBIF_CFG_DEV0_EPF0_*`, the SMN-named equivalent of the EPF0 configuration-space defaults. It reaches through ACS capability-list default (`0x2b000000`) and ACS capability default before the line boundary. The rest of the EPF0 SMN config-space block appears after this chunk.

## Control Flow and State

This header has no direct control flow. Its implicit flow is defined by the hardware reset and driver-initialization paths that consume the constants:

1. Hardware reset, straps, firmware, or generated register models establish default values for NBIO/BIF/RCC/GDC/System Hub and PCIe configuration registers.
2. AMDGPU initialization, reset, power-management, PCIe, virtualization, and debug code includes generated address/default/shift/mask headers and uses accessors such as MMIO, indirect MMIO, config-space, or SMN reads/writes to inspect or program the corresponding registers.
3. PCI enumeration observes the config-space defaults for vendor/device IDs, class codes, headers, BARs, interrupt pins, capability lists, PCIe capabilities, MSI/MSI-X, AER, ACS, ATS, PASID, SR-IOV, TPH, LTR, and related extended capabilities.
4. Reset and power paths rely on RCC/BIF reset defaults, FLR defaults, D3hot-D0 defaults, reset interrupt masks, transaction-idle defaults, BACO exit timers, pad controls, clock/deep-sleep controls, and page-gating values.
5. Virtualization and GPUIOV paths use PF/VF mailbox, doorbell, SR-IOV, VF aperture, scheduler, and vendor-specific configuration defaults to expose or isolate GPU functions.
6. RAS/debug paths use RAS leaf defaults, AER masks/severity defaults, scratch registers, error logs, MSI-X vector defaults, BIF performance/misc defaults, and System Hub idle/QoS defaults.

State represented here lives in GPU hardware registers, PCI configuration-space registers, strap latches, reset/power state machines, RAS status latches, MSI/MSI-X table storage, mailbox registers, scratch registers, and fabric/QoS controls. Some values are reset defaults only; some are writeable policy defaults; some are status or interrupt-mask defaults; and some are address/capability-chain encodings. This file does not persist anything by itself and does not enforce ordering, polling, locking, or cache coherency. Runtime persistence and synchronization are entirely in the driver code and hardware protocols that use these constants.

## Dependencies and Integration Points

The only direct dependency is the C preprocessor. The file is useful only when included with generated NBIO 2.3 register address and bitfield headers, typically the matching `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h` style headers in the AMDGPU ASIC register tree.

Integration points include:

- AMDGPU ASIC initialization and bring-up code that validates or writes NBIO/BIF/RCC/GDC/System Hub registers.
- PCI/PCIe enumeration and capability handling for AMD GPU endpoint functions and switch/downstream functions.
- SR-IOV and GPU IOV code that needs PF/VF capability, mailbox, doorbell, VF aperture, scheduler, and vendor-specific defaults.
- Reset and recovery paths handling hard reset, soft reset, FLR, D3hot-to-D0 transitions, link reset, BACO, transaction-idle checks, and reset interrupt status/masks.
- Power-management paths that use LTR, DPA, D-state, CLKREQ/pad controls, deep-sleep, clock-gating, and page-gating defaults.
- Interrupt and MSI/MSI-X setup code that interprets interrupt line, MSI message-control, MSI-X vector-control, pending-bit, and reset-event defaults.
- RAS and PCIe AER paths that use default masks, severity, leaf control, and status-register reset states.
- Debug/performance tooling that reads scratch, mailbox, fabric QoS, BIFC misc, performance, and System Hub idle controls.

## Risks

Default-value accuracy is critical because these macros document and sometimes drive low-level hardware expectations. A wrong constant can cause PCI enumeration differences, incorrect capability lists, bad BAR sizing, disabled or overexposed MSI/MSI-X, broken AER/ACS/ATS/PASID/SR-IOV behavior, reset hangs, missed interrupt events, invalid RAS policy, or subtle power/performance regressions.

The file is generated and highly repetitive. Copy-generation mistakes are plausible around duplicated `mm` versus `smn` aliases, endpoint function suffixes (`EPF0` through `EPF3`), switch/downstream names, lane equalization arrays, DPA substate arrays, GPUIOV VF framebuffer arrays, scheduler dwords, and repeated PFC restore blocks. The chunk boundary also cuts the SMN EPF0 configuration block mid-family, so the merge lane must not treat this document as complete file-level coverage.

Several defaults are isolation and security sensitive: SR-IOV fields, GPUIOV mailbox/context/VF framebuffer fields, doorbell apertures, ATS/ACS/PASID/page-request capability defaults, peer register ranges, BME/dummy behavior, PASID check controls, and nonzero PCIe capability-chain pointers. Incorrect values could expose configuration or memory access paths across PF/VF or function boundaries.

Reset and power defaults are timing-sensitive. BACO exit timers, FLR reset controls, D3hot-D0 reset controls, reset interrupt masks, reset miscellaneous controls, D-state values, LTR/DPA defaults, clock gating, and deep-sleep defaults can create intermittent failures that appear only under suspend/resume, virtualization teardown, FLR, hot reset, or recovery from GPU faults.

Many defaults are hardware-family-specific. Reusing NBIO 2.3 constants for a different ASIC revision, or mixing them with mismatched offset/mask headers, can compile cleanly while programming the wrong register layout.

## Test Signals

Useful validation is mostly build-time and hardware-facing:

- The AMDGPU driver should compile with this header and matching NBIO 2.3 offset/shift/mask headers without duplicate, missing, or mismatched macro references.
- PCI enumeration on NBIO 2.3 ASICs should report expected vendor/device IDs, class codes, header types, BARs, interrupt pins, capability chains, MSI/MSI-X, AER, ACS, ATS, PASID, SR-IOV, LTR, DPA, and power-management capabilities.
- Runtime register dumps after reset should match the documented defaults for sampled/reset registers before software intentionally changes them.
- GPU reset tests should cover FLR, PF/VF reset, D3hot-to-D0, link reset, BACO exit, suspend/resume, and error recovery without reset timeouts or stuck transaction-idle status.
- SR-IOV/virtualization tests should verify PF/VF isolation, mailbox behavior, doorbell apertures, VF BAR/aperture sizing, GPUIOV vendor-specific fields, and VF reset behavior.
- Interrupt tests should observe expected MSI/MSI-X vector masking defaults, reset-event interrupt masks/status, D-state events, and power/reset notifications.
- RAS/AER tests should confirm default uncorrectable/correctable masks and severity, RAS leaf controls, status reset values, and error reporting behavior.
- Power/performance telemetry should be checked around LTR/DPA, clock gating, deep sleep, page gating, GMI WRR weights, outstanding VC allocation, and BIFC/A2S controls.
