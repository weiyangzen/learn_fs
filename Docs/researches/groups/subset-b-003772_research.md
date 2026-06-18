# subset-b-003772 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_guc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_guc_regs.h

## Purpose

`xe_guc_regs.h` is the Xe driver's GuC/HuC MMIO register contract. It names GuC boot/status registers, WOPCM and DMA programming registers, soft-scratch windows, doorbell registers, GuC interrupt masks/vectors, VF-visible host interrupt registers, and the hardware doorbell cacheline format used by GuC submission and SR-IOV code.

## Important APIs, Types, and Definitions

- GuC boot/authentication definitions: `GUC_STATUS`, `BOOT_HASH_CHK`, `GUC_HEADER_INFO`, `GS_AUTH_STATUS_*`, `GS_BOOTROM_*`, and `GUC_BOOT_UKERNEL_VALID`.
- WOPCM/DMA programming definitions: `GUC_WOPCM_SIZE`, `DMA_ADDR_*`, `DMA_COPY_SIZE`, `DMA_CTRL`, `DMA_GUC_WOPCM_OFFSET`, and the WOPCM/GGTT address-space field values.
- Doorbell definitions: `DIST_DBS_POPULATED`, `DRBREGL()`, `DRBREGU()`, `DRB_VALID`, `GT_DOORBELL_ENABLE`, `GUC_NUM_DOORBELLS`, and `struct guc_doorbell_info`.
- Interrupt definitions: `GUC_SEND_INTERRUPT`, `GUC_INTR_CHICKEN`, `GUC_*_IER`, `GUC_INTR_*`, `GUC_HOST_INTERRUPT`, `MED_GUC_HOST_INTERRUPT`, and VF software flag ranges.
- TLB invalidation definitions: `GUC_TLB_INV_CR`, `PVC_GUC_TLB_INV_DESC0`, and `PVC_GUC_TLB_INV_DESC1`.

## Control Flow

This header has no executable control flow. Its macros are consumed by GuC firmware loading, HuC loading, submission, interrupt, TLB invalidation, relay/SR-IOV, and doorbell management code. The call flow is indirect: production code builds `struct xe_reg` constants through `XE_REG()`, then passes those constants to Xe MMIO helpers for read/write or poll loops.

## State and Persistence Behavior

The header defines persistent hardware state rather than software-owned state. Doorbell register validity, GuC boot/auth fields, WOPCM lock bits, interrupt enable bits, DMA control, scratch registers, and VF-visible flags persist in MMIO until firmware, reset, or driver reprogramming changes them. `struct guc_doorbell_info` is a packed shared-memory layout with status/cookie fields monitored by hardware.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h` for `XE_REG()` and on Linux bitfield helpers. It integrates with GuC firmware upload/authentication, HuC load verification, GuC CT and submission code, interrupt setup, SR-IOV PF/VF communication paths, and tests such as PF GT resource partitioning that rely on `GUC_NUM_DOORBELLS`.

## Risks and Edge Cases

- Register offsets and bit encodings are silent ABI with hardware and firmware; a wrong value usually becomes a boot, interrupt, or submission failure rather than a compile error.
- `GUC_TLB_INV_CR` is defined twice in this file with the same address and bit; this is benign if identical but creates drift risk if one copy is edited later.
- VF-accessible registers must retain `XE_REG_OPTION_VF` tags where VF paths use generic MMIO validation.
- `struct guc_doorbell_info` is packed and fixed-size; adding fields or changing alignment would break hardware-monitored cacheline semantics.

## Test Signals

Compile coverage catches missing macros but not semantic offset errors. Useful signals include GuC firmware boot/auth success, HuC load success, interrupt delivery from GuC to host, doorbell allocation/activation tests, SR-IOV PF resource tests for doorbell counts, and TLB invalidation completion on platforms using the PVC descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_guc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_hw_error_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_hw_error_regs.h

## Purpose

`xe_hw_error_regs.h` defines MMIO addresses and bit fields for Xe hardware error reporting, including GT correctable/nonfatal/fatal status, device-level error status, PVC GT error vectors, and PVC SoC global/local error registers.

## Important APIs, Types, and Definitions

- HEC firmware error registers: `HEC_UNCORR_ERR_STATUS(base)`, `UNCORR_FW_REPORTED_ERR`, and `HEC_UNCORR_FW_ERR_DW0(base)`.
- GT error status: `ERR_STAT_GT_COR`, `ERR_STAT_GT_NONFATAL`, `ERR_STAT_GT_FATAL`, `ERR_STAT_GT_REG(x)`, and bit masks for EU, SLM, GuC, and FPU errors.
- Device status: `DEV_ERR_STAT_REG(x)` and bit positions `XE_CSC_ERROR`, `XE_SOC_ERROR`, `XE_GT_ERROR`.
- Vector registers: `ERR_STAT_GT_FATAL_VECTOR_REG(x)`, `ERR_STAT_GT_COR_VECTOR_REG(x)`, and `ERR_STAT_GT_VECTOR_REG(hw_err, x)`.
- SoC error helpers: PVC master/slave bases, global event control, global status, local correctable/uncorrectable status, and IEH bits.

## Control Flow

There is no local execution. Consumers select a register with `_PICK_EVEN()`-based helpers for correctable versus nonfatal/fatal lanes, then read, decode, clear, or log error state according to the hardware error class being handled.

## State and Persistence Behavior

The represented state is hardware-latched error status. Bits may persist until explicitly cleared or until reset, depending on the underlying register semantics. Vector registers expose per-unit causes that downstream error code can map to GT or SoC subcomponents.

## Dependencies and Integration Points

The file expects `XE_REG`, `_PICK_EVEN`, and `REG_BIT`/`REG_GENMASK` helpers from adjacent Xe register infrastructure and DRM Intel bit helpers. It integrates with hardware error detection, error interrupt handlers, PVC-specific RAS handling, and diagnostics that classify correctable versus fatal events.

## Risks and Edge Cases

- `ERR_STAT_GT_VECTOR_REG()` depends on the `HARDWARE_ERROR_CORRECTABLE` enum value being visible and stable at use sites.
- `_PICK_EVEN()` helpers assume `x` is a 0/1-like selector; unexpected values can select unintended offsets.
- Error-status registers are high-impact diagnostics; incorrect masks can hide fatal hardware events or report false positives.

## Test Signals

Build tests should cover all hardware-error users. Unit tests can validate selector macros produce the expected addresses. Integration signals are correct interrupt classification, accurate logs for injected or firmware-reported errors, and no regressions on PVC RAS flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_hw_error_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_i2c_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_i2c_regs.h

## Purpose

`xe_i2c_regs.h` defines SoC-relative register offsets for the Xe I2C bridge, its PCI config-space aperture, memory-space aperture, SG remap address registers, and bridge interrupt/power-management control.

## Important APIs, Types, and Definitions

- Address bases: `I2C_BRIDGE_OFFSET`, `I2C_CONFIG_SPACE_OFFSET`, and `I2C_MEM_SPACE_OFFSET`, all based on `SOC_BASE`.
- Remapper registers: `REG_SG_REMAP_ADDR_PREFIX` and `REG_SG_REMAP_ADDR_POSTFIX`.
- Bridge/config registers: `I2C_BRIDGE_PCICFGCTL`, `ACPI_INTR_EN`, `I2C_CONFIG_CMD`, and `I2C_CONFIG_PMCSR`.

## Control Flow

This header has no local control flow. I2C bridge code uses the offsets to configure PCI command and PMCSR state, enable ACPI interrupts, and program remap state before accessing bridge memory/config spaces.

## State and Persistence Behavior

The state is SoC/bridge MMIO and PCI-config shadow state. Configuration persists until the device or bridge is reset, suspended, or reconfigured. Remap prefix/postfix state affects how subsequent accesses are routed.

## Dependencies and Integration Points

It depends on `<linux/pci_regs.h>` for PCI config offsets, `xe_reg_defs.h` for register construction, and `xe_regs.h` for `SOC_BASE`. It integrates with Xe display/I2C bridge bring-up and platform-specific SoC remapping paths.

## Risks and Edge Cases

- The file mixes SoC MMIO offsets and PCI config offsets; consumers must use the correct access path.
- `SOC_BASE` drift affects all derived addresses.
- Incorrect remap programming can make later I2C accesses target the wrong region.

## Test Signals

Useful signals include successful I2C bridge enumeration, PCI command/PMCSR programming, ACPI interrupt enable behavior, and platform display/I2C probing on SoCs using these bridge windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_i2c_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_irq_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_irq_regs.h

## Purpose

`xe_irq_regs.h` names the Xe interrupt control/status register block: master interrupt registers, GT interrupt dwords, per-engine interrupt enables/masks, identity registers, and special interrupt bits for GuC, GSC, display, I2C, SoC, and PXP/KCR events.

## Important APIs, Types, and Definitions

- Master interrupt registers: `DG1_MSTR_TILE_INTR`, `GFX_MSTR_IRQ`, and bits such as `MASTER_IRQ`, `GU_MISC_IRQ`, `DISPLAY_IRQ`, `SOC_H2DMEMINT_IRQ`, `I2C_IRQ`, and `GT_DW_IRQ(x)`.
- GT interrupt dwords: `GT_INTR_DW(x)` with engine and GuC/GSC bit helpers.
- Enable/mask registers: `RENDER_COPY_INTR_ENABLE`, `VCS_VECS_INTR_ENABLE`, `GUC_SG_INTR_ENABLE`, `GUNIT_GSC_INTR_ENABLE`, and engine mask registers.
- Identity decoding: `INTR_IDENTITY_REG(x)`, `INTR_DATA_VALID`, `INTR_ENGINE_INSTANCE()`, `INTR_ENGINE_CLASS()`, and `INTR_ENGINE_INTR()`.
- PXP/KCR interrupt bits: `KCR_PXP_STATE_TERMINATED_INTERRUPT`, `KCR_APP_TERMINATED_PER_FW_REQ_INTERRUPT`, and `KCR_PXP_STATE_RESET_COMPLETE_INTERRUPT`.

## Control Flow

This header only defines register contracts. Interrupt setup code writes enable/mask registers, top-half handlers read master/GT/identity registers, decode pending sources, and dispatch to GuC, engine, display, GSC, I2C, error, or PXP handlers.

## State and Persistence Behavior

Interrupt mask/enable bits persist in hardware until reprogrammed or reset. Identity registers expose transient pending interrupt records and include a valid bit plus class/instance/source fields. VF-tagged registers are accessible to virtual functions only on supported interface versions; comments note newer VF paths can move to memory-based interrupts.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h`. It integrates with Xe IRQ install/uninstall, engine interrupt routing, GuC/GSC communication, SR-IOV VF interrupt handling, display and I2C event routing, and PXP state handling.

## Risks and Edge Cases

- VF-accessibility comments encode version-dependent behavior; preserving `XE_REG_OPTION_VF` may be correct for legacy VFs but consumers must gate newer memory-based interrupt paths separately.
- Bit helper macros such as `INTR_BCS(x)` and `INTR_VECS(x)` assume valid engine indices.
- Incorrect masks can lose interrupts, leave sources storming, or route PXP/GSC events to the wrong handler.

## Test Signals

Signals include interrupt smoke tests, GuC event delivery, engine user/context-switch interrupts, PXP reset/termination events, SR-IOV VF interrupt paths, and no spurious interrupt storms during suspend/resume and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_irq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_lrc_layout.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_lrc_layout.h

## Purpose

`xe_lrc_layout.h` defines dword indexes inside Xe logical ring context (LRC) state and indirect context state images. It lets context setup and save/restore code address ring head/tail/start/control, context-control, timestamp, PDP, ASID, interrupt reporting, and indirect ring fields by symbolic offset.

## Important APIs, Types, and Definitions

- Main context fields: `CTX_CONTEXT_CONTROL`, `CTX_RING_HEAD`, `CTX_RING_TAIL`, `CTX_RING_START`, `CTX_RING_CTL`, `CTX_BB_PER_CTX_PTR`, `CTX_CS_INDIRECT_CTX`, `CTX_TIMESTAMP`, `CTX_ASID`, and `CTX_PDP0_*`.
- Interrupt report fields: `CTX_LRM_INT_MASK_ENABLE`, `CTX_INT_MASK_ENABLE_*`, `CTX_LRI_INT_REPORT_PTR`, `CTX_INT_STATUS_REPORT_*`, `CTX_INT_SRC_REPORT_*`, and `CTX_CS_INT_VEC_*`.
- Indirect context fields: `INDIRECT_CTX_RING_HEAD`, `INDIRECT_CTX_RING_TAIL`, `INDIRECT_CTX_RING_START`, `INDIRECT_CTX_RING_START_UDW`, and `INDIRECT_CTX_RING_CTL`.

## Control Flow

The file is pure layout metadata. Context image builders and context-restore code index into arrays of dwords using these constants when emitting LRI/LRM-style state or initializing indirect contexts.

## State and Persistence Behavior

The represented state lives in GPU context images persisted in memory and restored by hardware when contexts run. Incorrect indexes can corrupt context state across submissions or resets.

## Dependencies and Integration Points

There are no includes. The constants integrate with LRC allocation/init, engine submission, context switch save/restore, and interrupt-reporting context programming.

## Risks and Edge Cases

- Offsets include `+ 1` adjustments that reflect hardware context image conventions; removing or duplicating the adjustment would shift all state writes.
- There is no type checking on the dword array being indexed.
- Context layout varies by hardware generation; consumers must ensure these offsets match the context image they are programming.

## Test Signals

Signals include successful context creation, ring head/tail tracking, indirect context execution, interrupt reporting from contexts, and no context corruption after preemption, reset, or migration between engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_lrc_layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_mchbar_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_mchbar_regs.h

## Purpose

`xe_mchbar_regs.h` defines the Xe driver's mirrored MCHBAR power/thermal register addresses and field masks for package SKU power limits, unit conversion, energy status, package temperature, and RAPL limits.

## Important APIs, Types, and Definitions

- Base: `MCHBAR_MIRROR_BASE_SNB`.
- Power SKU: `PCU_CR_PACKAGE_POWER_SKU` with `PKG_TDP`, `PKG_MIN_PWR`, `PKG_MAX_PWR`, and window fields.
- Units/status: `PCU_CR_PACKAGE_POWER_SKU_UNIT`, `PKG_PWR_UNIT`, `PKG_ENERGY_UNIT`, `PKG_TIME_UNIT`, and `PCU_CR_PACKAGE_ENERGY_STATUS`.
- Thermal/RAPL: `PCU_CR_PACKAGE_TEMPERATURE`, `TEMP_MASK`, `PCU_CR_PACKAGE_RAPL_LIMIT`, `PWR_LIM_*`.

## Control Flow

No executable control flow is present. Power telemetry or management code reads these registers and applies bit masks to convert hardware units into driver-visible power, energy, time, and temperature values.

## State and Persistence Behavior

The hardware state represents package power limits, energy counters, temperature, and unit encodings. Energy counters are monotonically changing hardware counters; limit registers persist until firmware/driver/platform policy changes them.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h` and Linux/DRM bit helpers. It integrates with power management, telemetry, RAPL exposure, and platform diagnostics that use the MCHBAR mirror instead of directly mapping the host bridge MCHBAR.

## Risks and Edge Cases

- Unit fields must be applied correctly or telemetry values will be scaled incorrectly.
- Counter rollover must be handled by consumers, not this header.
- These addresses are mirror-specific; using them on platforms without the mirror or with different layout would produce invalid readings.

## Test Signals

Signals include plausible package temperature/energy readings, correct RAPL unit conversion, and no MMIO faults or zeroed telemetry on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_mchbar_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_mert_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_mert_regs.h

## Purpose

`xe_mert_regs.h` defines MERT-related registers for local memory configuration, TLB command translation interrupt error reporting, CATERR VF/code fields, and MERT TLB invalidation descriptors.

## Important APIs, Types, and Definitions

- `MERT_LMEM_CFG` for local memory configuration.
- `MERT_TLB_CT_INTR_ERR_ID_PORT` with `CATERR_VFID`, `CATERR_CODES`, `CATERR_NO_ERROR`, `CATERR_UNMAPPED_GGTT`, and `CATERR_LMTT_FAULT`.
- `MERT_TLB_INV_DESC_A` with `MERT_TLB_INV_DESC_A_VALID`.

## Control Flow

The header provides register constants only. MERT/LMTT/SR-IOV code reads error ID/code state after TLB command translation failures and programs invalidation descriptors when invalidating remapped translation state.

## State and Persistence Behavior

The registers expose hardware translation and error state. CATERR fields persist as reported hardware error information until cleared by the appropriate flow. Invalidation descriptor validity is transient command state.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h`. It integrates with local memory remapping, SR-IOV VF translation, LMTT fault handling, and MERT TLB invalidation flows.

## Risks and Edge Cases

- CATERR field decoding is meaningful only when an error is present.
- VFID extraction is security-sensitive in SR-IOV diagnostics; wrong masks can attribute faults to the wrong VF.
- Invalidation descriptor validity must be synchronized with the hardware invalidation protocol.

## Test Signals

Signals include LMTT fault injection/diagnostics, correct VF attribution for translation errors, successful MERT TLB invalidation, and clean behavior for `CATERR_NO_ERROR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_mert_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_oa_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_oa_regs.h

## Purpose

`xe_oa_regs.h` defines observability/performance counter registers for OA/OAR/OAG/OAC/OAM/OAMERT units, EU performance counters, OA buffer pointers, OA control/debug/status bits, media GT adjusted bases, and OA-related TLB invalidation.

## Important APIs, Types, and Definitions

- Global/EU controls: `RPM_CONFIG1`, `GT_NOA_ENABLE`, and `EU_PERF_CNTL*`.
- OAR/OAG controls: `OAR_OACONTROL`, `OACTXCONTROL(base)`, `OAG_OAGLBCTXCTRL`, `OAG_OAHEADPTR`, `OAG_OATAILPTR`, `OAG_OABUFFER`, `OAG_OACONTROL`, and `OAG_OA_DEBUG`.
- Common bits: counter enable/select masks, buffer pointer masks, memory-select bit, report/counter-size bits, overflow/lost-report status bits.
- OAM helpers: offset constants plus `OAM_HEAD_POINTER(base)`, `OAM_TAIL_POINTER(base)`, `OAM_BUFFER(base)`, `OAM_CONTROL(base)`, `OAM_DEBUG(base)`, and `OAM_STATUS(base)`.
- Media and MERT bases: `XE_OAM_*_BASE_ADJ` and `OAMERT_*` registers.

## Control Flow

The header has no local control flow. OA/perf code uses it to program counter selection, enable timers, set/report buffer head/tail pointers, configure debug behavior, trigger MMIO reports, and poll/clear overflow or lost-report conditions.

## State and Persistence Behavior

OA control/debug registers persist while a perf stream is configured. Head/tail pointers and status bits are runtime producer/consumer state. Buffer-overflow and report-lost bits are diagnostic state that must be handled carefully by perf stream code.

## Dependencies and Integration Points

It relies on `XE_REG`, `REG_BIT`, and `REG_GENMASK` through included register infrastructure at use sites. It integrates with Xe OA/perf, metrics set programming, media GT performance streams, and MERT/OAM telemetry on newer platforms.

## Risks and Edge Cases

- Multiple OA units have similar but not identical control layouts; mixing OAG/OAM/OAMERT helpers can program the wrong block.
- `OAG_OA_DEBUG` is marked masked, so consumers should use masked-register write semantics.
- Head/tail pointer masks imply alignment; unaligned buffer positions can be truncated.
- Overflow/lost-report status must be surfaced to userspace to avoid silently corrupting performance data.

## Test Signals

Signals include OA stream open/close, counter enable/disable, report generation, MMIO trigger behavior, overflow/lost-report handling, media GT OA streams, and metrics validation against known workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_oa_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pcode_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pcode_regs.h

## Purpose

`xe_pcode_regs.h` defines PCODE-visible GT MMIO registers for PVC power/energy telemetry and BMG fan/VRAM/package temperature telemetry.

## Important APIs, Types, and Definitions

- PVC telemetry: `PVC_GT0_PACKAGE_ENERGY_STATUS`, `PVC_GT0_PACKAGE_RAPL_LIMIT`, `PVC_GT0_PACKAGE_POWER_SKU_UNIT`, `PVC_GT0_PLATFORM_ENERGY_STATUS`, and `PVC_GT0_PACKAGE_POWER_SKU`.
- BMG telemetry: `BMG_FAN_1_SPEED`, `BMG_FAN_2_SPEED`, `BMG_FAN_3_SPEED`, `BMG_VRAM_TEMPERATURE_N(n)`, `BMG_VRAM_TEMPERATURE`, and `BMG_PACKAGE_TEMPERATURE`.
- Temperature fields: `TEMP_MASK_VRAM_N` and `TEMP_SIGN_MASK`.

## Control Flow

No executable logic exists. Consumers read the registers and decode fields to report package/platform energy, power limits, fan speeds, and temperatures.

## State and Persistence Behavior

The hardware state is telemetry and policy state. Energy values are changing counters, fan speed/temperature values are live sensor readings, and RAPL limits persist as platform policy state.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h` and integrates with Xe hwmon, power telemetry, PVC/BMG platform support, and diagnostics.

## Risks and Edge Cases

- Temperature sign/mask handling must be done by consumers; incorrect sign extension can produce invalid readings.
- `BMG_VRAM_TEMPERATURE_N(n)` uses `sizeof(u32)` as stride, tying the macro to C type width.
- Platform-specific registers must be gated by platform checks.

## Test Signals

Signals include plausible hwmon readings, sensor enumeration on BMG, PVC energy counter movement under load, and correct behavior when optional fans/VRAM sensors are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pcode_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pmt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pmt.h

## Purpose

`xe_pmt.h` defines BMG PMT discovery and telemetry offsets, including package/card energy fields, module and G-state residencies, and PCIe link residency counters.

## Important APIs, Types, and Definitions

- Base offsets: `BMG_PMT_BASE_OFFSET`, `BMG_DISCOVERY_OFFSET`, `BMG_TELEMETRY_BASE_OFFSET`, and `BMG_TELEMETRY_OFFSET`.
- Discovery/energy: `PUNIT_TELEMETRY_GUID`, `BMG_ENERGY_STATUS_PMT_OFFSET`, `ENERGY_PKG`, and `ENERGY_CARD`.
- Residency offsets: `BMG_MODS_RESIDENCY_OFFSET`, `BMG_G2_RESIDENCY_OFFSET`, `BMG_G6_RESIDENCY_OFFSET`, `BMG_G7_RESIDENCY_OFFSET`, `BMG_G8_RESIDENCY_OFFSET`, `BMG_G10_RESIDENCY_OFFSET`, and PCIe L0/L1/L1.2 offsets.

## Control Flow

No local control flow is present. PMT/telemetry code uses the constants to locate PMT discovery data and read 64-bit telemetry fields at the specified offsets.

## State and Persistence Behavior

The represented state is live telemetry exposed through a PMT aperture. Energy and residency counters change over time and may roll over; consumers own sampling and delta calculation.

## Dependencies and Integration Points

It includes `xe_regs.h` for `SOC_BASE` and `XE_REG`. It integrates with BMG telemetry/hwmon and power-management diagnostics.

## Risks and Edge Cases

- Offsets are BMG-specific and must be platform-gated.
- `ENERGY_PKG`/`ENERGY_CARD` are 64-bit masks over a combined telemetry value; consumers must use 64-bit reads and fields.
- Counter rollover and units are not described in this header.

## Test Signals

Signals include PMT GUID discovery, nonzero or changing energy counters under load, residency counter movement across power states, and correct PCIe residency reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pxp_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pxp_regs.h

## Purpose

`xe_pxp_regs.h` defines protected Xe Path (PXP) KCR registers that are valid on platforms with a media GT, including KCR initialization, session-in-play status, and global session termination.

## Important APIs, Types, and Definitions

- `KCR_INIT` and `KCR_INIT_ALLOW_DISPLAY_ME_WRITES` for KCR/display ME write enable.
- `KCR_SIP` for hardware DRM session-in-play status.
- `KCR_GLOBAL_TERMINATE` for global PXP session termination.

## Control Flow

The file is a register contract. PXP code programs KCR init state, reads session status, and writes global termination during protected content lifecycle and reset handling.

## State and Persistence Behavior

KCR state is hardware security/session state. Session-in-play bits persist while protected sessions exist, and global termination is a command-like write that affects active sessions.

## Dependencies and Integration Points

It includes `regs/xe_regs.h` and integrates with PXP, KCR interrupt handling from `xe_irq_regs.h`, media GT initialization, and display/protected-content flows.

## Risks and Edge Cases

- Registers are only valid on media-GT platforms; ungated use can access invalid MMIO.
- Global termination is high impact and must not be issued accidentally.
- Session status races with firmware or interrupt-driven state transitions.

## Test Signals

Signals include PXP initialization on media GT systems, KCR interrupt delivery, session status transitions, global termination recovery, and no access attempts on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pxp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_reg_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_reg_defs.h

## Purpose

`xe_reg_defs.h` defines the typed register representation used across the Xe driver. It wraps MMIO offsets plus access metadata in `struct xe_reg`, provides `struct xe_reg_mcr` for multicast/replicated registers, and supplies `XE_REG()`, `XE_REG_MCR()`, and related options.

## Important APIs, Types, and Definitions

- `XE_REG_ADDR_MAX` sets the encoded register offset limit to 4 MiB.
- `struct xe_reg` stores `addr`, `masked`, `mcr`, and `vf` fields in a 32-bit union with a `raw` representation.
- `struct xe_reg_mcr` wraps a `struct xe_reg` to enforce MCR-specific APIs by type.
- Options: `XE_REG_OPTION_MASKED` and `XE_REG_OPTION_VF`.
- Constructors: `XE_REG_INITIALIZER`, `XE_REG`, and `XE_REG_MCR`.
- `xe_reg_is_valid()` treats address zero as invalid.

## Control Flow

Only `xe_reg_is_valid()` has local executable logic. Other definitions are compile-time initializers that produce typed register constants for MMIO helpers, save/restore tables, RTP workarounds, tests, and validation code.

## State and Persistence Behavior

The file defines software metadata, not hardware state. The metadata persists in constants and tables and controls access behavior: masked write handling, MCR routing, and VF-access validation.

## Dependencies and Integration Points

It depends on DRM Intel `pick.h` and `reg_bits.h`, plus Linux build/log2/size helpers. It is foundational to nearly every Xe register header, MMIO path, workaround table, RTP tests, save/restore state, and SR-IOV VF register access checks.

## Risks and Edge Cases

- Address bit width is derived from `XE_REG_ADDR_MAX`; increasing the supported MMIO range requires validating bitfield packing and static assertions.
- Address zero is invalid by convention, so a real register at offset zero cannot be represented as valid by `xe_reg_is_valid()`.
- `XE_REG_MCR()` sets `.mcr = 1`; using `XE_REG()` for an MCR register can route access through the wrong path.
- Masked-register semantics require consumers to respect upper-16-bit write masks.

## Test Signals

`xe_rtp_test.c` exercises regular, masked, and MCR register metadata interactions. Compile coverage checks the 32-bit layout. Useful additional tests include constructor raw-value checks, invalid-zero behavior, VF option propagation, and MCR type separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_reg_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_regs.h

## Purpose

`xe_regs.h` defines miscellaneous top-level Xe and SoC registers used by initialization, force-reset, stolen memory discovery, frequency capability discovery, tile range discovery, and VF capability probing.

## Important APIs, Types, and Definitions

- `SOC_BASE` for SoC-relative register headers.
- Global control/debug: `GU_CNTL_PROTECTED`, `DRIVERINT_FLR_DIS`, `GU_CNTL`, `LMEM_INIT`, `DRIVERFLR`, `GU_DEBUG`, and `DRIVERFLR_STATUS`.
- Tile/memory discovery: `XEHP_MTCFG_ADDR`, `TILE_COUNT`, `GGC`, `GMS_MASK`, `GGMS_MASK`, `DSMBASE`, `BDSM_MASK`, `GSMBASE`, `STOLEN_RESERVED`, and `WOPCM_SIZE_MASK`.
- Tile address and frequency registers: `SG_TILE_ADDR_RANGE(_idx)`, `MTL_*_FREQUENCY`, `MTL_*_STATE_CAP`, `PVC_RP_STATE_CAP`.
- Virtualization: `VIRTUAL_CTRL_REG`, `GUEST_GTT_UPDATE_EN`, `VF_CAP_REG`, and `VF_CAP`.

## Control Flow

There is no executable code. Initialization and reset code reads or writes these registers to discover platform layout, control FLR, initialize local memory, read frequency caps, and determine VF capability.

## State and Persistence Behavior

The registers expose persistent hardware configuration and control state. FLR and LMEM bits are command/control bits, while memory base and capability registers describe platform configuration.

## Dependencies and Integration Points

It includes `regs/xe_reg_defs.h`. It is used by platform bring-up, memory/stolen-memory setup, tile enumeration, power/frequency code, SR-IOV/VF setup, and SoC-specific headers that derive offsets from `SOC_BASE`.

## Risks and Edge Cases

- `SOC_BASE` is reused by multiple headers; changing it has broad address impact.
- FLR control/status bits must be sequenced with reset code and interrupt masking.
- Field masks using 64-bit values require consumers to read the appropriate register width.

## Test Signals

Signals include correct tile count detection, local-memory initialization, stolen memory sizing, VF capability detection, frequency reporting, and reset/FLR recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_soc_remapper_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_soc_remapper_regs.h

## Purpose

`xe_soc_remapper_regs.h` defines a SoC remapper index register and masks for telemetry and system-control remap selections.

## Important APIs, Types, and Definitions

- `SG_REMAP_INDEX1` at `SOC_BASE + 0x08`.
- `SG_REMAP_TELEM_MASK` for telemetry remap selection.
- `SG_REMAP_SYSCTRL_MASK` for system-control remap selection.

## Control Flow

The file has no executable flow. SoC remapper code writes or reads the index register to select remapped telemetry and system-control regions before using related MMIO windows.

## State and Persistence Behavior

The remapper index is persistent hardware routing state until changed or reset. It affects where subsequent SoC-aperture accesses land.

## Dependencies and Integration Points

It includes `xe_regs.h` for `SOC_BASE` and integrates with SoC telemetry, PMT, I2C, and system-control remapping code.

## Risks and Edge Cases

- Incorrect index fields can route accesses to the wrong SoC target.
- Callers must serialize remapper changes if multiple subsystems share the same window.
- Platform gating is required for SoCs without this remapper layout.

## Test Signals

Signals include successful telemetry/system-control access after remap programming and no cross-subsystem corruption when remap users run concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_soc_remapper_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/Makefile

## Purpose

The Xe tests `Makefile` wires KUnit test objects into the kernel build when `CONFIG_DRM_XE_KUNIT_TEST` is enabled. It separates live hardware tests from normal unit tests.

## Important APIs, Types, and Definitions

- `obj-$(CONFIG_DRM_XE_KUNIT_TEST) += xe_live_test.o` and `xe_test.o`.
- `xe_live_test-y = xe_live_test_mod.o`.
- `xe_test-y` includes `xe_test_mod.o`, `xe_args_test.o`, `xe_pci_test.o`, `xe_rtp_test.o`, and `xe_wa_test.o`.

## Control Flow

Build-system control flow is controlled by Kconfig. When enabled, Kbuild links the listed object lists into test modules/objects; live tests then register suites from `xe_live_test_mod.c`, and normal tests register through individual test translation units.

## State and Persistence Behavior

There is no runtime state. The persistent effect is build composition: which test suites are included in the generated modules.

## Dependencies and Integration Points

It integrates with Kbuild, `CONFIG_DRM_XE_KUNIT_TEST`, `xe_test_mod.c`, `xe_live_test_mod.c`, and all listed KUnit sources. Some tests in this research set are not listed here because they may be included through other objects or conditional build paths in the wider tree.

## Risks and Edge Cases

- Missing a source from the object list makes its suite unreachable even if it compiles standalone.
- Live tests are hardware-dependent and should remain separated from pure unit tests.
- Build list drift can make test coverage appear present in source while not actually linked.

## Test Signals

Signals are successful `CONFIG_DRM_XE_KUNIT_TEST` builds, KUnit suite discovery for `args`, `xe_pci`, `xe_rtp`, `xe_wa`, and live suite module discovery for `xe_bo`, `xe_dma_buf`, `xe_migrate`, `xe_mocs`, and `xe_guc_g2g`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_args_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_args_test.c

## Purpose

`xe_args_test.c` is a KUnit suite for the variadic macro utilities in `xe_args.h`. It verifies argument counting, forced macro expansion, first/last/nth argument selection, dropping the first argument, optional-argument selection, and comma separator generation.

## Important APIs, Types, and Functions

- Example tests: `call_args_example`, `drop_first_arg_example`, `first_arg_example`, `last_arg_example`, `pick_arg_example`, `if_args_example`, and `sep_comma_example`.
- Functional tests: `count_args_test`, `call_args_test`, `drop_first_arg_test`, `first_arg_test`, `last_arg_test`, and `if_args_test`.
- Test suite: `args_test_suite` named `args`.

## Control Flow

Each test defines local macros and then asserts both computed C values and stringified macro expansions. The suite uses normal KUnit registration via `kunit_test_suite(args_test_suite)`.

## State and Persistence Behavior

The file has no persistent runtime state. State is preprocessor state local to each test through `#define`/`#undef` blocks. It intentionally tests cases where macro parameters are or are not expanded before counting.

## Dependencies and Integration Points

It depends on KUnit and `xe_args.h`. It guards macro behavior used by Xe metaprogramming, especially RTP/workaround definitions and future users that need optional variadic macro behavior.

## Risks and Edge Cases

- Macro behavior depends on compiler support for `__VA_OPT__` or the fallback path in `xe_args.h`.
- `COUNT_ARGS`/`PICK_ARG` only support up to 12 arguments.
- Preprocessor tests can pass value checks while stringification exposes expansion drift, so both forms matter.

## Test Signals

The suite itself is the primary signal. It should pass on both Clang and supported GCC versions, including fallback optional-argument paths where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_args_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_bo.c

## Purpose

`xe_bo.c` contains live KUnit tests for Xe buffer-object behavior: flat-CCS migration preservation/clearing, global VRAM eviction and restoration, and TTM shrinker/swap behavior for system BOs.

## Important APIs, Types, and Functions

- CCS migration path: `ccs_test_migrate`, `ccs_test_run_tile`, `ccs_test_run_device`, and `xe_ccs_migrate_kunit`.
- Eviction path: `evict_test_run_tile`, `evict_test_run_device`, and `xe_bo_evict_kunit`.
- Shrinker path: `struct xe_bo_link`, `shrink_test_fill_random`, `shrink_test_verify`, `shrink_test_run_device`, and `xe_bo_shrink_kunit`.
- Suites: exported `xe_bo_test_suite` and `xe_bo_shrink_test_suite`.

## Control Flow

The CCS test creates a user BO, validates it into VRAM where applicable, optionally clears data and CCS via `xe_migrate_clear`, evicts it to system memory with `xe_bo_evict`, waits on reservation fences, maps the TTM backing pages, checks first/last CCS values, and writes values for the next round. It skips unsupported flat-CCS or Xe2+ discrete cases as needed.

The eviction test creates VM-backed and external BOs, pins the external BO, calls `xe_bo_evict_all`, sanitizes and resets GTs, restores kernel and user BOs, then checks that pinned external BOs remain in VRAM while normal BOs are evicted. The shrinker test allocates roughly twice free RAM in 64 MiB system BOs, marks some purgeable when swap is insufficient, fills non-purgeable BOs with deterministic PRNG data, validates/readbacks under shrink pressure, and reports interrupted/successful readbacks.

## State and Persistence Behavior

The tests mutate live device memory placement, BO TTM resources, reservation fences, VM state, GT reset state, purgeable accounting, and runtime PM state. BO data and CCS metadata are expected to persist correctly across migration, eviction, restore, and shrinker pressure unless intentionally purgeable.

## Dependencies and Integration Points

It depends on live Xe devices from `xe_pci_live_device_gen_param`, KUnit helpers for runtime PM, BO creation/locking/validation, `xe_bo_evict`, `xe_bo_restore_early/late`, migration clear, GT reset/sanitize, TTM swap/shrinker behavior, PRNG helpers, and sysinfo/swap accounting.

## Risks and Edge Cases

- These are live tests and can be slow or disruptive, especially shrinker and GT reset flows.
- Shrinker coverage depends on available RAM/swap and skips large-memory systems to avoid excessive runtime.
- CCS validation inspects only first and last values in the first CCS page, so middle-page corruption can escape.
- Eviction test comments call out CTB/ADS snapshot risk and compensates with GT reset; failures can indicate fragile restore ordering.

## Test Signals

Passing live suites indicate CCS metadata survives migration, clears correctly, pinned external BOs resist eviction, user BOs restore from eviction, and non-purgeable system BO contents survive shrink pressure. Timeouts, wrong placement, PRNG mismatch, or restore errors are strong regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_dma_buf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_dma_buf.c

## Purpose

`xe_dma_buf.c` is a live KUnit suite for Xe dma-buf export/import behavior. It verifies same-driver imports across combinations of VRAM/system residency, P2P capability, dynamic attachment support, and fake different-device behavior.

## Important APIs, Types, and Functions

- Capability helpers: `p2p_enabled()` and `is_dynamic()`.
- Placement validator: `check_residency()`.
- Main scenario: `xe_test_dmabuf_import_same_driver()`.
- Test parameter table: `test_params` with memory masks, attach ops, and `force_different_devices`.
- Runner/suite: `dma_buf_run_device`, `xe_dma_buf_kunit`, and exported `xe_dma_buf_test_suite`.

## Control Flow

For each live device and parameter set, the test creates a BO with the requested memory mask, exports it with `xe_gem_prime_export`, imports it with `xe_gem_prime_import`, validates the imported BO, checks expected success/failure depending on P2P and dynamic attachment capabilities, evicts exporter state, revalidates importer state, and optionally pins/unpins the dma-buf attachment.

## State and Persistence Behavior

The test mutates BO residency, dma-buf attachment lists, GEM dma-buf backpointers, TTM placement, exporter/importer object references, and runtime PM state. Dynamic attachments are expected to propagate eviction invalidation from exporter to importer.

## Dependencies and Integration Points

It depends on live-device parameter generation, Xe BO/GEM prime export/import, dma-buf attachment ops (`xe_dma_buf_attach_ops` and a no-P2P variant), TTM memory managers, runtime PM, and test-private tagging through `XE_TEST_LIVE_DMA_BUF`.

## Risks and Edge Cases

- P2P behavior is conditional on `CONFIG_PCI_P2PDMA`; expected outcomes change with config.
- Fake different-device behavior avoids same-object import shortcuts and is important for cross-device paths.
- Non-dynamic attachments can reject VRAM pinning without system fallback.
- The test tolerates interrupt-related validation failures but treats unexpected errors as regressions.

## Test Signals

Passing signals include correct import reuse on same device, correct `-EOPNOTSUPP` or `-EINVAL` cases, expected system-memory fallback without P2P, exporter/importer residency synchronization, and successful attachment pinning without unwanted migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_dma_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_gt_sriov_pf_config_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_gt_sriov_pf_config_kunit.c

## Purpose

`xe_gt_sriov_pf_config_kunit.c` tests SR-IOV PF fair resource partitioning for GuC contexts, doorbells, GGTT, and local memory across 1 to 63 VFs.

## Important APIs, Types, and Functions

- Setup helpers: `pf_set_admin_mode`, `pf_set_usable_vram`, `num_vfs_gen_param`, and `pf_gt_config_test_init`.
- Fair-share tests: `fair_contexts_1vf`, `fair_contexts`, `fair_doorbells_1vf`, `fair_doorbells`, `fair_ggtt_1vf`, `fair_ggtt`, `fair_vram_1vf`, `fair_vram_1vf_admin_only`, and `fair_vram`.
- Parameter data: `TEST_MAX_VFS`, `TEST_VRAM`, and `vram_sizes`.
- Suite: `pf_gt_config_suite`.

## Control Flow

The init path creates a fake BMG SR-IOV PF device, attaches fake VRAM, installs LMTT ops, sets total/driver VF limits, disables admin-only mode, and calls `xe_sriov_init`. Parameterized tests toggle admin-only mode and VF counts, then assert fair-share functions return aligned, power-of-two, capacity-respecting values with specific thresholds.

## State and Persistence Behavior

The tests mutate fake device SR-IOV PF fields, admin-only state, VRAM usable size, tile VRAM pointers, and LMTT ops. No live hardware state is touched.

## Dependencies and Integration Points

It depends on KUnit static/fake device helpers, `xe_sriov_init`, PF profile functions (`pf_profile_fair_ctxs`, `pf_profile_fair_dbs`, `pf_profile_fair_ggtt`, `pf_profile_fair_lmem`), GuC ID/doorbell limits, LMTT ops, and VRAM region helpers.

## Risks and Edge Cases

- Threshold expectations encode policy; intentional resource policy changes require updating tests.
- `TEST_VRAM` is chosen to work on 32-bit but may not represent all real device sizes.
- The fake device must remain close enough to real PF initialization for profile results to be meaningful.

## Test Signals

Passing tests indicate fair shares remain aligned, power-of-two, and within available contexts/doorbells/GGTT/VRAM. Admin-only single-VF cases verify reserved PF resources are accounted differently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_gt_sriov_pf_config_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_buf_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_buf_kunit.c

## Purpose

`xe_guc_buf_kunit.c` tests the GuC buffer cache allocator: reservation sizing, uniqueness, non-overlap, reuse, bounds failure, CPU-to-BO flush, pointer-to-GPU-address lookup, data initialization, and cleanup-class behavior.

## Important APIs, Types, and Functions

- Static replacement: `replacement_xe_managed_bo_create_pin_map()` creates a fake BO and optional GGTT node.
- Setup: `guc_buf_test_init()` initializes fake device, GGTT, static stub, and `xe_guc_buf_cache_init`.
- Tests: `test_smallest`, `test_largest`, `test_granular`, `test_unique`, `test_overlap`, `test_reusable`, `test_too_big`, `test_flush`, `test_lookup`, `test_data`, and `test_class`.
- Suite: `guc_buf_suite`.

## Control Flow

Initialization builds a fake PF device, initializes a bounded fake GGTT range, replaces managed BO allocation, and creates the GuC buffer cache. Tests reserve buffers of different sizes, inspect CPU pointers and GGTT addresses, release buffers, validate address ranges and non-overlap, copy data into reserved buffers and flush to the backing BO map, and use the cleanup-class wrapper for automatic release.

## State and Persistence Behavior

The cache owns a fake BO/suballocator, GGTT node state, and reservation/free state. Released ranges are expected to be reusable. Flushed data persists in the backing BO vmap.

## Dependencies and Integration Points

It depends on KUnit static stubs, fake Xe device setup, GGTT KUnit initialization, GuC CT/buffer APIs, managed BO creation, `iosys_map`, and cleanup-class support.

## Risks and Edge Cases

- The fake BO path bypasses real memory-management behavior; this is allocator/API coverage, not full hardware coverage.
- Pointer arithmetic tests assume reserved CPU ranges can be compared directly.
- The too-big case ensures invalid buffers are safe to release, guarding cleanup paths.

## Test Signals

Passing tests indicate correct allocation granularity, no overlapping CPU/GPU ranges, stable reuse, flush propagation, lookup bounds, copied data initialization, and cleanup-class release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_buf_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_db_mgr_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_db_mgr_test.c

## Purpose

`xe_guc_db_mgr_test.c` tests the GuC doorbell manager's bitmap/range allocator across empty, default, sized, reuse, overlap, compaction, and spare-at-end scenarios.

## Important APIs, Types, and Functions

- Setup: `guc_dbm_test_init()` creates a fake device and selects `guc.dbm`.
- Tests: `test_empty`, `test_default`, `test_size`, `test_reuse`, `test_range_overlap`, `test_range_compact`, and `test_range_spare`.
- Parameterization: `guc_dbm_params` over fractions/full `GUC_NUM_DOORBELLS`.
- Suite: `guc_dbm_suite`.

## Control Flow

Initialization prepares the fake device and doorbell-manager mutex. Tests call `xe_guc_db_mgr_init` with different counts, reserve IDs under lock, reserve/release ranges, and assert exhaustion, reuse ordering, non-overlap, divisibility-based compaction, and spare-region constraints.

## State and Persistence Behavior

The tested state is the manager's doorbell count, allocation bitmap, and mutex-protected reservation state. Releases must make IDs/ranges available again.

## Dependencies and Integration Points

It depends on fake Xe device setup, GuC doorbell manager internals, `GUC_NUM_DOORBELLS` from `xe_guc_regs.h`, and KUnit parameter generation.

## Risks and Edge Cases

- Tests lock around ID reserve/release but range APIs manage their own locking; mismatched locking assumptions can hide races not modeled here.
- Exhaustion and spare tests guard off-by-one errors near the end of the doorbell space.
- `~0` means default max and relies on production init semantics.

## Test Signals

Passing tests indicate correct empty/default sizing, full exhaustion behavior, immediate reuse of released IDs, non-overlapping range allocation, compact packing, and correct rejection of oversized/spare reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_db_mgr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_g2g_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_g2g_test.c

## Purpose

`xe_guc_g2g_test.c` is a live KUnit suite for GuC-to-GuC (G2G) communication across GTs. It verifies message routing, payload integrity, sequence ordering, default driver CTB allocation, and alternate CTB placement in host or tile-local memory.

## Important APIs, Types, and Functions

- Payload and routing helpers: `struct g2g_test_payload`, `slot_index_from_gts`, `g2g_test_send`, and exported `xe_guc_g2g_test_notification`.
- Test loop: `g2g_test_in_order`, `g2g_wait_for_complete`, `g2g_run_test`, and `g2g_clean_array`.
- CTB lifecycle: `g2g_ct_stop`, `g2g_ctb_size`, `g2g_alloc_default`, `g2g_alloc_host`, `g2g_alloc_tile`, `g2g_distribute`, `g2g_free`, `g2g_stop`, and `g2g_reinit`.
- Flat CTB indexing/registering: `g2g_slot_flat`, `g2g_register_flat`, and `g2g_start`.
- Test entry points: `xe_live_guc_g2g_kunit_default` and `xe_live_guc_g2g_kunit_allmem`.

## Control Flow

The notification handler validates async G2H notification length, payload length, source/destination tile/device IDs, finds the transmitting GT, computes a slot index, checks the sequence number, updates the per-pair sequence array, and decrements an outstanding-message counter.

The main test allocates a `gt_count * gt_count` sequence array, sends increasing sequence numbers from every GT to every other GT, waits for each prior sequence before queueing the next message on the same route, waits for all notifications, and finally checks that identity slots remain zero and all cross-GT slots reached the final sequence. The all-memory test stops/recreates CTBs, runs the same traffic through default, host-backed, and per-tile local-memory CTB placements, then restores the original default CTBs through a KUnit cleanup action.

## State and Persistence Behavior

The test mutates live GuC G2G CTB registration state, `guc->g2g.bo` ownership/reference state, GGTT mappings, device `g2g_test_array`, and atomic outstanding notification counts. Runtime PM references and CTB recreation are registered as cleanup actions to restore the device.

## Dependencies and Integration Points

It depends on live Xe devices, GuC CT send APIs, GuC G2G registration/deregistration actions, managed BO pin/map, GGTT addresses, runtime PM, GuC firmware build type, and the production `xe_guc_g2g_wanted` policy. It only runs when there are at least two GTs and the firmware exposes the test interface.

## Risks and Edge Cases

- The notification handler cannot use aborting KUnit assertions because it runs asynchronously from the G2H notification path; failures must be logged and returned.
- The all-memory test deliberately recreates CTBs and can leave G2G communication broken if cleanup fails.
- Sequence waiting uses polling and bounded sleeps; overloaded systems or firmware latency can cause false timeouts.
- The flat slot-index math is duplicated from driver logic to force coverage of alternate placement schemes; drift between test and driver is both a risk and a signal that tests must be updated.

## Test Signals

Passing default tests show production G2G CTBs can route messages between GTs. Passing all-memory tests show host and local-memory CTB placements are reachable from all participating GuCs. Failures in payload IDs, sequence numbers, outstanding count, registration, or CTB cleanup are strong regressions in G2G transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_g2g_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_id_mgr_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_id_mgr_test.c

## Purpose

`xe_guc_id_mgr_test.c` tests the GuC ID manager allocation lifecycle, invalid initialization, uninitialized behavior, used-count accounting, quota enforcement, and full-space allocation/release.

## Important APIs, Types, and Functions

- Setup: `guc_id_mgr_test_init()` creates a fake device and selects `guc.submission_state.idm`.
- Tests: `bad_init`, `no_init`, `init_fini`, `check_used`, `check_quota`, and slow `check_all`.
- Suite: `guc_id_mgr_suite`.

## Control Flow

The init path prepares the manager mutex. Tests call `xe_guc_id_mgr_init` with invalid and valid totals, reserve IDs through locked and public APIs, exercise internal chunk reserve/release helpers, check `used` updates after each operation, and call `__fini_idm` to confirm teardown resets bitmap and total.

## State and Persistence Behavior

The manager owns a bitmap, total ID count, used count, and mutex-protected allocation state. Initialization allocates bitmap state; teardown frees and resets it.

## Dependencies and Integration Points

It depends on fake Xe device setup, GuC submission state, `GUC_ID_MAX`, internal ID manager helpers, and KUnit.

## Risks and Edge Cases

- The tests use internal helpers, so refactors of manager internals will need test updates.
- Quota checks cover several over-quota shapes and guard against off-by-one errors.
- `check_all` is slow because it walks the full ID space.

## Test Signals

Passing tests indicate correct init/fini behavior, correct error codes for bad/uninitialized use, accurate used counts, quota rejection, and full-space allocation/release coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_id_mgr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_relay_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_relay_test.c

## Purpose

`xe_guc_relay_test.c` tests SR-IOV GuC relay message validation and transaction handling for PF, VF, and not-ready paths, including optional debug test-loop behavior.

## Important APIs, Types, and Functions

- Setup/stubs: `replacement_relay_get_totalvfs`, `relay_test_init`, send/recv replacement stubs, and loopback send/recv stub.
- PF tests: malformed GUC2PF messages, bad payload origin/type, transaction error propagation, PF2GUC send formatting, and loopback NOP/ECHO/FAIL/BUSY/RETRY.
- VF tests: malformed GUC2VF length/no-payload handling.
- Not-ready tests: drops for GUC2PF/GUC2VF and send rejection before relay init.
- Suites: `pf_relay_suite`, `vf_relay_suite`, and `no_relay_suite`.

## Control Flow

Initialization builds a fake SR-IOV PF device, initializes SR-IOV and relay state, stubs VF count, and sets a deterministic relay ID. Tests feed crafted HXG/relay messages into `xe_guc_relay_process_guc2pf`, `xe_guc_relay_process_guc2vf`, `relay_process_msg`, or send APIs. Static stubs check outgoing CT messages or loop requests back through the opposite relay processing function. Debug loop tests skip unless `CONFIG_DRM_XE_DEBUG_SRIOV` is enabled.

## State and Persistence Behavior

The relay stores readiness state, last relay ID, transaction state, and fake VF count. Tests use KUnit static stubs to replace CT send/recv and worker kicking, and cleanup is handled by KUnit.

## Dependencies and Integration Points

It depends on fake Xe device setup, SR-IOV initialization, GuC HXG message fields, relay internals, GuC CT send/recv, KUnit static stubs, and optional debug SR-IOV config.

## Risks and Edge Cases

- Message length and payload validation are protocol-critical; off-by-one errors can create malformed relay handling.
- Static stubs validate formatting but do not exercise real GuC CT transport except through integration tests.
- Loopback debug action availability depends on build config.
- Transaction cleanup must release allocated transaction objects after error paths.

## Test Signals

Passing tests indicate correct error codes for malformed messages, correct PF2GUC relay request formatting, CT error propagation, not-ready rejection, and debug loop handling for success, echo, remote failure, busy, and retry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_relay_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.c

## Purpose

`xe_kunit_helpers.c` provides reusable helpers to allocate fake Xe DRM devices for unit tests and prepare live Xe devices for live KUnit suites.

## Important APIs, Types, and Functions

- `xe_kunit_helper_alloc_xe_device()` allocates a `struct xe_device` embedded in a KUnit DRM device.
- `xe_kunit_helper_xe_device_test_init()` allocates a fake parent device, allocates an Xe device, initializes it through `xe_pci_fake_device_init`, restores prior `test->priv` through a KUnit action, and stores the fake device in `test->priv`.
- `xe_kunit_helper_xe_device_live_test_init()` obtains a live device from `test->param_value`, checks it is not wedged, takes runtime PM, registers a runtime-PM put action, and stores it in `test->priv`.

## Control Flow

Fake init allocates resources with KUnit-managed helpers, initializes fake PCI/platform data, registers a cleanup action to restore original private data, and returns zero or aborts through KUnit assertions. Live init uses the parameterized device pointer, resumes runtime PM, registers cleanup, and returns zero.

## State and Persistence Behavior

Fake-device state is KUnit-managed and freed with the test. The helper temporarily overwrites `test->priv` and restores it through an action. Live helper holds a runtime PM reference for the test duration and releases it through a KUnit action.

## Dependencies and Integration Points

It depends on DRM KUnit helpers, `xe_pci_fake_device_init`, Xe PM runtime APIs, and KUnit visibility exports. It is used by most Xe unit and live KUnit suites in this group.

## Risks and Edge Cases

- Tests that rely on incoming `test->priv` fake data must call the helper before overwriting it themselves.
- Live tests abort if the device is wedged, so failure can mean environment/device state rather than test logic.
- Missing cleanup actions would leak runtime PM references or leave `test->priv` altered.

## Test Signals

Signals include fake device initialization success, correct parameterized live device binding, runtime PM get/put balance, and stable use by dependent suites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.h

## Purpose

`xe_kunit_helpers.h` declares the shared Xe KUnit helper API for fake and live device setup.

## Important APIs, Types, and Functions

- Forward declarations for `struct device`, `struct kunit`, and `struct xe_device`.
- `xe_kunit_helper_alloc_xe_device(struct kunit *test, struct device *dev)`.
- `xe_kunit_helper_xe_device_test_init(struct kunit *test)`.
- `xe_kunit_helper_xe_device_live_test_init(struct kunit *test)`.

## Control Flow

There is no executable logic in the header. Test suites include it and assign the init helpers to KUnit suite `.init` callbacks or call allocation directly.

## State and Persistence Behavior

No state is stored here. The declared functions manage KUnit device state and runtime PM in the implementation.

## Dependencies and Integration Points

It provides the public test helper contract for Xe KUnit files, avoiding direct dependence on implementation details in each suite.

## Risks and Edge Cases

- Prototype drift will break many test suites.
- The header intentionally uses forward declarations to keep includes light; implementation-specific types must not leak into it unnecessarily.

## Test Signals

Successful compilation of all dependent KUnit suites is the main signal; runtime signals come from fake/live initialization in `xe_kunit_helpers.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_live_test_mod.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_live_test_mod.c

## Purpose

`xe_live_test_mod.c` is the module glue that registers live Xe KUnit suites requiring real hardware or live driver devices.

## Important APIs, Types, and Functions

- External suite declarations: `xe_bo_test_suite`, `xe_bo_shrink_test_suite`, `xe_dma_buf_test_suite`, `xe_migrate_test_suite`, `xe_mocs_test_suite`, and `xe_guc_g2g_test_suite`.
- `kunit_test_suite(...)` registrations for each live suite.
- Module metadata and `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.

## Control Flow

When the live test module is loaded, KUnit sees the registered suites and runs their parameterized live-device tests according to KUnit selection.

## State and Persistence Behavior

The file owns no test state. It affects module-level suite registration and imports the namespace needed to access exported-for-KUnit symbols.

## Dependencies and Integration Points

It depends on the live suites being linked/exported and on KUnit/module infrastructure. It is built through the tests `Makefile` as `xe_live_test.o`.

## Risks and Edge Cases

- Missing externs or suite exports cause link failures.
- Registering live suites in the wrong module can make hardware-affecting tests run unexpectedly.
- Suite discovery depends on this file staying aligned with live test sources.

## Test Signals

Signals include module load success, KUnit discovery of all live suites, and no missing namespace/link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_live_test_mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_lmtt_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_lmtt_test.c

## Purpose

`xe_lmtt_test.c` tests the LMTT operations tables for two-level and multi-level local-memory translation table implementations.

## Important APIs, Types, and Functions

- Parameter table: `lmtt_ops_params` with `lmtt_2l_ops` and `lmtt_ml_ops`.
- Descriptor: `lmtt_ops_param_get_desc`.
- Main test: `test_ops`.
- Suite: `lmtt_suite`.

## Control Flow

For each ops table, `test_ops` asserts required callbacks are present, root page-directory level is nonzero, each level has nonzero PTE count/size and non-invalid encoded PTEs, and lower levels produce expected index transitions around shift-size boundaries.

## State and Persistence Behavior

No persistent runtime state is mutated. The test only calls pure ops callbacks and checks returned values.

## Dependencies and Integration Points

It depends on LMTT ops definitions being visible in the KUnit compilation unit and KUnit parameter generation. It guards SR-IOV local-memory mapping code that relies on these ops.

## Risks and Edge Cases

- Tests validate generic invariants, not every address or encoding.
- A semantically wrong but nonzero callback result could still pass unless it violates boundary index checks.
- New LMTT ops variants must be added to the parameter table.

## Test Signals

Passing tests show both ops tables are complete, produce usable encoded entries, and calculate PTE indexes correctly at key boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_lmtt_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_migrate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_migrate.c

## Purpose

`xe_migrate.c` is a live KUnit suite for migration engine behavior. It validates page-table update jobs, buffer clear/copy operations across system/VRAM regions, and flat-CCS preservation/clear semantics on Xe2 discrete devices.

## Important APIs, Types, and Functions

- Sanity helpers: `sanity_fence_failed`, `run_sanity_job`, `test_copy`, `test_copy_sysmem`, `test_copy_vram`, and `xe_migrate_sanity_test`.
- Device runner: `migrate_test_run_device` and `xe_migrate_sanity_kunit`.
- BLT/CCS helpers: `blt_copy`, `test_migrate`, `test_clear`, `validate_ccs_test_run_tile`, `validate_ccs_test_run_device`, and `xe_validate_ccs_kunit`.
- Suite: exported `xe_migrate_test_suite`.

## Control Flow

The sanity test maps migration page tables, creates big/tiny BOs, emits PTE updates into a batch buffer, submits migration jobs, verifies PTE writes, clears mapped memory, and then clears/copies small and big BOs to system memory or other VRAM. The CCS validation path creates pinned system, VRAM, and CCS BOs, uses custom BLT copy jobs to compress/decompress or copy CCS only, evicts/restores VRAM BOs, and checks first/last values and CCS zeroing.

## State and Persistence Behavior

The tests mutate live migration queues, batch buffers, page-table BOs, BO vmap contents, TTM resources, migration fences, `m->fence`, job mutex state, and runtime PM. They expect data and CCS metadata to persist or clear according to migration operations.

## Dependencies and Integration Points

It depends on Xe migration internals, batch-buffer helpers, scheduler jobs, VM/page-table encoding, BO creation/validation/vmap, resource cursors, BLT emit helpers, flat-CCS helpers, runtime PM, and live device enumeration.

## Risks and Edge Cases

- The test reaches into internal migration emit helpers and job sequencing, so refactors can require synchronized test updates.
- Fence timeout failures may reflect hardware hangs, scheduling delays, or test bugs.
- CCS validation is platform-gated; non-flat-CCS or non-Xe2 discrete systems skip important paths.
- `blt_copy` updates `m->fence` and must maintain synchronization on error paths.

## Test Signals

Passing tests indicate migration PTE updates execute, clear/copy jobs complete, first/last data values are correct, cross-memory transfers work, compressed VRAM data decompresses correctly, CCS-only copies report expected zeroes, and BO eviction/restore preserves data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_mocs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_mocs.c

## Purpose

`xe_mocs.c` is a live KUnit suite that verifies Memory Object Control State (MOCS) and L3 cache-control register programming against the platform table, both before and after GT reset.

## Important APIs, Types, and Functions

- `struct live_mocs` wraps `struct xe_mocs_info`.
- Setup/read helpers: `live_mocs_init`, `read_l3cc_table`, and `read_mocs_table`.
- Tests: `mocs_kernel_test_run_device`, `xe_live_mocs_kernel_kunit`, `mocs_reset_test_run_device`, and `xe_live_mocs_reset_kunit`.
- Suite: exported `xe_mocs_test_suite`.

## Control Flow

For each GT on a live device, the test computes expected MOCS settings with `get_mocs_settings`, takes forcewake, reads either MCR or regular MOCS/L3CC registers, compares each entry against table-derived expected values, optionally resets the GT, and repeats the reads. It skips SR-IOV VFs.

## State and Persistence Behavior

The test reads live GT register state and triggers GT reset in the reset case. It relies on forcewake references and runtime PM guards. Expected MOCS state should persist or be restored across reset.

## Dependencies and Integration Points

It depends on live device helpers, MOCS table helpers, forcewake, MMIO/MCR reads, GT reset, runtime PM, and platform MOCS definitions.

## Risks and Edge Cases

- GT reset is disruptive and may interact with other live workloads.
- MCR versus regular register paths must match platform register layout.
- The test checks programmed register values, not performance behavior of cache policies.

## Test Signals

Passing tests show initial MOCS/L3CC programming matches tables and reset reinitialization restores the same values. Failures identify incorrect table entries, MCR routing, forcewake, or reset restore logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_mocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci.c

## Purpose

`xe_pci.c` provides fake PCI/platform data generation, parameter descriptions, IP and PCI ID parameter generators, fake Xe device initialization, and live Xe device iteration for KUnit tests.

## Important APIs, Types, and Functions

- Fake platform data: `cases`, `xe_pci_fake_data_gen_params`, and `xe_pci_fake_data_desc`.
- Lookup/description helpers for platform, subplatform, step, SR-IOV mode, graphics IP, and media IP.
- IP/PCI generators: `xe_pci_graphics_ip_gen_param`, `xe_pci_media_ip_gen_param`, and `xe_pci_id_gen_param`.
- Fake init stubs: `fake_read_gmdid`, `fake_xe_info_probe_tile_count`, and `xe_pci_fake_device_init`.
- Live generator: `xe_pci_live_device_gen_param`.

## Control Flow

Fake initialization chooses a PCI ID descriptor matching requested fake data, validates subplatform, installs static stubs for GMDID reads and tile-count probing, initializes early and full Xe info, and sets requested SR-IOV mode. Parameter generators iterate static arrays, bridge pre-GMDID and GMDID IP lists, and stop before sentinel PCI IDs.

## State and Persistence Behavior

Fake init mutates a test-owned `struct xe_device` info and SR-IOV mode fields and uses KUnit static stubs tied to the test. Live iteration takes and releases device references through `driver_find_next_device`/`put_device`.

## Dependencies and Integration Points

It depends on KUnit visibility/static stubs, Xe PCI ID tables, platform/subplatform descriptors, GMDID/IP tables, SR-IOV mode strings, step conversion helpers, and `xe_info_init_early`/`xe_info_init`. It is foundational for most fake and live tests.

## Risks and Edge Cases

- Fake data must remain representative of real platform descriptors or unit tests can pass with unrealistic devices.
- `test->priv` is used both as input fake data and later as device pointer; helper ordering matters.
- Live device iteration depends on the global Xe PCI driver and real device availability.

## Test Signals

Signals include fake init success for all listed platforms/subplatforms, meaningful KUnit parameter names, correct GMDID/step injection, PCI ID generator coverage, and live test enumeration on systems with Xe devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.c

## Purpose

`xe_pci_test.c` is a KUnit suite that validates Xe graphics/media IP descriptors and PCI platform descriptors for basic consistency.

## Important APIs, Types, and Functions

- `check_graphics_ip()` validates graphics engine masks and fuse-register availability.
- `check_media_ip()` validates media engine masks.
- `check_platform_desc()` validates descriptor bounds such as DMA mask, GT count, VA bits, and VM levels.
- Suite: `xe_pci_test_suite`.

## Control Flow

Parameterized KUnit cases iterate graphics IPs, media IPs, and PCI IDs using generators from `xe_pci.c`. Each test extracts the descriptor and asserts masks only contain allowed engine classes and platform descriptor numeric fields are nonzero/in-range.

## State and Persistence Behavior

The suite is read-only over static descriptor tables and has no persistent runtime state.

## Dependencies and Integration Points

It depends on `xe_pci_test.h`, IP/PCI parameter generators, Xe platform descriptors, and hardware engine mask definitions. It provides low-cost guard coverage for descriptor table edits.

## Risks and Edge Cases

- These checks are structural, not exhaustive; invalid but structurally plausible descriptors can pass.
- Adding a new engine class requires updating allowed masks.
- Descriptor generator coverage depends on `xe_pci.c` arrays and PCI ID tables.

## Test Signals

Passing tests indicate descriptor fields are present and engine masks remain in expected graphics/media domains. Failures usually point to descriptor table drift or missing platform metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.h

## Purpose

`xe_pci_test.h` declares the fake PCI data structure and KUnit parameter/helper functions shared by Xe PCI-related tests and fake device setup.

## Important APIs, Types, and Functions

- `struct xe_pci_fake_data` with SR-IOV mode, platform, subplatform, step info, graphics version, and media version.
- Fake initialization: `xe_pci_fake_device_init`.
- Parameter helpers: `xe_pci_fake_data_gen_params`, `xe_pci_fake_data_desc`, `xe_pci_graphics_ip_gen_param`, `xe_pci_media_ip_gen_param`, `xe_pci_id_gen_param`, and `xe_pci_live_device_gen_param`.

## Control Flow

There is no executable code. Test suites include this header to request fake devices or parameterized live/static descriptor iteration.

## State and Persistence Behavior

The header stores no state. `struct xe_pci_fake_data` instances are passed through `test->priv` or parameter values to drive fake device initialization.

## Dependencies and Integration Points

It includes Linux types, KUnit, platform type headers, SR-IOV types, and step types. It is used by fake KUnit helpers, PCI descriptor tests, WA/RTP tests, SR-IOV tests, and live test parameterization.

## Risks and Edge Cases

- The fake data structure is a cross-test contract; adding platform dimensions requires coordinated updates in initializers and descriptors.
- Function prototypes must stay exported when used across test modules.

## Test Signals

Compile coverage across all dependent tests is the main signal. Runtime signals come from successful fake device creation and live device parameter iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_rtp_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_rtp_test.c

## Purpose

`xe_rtp_test.c` tests Xe RTP rule processing and conversion to save/restore register entries. It covers rule matching, OR semantics, active tracking, action coalescing, field set/clear handling, duplicate/conflict detection, and regular versus MCR/masked register conflicts.

## Important APIs, Types, and Functions

- Test case types: `struct rtp_to_sr_test_case` and `struct rtp_test_case`.
- Match callbacks: `match_yes` and `match_no`.
- Case arrays: `rtp_to_sr_cases` and `rtp_cases`.
- Test functions: `xe_rtp_process_to_sr_tests` and `xe_rtp_process_tests`.
- Init/exit: `xe_rtp_test_init` and `xe_rtp_test_exit`.
- Suite: `xe_rtp_test_suite`.

## Control Flow

Initialization builds an empty fake Xe device. For RTP-to-SR cases, the test initializes a register save/restore table, enables active tracking, calls `xe_rtp_process_to_sr`, iterates the xarray of SR entries, and compares active bitmap, entry count, set/clear bits, register raw value, and error count. For pure RTP cases, the test calls `xe_rtp_process` and checks the active bitmap for named and OR-combined rule groups.

## State and Persistence Behavior

The test mutates a fake GT's `reg_sr` xarray and error count and local active bitmaps. KUnit exit frees the DRM helper device. No live hardware is touched.

## Dependencies and Integration Points

It depends on fake device helpers, `xe_reg_defs.h`, RTP macros, register save/restore infrastructure, xarray iteration, and KUnit parameter generation. It guards workaround and tuning pipelines that translate RTP entries into register programming.

## Risks and Edge Cases

- `XE_REG_MCR` is temporarily redefined to regular `XE_REG(..., .mcr = 1)` so the test can compare raw metadata; that is intentional but sensitive to macro changes.
- Active tracking uses entry count; adding entries without expected bitmap updates causes failures.
- Conflict tests encode current policy for duplicate/not-disjoint/register-type errors.

## Test Signals

Passing tests indicate RTP rules match as expected, OR syntax is validated, active tracking is correct, same-register actions coalesce safely, field masks produce expected clear/set bits, and conflicts increment SR errors without corrupting accepted entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_rtp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_sriov_pf_service_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_sriov_pf_service_kunit.c

## Purpose

`xe_sriov_pf_service_kunit.c` tests PF/VF ABI version negotiation for SR-IOV PF service setup.

## Important APIs, Types, and Functions

- Setup: `pf_service_test_init()` creates a fake Tiger Lake PF, initializes SR-IOV and PF service versions, and sanity-checks base/latest versions.
- Negotiation tests: `pf_negotiate_any`, base match/newer/next/older/previous cases, and latest match/newer/next/older/previous cases.
- Suite: `pf_service_suite`.

## Control Flow

After setup, each test calls `pf_negotiate_version` with requested major/minor values and asserts success/failure plus returned negotiated version. `ANY` selects latest. Older-than-base cases fail. Newer-than-latest requests clamp to latest. Some multi-major cases include FIXME failure branches because multi-version policy is not fully modeled yet.

## State and Persistence Behavior

The fake device stores SR-IOV PF service base/latest versions. Tests read negotiation outputs but do not mutate service state after init.

## Dependencies and Integration Points

It depends on fake Xe device setup, `xe_sriov_init`, `xe_sriov_pf_service_init`, VF2PF handshake version constants, and `pf_negotiate_version`.

## Risks and Edge Cases

- Multi-major-version support is explicitly incomplete in test expectations.
- Skip paths depend on minor/major values; coverage changes as ABI versions change.
- Negotiation policy is compatibility-critical for PF/VF interoperability.

## Test Signals

Passing tests indicate base/latest versions are defined and ordered, wildcard negotiation selects latest, compatible requests succeed, unsupported older requests fail, and newer requests clamp according to current policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_sriov_pf_service_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_test.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_test.h

## Purpose

`xe_test.h` provides conditional test-only declarations and helpers for Xe KUnit builds, including a small base private-data type used to identify test-specific `kunit->priv` payloads.

## Important APIs, Types, and Definitions

- `enum xe_test_priv_id` with `XE_TEST_LIVE_DMA_BUF` and `XE_TEST_LIVE_MIGRATE`.
- `struct xe_test_priv` containing the ID.
- Test-build macros: `XE_TEST_DECLARE(x)` and `XE_TEST_ONLY(x)`.
- `xe_cur_kunit_priv(enum xe_test_priv_id id)` returns the current KUnit private base if present and matching.
- Non-test builds compile these helpers away.

## Control Flow

In KUnit-enabled builds, `xe_cur_kunit_priv` checks for a current KUnit test, reads `test->priv`, compares the embedded ID, and returns it or NULL. In non-KUnit builds the helper always returns NULL and test-only declarations disappear.

## State and Persistence Behavior

The header does not own state. It interprets `current->kunit->priv` when a running test supplies a structure embedding `struct xe_test_priv`.

## Dependencies and Integration Points

It depends conditionally on KUnit headers and is used by production code that needs minor test-only behavior without affecting non-test builds, plus live tests that tag private data.

## Risks and Edge Cases

- `xe_cur_kunit_priv` assumes `test->priv` is non-NULL and points to an object whose first member is `struct xe_test_priv`; misuse can dereference invalid memory.
- Test-only hooks must remain compiled out of production builds.
- Adding new test private IDs requires keeping producer and consumer code synchronized.

## Test Signals

Build coverage under both KUnit and non-KUnit configs is the main signal. Runtime signals are correct test-private dispatch in dma-buf/migrate test paths without affecting production behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_test_mod.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_test_mod.c

## Purpose

`xe_test_mod.c` is minimal module metadata for the normal Xe KUnit test module.

## Important APIs, Types, and Definitions

- Module metadata: author, GPL license, description, and `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.

## Control Flow

There is no suite registration here; individual normal test sources register their own suites. Loading the module imports the namespace needed for KUnit-only exports.

## State and Persistence Behavior

No runtime state is owned by this file.

## Dependencies and Integration Points

It integrates with Kbuild's `xe_test-y` object list and Linux module metadata. It complements individual test files such as `xe_args_test.c`, `xe_pci_test.c`, `xe_rtp_test.c`, and `xe_wa_test.c`.

## Risks and Edge Cases

- Removing namespace import can break access to exported-for-KUnit symbols.
- Adding suite registration here without coordinating with individual files could duplicate registration.

## Test Signals

Signals are successful module build/load and no namespace import failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_test_mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_wa_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_wa_test.c

## Purpose

`xe_wa_test.c` tests that GT workaround and tuning RTP processing for fake platform variants produces no register save/restore errors.

## Important APIs, Types, and Functions

- Init: `xe_wa_test_init()` allocates a fake Xe device from parameterized fake PCI data and sets step information for non-GMDID platforms.
- Test: `xe_wa_gt()` initializes each GT's `reg_sr`, runs `xe_wa_process_gt` and `xe_tuning_process_gt`, and asserts zero SR errors.
- Suite: KUnit suite named `xe_wa`.

## Control Flow

For each fake platform parameter, init creates a fake DRM/Xe device. The test iterates GTs, initializes save/restore state, runs workaround and tuning processing, and fails if RTP-to-SR processing reports conflicts or invalid entries.

## State and Persistence Behavior

The fake device and each GT's register save/restore table are test-owned. The test populates `gt->reg_sr` and checks its error count. No live hardware state is touched.

## Dependencies and Integration Points

It depends on fake PCI data generation, fake Xe device init, workaround processing, tuning processing, and register save/restore infrastructure. It indirectly exercises many RTP match rules for platform/step combinations.

## Risks and Edge Cases

- The test validates internal consistency, not that every required workaround is present.
- Missing fake hw engine initialization is noted as a TODO, so engine/LRC workaround coverage is incomplete.
- Platform-step data must stay aligned with workaround rule expectations.

## Test Signals

Passing tests indicate GT workaround and tuning tables do not produce SR conflicts/errors across fake platform parameters. Failures usually identify invalid masks, duplicate/conflicting entries, or match-rule drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_wa_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_args.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_args.h

## Purpose

`xe_args.h` provides Xe-local variadic macro helpers for manipulating argument lists, with the intent to eventually move broadly useful forms to `linux/args.h`.

## Important APIs, Types, and Definitions

- `CALL_ARGS(f, args...)` expands arguments before invoking macro `f`.
- `DROP_FIRST_ARG(args...)`, `FIRST_ARG(args...)`, and `LAST_ARG(args...)`.
- `PICK_ARG(n, args...)` and specialized `PICK_ARG1` through `PICK_ARG12`.
- `IF_ARGS(then, else, ...)` selects based on whether optional arguments are present, using `__VA_OPT__` on Clang or GCC >= 10.1 and a fallback otherwise.
- `ARGS_SEP_COMMA` provides a comma token for staged macro expansion.

## Control Flow

All behavior occurs in the C preprocessor. The macros expand in stages to force or prevent argument expansion as needed. There is no runtime code.

## State and Persistence Behavior

No runtime state exists. Preprocessor definitions affect compilation of including files only.

## Dependencies and Integration Points

It includes `<linux/args.h>` for `COUNT_ARGS`, `CONCATENATE`, and related helpers. It is tested by `xe_args_test.c` and can support RTP/workaround macro definitions and other Xe compile-time metaprogramming.

## Risks and Edge Cases

- Argument-counting and picking support only up to 12 arguments.
- Fallback `IF_ARGS` behavior is compiler-version sensitive and should be maintained with tests.
- Empty-argument detection in the preprocessor is subtle; nested macro expansion changes can break callers.

## Test Signals

`xe_args_test.c` validates value and stringification behavior for all major macros, including optional arguments, nested expansion, and comma insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_assert.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_assert.h

## Purpose

`xe_assert.h` defines debug-only Xe assertion macros that emit rich DRM warnings in `CONFIG_DRM_XE_DEBUG` builds while compiling away to type/condition validation in production builds.

## Important APIs, Types, and Definitions

- Internal backend: `__xe_assert_msg`.
- Device assert: `xe_assert` and `xe_assert_msg`.
- Tile assert: `xe_tile_assert` and `xe_tile_assert_msg`.
- GT assert: `xe_gt_assert` and `xe_gt_assert_msg`.
- Production-build behavior uses `typecheck` and `BUILD_BUG_ON_INVALID` to keep expressions type-checked without runtime code.

## Control Flow

In debug builds, the macros evaluate a condition and call `drm_WARN` when it is false, adding platform, subplatform, graphics/media version, step, tile VRAM, and GT details as appropriate. In non-debug builds, they do not evaluate at runtime and cannot be used as expressions.

## State and Persistence Behavior

The macros do not store state. Debug builds can emit warning records. They read device/tile/GT metadata and VRAM size for diagnostics.

## Dependencies and Integration Points

It depends on Linux string helpers, DRM print, Xe GT/tile/device conversion helpers, step naming, and VRAM region helpers. It is used by code such as `xe_bb.c` to enforce internal invariants without production cost.

## Risks and Edge Cases

- Assert macros are not safe fallback handling; production code must still handle real error conditions.
- `xe_tile_assert_msg` reads `__tile->mem.vram`; callers must only use it where that pointer is safe for diagnostics.
- Conditions must remain side-effect-free because production builds do not execute them at runtime.

## Test Signals

Build coverage under debug and non-debug configs is important. Runtime debug signals are WARNs on violated invariants; production signals are absence of generated runtime overhead while preserving type checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb.c

## Purpose

`xe_bb.c` implements Xe batch-buffer allocation, initialization, job creation, and release on top of suballocated GPU-visible memory.

## Important APIs, Types, and Functions

- `bb_prefetch(struct xe_gt *gt)` returns platform/engine prefetch padding: 1 KiB for Xe HPG/HPC+ main GT RCS/CCS-like requirements, otherwise 512 bytes.
- `xe_bb_new()` allocates a `struct xe_bb` and suballocates pre-sized memory from the kernel or USM batch-buffer pool.
- `xe_bb_alloc()` allocates an uninitialized `struct xe_bb` with an uninitialized suballoc object.
- `xe_bb_init()` initializes a previously allocated batch buffer from a given `xe_sa_manager`.
- `__xe_bb_create_job()` appends `MI_BATCH_BUFFER_END` if missing, asserts size including prefetch, flushes writes, and creates a scheduler job.
- `xe_bb_create_migration_job()` creates a two-address migration job with batch base and second batch index.
- `xe_bb_create_job()` creates a normal one-address job.
- `xe_bb_free()` releases suballocated memory, optionally deferred by a fence, and frees the wrapper.

## Control Flow

Allocation paths allocate the wrapper first, then suballocator storage, set `cs` to the CPU address, and initialize `len` to zero. Job creation ensures a batch terminator exists, validates batch length against suballocation size plus prefetch padding through debug asserts, flushes CPU writes to the suballocated BO, and delegates to `xe_sched_job_create`. Migration jobs compute two GPU addresses for the primary and secondary batch entry points and assert the queue is a width-1 migration queue.

## State and Persistence Behavior

`struct xe_bb` owns a suballocation pointer, CPU command stream pointer, and command length in dwords. Commands persist in GPU-visible memory until the suballocation is reused. `xe_bb_free` can defer reuse until the supplied fence signals.

## Dependencies and Integration Points

It depends on MI command definitions, Xe assert macros, GT/tile/device types, execution queue types, suballocator APIs, scheduler job creation, VM/migration queue state, and DMA fences. It is used by migration tests and production command submission helpers needing small driver-generated batches.

## Risks and Edge Cases

- Callers must request enough dwords; debug asserts catch overflow but production builds rely on correct sizing.
- `xe_bb_init()` does not add prefetch padding unlike `xe_bb_new`; callers using it must account for the documented guard and hardware needs.
- Missing or misplaced `MI_BATCH_BUFFER_END` is corrected only at the current `len` position.
- Deferred free requires correct fence ownership to avoid reuse while hardware may still read the batch.

## Test Signals

Migration live tests exercise `xe_bb_new`, migration job creation, fence completion, and deferred free. Additional useful tests would cover normal job creation, size-boundary assertions in debug builds, USM versus kernel pool selection, and `xe_bb_alloc`/`xe_bb_init` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb.h

## Purpose

`xe_bb.h` declares the public batch-buffer helper API for allocation, initialization, scheduler job creation, migration job creation, and cleanup.

## Important APIs, Types, and Functions

- `xe_bb_new(struct xe_gt *gt, u32 dwords, bool usm)`.
- `xe_bb_alloc(struct xe_gt *gt)`.
- `xe_bb_init(struct xe_bb *bb, struct xe_sa_manager *bb_pool, u32 dwords)`.
- `xe_bb_create_job(struct xe_exec_queue *q, struct xe_bb *bb)`.
- `xe_bb_create_migration_job(struct xe_exec_queue *q, struct xe_bb *bb, u64 batch_ofs, u32 second_idx)`.
- `xe_bb_free(struct xe_bb *bb, struct dma_fence *fence)`.

## Control Flow

There is no executable code in the header. Consumers include it to use the implementation in `xe_bb.c`.

## State and Persistence Behavior

The header exposes operations on `struct xe_bb` from `xe_bb_types.h`; ownership and deferred-free semantics are implemented in `xe_bb.c`.

## Dependencies and Integration Points

It includes `xe_bb_types.h` and forward-declares scheduler, execution queue, GT, suballocator, and fence types. It integrates with migration, command submission, and driver-generated batch construction.

## Risks and Edge Cases

- API users must respect ownership: every successful allocation/init needs a matching `xe_bb_free`.
- Migration job users must pass a valid second batch index and migration queue.
- The header does not document all sizing constraints; implementation comments and asserts provide details.

## Test Signals

Compile coverage catches signature drift. Runtime signals come from migration tests and any driver-generated batch users completing jobs without GPU faults or suballocator reuse issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb_types.h

## Purpose

`xe_bb_types.h` defines the `struct xe_bb` data structure used by Xe batch-buffer helper APIs.

## Important APIs, Types, and Definitions

- `struct xe_bb` contains:
  - `struct drm_suballoc *bo`, the suballocated backing storage.
  - `u32 *cs`, CPU pointer to the command stream.
  - `u32 len`, current command length in dwords.

## Control Flow

There is no executable logic. The structure is initialized and consumed by `xe_bb.c` and command construction code.

## State and Persistence Behavior

The structure tracks mutable batch construction state. `len` advances as callers write commands into `cs`; `bo` owns the GPU-visible backing memory until freed.

## Dependencies and Integration Points

It depends on Linux fixed-width types and forward-declares `struct drm_suballoc`. It is included by `xe_bb.h` and all batch-buffer users.

## Risks and Edge Cases

- `len` is in dwords, while suballocation sizes and flushes are byte-oriented; callers must convert carefully.
- The structure has no capacity field, so sizing enforcement lives in allocation and debug asserts.
- Direct external mutation of `cs` and `len` is expected but requires discipline to avoid overflow or unterminated batches.

## Test Signals

Signals include successful batch construction in migration tests, correct automatic `MI_BATCH_BUFFER_END` append, and absence of out-of-bounds writes or GPU batch parse errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bb_types.h -->
