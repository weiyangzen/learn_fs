# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002891`: lines 1-2947, `Docs/researches/chunks/subset-b-002891_research.md`
- `subset-b-002892`: lines 2948-5828, `Docs/researches/chunks/subset-b-002892_research.md`
- `subset-b-002893`: lines 5829-8700, `Docs/researches/chunks/subset-b-002893_research.md`
- `subset-b-002894`: lines 8701-11799, `Docs/researches/chunks/subset-b-002894_research.md`
- `subset-b-002895`: lines 11800-14994, `Docs/researches/chunks/subset-b-002895_research.md`
- `subset-b-002896`: lines 14995-17881, `Docs/researches/chunks/subset-b-002896_research.md`
- `subset-b-002897`: lines 17882-18521, `Docs/researches/chunks/subset-b-002897_research.md`

## Chunk Research

### subset-b-002891: lines 1-2947

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

### subset-b-002892: lines 2948-5828

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 2948-5828

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register-default header fragment. It contains preprocessor `*_DEFAULT` constants only; there are no functions, structs, enums, allocations, locks, or direct branches. The constants describe reset or hardware-default values for NBIO/BIF PCI configuration-space registers and PCIe extended capability structures.

The range starts in the middle of the `smnBIF_CFG_DEV0_EPF0` physical-function 0 default block and ends in the middle of the `smnBIF_CFG_DEV0_EPF0_VF23` virtual-function block. Within the range there are 2,800 `#define` entries: 206 trailing PF0 defaults, complete PF1/PF2/PF3 blocks, complete PF0 VF0 through VF22 blocks, and the first 46 defaults for PF0 VF23. Adjacent chunks are required to reconstruct the full PF0 and VF23 sections.

Although this repository path is under `distributed-fs/ceph-client`, the source is Linux AMD GPU driver hardware-description data under `drivers/gpu/drm/amd/include/asic_reg/nbio`; it is not Ceph client or filesystem logic.

## Purpose

The chunk provides default values for PCI endpoint functions exposed through NBIO 2.3. Driver code and generated register tooling use these values alongside register address and shift/mask headers to understand the expected reset image of PCI configuration space, PCIe capability chains, SR-IOV/VF capability templates, MSI/MSI-X state, AER logging state, link capability state, and vendor-specific GPU virtualization data.

The constants are not active initialization logic by themselves. They are hardware contract data: each macro names an SMN-visible BIF configuration register and records its default value for this ASIC generation.

## Important Macro Families

`smnBIF_CFG_DEV0_EPF0_*` in this range covers the tail of physical function 0. It includes ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s PHY, lane equalization, PCIe margining, VF resize BAR, and GPU IOV vendor-specific defaults. This is the most virtualization-heavy part of the chunk. Many values are zero, but the capability-list defaults encode the extended capability chain offsets, and several non-zero defaults matter: page request status `0x00000100`, PASID cap `0x00001000`, SR-IOV supported/system page sizes `0x00000553` and `0x00000001`, data-link feature list/header `0x41010025`, per-lane equalization `0x000000f0`, per-lane margining control `0x00009c38`, VF resize BAR1 control `0x00000020`, and GPUIOV offsets `0x0012000c`.

`smnBIF_CFG_DEV0_EPF1_*` is a complete PF1 PCI configuration/default block. It starts with AMD vendor ID `0x1002`, device ID `0xab38`, adapter ID `0xab381002`, header type `0x80`, capability pointer `0x48`, interrupt line `0xff`, and interrupt pin `2`. It carries normal PCI/PCIe capability defaults plus MSI, AER, resize BAR, power budget, DPA, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH, DLF, 16 GT/s PHY, per-lane equalization/margining, VF resize BAR, and a large GPUIOV vendor-specific region. PF1 has the largest complete block in this chunk, with 349 defines.

`smnBIF_CFG_DEV0_EPF2_*` and `smnBIF_CFG_DEV0_EPF3_*` are complete secondary physical-function blocks with 191 defines each. PF2 identifies as AMD vendor `0x1002`, device `0x7316`, adapter ID `0x73161002`, class code `0x0c0300` style values (`BASE_CLASS` `0x0c`, `SUB_CLASS` `0x03`, `PROG_INTERFACE` `0x30`), interrupt pin `3`, device capability `0x00000f81`, device control `0x00002810`, link defaults, MSI control `0x86`, AER masks/severity, resize BAR, power budget, DPA, ACS, PASID, ARI, TPH requester, and a 64-entry TPH steering-table default region. PF3 identifies as AMD vendor `0x1002`, device `0x7314`, adapter ID `0x73141002`, base class `0x0c`, subclass `0x80`, interrupt pin `4`, and otherwise follows the same PCIe/MSI/AER/BAR/power/DPA/ACS/PASID/ARI/TPH pattern as PF2.

`smnBIF_CFG_DEV0_EPF0_VF0_*` through `smnBIF_CFG_DEV0_EPF0_VF22_*` are repeated virtual-function templates under PF0. Each complete VF block has 79 defaults. The VF identity fields default mostly to zero, while `ADAPTER_ID` defaults to `0x73101002`, `CAP_PTR` to `0x48`, `PCIE_CAP_LIST` to `0x0000a000`, `PCIE_CAP` to `0x00000002`, `LINK_CAP` to `0x00000d04`, `DEVICE_CAP2` to `0x00010000`, `LINK_CAP2` to `0x0000001e`, `MSI_CAP_LIST` to `0x0000c000`, and `MSI_MSG_CNTL` to `0x00000082`. Each complete VF block includes MSI and MSI-X registers, vendor-specific PCIe capability headers, AER status/mask/severity/log registers, ATS enhanced capability defaults, and ARI placeholders.

`smnBIF_CFG_DEV0_EPF0_VF23_*` begins another VF template but this chunk stops after `MSI_MASK_DEFAULT`. The remaining VF23 MSI, MSI-X, vendor-specific, AER, ATS, and ARI defaults are outside this work item.

## APIs, Types, and Functions

There are no callable APIs or C types in this chunk. The interface is a set of C preprocessor symbols consumed at compile time. Names encode the register path, function identity, capability/register name, and that the value is a default. For example, `smnBIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_MASK_DEFAULT` is the default value for PF2's PCIe uncorrectable error mask register.

The companion generated files are required to use these constants meaningfully: `nbio_2_3_offset.h` provides register addresses or offsets, and `nbio_2_3_sh_mask.h` provides bit shifts and masks. The C implementation `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this default header along with those companion headers and uses the NBIO register definitions through AMDGPU access helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `WREG32_FIELD15`.

## Control Flow

This header has no direct runtime control flow. The implicit flow comes from PCIe/NBIO hardware enumeration and driver register programming:

1. Hardware or firmware exposes configuration-space defaults for PFs and VFs after reset.
2. Linux PCI enumeration reads IDs, class codes, headers, BARs, capability pointers, MSI/MSI-X capability records, PCIe link/device capability records, and extended capability chains.
3. AMDGPU NBIO code programs runtime policy for link power management, LTR, doorbells, interrupt handling, clock gating, and reset behavior using the generated offset and shift/mask headers; these defaults describe the expected baseline for the same register space.
4. SR-IOV and VF paths rely on the PF0 SR-IOV capability defaults and the repeated VF templates to expose or validate virtual function config-space state.
5. AER, ATS, ARI, PASID, DPA, TPH, LTR, margining, and 16 GT/s link capability records are interpreted by PCI/AMDGPU code according to the capability-chain defaults.

## State and Persistence Behavior

The state described here lives in GPU hardware configuration registers, PCIe capability registers, status latches, BAR controls, MSI/MSI-X message storage, AER log/status fields, SR-IOV/VF controls, and vendor-specific GPUIOV mailbox or scheduling registers. Many default values are zero because the register is disabled, empty, write-owned by software, or a status/log field that starts clear.

Some defaults represent stable reset identity or topology, such as vendor/device IDs, class codes, adapter IDs, capability pointers, PCIe capability chain entries, link capability values, and TPH table size. Others represent mutable runtime state, such as command/status, BAR values, MSI message address/data/mask/pending fields, AER status/log registers, SR-IOV controls, page request status, margining status, and GPUIOV mailbox/context/scheduling fields.

The header does not enforce persistence, ordering, locking, polling, or clear-on-write behavior. Callers must follow PCIe and NBIO hardware rules when writing registers, especially across reset, FLR, SR-IOV enable/disable, suspend/resume, and virtualization transitions.

## Dependencies and Integration Points

The file depends only on the C preprocessor, but its practical dependencies are the generated NBIO 2.3 offset and shift/mask headers. `amdgpu/nbio_v2_3.c` includes this header as part of the NBIO 2.3 support set, tying the constants to ASIC-specific register access code.

Integration points include:

- PCI enumeration and capability decoding for AMD NBIO 2.3 physical and virtual functions.
- AMDGPU NBIO initialization and power-management code that configures PCIe link control, LTR, ASPM, clock gating, and related strap/capability registers.
- SR-IOV setup and teardown paths that depend on PF0 SR-IOV defaults, VF BAR defaults, VF page-size support, VF capability chains, and repeated VF config-space templates.
- GPU virtualization and GPUIOV flows using vendor-specific headers, interrupt enable/status fields, reset control, hypervisor/VM mailbox dwords, framebuffer partition registers for VF0-VF30, and scheduler dwords for UVD/VCN/GFX engines.
- PCIe error handling through AER status, mask, severity, header log, and TLP prefix log defaults.
- PCIe MSI/MSI-X interrupt setup through message control, address, data, mask, and pending defaults.
- Link training, signal-quality, and high-speed PCIe validation through 16 GT/s capability, lane equalization, and margining defaults.

## Risks

Default-value accuracy is hardware critical. An incorrect identity, class-code, capability-list, BAR-control, or MSI default can change PCI enumeration or cause Linux to bind the wrong driver, size resources incorrectly, miss interrupts, or misread the available PCIe capabilities.

Virtualization fields are isolation-sensitive. Mistakes in SR-IOV, VF resize BAR, ATS, PASID, ARI, page request, multicast, GPUIOV mailbox, framebuffer partition, or scheduler defaults can break VF creation, expose incorrect VF resources, confuse guest-visible config space, or destabilize PF/VF reset flows.

The chunk is highly repetitive. Generation or copy errors are plausible across `EPF1`, `EPF2`, `EPF3`, and especially `VF0` through `VF23` suffixes. Because VF blocks are nearly identical, a single off-by-one suffix or missed value can be hard to see in review while still affecting one VF only.

Range boundaries are a reconciliation risk. This work item begins after PF0's earlier PCI config and capability defaults and ends before VF23 is complete. The merge lane must combine neighboring chunks to avoid treating PF0 or VF23 as complete from this document alone.

Several non-zero values encode capability-chain offsets and capability IDs rather than ordinary scalar configuration. Changing values such as `0x2c000000`, `0x33000000`, `0x41010025`, or `0x4c010027` without matching the generated offset/mask model could corrupt the extended capability list.

## Test Signals

Useful validation is mostly build-time and hardware-facing:

- AMDGPU should compile with `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h` included by `amdgpu/nbio_v2_3.c` without missing, duplicate, or mismatched macro errors.
- PCI enumeration on NBIO 2.3 ASICs should expose the expected PF1/PF2/PF3 vendor IDs, device IDs, class codes, header types, interrupt pins, BAR behavior, PCIe capability chain, MSI capability, AER capability, resize BAR support, and TPH/DPA/ACS/PASID/ARI/LTR capability visibility.
- SR-IOV tests should create and remove VFs cleanly, verify VF0 through at least VF23 config-space templates, and confirm VF BAR sizing, MSI state, ATS/ARI capability behavior, and GPUIOV resource partition defaults.
- Reset and power tests should include FLR, VF FLR, suspend/resume, D3 transitions, ASPM/LTR programming, and hot reset to catch defaults that interact with status or capability restoration.
- Error-handling tests should confirm AER status/mask/severity/log defaults and TLP prefix log fields behave as expected after injected or observed PCIe errors.
- Link validation should inspect 16 GT/s link capability, lane equalization defaults, and PCIe margining controls/status on hardware that supports those features.
- Generated-header consistency checks should compare this default header against the matching register database so repeated PF/VF blocks, capability-list offsets, and range-boundary blocks are not truncated or shifted.

### subset-b-002893: lines 5829-8700

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 5829-8700

## Scope

This chunk is a generated AMD NBIO 2.3 default-register header segment. It contains preprocessor constants only: each `*_DEFAULT` macro names the reset/default value for a concrete NBIO register or PCI configuration-space register. There are no C functions, structs, runtime branches, loops, locks, allocations, or direct MMIO operations in this range.

The range starts in the middle of the `nbio_nbif0_bif_cfg_dev0_epf0_vf23_bifcfgdecp` address block, so it only contains the tail defaults for `smnBIF_CFG_DEV0_EPF0_VF23_*`. It then covers complete `smn` defaults for virtual functions `VF24` through `VF30`, the USB MSI-X table/PBA defaults, PCIe port/link/default-control blocks, the `cfgBIF_CFG_DEV0_SWDS0_*` downstream-switch configuration defaults, and complete `cfg` defaults for virtual functions `VF0` through `VF9`. The final covered source line is only the `// addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf10_bifcfgdecp` marker; the `VF10` defaults begin after this chunk.

Major covered families are:

- Tail of `smnBIF_CFG_DEV0_EPF0_VF23_*` MSI, MSI-X, vendor-specific, AER, ATS, and ARI defaults.
- Full `smnBIF_CFG_DEV0_EPF0_VF24_*` through `smnBIF_CFG_DEV0_EPF0_VF30_*` virtual-function PCIe configuration defaults.
- `smnPCIEMSIX_VECT0_*` through `smnPCIEMSIX_VECT255_*`, four default registers per MSI-X vector: low address, high address, message data, and vector control.
- `smnPCIEMSIX_PBA_0_DEFAULT` through `smnPCIEMSIX_PBA_7_DEFAULT`.
- `smnPCIEP_*`, `smnPCIE_TX_*`, `smnPCIE_RX_*`, `smnPCIE_LC_*`, flow-control, error-injection, SR-IOV, clock/power, and save/restore defaults for the PCIe port-side directory block.
- `smnPCIE_*`, performance-counter, PRBS, software-reset, CPM, aperture, lane-counter, power-gating, RX margining, and presence-detect defaults for the broader PCIe directory block.
- `cfgBIF_CFG_DEV0_SWDS0_*` PCIe downstream-switch defaults, including bridge config header fields, PCIe capabilities, virtual-channel capability defaults, AER defaults, secondary PCIe capability, ACS, data-link feature, 16 GT/s PHY capability placeholders, and per-lane equalization/margining defaults.
- `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` through `cfgBIF_CFG_DEV0_EPF0_VF9_0_*` virtual-function PCIe configuration defaults.

## Purpose

The purpose of this header segment is to publish ASIC reset/default values for NBIO 2.3 hardware registers so driver code, diagnostics, generated register tooling, and bring-up checks have a single symbolic view of expected initial state. The companion `nbio_2_3_offset.h` header identifies register offsets, and `nbio_2_3_sh_mask.h` identifies field positions. This default header supplies the value expected before driver or firmware programming changes the register.

For the virtual-function blocks, these defaults describe SR-IOV VF PCI configuration space as exposed by the NBIO/BIF register database. Most fields default to zero because VF identity, BARs, MSI state, AER status, ATS control, ARI state, and error logs are either disabled, assigned by later software/firmware, or status-like. The repeated nonzero defaults encode the static capability list shape:

- VF config blocks use `CAP_PTR_DEFAULT` of `0x00000048`.
- PCIe capability list defaults commonly use `0x0000a000`, with `PCIE_CAP_DEFAULT` of `0x00000002`.
- Link capability defaults use `0x00000d04`, and Link Capability 2 defaults use `0x0000001e`.
- Device Capability 2 defaults use `0x00010000`.
- MSI capability list defaults use `0x0000c000`, and VF MSI message control defaults usually use `0x00000082`.
- Vendor-specific enhanced capability list defaults use `0x11000000`.
- Advanced Error Reporting enhanced capability list defaults use `0x20020000`.
- ATS enhanced capability list defaults use `0x2c000000`.
- VF adapter ID defaults are `0x73101002` for the full VF blocks in this chunk.

For the PCIe directory and port blocks, the defaults describe low-level link, transaction, flow-control, clock/power, reset, debug, and training behavior. These values are not policy chosen by C code in this file; they are generated hardware metadata that driver code may compare with, rely on as reset baseline, or override through MMIO programming paths.

For the USB MSI-X table and PBA blocks, all defaults are zero. This models unprogrammed MSI-X vector address/data/control entries and clear pending bits before software assigns interrupt vectors.

## Important Macro Families

### SR-IOV VF Config Defaults

The chunk contains two VF naming styles:

- `smnBIF_CFG_DEV0_EPF0_VF23_*` tail and full `smnBIF_CFG_DEV0_EPF0_VF24_*` through `VF30_*`.
- `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` through `VF9_0_*`.

The full VF blocks each expose the same PCI config-space default layout:

- Type/header identity fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- BAR and ROM defaults: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ROM_BASE_ADDR`, and `ADAPTER_ID`.
- Interrupt and capability-list pointers: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- PCIe capability registers: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X defaults: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data fields, mask and pending fields, and MSI-X capability/table/PBA fields.
- Extended capabilities and error reporting: vendor-specific enhanced capability, AER status/mask/severity/log fields, TLP prefix logs, ATS capability/control, and ARI capability/control.

Most VF control, status, address, and log defaults are zero. The repeated nonzero capability constants are important because they define the PCI capability chain and the advertised static capability baseline for each VF. Incorrect values here can make a VF appear to have a malformed PCIe capability list, bad MSI capability state, wrong link capability, or incorrect extended capability chaining.

### USB MSI-X Table and PBA

The `nbio_nbif0_pciemsix_0_usb_MSIXTDEC` block defines 256 MSI-X vector entries:

- `smnPCIEMSIX_VECTn_ADDR_LO_DEFAULT`
- `smnPCIEMSIX_VECTn_ADDR_HI_DEFAULT`
- `smnPCIEMSIX_VECTn_MSG_DATA_DEFAULT`
- `smnPCIEMSIX_VECTn_CONTROL_DEFAULT`

Every entry defaults to `0x00000000`. This is the reset state for an unprogrammed MSI-X table: no target address, no message data, and no vector-control state set by this generated default table. The `nbio_nbif0_pciemsix_0_usb_MSIXPDEC` block adds `smnPCIEMSIX_PBA_0_DEFAULT` through `PBA_7_DEFAULT`, also all zero, representing a clear pending-bit array.

This family is stateful at runtime even though this header is static. Once Linux configures MSI-X, vector address/data/control and pending bits are hardware/software state, not persistent constants from this header.

### PCIe Port Directory Defaults

The `nbio_pcie0_pswusp0_pciedir_p` address block covers port-side PCIe defaults. Nonzero values include:

- `smnPCIEP_PORT_CNTL_DEFAULT` at `0x06000009`.
- `smnPCIE_TX_CNTL_DEFAULT` at `0x00408000`, `smnPCIE_TX_REQUEST_NUM_CNTL_DEFAULT` at `0x02000000`, `smnPCIE_TX_REPLAY_DEFAULT` at `0x00480003`, `smnPCIE_TX_CNTL_2_DEFAULT` at `0x00000004`, and `smnPCIE_TX_CREDITS_FCU_THRESHOLD_DEFAULT` at `0x03330333`.
- Flow-control defaults such as `smnPCIE_FC_P_DEFAULT` and `smnPCIE_FC_P_VC1_DEFAULT` at `0x00020008`, and `smnPCIE_FC_NP_DEFAULT` at `0x00020002`.
- Error/link-control defaults such as `smnPSWUSP0_PCIE_ERR_CNTL_DEFAULT` at `0x00000500`, `smnPSWUSP0_PCIE_RX_CNTL_DEFAULT` at `0x01084000`, `smnPCIE_LC_CNTL_DEFAULT` at `0x40010050`, `smnPCIE_LC_TRAINING_CNTL_DEFAULT` at `0x94009880`, `smnPCIE_LC_LINK_WIDTH_CNTL_DEFAULT` at `0xda800006`, `smnPCIE_LC_N_FTS_CNTL_DEFAULT` at `0x00ffc20c`, and `smnPSWUSP0_PCIE_LC_SPEED_CNTL_DEFAULT` at `0x10000200`.
- Link-control extension defaults such as `smnPSWUSP0_PCIE_LC_CNTL2_DEFAULT` at `0x96180280`, `smnPCIE_LC_CDR_CNTL_DEFAULT` at `0x01018060`, `smnPCIE_LC_CNTL3_DEFAULT` at `0xa850a020`, `smnPCIE_LC_CNTL4_DEFAULT` at `0x0340048c`, `smnPCIE_LC_CNTL5_DEFAULT` at `0x40200000`, `smnPCIE_LC_CNTL6_DEFAULT` at `0x8a000090`, `smnPCIE_LC_CNTL7_DEFAULT` at `0x010002ee`, `smnPCIE_LC_CNTL8_DEFAULT` at `0x00400000`, `smnPCIE_LC_CNTL9_DEFAULT` at `0xf0ffec00`, `smnPCIE_LC_CNTL10_DEFAULT` at `0x30000003`, `smnPCIE_LC_CNTL11_DEFAULT` at `0x00602000`, and `smnPCIE_LC_CNTL12_DEFAULT` at `0x00000017`.
- Link management mask/default state such as `smnPCIE_LINK_MANAGEMENT_MASK_DEFAULT` at `0x00003fff`.
- Power/substate and ECC defaults such as `smnPCIE_LC_L1_PM_SUBSTATE_DEFAULT` at `0x04540000` and `smnPCIEP_BCH_ECC_CNTL_DEFAULT` at `0x00000100`.

These defaults align with runtime code in `amdgpu/nbio_v2_3.c`, which uses direct `smn...` addresses for PCIe config, link training, ASPM, clock gating, LTR, and workaround programming. The header is not where those policies execute, but it documents generated baseline values for the same hardware domain.

### PCIe Directory Defaults

The `nbio_pcie0_pciedir` address block defines defaults for the broader PCIe directory:

- Core control/config/debug: `smnPCIE_CNTL_DEFAULT` is `0x80811000`, `smnPCIE_CONFIG_CNTL_DEFAULT` is `0x0000000f`, `smnPCIE_DEBUG_CNTL_DEFAULT` is `0x00000001`, `smnPCIE_CNTL2_DEFAULT` is `0x0e000109`, `smnPCIE_CI_CNTL_DEFAULT` is `0x40000010`, and `smnPCIE_WPR_CNTL_DEFAULT` is `0x00000005`.
- Link/power defaults: `smnPCIE_LC_PM_CNTL_DEFAULT` is `0x76543210`, `smnPCIE_P_CNTL_DEFAULT` is `0x00850000`, `smnPCIE_P_RCV_L0S_FTS_DET_DEFAULT` is `0x000000ff`, `smnPCIE_RX_AD_DEFAULT` is `0x00000003`, and `smnPCIE_SDP_CTRL_DEFAULT` is `0x00000002`.
- HIP, strap, PRBS, performance, last-TLP, and tracking registers mostly default to zero, except `smnPCIE_HIP_REG8_DEFAULT` at `0x00008000`.
- Software reset defaults include `smnSWRST_GENERAL_CONTROL_DEFAULT` at `0x02001002`, `smnSWRST_COMMAND_1_DEFAULT` at `0x04000000`, `smnSWRST_CONTROL_0_DEFAULT` at `0x5600ff00`, `smnSWRST_CONTROL_1_DEFAULT` at `0xc220ffff`, `smnSWRST_CONTROL_4_DEFAULT` at `0x5c00ff01`, `smnSWRST_CONTROL_5_DEFAULT` at `0xfe20ffff`, `smnSWRST_CONTROL_6_DEFAULT` at `0x000007ff`, and `smnSWRST_EP_CONTROL_0_DEFAULT` at `0x00000500`.
- Clock/power and margining defaults include `smnCPM_CONTROL_DEFAULT` at `0x0080ca00`, `smnPCIE_PGSLV_CNTL_DEFAULT` at `0x00000004`, `smnLC_CPM_CONTROL_1_DEFAULT` at `0x00000001`, and `smnPCIE_LC_DEBUG_CNTL_DEFAULT` at `0x00010000`.

This family is the default baseline for PCIe operations that `nbio_v2_3.c` later changes through `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `WREG32_SOC15` helpers.

### SWDS0 Downstream-Switch Config Defaults

The `cfgBIF_CFG_DEV0_SWDS0_*` block represents a PCIe downstream switch/bridge config-space default set. It differs from the VF blocks because several bridge and downstream-port fields have meaningful nonzero defaults:

- `VENDOR_ID_DEFAULT` is `0x00001002`.
- `SUB_CLASS_DEFAULT` is `0x00000004`, and `BASE_CLASS_DEFAULT` is `0x00000006`, matching a PCI bridge class layout.
- `INTERRUPT_LINE_DEFAULT` is `0x000000ff`.
- `PMI_CAP_DEFAULT` is `0x0000c800`.
- `PCIE_CAP_LIST_DEFAULT` is `0x0000a000`, and `PCIE_CAP_DEFAULT` is `0x00000062`.
- `DEVICE_CNTL_DEFAULT` is `0x00002810`.
- `LINK_STATUS_DEFAULT` is `0x00002001`, and `LINK_CNTL2_DEFAULT` is `0x00000004`.
- MSI message control defaults to `0x00000080`.
- Virtual-channel enhanced capability list defaults to `0x14000000`, with `VC0_RESOURCE_CNTL_DEFAULT` at `0x000000fe`.
- Device serial number, AER, secondary PCIe, ACS, data-link feature, 16 GT/s PHY, and margining enhanced capability list defaults are represented.
- AER masks/severity are nonzero: uncorrectable error mask `0x00400000`, uncorrectable error severity `0x00440010`, and correctable error mask `0x00006000`.
- PCIe lane equalization defaults for lanes 0 through 15 are `0x00007f7f`.
- PCIe margining lane control defaults for lanes 0 through 15 are `0x00009c38`.

These defaults define the static config-space and capability baseline for the downstream-switch entity. They are sensitive because PCI enumeration, topology reporting, AER policy, lane equalization, and margining behavior can depend on these register reset values.

## APIs, Types, and Functions

This chunk defines no APIs, types, or functions in the C sense. Its exported interface is the set of macro names and literal constants. The effective API contract is naming consistency with the generated AMDGPU register headers:

- `nbio_2_3_offset.h` supplies the matching `mm...`, `smn...`, and `cfg...` register offsets or addresses.
- `nbio_2_3_sh_mask.h` supplies the matching field shift and mask macros.
- Driver code includes all three headers and uses the names through SOC15 and PCIE access helpers.

The important "callers" are preprocessor consumers. If a macro is renamed, deleted, or assigned a wrong value, the build may fail only when a consumer references it directly. If a wrong default remains syntactically valid, it can silently corrupt diagnostics, default-state checks, or generated-table consumers.

## Control Flow and State Behavior

There is no executable control flow in this chunk. There are no conditionals, no state machines, and no software-side persistence.

The state represented by the macros is hardware register state:

- Reset/default configuration state for SR-IOV VF PCI config spaces.
- Reset/default MSI-X table and pending-bit-array state.
- Reset/default PCIe link, transaction, flow-control, power, clock, reset, and debug state.
- Reset/default downstream-switch PCIe bridge/capability state.
- Reset/default status/log placeholders for AER, ATS, ARI, TLP prefix logs, last TLPs, PRBS counters, performance counters, and software reset status fields.

Runtime persistence belongs to hardware and to the driver/firmware programming sequence. For example, MSI/MSI-X vector registers are zero in this header but become live interrupt-routing state after PCI/MSI setup. PCIe link-control defaults become runtime link-training, ASPM, clock-gating, and workaround state once `nbio_v2_3.c` writes the corresponding registers. AER status/log fields default to zero but can later hold error state that should not be confused with immutable software constants.

## Dependencies and Integration Points

Direct dependencies are the generated AMD register-header convention and the matching NBIO 2.3 files:

- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` for register offsets and addresses.
- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h` for field masks and shifts.
- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h`.

Observed runtime integration in `nbio_v2_3.c` includes:

- PCIe indirect/data access helpers via `nbio_v2_3_get_pcie_index_offset()` and `nbio_v2_3_get_pcie_data_offset()`, returning the `mmPCIE_INDEX2` and `mmPCIE_DATA2` offsets from the same NBIO generation.
- PCIe config initialization in `nbio_v2_3_init_registers()`, which reads and updates `smnPCIE_CONFIG_CNTL`.
- Medium-grain clock gating in `nbio_v2_3_update_medium_grain_clock_gating()`, which reads and writes `smnCPM_CONTROL`.
- Light sleep in `nbio_v2_3_update_medium_grain_light_sleep()`, which reads and writes `smnPCIE_CNTL2`.
- ASPM and LTR programming in `nbio_v2_3_enable_aspm()`, `nbio_v2_3_program_ltr()`, and `nbio_v2_3_program_aspm()`, which program registers in the same PCIe/link-control family represented by `smnPCIE_LC_CNTL*`, `smnPSWUSP0_PCIE_LC_CNTL2`, `smnBIF_CFG_DEV0_EPF0_DEVICE_CNTL2`, and related defaults.
- Link-width workarounds in `nbio_v2_3_apply_lc_spc_mode_wa()` and `nbio_v2_3_apply_l1_link_width_reconfig_wa()`, which interact with `smnPCIE_LC_LINK_WIDTH_CNTL` and `smnPCIE_LC_CNTL6`.
- SR-IOV-aware register-remap behavior in `nbio_v2_3_set_reg_remap()`, which uses VF-related NBIO registers from the same generated family.

The header also integrates indirectly with Linux PCI enumeration, SR-IOV VF setup, MSI/MSI-X programming, AER handling, GPU reset flows, suspend/resume, and clock/power-management paths because those subsystems read or modify the hardware state whose defaults are described here.

## Risks

- Generated default drift is often silent. A wrong literal can compile cleanly but make diagnostics, reset comparisons, or generated register-table consumers trust a bad hardware baseline.
- PCI capability-list defaults are enumeration-sensitive. Bad `CAP_PTR`, `PCIE_CAP_LIST`, `MSI_CAP_LIST`, or enhanced-capability-list defaults can make a virtual function or downstream port appear to have a malformed capability chain.
- MSI/MSI-X defaults are interrupt-sensitive. Incorrect table/PBA defaults could hide stale pending state assumptions or cause a driver to mishandle vector initialization in diagnostics or emulation-like flows.
- SR-IOV VF defaults are virtualization-sensitive. Wrong VF BAR, MSI, ATS, ARI, AER, or adapter-ID defaults may only surface under VF assignment, guest probing, or reset of virtual functions.
- PCIe link-control defaults are platform-sensitive. Values in `PCIE_LC_*`, `PSWUSP0_PCIE_*`, flow-control, CDR, equalization, and speed-control registers can affect link training, ASPM, L1 substates, hotplug/removable-device behavior, and Navi-specific workarounds.
- SWDS0 AER defaults are error-reporting-sensitive. Wrong uncorrectable/correctable masks or severity values can change which PCIe errors are surfaced, masked, or classified as fatal/nonfatal.
- Lane equalization and margining defaults are signal-integrity-sensitive. Incorrect per-lane defaults may only show up on certain boards, link widths, cable/removable paths, or high-speed modes.
- Software-reset defaults are sequencing-sensitive. Bad `SWRST_*` defaults can affect reset isolation, endpoint reset, or recovery behavior if tooling or firmware relies on the generated reset baseline.
- Status and log defaults should not be treated as durable configuration. Fields such as AER status/logs, PRBS counters, last-TLP registers, and MSI-X PBA bits become live hardware state after boot.
- The chunk boundaries are artificial. The beginning omits the first part of `VF23`, and the ending includes only the `VF10` address-block marker without any `VF10` defaults.

## Test and Validation Signals

Useful validation is mostly build, register-database comparison, and hardware integration testing:

- Build AMDGPU with NBIO 2.3 support to catch missing or renamed generated macros referenced by `nbio_v2_3.c` or related register tooling.
- Compare this generated `nbio_2_3_default.h` segment with the authoritative AMD register database, especially repeated VF blocks, MSI-X vector ranges, AER masks/severity values, and per-lane SWDS0 equalization/margining defaults.
- Boot hardware using NBIO 2.3 and verify PCI enumeration, GPU device config space, bridge/downstream-port config space, and SR-IOV VF creation/probing.
- Enable and assign VFs where supported; check that guest-visible config space, MSI/MSI-X setup, ATS/ARI exposure, and VF reset behavior are consistent with expectations.
- Exercise MSI and MSI-X interrupt setup and teardown, including USB/MSI-X vectors if that block is used by the platform, and verify no stale pending bits or malformed vector-table assumptions.
- Stress PCIe link-management paths: ASPM enable/disable, LTR programming, suspend/resume, link retraining, removable-device paths, and the Navi10/Navi12 link-width workarounds in `nbio_v2_3.c`.
- Check AER behavior with controlled PCIe error injection or platform error logs, confirming SWDS0 and VF error masks/status/severity fields decode and reset as expected.
- Run GPU reset and recovery tests to exercise `SWRST_*`, endpoint reset, and doorbell/register-remap flows around NBIO.
- Validate clock-gating and light-sleep transitions by checking `CPM_CONTROL`, `PCIE_CNTL2`, and related link-control state before and after power-management operations.
- For generated-table maintenance, count the MSI-X table shape: 256 vectors with four defaults each, plus eight PBA defaults, and verify the range does not accidentally drop or duplicate a vector.

## Cross-Chunk Notes

The first covered line is already inside `VF23`; the complete `smnBIF_CFG_DEV0_EPF0_VF23_*` block must be reconciled with the previous chunk. Line 8700 is only the address-block comment for `VF10`; the actual `cfgBIF_CFG_DEV0_EPF0_VF10_0_*` defaults belong to the following chunk. The final per-file report should merge these boundaries before making whole-file statements about VF coverage.

### subset-b-002894: lines 8701-11799

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 8701-11799

## Scope

This chunk covers a generated AMD NBIO 2.3 default-value header section. It starts at the first `cfgBIF_CFG_DEV0_EPF0_VF10_0_*_DEFAULT` macro and covers 2,754 C preprocessor constants through `mmBIF_BX_DEV0_EPF0_VF23_HDP_REG_COHERENCY_FLUSH_CNTL_DEFAULT`.

The range has two major parts:

- Lines 8701-10421 define PCI configuration-space reset/default values for SR-IOV virtual functions `VF10` through `VF30` under `nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp`.
- Lines 10422-11799 define per-VF MMIO/RCC/BIF defaults for `VF0` through the first part of `VF23`, covering `SYSPFVFDEC`, `BIFPFVFDEC1`, and `BIFDEC2` address blocks.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct register accesses. Its public interface is the generated `<register>_DEFAULT` macro convention used with matching NBIO address and shift/mask headers.

## Purpose

`nbio_2_3_default.h` records hardware reset/default values for the NBIO 2.3 register namespace used by AMDGPU. In this chunk, the defaults describe how SR-IOV virtual functions initially expose PCIe configuration space and per-VF NBIO facilities before runtime driver, firmware, host, or guest software programs them.

The PCI config-space defaults give each covered VF a mostly disabled or zeroed function image, with a small set of nonzero capability-list and identity defaults. For `VF10` through `VF30`, each VF repeats the same 79 `cfgBIF_CFG_DEV0_EPF0_VF*_0_*_DEFAULT` entries. Nonzero values include:

- `ADAPTER_ID_DEFAULT` as `0x73101002`, carrying an AMD vendor-oriented adapter identity value in the generated config image.
- `CAP_PTR_DEFAULT` as `0x00000048`.
- PCIe capability-list and MSI capability-list links such as `PCIE_CAP_LIST_DEFAULT` `0x0000a000` and `MSI_CAP_LIST_DEFAULT` `0x0000c000`.
- `PCIE_CAP_DEFAULT` `0x00000002`, `LINK_CAP_DEFAULT` `0x00000d04`, `DEVICE_CAP2_DEFAULT` `0x00010000`, `LINK_CAP2_DEFAULT` `0x0000001e`, and `MSI_MSG_CNTL_DEFAULT` `0x00000082`.
- Enhanced capability-list pointers such as vendor-specific `0x11000000`, advanced error reporting `0x20020000`, and ATS `0x2c000000`.

The per-VF MMIO/RCC/BIF defaults then describe the reset state for host-visible or function-visible control/status areas: indirect MMIO index/data windows, RCC error/logging and doorbell aperture controls, BIF bus-master/atomic status, self-ring doorbell GPA aperture registers, HDP coherency flush registers, mailbox transfer/receive buffers, VF mailbox interrupt control, and GFX MSI-X table/PBA defaults.

## Important Macro Families

### VF PCI Configuration Defaults

`cfgBIF_CFG_DEV0_EPF0_VF10_0_*_DEFAULT` through `cfgBIF_CFG_DEV0_EPF0_VF30_0_*_DEFAULT` provide the virtual PCI function's generated defaults. Each VF includes conventional PCI header fields such as vendor ID, device ID, command, status, revision, class code, cache line, latency, header, BIST, BARs, ROM base, interrupt line/pin, min grant, and max latency.

The same block also covers PCIe capability state:

- Base PCIe capability and link/device capability/control/status defaults.
- PCIe Capability 2 link/device defaults.
- MSI and MSI-X capability defaults. MSI has a nonzero message-control default, while MSI-X capability/table/PBA defaults are zero in these config-space blocks.
- Vendor-specific, AER, ATS, and ARI enhanced capability defaults. AER status/mask/severity/header-log and TLP-prefix log values reset to zero; ARI defaults are zero; ATS has a nonzero enhanced-capability list pointer but zero capability/control defaults.

Most config fields are `0x00000000`. The repeated nonzero capability pointers make the generated layout sensitive to PCI capability-chain consistency.

### Per-VF SYSPFVFDEC Indirect MMIO Windows

For `VF0` through `VF23`, the chunk introduces or partially covers `mmBIF_BX_DEV0_EPF0_VF*_MM_INDEX_DEFAULT`, `MM_DATA_DEFAULT`, and `MM_INDEX_HI_DEFAULT`. These reset to zero and represent the per-VF indirect MMIO access window defaults. The companion offset header maps these to per-VF base regions such as the `0xd0400000` style windows seen for later VFs.

### RCC Per-VF Control Defaults

`mmRCC_DEV0_EPF0_VF*_RCC_ERR_LOG_DEFAULT`, `RCC_DOORBELL_APER_EN_DEFAULT`, `RCC_CONFIG_MEMSIZE_DEFAULT`, `RCC_CONFIG_RESERVED_DEFAULT`, and `RCC_IOV_FUNC_IDENTIFIER_DEFAULT` reset to zero for each covered VF. These fields are tied to error logging, doorbell aperture enablement, reported memory size/configuration, reserved config state, and SR-IOV function identification.

The generated `amdgpu/nbio_v2_3.c` consumer uses the non-VF/PF versions of the same NBIO register families for memory size reads and doorbell aperture control, so these VF defaults document the reset baseline for the corresponding virtualized control surfaces.

### BIF Per-VF Doorbell, HDP Flush, Mailbox, and Transaction Defaults

Each complete per-VF `BIFPFVFDEC1` block includes:

- `BIF_BME_STATUS_DEFAULT` and `BIF_ATOMIC_ERR_LOG_DEFAULT`, both zero.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH/LOW_DEFAULT`, both zero.
- `DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT` as `0x00000100`.
- `HDP_REG_COHERENCY_FLUSH_CNTL_DEFAULT`, `HDP_MEM_COHERENCY_FLUSH_CNTL_DEFAULT`, `GPU_HDP_FLUSH_REQ_DEFAULT`, and `GPU_HDP_FLUSH_DONE_DEFAULT`, all zero.
- `BIF_TRANS_PENDING_DEFAULT` and `NBIF_GFX_ADDR_LUT_BYPASS_DEFAULT`, both zero.
- Four transmit mailbox data words, four receive mailbox data words, `MAILBOX_CONTROL_DEFAULT`, `MAILBOX_INT_CNTL_DEFAULT`, and `BIF_VMHV_MAILBOX_DEFAULT`, all zero.

This mirrors active NBIO 2.3 driver responsibilities: `nbio_v2_3_remap_hdp_registers()` remaps HDP flush controls, `nbio_v2_3_enable_doorbell_selfring_aperture()` writes the PF self-ring doorbell aperture base/control fields, and other NBIO paths use mailbox, interrupt, and transaction status registers in the same generated namespace.

### RCC GFX MSI-X Defaults

For complete `BIFDEC2` per-VF blocks, `mmRCC_DEV0_EPF0_VF*_GFXMSIX_VECT0..3_*_DEFAULT` define four MSI-X vector slots. Address-low, address-high, and message-data defaults are zero; each vector `CONTROL_DEFAULT` is `0x00000001`; and `GFXMSIX_PBA_DEFAULT` is zero.

That reset state means vector address/data are unprogrammed, while the control field begins in the generated default state indicated by bit 0. Software that enables interrupts must program address/data and honor the control-mask semantics from the paired shift/mask definitions and PCI MSI-X rules.

## Control Flow and State Behavior

There is no runtime control flow in this header. The only "execution" effect is compile-time macro substitution when AMDGPU code includes the NBIO 2.3 generated headers.

The state represented here is persistent hardware register state after reset or when comparing against expected defaults. Important state categories are:

- SR-IOV VF PCI identity and capability-chain defaults.
- PCIe device/link/MSI/AER/ATS/ARI capability defaults for each virtual function.
- Per-VF indirect MMIO index/data reset state.
- Per-VF RCC doorbell aperture, memory-size/configuration, error-log, and IOV identifier reset state.
- Per-VF BIF bus-master/atomic status, self-ring doorbell GPA aperture state, HDP flush request/done state, transaction-pending state, and mailbox buffers/control.
- Per-VF GFX MSI-X table and pending-bit-array defaults.

Many of these registers are not normal durable software configuration. PCI config command/status fields, AER status logs, HDP flush request/done bits, transaction-pending bits, mailbox buffers, and MSI-X vectors are runtime stateful interfaces. The default macros do not encode ordering, polling, timeout, locking, guest/host ownership, or clear-on-write semantics.

## Dependencies and Integration Points

This chunk belongs to a generated NBIO header set:

- `nbio_2_3_offset.h` supplies matching register addresses and base indices for the names in this default header.
- `nbio_2_3_sh_mask.h` supplies matching bitfield shifts and masks used by `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.
- `amdgpu/nbio_v2_3.c` includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h`, and uses the NBIO 2.3 namespace through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, and `WREG32_FIELD15`.
- Linux PCI/SR-IOV and AMDGPU virtualization paths depend on these generated register names matching the hardware and firmware contract for virtual functions.

The active NBIO 2.3 driver code around this namespace handles revision ID reads, memory-controller access enablement, memory-size reads, SDMA/VCN/IH doorbell ranges, doorbell aperture enablement, self-ring aperture programming, HDP flush remapping, interrupt control, and NBIO clock/power gating. This chunk's VF defaults document the reset baseline for related per-VF hardware surfaces even though the chunk itself does not implement those operations.

## Risks

- Generated macro drift is high impact. Wrong defaults for PCI config-space capability pointers can break the VF capability chain seen by the host or guest.
- SR-IOV repetition is easy to damage mechanically. `VF10` through `VF30` config blocks are structurally identical; a one-off rename, value change, or missing macro can affect only one VF and be hard to detect without enumerating many VFs.
- Capability defaults are security and compatibility sensitive. MSI/MSI-X, AER, ATS, and ARI defaults influence interrupt setup, PCIe error handling, address translation behavior, and guest-visible device features.
- Doorbell aperture defaults affect queue submission isolation. Incorrect reset values for `RCC_DOORBELL_APER_EN` or self-ring GPA aperture controls can expose, hide, or misroute doorbell writes in virtualized environments.
- HDP flush defaults are coherency-sensitive. Incorrect request/done/control defaults can make CPU/GPU visibility bugs appear as sporadic memory corruption or hangs.
- Mailbox defaults are virtualization-sensitive. VF-to-host or VF-to-hypervisor mailbox registers must start cleanly; stale nonzero defaults could confuse reset, FLR, or guest-driver initialization flows.
- MSI-X vector-control defaults must stay aligned with hardware semantics. An incorrect default could expose vectors before address/data are programmed or leave interrupts masked when the driver expects otherwise.
- This chunk ends mid-family. The `VF23` per-VF MMIO block continues after line 11799, so final per-file analysis must merge later chunks before claiming complete `VF23` coverage.

## Test and Validation Signals

Useful validation is mostly build, enumeration, virtualization, and hardware bring-up coverage:

- Build AMDGPU code that includes `nbio/nbio_2_3_default.h`; this catches missing or renamed generated macros at compile time.
- Boot an NBIO 2.3 ASIC and verify `amdgpu/nbio_v2_3.c` still reads/writes matching NBIO registers for revision ID, memory size, doorbell aperture setup, HDP remap, and interrupt control.
- Enable SR-IOV and enumerate VFs beyond `VF9`, especially `VF10` through `VF30`, checking PCI config headers, capability chains, MSI/MSI-X capability visibility, AER/ATS/ARI capability layout, and BAR/ROM defaults.
- Exercise guest VF reset/FLR paths and confirm RCC, BIF, mailbox, transaction-pending, HDP flush, and MSI-X state returns to expected defaults.
- Run doorbell submission tests for PF and VF queues, including SDMA/VCN/IH paths, to detect aperture or self-ring default regressions.
- Run interrupt tests with MSI/MSI-X enabled and disabled, verifying vector programming, vector masking, PBA state, and interrupt delivery after VF reset.
- Run GPU memory coherency and HDP flush stress tests across host and guest contexts to catch incorrect flush-control or flush-done expectations.
- Run PCIe AER and virtualization fault-injection tests where available to validate error-log defaults, AER capability visibility, and mailbox/error-reporting behavior.

## Unresolved Cross-Chunk References

Line 8701 starts immediately after the `VF9` PCI config block; the `VF10` address-block comment is at line 8700 just outside the requested range. Line 11799 stops inside `nbio_nbif0_bif_bx_dev0_epf0_vf23_BIFPFVFDEC1`; the remaining `VF23` BIF mailbox fields and later RCC MSI-X defaults continue in a later chunk. The merge/reconciliation lane should stitch those boundaries before producing the final source-file report.

### subset-b-002895: lines 11800-14994

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 11800-14994

## Purpose

This chunk is part of AMDGPU's generated NBIO 2.3 register-default header. It provides compile-time `_DEFAULT` constants for NBIO/NBIF PCIe, BIF, RCC, SR-IOV virtual-function, MSI/MSI-X, GPUIOV, and endpoint configuration registers. The constants are not executable logic; they are the reset/default values paired with the related `nbio_2_3_offset.h` register addresses and `nbio_2_3_sh_mask.h` bit layouts.

The mapped source range contains 2,718 `#define` constants. Most values are zero reset values, with non-zero defaults marking enabled/masked capability bits, PCI capability-list offsets, device/vendor IDs, interrupt defaults, MSI-X vector mask state, doorbell aperture mode bits, PCIe link capability values, lane equalization presets, and GPUIOV layout metadata.

## Important API, Types, And Macro Families

- Header contract: guarded by `_nbio_2_3_DEFAULT_HEADER`; exports only preprocessor constants.
- Per-VF MMIO defaults:
  - `mmBIF_BX_DEV0_EPF0_VF*_..._DEFAULT` appears for the tail of VF23 and then VF24-VF30 / VF0-VF30 blocks in this chunk.
  - `mmRCC_DEV0_EPF0_VF*_..._DEFAULT` covers RCC VF state and four GFX MSI-X vector table entries.
- Config-space per-VF defaults:
  - `cfgBIF_BX_DEV0_EPF0_VF*_..._DEFAULT` and `cfgRCC_DEV0_EPF0_VF*_..._DEFAULT` mirror the VF BIF/RCC defaults for config-access views.
  - `cfgBIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF*_FB_DEFAULT` reserves per-VF framebuffer assignment fields for VF0-VF30.
- PCIe switch/upstream config defaults:
  - `cfgPSWUSCFG0_1_*_DEFAULT` describes the `nbio_pcie0_pswuscfg0_cfgdecp` PCIe config block, including standard header, PCIe capability, AER, VC, lane equalization, 16 GT, ESM, DLF, margining, CCIX, and related enhanced-capability fields.
- Endpoint function config defaults:
  - `cfgBIF_CFG_DEV0_EPF0_1_*_DEFAULT` is the large EPF0 config image. It includes AMD vendor ID `0x1002`, device ID `0x7310`, PCI/PCIe capability pointers, AER defaults, BAR controls, SR-IOV, ATS, PRI, PASID, ACS, DLF, 16 GT, margining, and GPUIOV fields.
  - `cfgBIF_CFG_DEV0_EPF1_1_*_DEFAULT` begins the EPF1 config image. It includes vendor ID `0x1002`, device ID `0xab38`, a type/multifunction-looking header default `0x80`, interrupt pin `0x2`, and a shorter PCIe capability set.

Representative non-zero defaults in this chunk include:

- VF self-ring doorbell control: `*_DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT = 0x00000100`.
- VF MSI-X vector controls: `*_GFXMSIX_VECT[0-3]_CONTROL_DEFAULT = 0x00000001`, leaving vector entries masked/disabled until programmed.
- PCI config identity/capabilities: `VENDOR_ID_DEFAULT = 0x00001002`, EPF0 `DEVICE_ID_DEFAULT = 0x00007310`, EPF1 `DEVICE_ID_DEFAULT = 0x0000ab38`, `CAP_PTR_DEFAULT = 0x00000048`, `PCIE_CAP_LIST_DEFAULT = 0x0000a000`, `MSI_CAP_LIST_DEFAULT = 0x0000c000`.
- PCIe link/control defaults: `DEVICE_CNTL_DEFAULT = 0x00002810`, `LINK_CAP_DEFAULT = 0x00000d04` for EPF functions and `0x00011c04` for PSWUSCFG0, `LINK_CNTL2_DEFAULT = 0x00000004`, `LINK_CAP2_DEFAULT = 0x0000001e`.
- AER defaults: `PCIE_UNCORR_ERR_MASK_DEFAULT = 0x00400000` or `0x04400000` for PSWUSCFG0, `PCIE_UNCORR_ERR_SEVERITY_DEFAULT = 0x00440010`, `PCIE_CORR_ERR_MASK_DEFAULT = 0x00006000`.
- Lane defaults: Gen3-style `PCIE_LANE_*_EQUALIZATION_CNTL_DEFAULT` often uses `0x00007f00` or `0x00007f7f`, 16 GT equalization uses `0x000000f0` or `0x000000ff`, and margining lane control uses `0x00009c38`.
- GPUIOV layout: `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_OFFSETS_DEFAULT = 0x0012000c`, with per-VF FB and engine scheduler DW fields defaulting to zero.

## Control Flow

There is no runtime control flow in this header. The effective flow is build-time inclusion:

1. `amdgpu/nbio_v2_3.c` includes `nbio/nbio_2_3_default.h`, `nbio/nbio_2_3_offset.h`, and `nbio/nbio_2_3_sh_mask.h`.
2. Driver code uses offset macros to read/write NBIO registers and mask/shift macros to update fields.
3. `_DEFAULT` constants from this file provide reset/reference values for generated register definitions or code paths that need known hardware defaults.

Within the chunk, register families are ordered by generated address-block comments. VF blocks repeat the same BIF/RCC field pattern across virtual functions, then the source transitions into PCIe config-space blocks for the upstream/switch view and endpoint functions.

## State And Persistence Behavior

The constants model hardware reset/configuration state; they do not store mutable driver state and do not persist across boots. Runtime state is held by the GPU hardware registers, PCI config space, firmware/BIOS initialization, and AMDGPU device structures. Defaults such as MSI-X vector control, doorbell aperture control, AER masks, and PCI capability pointers are baseline values that can be superseded by firmware, PCI enumeration, SR-IOV setup, VF provisioning, interrupt setup, and AMDGPU register writes.

Because many VF fields default to zero, the hardware starts with unprogrammed mailbox buffers, no VF framebuffer assignment, no VF BAR base values, no MSI/MSI-X addresses/data, and no enabled doorbell aperture base until the PF/hypervisor/driver provisions them. Non-zero control defaults indicate reset-time masking or capability advertisement, not necessarily enabled runtime behavior.

## Dependencies And Integration Points

- Direct include integration: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes this header with the matching offset and shift/mask headers.
- Register access integration: `nbio_v2_3.c` uses AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` against NBIO registers whose names are defined by the generated headers.
- PCI subsystem integration: endpoint and upstream config defaults align with Linux PCI enumeration, capability parsing, MSI/MSI-X setup, AER handling, ACS/ATS/PRI/PASID capabilities, BAR sizing, and power-management capability exposure.
- SR-IOV/virtualization integration: the repeated VF0-VF30 BIF/RCC fields, SR-IOV capability fields, GPUIOV vendor-specific header, mailbox registers, per-VF framebuffer fields, and MSI-X vector defaults are the hardware contract used by PF/VF virtualization flows.
- Doorbell/HDP integration: VF and PF BIF doorbell aperture, HDP coherency flush, GPU HDP flush request/done, and mailbox defaults are tied to AMDGPU ring submission, interrupt, KFD, and host-data-path flush programming performed outside this generated header.

## Risks And Edge Cases

- Generated-header drift is the main risk. If a `_DEFAULT` value no longer matches the ASIC register database, the driver may compare against or initialize from stale reset assumptions.
- The chunk has many repeated VF patterns. Mechanical edits can easily alter one VF but not the others, causing asymmetric behavior that may only appear under SR-IOV with specific VF numbers.
- `mm*` and `cfg*` families expose similar register names through different access paths. Mixing config-space defaults with MMIO register offsets can produce incorrect programming.
- Non-zero defaults are semantically loaded. Examples include MSI-X vector control `0x1`, doorbell self-ring control `0x100`, AER masks/severity values, capability-list encodings, and lane equalization presets. Treating them as arbitrary constants can break enumeration, interrupt delivery, link training, or virtualization isolation.
- EPF0 and EPF1 intentionally differ: EPF0 advertises GPUIOV/SR-IOV-oriented fields and device ID `0x7310`; EPF1 advertises device ID `0xab38` and a reduced visible capability set in this range. Code assuming one endpoint layout for all functions would be fragile.
- Most GPUIOV per-VF FB and scheduler fields default to zero, so runtime provisioning code must not infer that a VF is assigned resources merely because the capability exists.

## Test Signals

- Kernel build should compile `amdgpu/nbio_v2_3.c` without macro redefinition or missing-symbol errors when this generated header is included with `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h`.
- PCI enumeration on NBIO 2.3 ASICs should report AMD vendor ID `1002`, expected EPF0/EPF1 device IDs, valid capability-list traversal, correct MSI/MSI-X capability behavior, and sane AER/ACS/ATS/PRI/PASID exposure for the supported hardware mode.
- SR-IOV validation should create/provision VFs consistently across VF0-VF30: mailbox buffers start clear, per-VF FB fields are zero until assigned, VF MSI-X vectors are masked until programmed, and doorbell/HDP controls are initialized by PF or host logic.
- Interrupt tests should verify MSI/MSI-X setup after the driver writes vector address/data/control fields, since reset defaults intentionally leave vector address/data as zero and controls at `0x1`.
- PCIe link training and power-management tests should catch incorrect `LINK_CAP`, `LINK_CAP2`, lane equalization, DLF, LTR, L1 PM, DPA, and margining defaults through link width/speed, AER error reporting, and suspend/resume behavior.
- Register-database regeneration tests or diffs should flag any change to non-zero defaults in this range, especially `VENDOR_ID`, `DEVICE_ID`, capability-list offsets, AER masks/severity, `GPUIOV_OFFSETS`, SR-IOV page-size values, and lane equalization/margining constants.

### subset-b-002896: lines 14995-17881

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 14995-17881

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register-default header. It contains C preprocessor `#define` constants only, with default reset/configuration values for NBIF PCIe configuration-space registers. There are no functions, structs, enums, allocations, locks, or executable branches in this line range.

The range starts in the tail of the `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` address block and ends in the middle of `nbio_nbif0_bif_cfg_dev0_epf0_vf27_bifcfgdecp`. It covers 2,797 default-value macros. Adjacent chunks are required for a complete per-file view of the EPF1 block before line 14995 and the VF27 and later VF blocks after line 17881.

Although this repository path is under a Ceph client tree, the file is Linux AMDGPU hardware-description data for GPU NBIO/NBIF PCIe programming.

## Purpose

`nbio_2_3_default.h` supplies compile-time defaults for NBIO 2.3 registers. The companion headers provide addresses and bitfields: `nbio_2_3_offset.h` maps register names to offsets and base indices, while `nbio_2_3_sh_mask.h` maps register fields to shifts and masks. AMDGPU runtime code includes all three so it can compare against, initialize, restore, or document ASIC-default values without hard-coding raw reset constants at every use site.

This chunk describes default PCI configuration-space images for device 0 endpoint functions and virtual functions:

- The tail of physical function `EPF1`, including secondary PCIe, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data link feature, 16 GT/s PHY, margining, VF resizable BAR, and GPU IOV vendor-specific capability defaults.
- Full physical functions `EPF2` and `EPF3`, including PCI identity/class-code defaults, power-management, PCIe capability, MSI/MSI-X, SATA/USB-like capability fields, AER, BAR, DPA, ACS, PASID, ARI, TPH requester, and TPH steering-table defaults.
- Virtual functions `EPF0_VF0` through `EPF0_VF26` and the beginning of `EPF0_VF27`, each with a compact repeated PCIe VF config-space default image.

## Important Macro Families

The `cfgBIF_CFG_DEV0_EPF1_1_*` tail continues a physical endpoint function. It sets PCIe lane equalization defaults (`0x00007f00` for Gen3-style lane controls and `0x000000f0` for 16 GT/s lane controls), leaves most error/status/capability control registers at zero, and encodes capability-list linkage constants such as ACS `0x2b000000`, ATS `0x2c000000`, page request `0x2d000000`, PASID `0x2f000000`, multicast `0x32000000`, LTR `0x32800000`, ARI `0x33000000`, SR-IOV `0x37000000`, TPH requester `0x40000000`, data link feature `0x41010025`, 16 GT/s PHY `0x44010026`, and margining `0x4c010027`.

The EPF1 SR-IOV and GPU IOV defaults are mostly disabled or zeroed. Notable non-zero values are `PCIE_SRIOV_SYSTEM_PAGE_SIZE_DEFAULT` at `0x00000001`, `PCIE_PASID_CAP_DEFAULT` at `0x00001000`, `DATA_LINK_FEATURE_CAP_DEFAULT` at `0x00000001`, VF resize BAR1 control at `0x00000020`, and GPU IOV offsets at `0x0012000c`. The GPU IOV area includes hypervisor/VM mailbox words, interrupt enable/status, reset control, total framebuffer and per-VF framebuffer slots for VF0-VF30, P2P-over-XGMI enable, and scheduler dwords for UVD, VCE, GFX, and UVD1. Their zero defaults mean the driver or firmware must actively provision virtualization resources before use.

`cfgBIF_CFG_DEV0_EPF2_1_*` describes a physical function with AMD vendor ID `0x1002`, device ID `0x7316`, adapter ID `0x73161002`, class code `0x0c0330`, interrupt pin 3, and multifunction header `0x80`. It has PCIe, PM, MSI, AER, BAR, power budget, DPA, ACS, PASID, ARI, and TPH requester defaults. It also has function-specific USB/SATA-style defaults such as `SBRN`, `FLADJ`, `DBESL_DBESLD`, `SATA_CAP_*`, and `SATA_IDP_*`.

`cfgBIF_CFG_DEV0_EPF3_1_*` is similar to EPF2 but with device ID `0x7314`, adapter ID `0x73141002`, class code `0x0c8000`, interrupt pin 4, and no enabled PM capability bits by default. It repeats the same PCIe, MSI, AER, BAR, DPA, ACS, PASID, ARI, and TPH requester shape, including a 64-entry TPH steering table initialized to zero.

The `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` families define virtual-function config-space defaults for VF0 through VF26 and the start of VF27. Each full VF block contains 82 macros. Common defaults include zero vendor/device IDs, command/status/class fields, BARs, MSI address/data/mask/pending fields, MSI-X table/PBA fields, vendor-specific dwords, AER status/mask/severity/log fields, ATS capability/control, and ARI capability/control. The repeated non-zero defaults are adapter ID `0x73101002`, capability pointer `0x00000048`, PCIe capability list `0x0000a000`, PCIe capability `0x00000002`, link capability `0x00000d04`, device capability 2 `0x00010000`, link capability 2 `0x0000001e`, MSI capability list `0x0000c000`, MSI message control `0x00000082`, vendor-specific extended capability list `0x11000000`, AER extended capability list `0x20020000`, and ATS extended capability list `0x2c000000`.

## Control Flow and State

This header has no direct control flow. The implicit hardware workflow is:

1. ASIC-generated defaults define the reset/configuration image for physical and virtual PCIe functions.
2. Driver code includes this header with the offset and shift/mask headers.
3. Runtime NBIO code reads and writes actual hardware registers through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `WREG32_FIELD15`.
4. PCIe enumeration, SR-IOV setup, VF reset, AER handling, MSI/MSI-X programming, ATS/PASID enablement, TPH steering, BAR sizing, and power-management paths observe or modify the corresponding live registers.

State is persistent in hardware registers, not in this header. The default values represent reset-time or generated baseline state. Runtime state can be changed by the kernel driver, firmware, BIOS/platform code, PCI core, hypervisor, guest VFs, or device reset/power transitions.

Several defaults are intentionally inert. Error status and log fields start at zero, BAR address/control defaults avoid preprogrammed host apertures, MSI/MSI-X message fields are zero until the OS programs interrupts, and most virtualization resource registers are zero until SR-IOV or GPU IOV provisioning occurs. Capability-list dwords are different: their non-zero defaults encode the advertised PCIe extended capability chain and must remain consistent with the offset/header layout.

## Dependencies and Integration Points

The direct dependency is the C preprocessor. The header is guarded by `_nbio_2_3_DEFAULT_HEADER` and is normally included by AMDGPU NBIO 2.3 code alongside:

- `nbio/nbio_2_3_offset.h` for register offsets and base indices.
- `nbio/nbio_2_3_sh_mask.h` for field shifts and masks.
- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes this header and implements the NBIO 2.3 function table.

`nbio_v2_3.c` is the main in-tree runtime integration point. It handles revision ID reads, memory-controller access enablement, memsize reads, SDMA/VCN/IH doorbell ranges, doorbell aperture and self-ring aperture setup, HDP flush remapping, interrupt control, clock gating/light sleep, PCIe index/data offsets, ASPM/LTR programming, link-width workarounds, doorbell interrupt clearing, and MMIO remap selection. This chunk's config-space defaults are not the core fields directly manipulated by most of those helpers, but they are part of the same NBIO 2.3 generated register ABI consumed by that implementation and by PCIe/SR-IOV-facing code.

Broader integration points include Linux PCI enumeration, AMDGPU device discovery, physical-function capability advertisement, virtual-function config-space exposure, hypervisor-mediated SR-IOV, AER diagnostics, MSI/MSI-X interrupt programming, ATS/PASID address-translation features, PCIe link training/status reporting, BAR probing/resizing, and GPU IOV framebuffer/scheduler partitioning.

## Risks

Generated default-value headers are easy to treat as passive data, but incorrect constants can still be high impact. A wrong PCIe capability-list pointer can make the OS or hypervisor parse the wrong extended capability chain. A wrong device/class ID can bind the wrong driver or change how Linux enumerates the function. Wrong MSI/MSI-X defaults can affect interrupt capability discovery. Wrong AER masks or severity defaults can hide or misclassify PCIe errors.

The physical-function defaults encode different function personalities. EPF2 advertises class `0x0c0330` and device `0x7316`; EPF3 advertises class `0x0c8000` and device `0x7314`; EPF1's earlier identity fields are outside this chunk. Copying defaults across EPFs without preserving those distinctions can break function-specific kernel binding and platform assumptions.

The VF blocks are extremely repetitive. Off-by-one generation mistakes in `VF0` through `VF27` names or values would compile successfully while exposing the wrong virtual-function config image. Because the range ends inside VF27, final file-level reconciliation must ensure VF27 is completed and later VFs are covered by adjacent chunks.

Virtualization-facing defaults carry isolation risk. SR-IOV, ATS, PASID, ARI, VF BAR sizing, GPU IOV framebuffer allocation, P2P-over-XGMI enablement, and per-engine scheduling registers affect guest-visible resource assignment and DMA/address-translation behavior. Incorrect defaults or incorrect runtime assumptions based on them can produce guest enumeration failures, stale VF state after reset, DMA isolation problems, or unusable GPU partitions.

Many status and control registers are defaulted to zero because hardware or software fills them later. Tests that only compare against this header can miss runtime-only failures in AER logging, MSI delivery, TPH steering, lane margining, or SR-IOV provisioning.

## Test and Validation Signals

Useful validation is mostly build, enumeration, and hardware integration based:

- Build AMDGPU with NBIO 2.3 support; missing or renamed default macros should fail at include or use sites.
- Boot NBIO 2.3 hardware and confirm `nbio_v2_3_funcs` initializes normally, including doorbells, HDP flush remaps, clock/power setup, ASPM/LTR programming, and MMIO remap selection.
- Inspect `lspci -vvv` for the relevant physical functions and verify vendor/device IDs, class codes, capability pointer chains, PCIe capability versions, link capability/status, MSI/MSI-X capabilities, AER capability, ACS/ATS/PASID/ARI exposure, and TPH requester capability match expectations.
- Exercise suspend/resume, D3 transitions, FLR, and GPU reset paths while checking that capability and AER state is restored or reinitialized correctly.
- On SR-IOV-capable platforms, enable VFs and verify VF0 through VF27 enumerate with the expected config-space image, receive working MSI/MSI-X interrupts if enabled by the stack, and survive guest FLR/reset cycles.
- Validate ATS/PASID/page-request related behavior with IOMMU enabled when those capabilities are advertised or consumed by the platform.
- Use AER injection or platform error reporting to confirm uncorrectable/correctable error masks, severities, header logs, and TLP prefix logs behave according to PCIe expectations.
- For GPU IOV paths, verify framebuffer partitioning, mailbox/reset control, scheduler dwords, and P2P-over-XGMI state are provisioned by firmware/driver before guest use rather than relying on the zero defaults in this chunk.

## Cross-Chunk Notes

This report covers only lines 14995-17881 of `nbio_2_3_default.h`. It starts after the beginning of the EPF1 physical-function config-space defaults and ends before the full VF27 block is visible. The final per-file research document should merge this with neighboring chunks before making complete claims about EPF1, VF27, or the full set of NBIO 2.3 PF/VF default registers.

### subset-b-002897: lines 17882-18521

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 17882-18521

## Scope

This chunk is the final slice of AMD's generated NBIO 2.3 default-register header. It contains 604 preprocessor constants and the closing `#endif`; there are no C functions, structs, enums, variables, includes, locks, allocations, or direct MMIO reads/writes in this range.

The covered lines begin in the tail of the `nbio_nbif0_bif_cfg_dev0_epf0_vf27_bifcfgdecp` block, define the full default PCIe configuration spaces for VFs 28, 29, and 30, then cover default values for shadow config registers, BIF/SYSHUB windows, RCC straps and endpoint/downstream PCIe blocks, RCC and BIF core control blocks, PF mailbox and doorbell registers, GDC doorbell/power-gating registers, and four GFX MSI-X vector-table defaults.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU/NBIO hardware metadata, not distributed filesystem code.

## Purpose

`nbio_2_3_default.h` publishes reset/default values for NBIO 2.3 registers. The companion `nbio_2_3_offset.h` provides the matching register addresses, and `nbio_2_3_sh_mask.h` provides field masks and shifts for code that needs to compose or decode register values.

This exact chunk describes default state for several integration surfaces:

- SR-IOV VF PCIe config defaults for `cfgBIF_CFG_DEV0_EPF0_VF28_1_*`, `VF29_1_*`, and `VF30_1_*`, plus the ending AER/ATS/ARI defaults for `VF27_1`.
- Host-visible config shadow and system access portals, including `cfgSHADOW_*`, `cfgSUC_*`, `cfgBIF_BX_PF1_MM_*`, `cfgPCIE_INDEX*`, `cfgPCIE_DATA*`, BIOS/SBIOS scratch registers, and GFX MMIO register CAM defaults.
- RCC strap and endpoint defaults that seed PCIe link identity, requestor behavior, dynamic power allocation, LTR, PME, error-control, and lane-speed-related state.
- Core RCC/BIF defaults for reset enables, peer ranges, host bus-number capture, peer framebuffer offsets, HDP coherency flush remaps, BACO exit timers, NBIF GFX address LUT entries, BIF ring registers, interrupts, pad controls, and GPU IOV config sizes.
- PF-only doorbell, HDP flush, transaction-pending, mailbox, and VM/HV mailbox defaults used by bare-metal and SR-IOV paths.
- GDC defaults for A2S/S2A control, SDP ports, clock/power gating, doorbell ranges for SDMA/IH/MMSCH/ACV, and doorbell fencing.
- RCC GFX MSI-X vector-table defaults for four vectors plus the PBA register, with vector control defaults set to `0x00000001`.

The generated constants are compile-time data. They do not enforce reset sequencing or access permissions; the owning AMDGPU code and hardware specification determine when these defaults are used as reset baselines, comparison values, or documentation of hardware reset state.

## Important Macros And Register Groups

The public interface is the generated `<register>_DEFAULT` macro namespace. Important groups in this range are:

- `cfgBIF_CFG_DEV0_EPF0_VF27_1_PCIE_*_DEFAULT`: final VF27 PCIe vendor-specific, AER, header-log, TLP-prefix-log, ATS, and ARI defaults at the chunk boundary.
- `cfgBIF_CFG_DEV0_EPF0_VF28_1_*_DEFAULT`, `cfgBIF_CFG_DEV0_EPF0_VF29_1_*_DEFAULT`, and `cfgBIF_CFG_DEV0_EPF0_VF30_1_*_DEFAULT`: complete repeated VF PCIe config-space default sets. Each includes vendor/device/class/header/BAR/capability-pointer defaults, PCIe capability defaults, link capability defaults (`LINK_CAP_DEFAULT` `0x00000d04`, `LINK_CAP2_DEFAULT` `0x0000001e`), MSI defaults (`MSI_MSG_CNTL_DEFAULT` `0x00000082`), empty MSI-X capability defaults, AER defaults, ATS enhanced capability list default `0x2c000000`, and empty ARI defaults. The adapter ID default is `0x73101002`.
- `cfgSHADOW_*_DEFAULT` and `cfgSUC_*_DEFAULT`: bridge/config shadow and sideband/user-config access defaults, all zero in this chunk.
- `cfgBIF_BX_PF1_MM_INDEX_DEFAULT`, `cfgBIF_BX_PF1_MM_DATA_DEFAULT`, and `cfgBIF_BX_PF1_MM_INDEX_HI_DEFAULT`: PF1 indirect MMIO access defaults.
- `cfgSYSHUB_*`, `cfgPCIE_INDEX*`, `cfgPCIE_DATA*`, `cfgSBIOS_SCRATCH_*`, `cfgBIOS_SCRATCH_*`, `cfgBIF_*_INTR_CNTL`, and `cfgGFX_MMIOREG_CAM_*`: system hub, PCIe indirect access, scratch, interrupt, and MMIO remap/CAM defaults.
- `cfgRCC_BIF_STRAP*`, `cfgRCC_DEV0_PORT_STRAP*`, and `cfgRCC_DEV0_EPF[01]_STRAP*`: RCC strap defaults that encode device/port/function identity and link capabilities. These are nonzero and topology-sensitive.
- `cfgEP_PCIE_*` and `cfgPCIE_F[01]_DPA_*`: endpoint PCIe defaults for scratch/control, bus control, LTR transmit control, dynamic power allocation capability/latency/control, DPA substate power allocations, PME, error control, RX control, and link-speed control.
- `cfgDN_PCIE_*` and `cfgPCIE_*` downstream/downstream-port defaults: downstream-side control, config, strap, error, RX, link-speed, link-control, and LTR-message defaults.
- `cfgRCC_DEV0_EPF0_RCC_*`: PF/VF decode defaults for RCC error logging, doorbell aperture enablement, memory-size configuration, reserved config, and IOV function identifier.
- `cfgRCC_*`: RCC core defaults for BACO, reset, margining parameters, peer register ranges, bus/config aperture, XDMA address, bus-number lists, peer framebuffer offsets, device/function lists, link controls, LTR low-switch control, and MH arbitration.
- `cfgBIF_*`, `cfgBX_*`, `cfgINTERRUPT_*`, `cfgBACO_*`, `cfgNBIF_GFX_ADDR_LUT_*`, and pad-control defaults: BIF core control, reset, interrupt, FB enable, pending-transaction, BACO timing, address LUT, HDP flush remap, ring buffer, MP1 interrupt, GPU IOV config-size, and physical pad defaults.
- `cfgBIF_BX_PF_*`: PF-only BIF status, atomic error log, self-ring doorbell GPA aperture, HDP coherency flush, GPU HDP flush request/done, transaction pending, LUT bypass, PF mailbox message buffers, mailbox control/interrupt, and VM/HV mailbox defaults.
- `cfgA2S_*`, `cfgNGDC_*`, `cfgBIF_*_DOORBELL_RANGE`, `cfgBIF_DOORBELL_FENCE_CNTL`, and `cfgS2A_MISC_CNTL`: GDC bridge, SDP, clock/power-gating, and engine doorbell range defaults.
- `cfgRCC_DEV0_EPF0_GFXMSIX_VECT[0-3]_*` and `cfgRCC_DEV0_EPF0_GFXMSIX_PBA_DEFAULT`: MSI-X table/PBA defaults for the graphics function. Address and data defaults are zero; each vector control default is `0x00000001`, which conventionally corresponds to a masked vector.

## Control Flow

There is no executable control flow in this header. Runtime behavior comes from consumers that include the generated NBIO 2.3 headers:

1. AMDGPU NBIO 2.3 code includes this file with `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h`.
2. Register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `REG_SET_FIELD`, and `SOC15_REG_OFFSET` use the offset and shift/mask headers to access actual hardware registers.
3. Default macros can be used as reset baselines, initial values, or generated metadata for bring-up and diagnostics. In this source tree, `amdgpu/nbio_v2_3.c` is the direct include site for `nbio_2_3_default.h`; it programs related NBIO surfaces such as HDP flush remaps, framebuffer access, SDMA/VCN/IH doorbell ranges, doorbell apertures, interrupt control, clock gating, and PCIe state.
4. SR-IOV paths such as `amdgpu/mxgpu_nv.c` use the matching NBIO offset and shift/mask headers for PF/VF mailbox message buffers and mailbox control registers whose defaults are listed in this chunk.
5. Power-management paths for Navi10/Sienna Cichlid include the NBIO 2.3 offset and shift/mask headers when integrating PCIe/link/power behavior with SMU policy.

The defaults do not encode the order for reset, SR-IOV handshakes, mailbox ACK/valid transitions, HDP flush polling, doorbell aperture setup, BACO exit, power-gating, or MSI-X programming. Those rules live in the driver code and hardware documentation.

## State And Persistence Behavior

This chunk stores no software state. It describes hardware reset/default state for NBIO 2.3 registers.

State represented here includes:

- VF PCIe configuration space defaults for identity, BARs, PCIe capabilities, MSI/MSI-X capability tables, AER status/mask/severity/log registers, ATS, and ARI.
- Shadow config and system-hub portal defaults used to access or mirror configuration registers.
- BIOS/SBIOS scratch and GFX MMIO remap/CAM defaults, which can be used by firmware, boot, or driver handoff paths.
- Strap-derived state for device/function identity, revision/device IDs, link capability, and endpoint behavior.
- Endpoint and downstream PCIe control state for LTR, DPA, PME, error control, RX control, link speed, and bus/config controls.
- RCC/BIF state for memory sizing, doorbell aperture enablement, peer access, host bus numbering, XDMA addresses, link control, reset enables, BACO exit timing, framebuffer access, pending transactions, and HDP flush remap addresses.
- PF/VF mailbox message buffer and control defaults used by SR-IOV virtualization protocol paths.
- Doorbell range defaults for SDMA, IH, MMSCH, and ACV engines, plus self-ring doorbell aperture defaults.
- GDC bridge and power/clock gating defaults.
- MSI-X vector table defaults for graphics interrupt delivery.

Persistence is hardware-defined. Configuration defaults are reset baselines and may be overwritten by firmware, PCI enumeration, SR-IOV setup, AMDGPU initialization, runtime power management, suspend/resume restore, BACO transitions, GPU reset, or guest/host virtualization flows. Status and log registers may be read-only, sticky, write-one-to-clear, self-clearing, or undefined while their clock/power domains are gated; this default header does not describe those access semantics.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 header set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` supplies the matching addresses for every register named here. For example, `cfgBIF_CFG_DEV0_EPF0_VF28_1_*` starts at base address `0xfffe1031c000`, the RCC/BIF/GDC groups sit under `0x30300000`, and GFX MSI-X vector registers start at `0x30342000`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h` supplies bitfield layouts used to modify the same registers safely.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` directly includes this default header and uses the sibling headers for NBIO operations such as HDP remapping, memory-controller access gating, doorbell ranges, doorbell self-ring aperture programming, interrupt setup, clock gating, PCIe link handling, and revision/memsize reads.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` integrates with PF/VF mailbox registers from the same NBIO 2.3 register map for SR-IOV host/guest messaging.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include NBIO 2.3 offset and shift/mask headers for SMU/PCIe link and power-management integration.
- Display resource files include the NBIO 2.3 offset header where display code needs SOC15 register addresses for NBIO-adjacent resources.

The most important integration surfaces from this chunk are PCIe enumeration and capabilities, SR-IOV VF config spaces, doorbell aperture/range setup, PF/VF mailbox protocol, HDP flush/coherency plumbing, BACO/reset/power transitions, and graphics MSI-X interrupt delivery.

## Risks And Edge Cases

- Generated default drift can be subtle. A wrong `_DEFAULT` value can compile cleanly while misleading reset comparison logic, documentation, or bring-up assumptions.
- The VF PCIe config blocks are highly repetitive. A single VF instance can diverge from neighboring VFs without obvious compile-time failures, causing one SR-IOV virtual function to expose different capabilities, AER defaults, MSI capability defaults, ATS pointers, or BAR/reset behavior.
- The chunk starts mid-block for VF27 and ends at the file footer. Whole-file reconciliation must merge the previous chunk before treating the VF27 PCIe config block as complete.
- PCIe capability list and enhanced capability pointer defaults are topology-sensitive. Incorrect values such as `CAP_PTR`, PCIe capability headers, AER capability list entries, or ATS/ARI entries can break host PCI enumeration or hide capabilities from guest VFs.
- MSI/MSI-X defaults are interrupt-sensitive. Incorrect MSI message-control defaults or MSI-X vector-control defaults can cause masked interrupts, unexpected interrupt enablement, or host/guest interrupt routing failures.
- Strap and reset-enable defaults are silicon- and board-sensitive. Hand-editing `cfgRCC_*_STRAP*`, `cfgRCC_RESET_EN_DEFAULT`, or `cfgBX_RESET_EN_DEFAULT` risks mismatching firmware straps, ASIC revisions, and board wiring.
- Doorbell range and self-ring aperture defaults interact with engine submission paths. Wrong range defaults, size fields, or aperture defaults can make SDMA/IH/VCN/MMSCH/ACV doorbells inaccessible or overlap another engine's doorbell window.
- PF/VF mailbox registers are protocol-sensitive. Incorrect defaults or offsets around message buffers, valid/ACK control, and mailbox interrupts can lead to SR-IOV timeouts or failed host/guest state transitions.
- HDP flush and coherency defaults are ordering-sensitive. Bad flush remap defaults or coherency defaults can produce stale CPU/GPU memory visibility, especially around KFD, VM, and interrupt handling.
- BACO, power-gating, clock-gating, and pad-control defaults can affect low-power transitions and resume reliability. Values that work at cold boot may still be wrong across BACO exit, suspend/resume, or GPU reset.
- Default headers do not carry read/write semantics. Some named registers are status, clear, sticky, strap, reserved, or firmware-owned; software should not infer writability from the presence of a `_DEFAULT` macro.

## Test Signals

Useful validation combines generated-header checks with hardware and driver behavior:

- Build AMDGPU with NBIO 2.3 support enabled. Missing or renamed macros should be caught by `amdgpu/nbio_v2_3.c` and related users of the sibling offset/shift-mask headers.
- Mechanically compare this range against the authoritative AMD NBIO 2.3 register database and against `nbio_2_3_offset.h` to confirm that every `_DEFAULT` macro has a matching offset macro where expected.
- Run PCI enumeration checks on Navi10-family NBIO 2.3 hardware and SR-IOV VFs, verifying VF28-VF30 capability list layout, MSI/MSI-X visibility, AER/ATS/ARI capability presence, BAR defaults, and class/device identity.
- Exercise SR-IOV mailbox flows in `mxgpu_nv.c`: guest init/fini/reset access requests, mailbox ACK/valid polling, RAS request/response paths, timeout handling, and unrecoverable-state notification.
- Validate doorbell setup for SDMA, IH, VCN/MMSCH, and ACV paths by checking ring submission, interrupt delivery, and no overlap in allocated doorbell ranges.
- Validate HDP flush and coherency behavior through KFD/AMDGPU memory-visibility tests, especially after remapping `REMAP_HDP_MEM_FLUSH_CNTL` and `REMAP_HDP_REG_FLUSH_CNTL`.
- Test BACO, suspend/resume, GPU reset, PCIe link retraining, and clock/power-gating transitions while watching for link errors, mailbox timeouts, stuck pending-transaction bits, and lost interrupts.
- Confirm MSI/MSI-X behavior by checking interrupt allocation, vector masking/unmasking, graphics interrupt delivery, and PBA behavior on bare metal and under virtualization.
- Monitor kernel logs for AER reports, PCI config-space read failures, SR-IOV VF access failures, doorbell faults, HDP flush timeouts, BACO exit failures, and resume-only PCIe/link regressions.

## Cross-Chunk Notes

Lines 17882-17903 are only the tail of the VF27 PCIe config default block; earlier VF27 identity, BAR, link, and MSI defaults are in the previous chunk. Lines 18502-18519 complete the final generated register block, and line 18521 closes the header guard. The merge lane should stitch this final chunk with the preceding chunks before making file-level claims about all NBIO 2.3 default registers or all SR-IOV VF instances.
