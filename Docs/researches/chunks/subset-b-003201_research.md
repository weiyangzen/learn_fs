# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 99659-102060

## Scope

This chunk is a generated AMD NBIO 7.2.0 shift/mask header segment. It contains 2,177 `#define` macros: 1,092 `__SHIFT` definitions and 1,085 `_MASK` definitions. It also contains register and address-block comments that group the macros into NBIO PCIe, I/O hub, fast-register, software-interrupt, reset, power-management, CAM, and DMA dropped-log register families.

There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range. The source path is under a `ceph-client` mirror, but this file is AMDGPU hardware register metadata and has no direct Ceph or distributed-filesystem behavior.

The range starts in the middle of `BIFP6_PCIEP_STRAP_LC`: only the final `STRAP_RTM2_PRESENCE_DET_SUPP__SHIFT` and the masks for that register are visible here. It then covers complete `BIFP6_*` PCIe strap, link-control, hot-plug, performance-counter, save/restore, and clock-gating definitions; the `nbio_pcie0_pciedir` address block; several empty/comment-only I/O-hub shadow address blocks; `FASTREG_APERTURE`; and the beginning of the NBIO misc configuration block. The range ends inside `NP_DMA_DROPPED_LOG_LOWER`, after bit 19 shift definitions and before that register's remaining shifts and masks.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield half of the NBIO 7.2.0 register interface. For each hardware register field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, preserve, clear, or update the field.

This chunk describes low-level NBIO PCIe port behavior rather than high-level software policy. The macros cover PCIe strap state, L1 PM substates, equalization and retimer controls, fine-grain clock gating, link save/restore state, PCIe transaction and bus-control knobs, last-TLP/debug capture, CCIX controls, sideband attributes, performance counters, PRBS test controls and counters, software reset commands, component power management, receive margining settings, software interrupt routing, CAM target matching, and dropped DMA transaction logs.

## Important Macro Families

The initial `BIFP6_*` portion covers PCIe port and link-control fields:

- `BIFP6_PCIEP_STRAP_MISC`, `BIFP6_PCIEP_STRAP_LC2`, and the tail of `BIFP6_PCIEP_STRAP_LC` expose strap-derived capability and policy bits such as lane reversal, E2E prefix, extended format, OBFF/LTR, CCIX, enhanced speed mode support, retimer presence support, and lane negotiation.
- `BIFP6_PCIE_LC_L1_PM_SUBSTATE` and `BIFP6_PCIE_LC_L1_PM_SUBSTATE2` define ASPM/PCI-PM L1.1/L1.2 override bits, CLKREQ filtering, common-mode restore timing, power-on scale/value, LTR threshold fields, and L1.2 exit/defer behavior.
- `BIFP6_PCIE_LC_CNTL8`, `BIFP6_PCIE_LC_CNTL9`, `BIFP6_PCIE_LC_FORCE_COEFF2`, and `BIFP6_PCIE_LC_FORCE_EQ_REQ_COEFF2` describe Gen4/16 GT equalization search mode, bypass/redo behavior, forced presets and coefficients, retimer presence override, ESM timer factors, and acceptable preset/redo controls.
- `BIFP6_PCIE_LC_FINE_GRAIN_CLK_GATE_OVERRIDES`, `BIFP6_PCIE_LC_CNTL10`, `BIFP6_PCIE_LC_CNTL11`, and `BIFP6_PCIE_LC_CNTL12` expose clock-gating overrides, ESM enablement, TX/RX frequency-ready delays, sleep/wake behavior, equalization counters, link-rate controls, and ESM transition status bits.
- `BIFP6_PCIE_LC_SAVE_RESTORE_1` through `BIFP6_PCIE_LC_SAVE_RESTORE_3` provide fields for serialized link-state save/restore data.
- `BIFP6_PCIEP_BCH_ECC_CNTL`, `BIFP6_PCIEP_HPGI_PRIVATE`, `BIFP6_PCIEP_HPGI`, `BIFP6_PCIEP_HCNT_DESCRIPTOR`, and `BIFP6_PCIEP_PERF_CNTL_COUNT_TXCLK*` cover BCH ECC enable/status, hot-plug presence-detect state/status/interrupt routing, hot-plug descriptor data, and TXCLK event counters.

The `nbio_pcie0_pciedir` address block is the largest complete block in this slice:

- `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, `PCIE_CNTL2`, `PCIE_RX_CNTL2`, `PCIE_TX_CTRL_4`, `PCIE_TX_CNTL3`, `PCIE_TX_STATUS`, `PCIE_BUS_CNTL`, `PCIE_MST_CTRL_1`, and `PCIE_COMMON_AER_MASK` define PCIe core controls for ordering, completion timeout, CRS handling, relaxed/no-snoop attributes, poison/error behavior, bus-master routing, and common AER masking.
- `PCIE_TX_TRACKING_ADDR_LO`, `PCIE_TX_TRACKING_ADDR_HI`, and `PCIE_TX_TRACKING_CTRL_STATUS` define an address-based tracking/debug window for posted, non-posted, and completion traffic.
- `PCIE_LC_STATE6` through `PCIE_LC_STATE11`, `PCIE_LC_STATUS1`, and `PCIE_LC_STATUS2` expose link-training/link-control state snapshots, receiver state, lane status, equalization status, and speed/width-related status fields.
- `PCIE_RX_LAST_TLP0..3` and `PCIE_TX_LAST_TLP0..3` are full-register masks for captured last received/transmitted TLP dwords.
- `PCIE_I2C_REG_ADDR_EXPAND`, `PCIE_I2C_REG_DATA`, and `PCIE_CFG_CNTL` provide sideband/I2C/configuration access fields.
- `PCIE_LC_PM_CNTL`, `PCIE_LC_PORT_ORDER_CNTL`, `PCIE_P_CNTL`, `PCIE_P_BUF_STATUS`, `PCIE_P_DECODER_STATUS`, `PCIE_P_MISC_STATUS`, and `PCIE_P_RCV_L0S_FTS_DET` cover link power management, port ordering, posted path control/status, decoder state, and L0s FTS detection.
- `PCIE_TX_CCIX_CNTL0`, `PCIE_TX_CCIX_CNTL1`, `PCIE_TX_CCIX_PORT_MAP`, `PCIE_TX_CCIX_ERR_CTL`, and `PCIE_RX_CCIX_CTL0` describe CCIX transmit/receive enablement, port mapping, credit/flush handling, optimized TLP format, and error reporting controls.
- `PCIE_RX_AD`, `PCIE_SDP_CTRL`, `NBIO_CLKREQb_MAP_CNTL`, `PCIE_SDP_SWUS_SLV_ATTR_CTRL`, and `PCIE_SDP_RC_SLV_ATTR_CTRL` define address decode, sideband data path, CLKREQ mapping, and slave attribute controls.
- `PCIE_PERF_COUNT_CNTL`, `PCIE_PERF_CNTL_TXCLK1..4`, `PCIE_PERF_COUNT0/1_TXCLK1..4`, `PCIE_PERF_CNTL_SCLK1..2`, `PCIE_PERF_COUNT0/1_SCLK1..2`, `PCIE_PERF_CNTL_EVENT_LC_PORT_SEL`, and `PCIE_PERF_CNTL_EVENT_CI_PORT_SEL` define event selectors and counters for TXCLK and SCLK performance monitoring.
- `PCIE_STRAP_F0`, `PCIE_STRAP_NTB`, `PCIE_STRAP_MISC`, `PCIE_STRAP_MISC2`, `PCIE_STRAP_PI`, and `PCIE_STRAP_I2C_BD` expose strap-derived PCIe capability, BAR, NTB, timing, lane, and I2C-board behavior.
- `PCIE_PRBS_CLR`, `PCIE_PRBS_STATUS1`, `PCIE_PRBS_STATUS2`, `PCIE_PRBS_FREERUN`, `PCIE_PRBS_MISC`, `PCIE_PRBS_USER_PATTERN`, `PCIE_PRBS_LO_BITCNT`, `PCIE_PRBS_HI_BITCNT`, and `PCIE_PRBS_ERRCNT_0..15` define PRBS test setup, lock/status, bit counters, and per-lane error counters.
- `SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0`, `SWRST_COMMAND_1`, `SWRST_CONTROL_0..6`, `SWRST_EP_COMMAND_0`, and `SWRST_EP_CONTROL_0` define software reset command, acknowledgement, delay, multi-function/endpoint reset, reset mask, and reset-control fields.
- `CPM_CONTROL`, `CPM_SPLIT_CONTROL`, `CPM_CONTROL_EXT`, `LNCNT_CONTROL`, `LNCNT_QUAN_THRD`, `LNCNT_WEIGHT`, `PCIE_PGMST_CNTL`, `PCIE_PGSLV_CNTL`, and `LC_CPM_CONTROL_0/1` cover component power management, split control, lane-count policy, and master/slave power-gating behavior.
- `PCIE_RXMARGIN_CONTROL_CAPABILITIES`, `PCIE_RXMARGIN_1_SETTINGS`, `PCIE_RXMARGIN_2_SETTINGS`, and `PCIE_PRESENCE_DETECT_SELECT` expose receiver-margining capability/setting fields and presence-detect selection.

The later I/O-hub and misc portions include:

- Address-block comments for `nbio_iohub_nb_nbcfg_nb_cfgdec`, `PCIE0shadow0` through `PCIE0shadow6`, and `NBIF1shadow0` through `NBIF1shadow2`; this slice contains no field macros under most of those shadow block comments.
- `FASTREG_APERTURE`, which describes a fast-register aperture selection field.
- `NBIO_LCLK_DS_MASK`, `SB_LOCATION`, and `SW_US_LOCATION`, which define low-clock deep-sleep masking and software/system bridge location fields.
- `SW_NMI_CNTL`, `SW_SMI_CNTL`, `SW_SCI_CNTL`, `APML_SW_STATUS`, `SW_GIC_SPI_CNTL`, and `SW_SYNCFLOOD_CNTL`, which route or status software-triggered NMI/SMI/SCI/APML/GIC/SYNCFLOOD events.
- `CAM_CONTROL` and `CAM_TARGET_*` registers, which define CAM address/data match controls, index/data/mask payloads, and virtual-channel/cross-trigger fields.
- `P_DMA_DROPPED_LOG_LOWER`, `P_DMA_DROPPED_LOG_UPPER`, and the beginning of `NP_DMA_DROPPED_LOG_LOWER`, which expose bit-by-bit dropped posted and non-posted DMA log state.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly using an `L` suffix.

Consumers are expected to pair these field macros with register offsets from `nbio_7_2_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe/NBIO-specific accessors. The masks alone do not define register addresses, access widths, reset values, ownership, volatility, write-one-to-clear behavior, or legal programming sequences.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code includes the NBIO 7.2.0 offset and shift/mask headers.
2. A caller selects a `BIFP6_*`, `PCIE_*`, `SWRST_*`, `CPM_*`, `SW_*`, `CAM_*`, or DMA log register offset from the generated offset metadata.
3. The caller reads or composes a 32-bit value and uses the `__SHIFT` and `_MASK` constants to extract, test, clear, or set a specific field.
4. Hardware reacts asynchronously through PCIe link training, equalization, power-state transitions, interrupt delivery, reset sequencing, performance counting, PRBS checking, CAM matching, or DMA error logging.

Several hardware flows represented here are inherently state-machine driven: L1 substate entry/exit, ESM speed selection, retimer detection, TX/RX frequency readiness, hot-plug presence changes, performance counter sampling, PRBS lock/error detection, software reset acknowledgement, component power management, and dropped-DMA capture.

## State And Persistence Behavior

The header itself owns no software state and persists nothing. It describes fields in hardware-visible NBIO and PCIe registers. Persistence depends on the relevant reset and power domains: strap bits are generally sampled from platform configuration, control bits may be programmed by firmware or the driver, status bits may be live or latched by hardware, and debug/log fields may persist until explicitly cleared, reset, or overwritten by later events.

State represented in this chunk includes PCIe advertised capability and strap state, link-control policy, L1 PM substate timing, retimer/ESM/equalization state, hot-plug status and interrupt enables, TXCLK/SCLK performance counters, last-TLP capture buffers, CCIX controls, sideband attributes, PRBS test configuration and counters, reset command/status bits, component power-management controls, receiver-margining settings, software interrupt routing/status, CAM match state, and DMA dropped-transaction logs.

Callers must not infer safe write values from masks alone. Full-width `0xFFFFFFFFL` masks mark fields that occupy a whole 32-bit register, not fields that are necessarily writable as all ones. Status and log registers may be read-only, sticky, clear-on-write, hardware-updated, or reserved-bit sensitive depending on the hardware specification.

## Dependencies And Integration Points

The direct source-tree integration point for this generated header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio/nbio_7_2_0_offset.h` and `nbio/nbio_7_2_0_sh_mask.h`. Display resource files for DCN 3.0.1 and DCN 3.1 include the matching offset header for NBIO base/address integration, while bitfield use is available to AMDGPU NBIO and PCIe paths through this shift/mask header.

The companion generated file `nbio_7_2_0_offset.h` supplies register addresses. These shift/mask definitions must remain synchronized with that offset metadata and with AMD's authoritative NBIO 7.2.0 register database. Neighboring generated ASIC register headers for BIF/NBIO generations provide comparable field names for cross-generation validation, but they are not interchangeable because register layout is ASIC-specific.

Functional integration points include PCIe link bring-up and retraining, ASPM/L1 PM policy, Gen4/ESM equalization, retimer handling, hot-plug reporting, CCIX support, performance/debug instrumentation, PRBS diagnostics, software reset flows, component power management, receiver margining, sideband/config access, software interrupt routing, CAM-triggered debug, and DMA fault/drop diagnostics.

## Risks And Edge Cases

- The chunk starts and ends mid-register context. Whole-file research must reconcile `BIFP6_PCIEP_STRAP_LC` fields from the previous chunk and the remaining `NP_DMA_DROPPED_LOG_LOWER` fields from the next chunk.
- Generated macro drift can compile cleanly while causing silent misprogramming of link, reset, power, interrupt, or debug registers.
- Many repeated fields are lane-, counter-, or bit-indexed. Copy/generation errors in one lane or one counter can appear only under certain link widths, PRBS tests, or traffic patterns.
- Link-control fields are timing and partner sensitive. Equalization, ESM, retimer, L1 PM, and receiver-margining writes can cause link instability if applied outside the hardware-prescribed sequence.
- Reset and power-management fields can disrupt active traffic. Generic read-modify-write code must preserve reserved bits and account for acknowledgement, delay, and endpoint/multi-function reset semantics.
- Status and log registers such as hot-plug state, performance counters, PRBS status, last-TLP captures, CAM matches, and DMA dropped logs may be live, sticky, or clear-on-write. The header does not encode those access rules.
- Strap fields often mirror platform/firmware configuration. Treating them as ordinary software-owned control fields can produce ineffective writes or confusing register traces.
- `*_MASK_MASK` names are expected in generated headers when the hardware field is itself named `MASK`; consumers should not hand-normalize these identifiers.
- Comment-only address-block sections in this range may look like missing coverage, but they simply indicate generated blocks with no field macros in this particular line slice.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU configurations that include NBIO 7.2.0 support, especially translation units including `nbio_7_2_0_sh_mask.h`.
- Run generated-header consistency checks: each complete field should have compatible `__SHIFT` and `_MASK` definitions, masks should fit in 32 bits, and repeated lane/counter/log families should follow the expected bit pattern.
- Cross-check every register family in this range against `nbio_7_2_0_offset.h` so field definitions map to actual NBIO 7.2.0 offsets.
- Compare the generated values with AMD's authoritative NBIO 7.2.0 register database, with emphasis on dense blocks such as `PCIE_LC_CNTL*`, `PCIE_STRAP_*`, `PCIE_PRBS_ERRCNT_*`, `SWRST_*`, `CPM_*`, `CAM_TARGET_*`, and DMA dropped-log registers.
- On supported hardware, validate PCIe enumeration, negotiated link width/speed, retrain behavior, L1 PM substate transitions, reset recovery, hot-plug/presence reporting, CCIX/ESM capability reporting, and suspend/resume.
- Exercise diagnostic paths where available: PRBS lock/error counting, performance counters, last-TLP capture, receiver margining, CAM match triggers, software interrupt routes, and posted/non-posted DMA dropped-log collection.
- For any driver code that writes these fields, inspect register traces to ensure reserved bits are preserved, sticky status is cleared intentionally, counters/logs are sampled coherently, and link-sensitive fields are not changed while the link is training unless the required hardware sequence says so.
