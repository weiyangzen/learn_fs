# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 22703-25135

## Scope

This chunk covers lines 22703-25135 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, variables, allocation, locking, or direct register I/O. The range starts in the middle of `NB_SPARE2`, covers most of the `aid_nbio_iohub_nb_misc_misc_cfgdec` register field map, and then begins `aid_nbio_iohub_nb_rascfg_ras_cfgdec` through the first fields of `PARITY_ERROR_STATUS_UNCORR_GRP14`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU NBIO register metadata. It has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-definition companion for NBIO 7.9.0 registers. Each generated field exposes:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index of the field.
- `REGISTER__FIELD_MASK`: the raw mask for the field in the containing register.

Driver code combines these macros with matching offsets from `nbio_7_9_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`. The chunk's definitions describe northbridge configuration, memory window, software interrupt, VDM/MCTP routing, debug trap, bridge configuration, MCA interrupt, and RAS parity status fields.

## Important Register Families

The opening range completes `NB_SPARE2`, a 32-bit write-one-to-clear-style spare register family named `NB_SPARE2_RW1C_0` through `_31`. The chunk starts at bit 6, so the full register's shift list begins in the previous chunk. Its masks still cover every bit from `0x00000001L` through `0x80000000L`.

The NB miscellaneous configuration fields include:

- Identification and clock state: `NB_REVID` exposes a 10-bit `REVISION_ID`, and `NBIO_LCLK_DS_MASK` exposes a full-width LCLK deep-sleep mask.
- Bus and memory topology: `NB_BUS_NUM_CNTL` carries bus number, bus-latency mode, and segment fields; `NB_MMIOBASE` and `NB_MMIOLIMIT` are full-width MMIO aperture registers; `NB_LOWER_TOP_OF_DRAM2`, `NB_UPPER_TOP_OF_DRAM2`, `NB_LOWER_DRAM2_BASE`, `NB_UPPER_DRAM2_BASE`, `NB_TOP_OF_DRAM3`, and `NB_DRAM3_BASE` describe DRAM aperture boundaries and enables.
- Location and remap fields: `SB_LOCATION` and `SW_US_LOCATION` hold port/core locations; `NB_PROG_DEVICE_REMAP_PBr0` through `PBr8` and `PBr10` through `PBr13` expose 8-bit programmed device/function remap values.
- Software interrupt/status controls: `SW_NMI_CNTL`, `SW_SMI_CNTL`, and `SW_SCI_CNTL` are full-width software status registers; `APML_SW_STATUS` exposes `APML_NMI_STATUS`; `SW_GIC_SPI_CNTL` maps software NMI/SMI/SCI GIC SPI vectors; `SW_SYNCFLOOD_CNTL` exposes private and APML sync-flood request bits.

The CAM and dropped-DMA sections define debugging/diagnostic surfaces:

- `CAM_CONTROL` has enable, operation, access type, data-match enable, virtual channel, and cross-trigger fields.
- `CAM_TARGET_*` registers define index/data and address/data comparison values plus masks.
- `P_DMA_DROPPED_LOG_LOWER`, `P_DMA_DROPPED_LOG_UPPER`, `NP_DMA_DROPPED_LOG_LOWER`, and `NP_DMA_DROPPED_LOG_UPPER` are repeated 32-bit bitmaps for posted and non-posted dropped-DMA logging.

The PCIe VDM and stall-control fields include:

- `PCIE_VDM_NODE0_CTRL4` bus range base/limit and node-present fields.
- `PCIE_VDM_CNTL2` controls VDM peer-to-peer mode, MCTP endpoint/multisegment enablement, routing to SMU, route-all-to-MCTP-master policy, MCTP master segment, and MCTP master ID.
- `PCIE_VDM_CNTL3` exposes APMTP master valid and ID fields.
- `STALL_CONTROL_XBARPORT0_0` through `STALL_CONTROL_XBARPORT5_1` repeat request/response stall-enable fields for virtual channels 0, 1, 2, 3, 4, 5, and 7 on crossbar ports 0-5. Each VC field is a two-bit slot spaced on four-bit boundaries.

The PSP/SMU and trap sections are broad:

- `PSP_BASE_ADDR_LO/HI` and `SMU_BASE_ADDR_LO/HI` define low/high base-address fields, with low halves shifted by bit 16.
- `SCRATCH_4`, `SCRATCH_5`, `SMU_BLOCK_CPU`, and `SMU_BLOCK_CPU_STATUS` are full-width scratch/blocking/status surfaces.
- `TRAP_STATUS` reports trap request validity, trap number, stage-2 validity, and stage-2 number.
- `TRAP_REQUEST0` through `TRAP_REQUEST5`, `TRAP_REQUEST_DATASTRB0/1`, and `TRAP_REQUEST_DATA0` through `DATA15` expose captured trap request address, command, attributes, length, VC, block-level, chain, I/O, pass-posted-write flags, unit ID, security level, data VC/error/parity, byte enables, and payload data.
- `TRAP_RESPONSE_CONTROL`, `TRAP_RESPONSE0`, and `TRAP_RESPONSE_DATA0` through `DATA15` define response trigger/passthrough controls, response status, data status, and read-response payload fields.
- `TRAP0_*` through `TRAP15_*` define 16 configurable trap comparators. Each comparator has `CONTROL0` fields for enable, SMU interrupt, stage-2 pointer, cross-trigger, and stage-2 enable; address low/high match fields; command match fields; address masks; and command masks.

The SB bridge/MCA section maps PCI bridge-like and interrupt-routing fields:

- `SB_COMMAND`, `SB_SUB_BUS_NUMBER_LATENCY`, `SB_IO_BASE_LIMIT`, `SB_MEM_BASE_LIMIT`, `SB_PREF_BASE_LIMIT`, `SB_PREF_BASE_UPPER`, `SB_PREF_LIMIT_UPPER`, and `SB_IO_BASE_LIMIT_HI` describe I/O/memory/bus-master enables and bridge decode windows.
- `SB_IRQ_BRIDGE_CNTL`, `SB_EXT_BRIDGE_CNTL`, `SB_PMI_STATUS_CNTL`, `SB_SLOT_CAP`, `SB_ROOT_CNTL`, and `SB_DEVICE_CNTL2` expose ISA/VGA decode controls, port-80 enablement, power state, slot power limit, CRS visibility, and ARI forwarding.
- `MCA_SMN_INT_REQ_ADDR`, `MCA_SMN_INT_MCM_ADDR`, `MCA_SMN_INT_APERTUREID`, and `MCA_SMN_INT_CONTROL` define SMN interrupt target/request address fields and MCA cross-trigger control.

The RAS configuration block begins at line 24180:

- `PARITY_CONTROL_0` contains corrected and uncorrected-poison threshold fields.
- `PARITY_CONTROL_1` contains parity error injection controls: group selection, group type, ID, command, trigger, and inject-allow.
- `PARITY_SEVERITY_CONTROL_UNCORR_0`, `PARITY_SEVERITY_CONTROL_CORR_0`, and `PARITY_SEVERITY_CONTROL_UCP_0` assign two-bit severity values per group. Uncorrectable and corrected variants cover groups 0-15; UCP covers groups 0-12 in this chunk.
- `RAS_GLOBAL_STATUS_LO` reports global parity, SERR, hotplug wake alarm, software NMI/SMI/SCI, APML NMI, and sync-flood state.
- `RAS_GLOBAL_STATUS_HI` reports PCIe and NBIF port error bits.
- `PARITY_ERROR_STATUS_UNCORR_GRP0` through `GRP13` are complete 32-bit per-ID uncorrectable parity status bitmaps. The chunk ends inside `PARITY_ERROR_STATUS_UNCORR_GRP14`, after shifts and masks through bit 17; the remainder belongs to the next chunk.

## APIs, Types, And Functions

There are no callable APIs, types, or functions in this range. The exported surface is the generated macro namespace. Direct NBIO 7.9.0 in-tree consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which includes the matching offset and shift/mask headers for NBIO setup paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes these headers while registering NBIF RAS interrupt source IDs.

The current `amdgpu_ras_nbio_v7_9.c` implementation registers RAS controller and ATHUB error-event interrupts but leaves their process callbacks as dummy paths because the BIF-ring hardware path is disabled. That means many RAS macros in this chunk are available for decode/injection support, register dumps, or future paths, but this file does not currently perform active parity-status decoding with them.

## Control Flow

This header has no runtime control flow. Runtime use follows the standard generated-register pattern:

1. Driver code selects an NBIO 7.9.0 register offset from `nbio_7_9_0_offset.h`.
2. It reads a raw register value through the SOC15 MMIO/SMN/indirect access path appropriate for NBIO.
3. It decodes a field with the corresponding `_MASK` and `__SHIFT`, or composes a write value with `REG_SET_FIELD`.
4. Hardware applies the actual semantics: bus/memory window programming, software interrupt signaling, sync-flood generation, dropped-DMA logging, VDM/MCTP routing, crossbar stalling, trap matching, bridge decode, MCA interrupt triggering, or RAS parity reporting.

The order in this generated header follows the register database and address blocks, not an execution sequence.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It names fields whose state lives in NBIO hardware registers, PCI bridge/configuration decode registers, and RAS status/control registers. Persistence depends on the specific hardware reset domain, firmware initialization, GPU reset, function-level reset, power transitions, and explicit driver writes.

Represented hardware state includes:

- Configuration state: bus number/segment selection, MMIO/DRAM windows, programmed device remaps, VDM routing, stall controls, PSP/SMU base addresses, trap comparator configuration, SB bridge windows, slot/root/device controls, MCA interrupt targets, and parity severity/injection controls.
- Status and diagnostic state: revision ID, software NMI/SMI/SCI/APML status, dropped-DMA bitmaps, trap request/response captures, SMU block status, RAS global status, and parity error status groups.
- Request/side-effect state: software sync-flood bits, trap response trigger, parity error generation trigger, MCA cross-trigger, and possibly write-one-to-clear or sticky status bits.

The macros do not encode read/write permissions, write-one-to-clear behavior, reset values, volatility, reserved-bit rules, posted-write ordering, or whether a read/write has side effects. Callers must rely on ASIC documentation and local driver conventions for those semantics.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 header set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies matching register addresses and base indices.
- Other generated NBIO 7.9.0 headers, where present, provide reset/default values and adjacent register-family definitions.
- AMDGPU SOC15 register helper macros provide the extraction, composition, and access mechanisms that make these masks useful.

Practical integration points include GPU/NBIO initialization, memory aperture setup, PCIe bridge/resource decode, software interrupt delivery, APML and GIC SPI routing, VDM/MCTP control, SMU/PSP mailbox or base-address programming, diagnostics for dropped DMA and traps, MCA/SMN interrupt routing, RAS interrupt registration, parity severity/error injection, and debug register dumps.

## Risks And Edge Cases

- The chunk starts and ends mid-family. `NB_SPARE2` begins before line 22703, and `PARITY_ERROR_STATUS_UNCORR_GRP14` continues after line 25135. The later merge step must reconcile adjacent chunks before making whole-register claims.
- A generated shift/mask drift can compile cleanly while decoding or writing the wrong hardware bit. This is especially risky in repeated 32-bit bitmap families such as dropped-DMA logs and parity error status groups.
- Status, trigger, request, and clear registers are not distinguished by macro shape. Generic read-modify-write code can accidentally clear sticky diagnostics, trigger sync-flood/trap/parity injection, or preserve stale status if the field semantics are not checked.
- NB bus/MMIO/DRAM and SB bridge-window fields affect host-visible address decode. Incorrect values can break enumeration, memory routing, peer access, or MMIO isolation.
- VDM/MCTP routing fields can redirect vendor-defined messages to SMU or MCTP master paths. Wrong master segment/ID or route-all policy can affect platform management traffic.
- Crossbar stall controls and trap comparators are debug-sensitive. Enabling them on live systems without a narrow policy can stall traffic, redirect errors, interrupt SMU unexpectedly, or perturb timing-sensitive paths.
- PSP/SMU base-address fields and SMU block controls are firmware-facing. Incorrect masks or stale writes can interfere with firmware communication and CPU/SMU arbitration.
- RAS severity and injection controls intentionally share compact repeated layouts. Confusing corrected, uncorrected, and UCP severity families can misclassify errors or hide/fabricate parity events.
- High-bit masks use `0x80000000L` and full-width masks use `0xFFFFFFFFL`; consumers should keep values in unsigned 32-bit register paths to avoid signedness surprises.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU configurations that include NBIO 7.9.0 support; malformed symbols or header mismatches should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: each field should have the expected shift/mask, repeated bitmap groups should be monotonic, and every register here should have a matching offset definition.
- Cross-check `nbio_7_9_0_sh_mask.h` against nearby NBIO generations only where the hardware spec says fields are shared; similar names across generations may have different field presence or base indices.
- On matching hardware, compare decoded NBIO/SB bus numbers, segment, MMIO/DRAM windows, bridge command bits, and bridge resource windows with PCI configuration dumps and AMDGPU debug output.
- Exercise software interrupt/APML/sync-flood paths only in controlled debug or validation environments, confirming status bits and GIC SPI vector fields behave as expected.
- Validate VDM/MCTP routing with platform-management traffic tests, including endpoint enablement, route-to-SMU controls, and master ID/segment programming.
- Use debug or lab-only flows for trap comparators and crossbar stall controls; confirm trap request capture, response data/status, cross-trigger, and stage-2 fields decode correctly without affecting adjacent trap slots.
- Validate RAS paths by checking interrupt registration for NBIF RAS sources, register dumps for `RAS_GLOBAL_STATUS_*`, parity severity settings, and parity error group bitmaps. Error injection should verify trigger/allow/group/ID fields and ensure corrected/uncorrected/UCP classification matches the intended severity.
- Regression-test suspend/resume, GPU reset, and firmware reinitialization because many represented fields are hardware state rather than software-owned persistent state.
