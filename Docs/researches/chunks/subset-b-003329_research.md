# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 4979-7452

## Scope

This chunk is a generated AMD NBIO 7.9.0 shift/mask header segment. It contains C preprocessor constants only: 2,108 `#define` entries, split into 1,054 `__SHIFT` constants and 1,054 `_MASK` constants. The equal count hides two chunk-boundary partials: the range starts with only the mask for `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3`, whose shift is in the previous chunk, and ends with only the shift for `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO`, whose mask is in the next chunk.

The covered source belongs to AMDGPU's generated `drivers/gpu/drm/amd/include/asic_reg/nbio` register database. It has no Ceph or distributed-filesystem logic despite the source tree prefix. It also has no executable code, structs, enums, callbacks, locks, or allocation paths.

The range covers three main areas:

- The tail of the GPU IOV vendor-specific PCIe capability area for `DEV0_EPF0`, especially schedule dwords for UVD/VCN and GFX engines plus GPU IOV engine interrupt enable/status bitmaps.
- The complete visible `aid_nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` address block for `BIF_CFG_DEV0_EPF1`, from standard PCI config identity fields through ARI capability fields.
- The beginning and most of the PCIe capability area for `aid_nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, `BIF_CFG_DEV0_RC0`, from root-complex standard PCI bridge fields through the first MSI address-low shift.

## Purpose

The purpose of this header chunk is to define bit positions and masks for NBIO/BIF PCI configuration-space and GPU IOV vendor-specific registers on AMD ASICs using NBIO 7.9.0. The naming convention is consistent throughout the file:

- `<REGISTER>__<FIELD>__SHIFT` is the zero-based bit position of a field.
- `<REGISTER>__<FIELD>_MASK` is the already-shifted field mask used for extraction, tests, and read-modify-write updates.

The companion `nbio_7_9_0_offset.h` supplies the register addresses and base indices. For example, that file maps the GPU IOV schedule and interrupt registers under `regBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` with base index 8, maps `cfgPCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` config-space offsets such as UVD/GFX schedule dwords and engine interrupt status/enable dwords, and maps the `BIF_CFG_DEV0_EPF1` and `BIF_CFG_DEV0_RC0` PCI configuration registers. This chunk supplies the field geometry for those addresses.

Runtime code does not call this header directly. AMDGPU code includes it from `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` together with the offset header. Register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `WREG32_FIELD15_PREREG`, and PCIe index/data accessors consume these generated constants.

## Important Macro Families

### GPU IOV Schedule Dwords

The chunk begins inside `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3` and continues through UVD/VCN schedule dwords for `UVD0SCH` through `UVD11SCH`. Each schedule entry has dwords `DW0` through `DW8`; each dword field is represented as a full 32-bit value at shift 0 with mask `0xFFFFFFFFL`.

The same schedule shape then appears for graphics engines `GFX0SCH` through `GFX7SCH`, again with `DW0` through `DW8` full-dword fields. These definitions are opaque layout constants for AMD's GPU IOV vendor-specific PCIe capability. They do not interpret the schedule payload; they only state that each dword occupies the full register.

The preceding chunk defines the offset summary registers (`PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_OFFSETS*`) and the first UVD0 schedule dwords. The matching offsets in `nbio_7_9_0_offset.h` show the schedule register sequence in config space and in generated `regBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` macros.

### GPU IOV Engine Interrupt Enable and Status

After the schedule dwords, the chunk defines GPU IOV engine interrupt bitmaps:

- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGA_A0_7_INTR_ENABLE`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B0_7_INTR_ENABLE`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B8_15_INTR_ENABLE`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGA_A0_7_INTR_STATUS`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B0_7_INTR_STATUS`
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_ENGB_B8_15_INTR_STATUS`

For each engine slot, four interrupt classes repeat in adjacent bits: command complete, hang self recovered, hang needs FLR, and VM busy transition. The `A0_7` and `B0_7` registers use all 32 bits for eight engines times four events. The `B8_15` status/enable registers in this chunk define engines B8 through B11, using bits 0 through 15. Comments for `ENGA_A8_15_INTR_ENABLE` and `ENGA_A8_15_INTR_STATUS` appear without field definitions in this chunk, so those register blocks are empty in the generated range.

These fields are virtualization and recovery oriented. They describe how GPU IOV exposes per-engine completion, hang, FLR-needed, and VM-busy-transition events to the PCIe vendor-specific capability image. They are not Linux interrupt handlers by themselves.

### DEV0 EPF1 Standard PCI Header

The `BIF_CFG_DEV0_EPF1` block starts with ordinary PCI config header fields:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command and status registers: I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, interrupt disable, immediate readiness, interrupt status, capability-list presence, fast back-to-back support, DEVSEL timing, target/master abort, system error, and parity error bits.
- Header/control fields: cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, maximum latency, and vendor capability/adapter write fields.

These are PCI configuration-image fields for endpoint function 1. Firmware, PCI core enumeration, and device reset state normally own much of this surface. AMDGPU code using these masks must pair them with the `BIF_CFG_DEV0_EPF1` offsets, not with the visually similar root-complex or endpoint-function-zero registers.

### DEV0 EPF1 Power, PCIe, Link, and MSI Capabilities

The endpoint function 1 section includes PCI PM capability fields:

- `PMI_CAP_LIST` and `PMI_CAP` for capability ID, next pointer, version, PME clock, immediate readiness on return to D0, D1/D2 support, PME support, and auxiliary-current fields.
- `PMI_STATUS_CNTL` for power state, no-soft-reset, PME enable/status, bridge-extension bits, data select/scale, and PM data.

It also defines PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, PCIe capability version, device/port type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for payload size, phantom functions, extended tags, acceptable L0s/L1 latency, role-based error reporting, captured slot power, FLR capability/initiation, error-reporting enables, relaxed ordering, no-snoop, max read request size, aux power, transactions pending, and emergency power reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for speed/width, ASPM support/control, exit latencies, clock power management, surprise-down reporting, data-link active reporting, link bandwidth notification, link disable/retrain, common clock, extended sync, autonomous width disable, bandwidth interrupt enables, DRS signaling, current speed, negotiated width, link training, slot clock, and link active/status bits.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout, ARI, atomic ops, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS/DRS, Gen3 equalization state, crosslink state, RTM presence, and downstream component presence.

The MSI/MSI-X section defines capability headers, MSI message control, 32-bit and 64-bit message address/data registers, extended message data, MSI mask and pending registers, MSI-X message control, table BIR/offset, and PBA BIR/offset. These are bit layouts only; interrupt allocation, vector ownership, MSI remapping, and table lifetime are managed by PCI and AMDGPU interrupt code.

### DEV0 EPF1 Extended Capabilities

The `BIF_CFG_DEV0_EPF1` block continues through several PCIe extended capability families:

- Vendor-specific enhanced capability: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and scratch payload dwords.
- Advanced Error Reporting: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- BAR enhanced capability: BAR1 through BAR6 capability/control definitions for fixed-size support, size capability, selected size, BAR index, number of BARs, and atomic operation routing/blocking support.
- Power budget and DPA: power budget selectors/data/capability, DPA latency indicator, status/control, and substate power allocation 0 through 7.
- ACS, PASID, and ARI: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, PASID execution/privileged mode, max PASID width, PASID enable bits, ARI next function/function group, and ACS function group controls.

These fields are especially relevant to virtualization, IOMMU isolation, peer-to-peer routing, PCIe error reporting, power management, and BAR sizing. The masks do not encode policy or legal value transitions.

### DEV0 RC0 Root Complex and Bridge Fields

The final part of the chunk starts the `BIF_CFG_DEV0_RC0` root-complex block. It includes standard bridge-style PCI fields:

- Root-complex identity, class, revision, header, BIST, BARs, primary/secondary/subordinate bus numbers, secondary latency timer, I/O base/limit, memory base/limit, prefetchable base/limit and upper halves, I/O base/limit high, capability pointer, ROM BAR, interrupt line/pin, bridge control, and extended bridge control.
- PM capability and PCIe capability fields analogous to the endpoint block where applicable.
- Root port specific slot and root fields: `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`.
- Root-side device/link capability/control/status 1 and 2 fields.
- The start of root-complex MSI capability fields through `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO__MSI_MSG_ADDR_LO__SHIFT`.

The next chunk continues the `RC0` MSI address-low mask and later root-complex capability definitions. This chunk therefore should not be treated as a complete final description of `BIF_CFG_DEV0_RC0`.

## Control Flow and Runtime Behavior

There is no control flow in this header. It is compile-time data used to produce constants in AMDGPU code. Runtime behavior appears when other code:

1. Selects NBIO 7.9.0 support for the ASIC and includes `nbio_7_9_0_offset.h` plus this shift/mask header.
2. Computes an MMIO or PCI configuration register address using generated offset macros and SOC15/NBIO helper functions.
3. Uses a field macro pair through `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask tests, or read-modify-write helpers.
4. Reads or writes hardware-owned state such as GPU IOV interrupt status, PCIe link controls, AER status, MSI/MSI-X state, BAR capability values, ACS/PASID/ARI controls, or root port status.

The local `nbio_v7_9.c` integration demonstrates this pattern through NBIO init, doorbell range programming, interrupt-control setup, HDP flush offsets, PCIe index/data offset reporting, partition status reads, BACO setup, and RAS interrupt handling. The exact macros in this chunk are largely field definitions for config-space and vendor-specific capability surfaces rather than standalone call sites.

## State and Persistence

This header owns no software state and persists nothing. Its constants are fixed into the compiled driver.

The state described by the macros lives in NBIO/BIF hardware register and PCI configuration images:

- GPU IOV schedule dwords and engine interrupt status/enable bits reflect virtualization scheduling and per-engine event state.
- PCI command/status, BARs, capability pointers, ROM BAR, interrupt line/pin, and class-code fields reflect endpoint or root-complex enumeration state.
- PM, PCIe device, link, slot, root, MSI, MSI-X, ACS, PASID, ARI, AER, BAR, power-budget, and DPA registers reflect hardware capabilities, driver/PCI-core policy, sticky status, diagnostic logs, and reset-sensitive configuration.
- AER status and root/slot/link status fields can be sticky or write-one-to-clear according to PCIe semantics, but the generated masks do not express clear-on-write or read side effects.

Persistence across FLR, hot reset, GPU reset, BACO, runtime suspend, or full PCI reset depends on NBIO and PCIe hardware reset domains. A wrong generated mask value would persist in the driver binary until the header is regenerated or corrected.

## Dependencies and Integration Points

Direct dependencies and integration points in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`, the required companion for register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which includes this header and uses NBIO 7.9 generated masks with SOC15 register helpers for initialization, doorbells, HDP flushing, PCIe index/data windows, interrupt controls, partition status, and RAS interrupt fallback handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes this header while registering NBIO RAS interrupt sources.
- AMDGPU bitfield helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, which depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` spelling.
- PCIe and SR-IOV/IOV integration paths, where GPU IOV schedule, interrupt, FLR-needed, VM-busy, ACS, PASID, ARI, MSI/MSI-X, and AER fields interact with PCI core policy, IOMMU routing, firmware, and virtualization management.

Cross-generation headers such as `nbio_7_2_0_sh_mask.h`, `nbio_7_7_0_sh_mask.h`, and `nbio_7_11_0_sh_mask.h` contain structurally similar names, but consumers must use the NBIO 7.9.0 mask file with the matching NBIO 7.9.0 offset file. Register maps and endpoint coverage vary by generation.

## Risks

- Chunk-boundary incompleteness: this range starts with a mask whose shift is in the previous chunk and ends with a shift whose mask is in the next chunk. Pair-completeness checks must happen after merge.
- Register/mask mismatch: using these 7.9.0 masks with another NBIO generation's offsets can silently decode or program the wrong bits.
- Function confusion: `BIF_CFG_DEV0_EPF1` endpoint fields and `BIF_CFG_DEV0_RC0` root-complex fields have similar PCIe capability names but target different PCI configuration images.
- GPU IOV event corruption: engine interrupt enable/status bits are dense repeated bitmaps. A one-bit error can enable the wrong engine event, miss a hang-needs-FLR signal, or clear the wrong status.
- Full-dword schedule payloads: UVD/GFX schedule dwords are opaque `0xFFFFFFFF` fields. The mask says nothing about internal subfields, ownership, or valid values.
- PCIe control hazards: link control, completion timeout, max payload/read request, relaxed ordering, no-snoop, LTR, OBFF, emergency power reduction, DPA, ACS, PASID, and ARI fields can affect bus stability, isolation, and performance.
- Interrupt routing hazards: MSI/MSI-X enable, mask, pending, table, PBA, and message address/data fields must remain coordinated with PCI core, interrupt remapping, and AMDGPU interrupt setup.
- AER handling hazards: status, mask, and severity registers look similar but have different semantics. Confusing them can hide faults, over-report recoverable errors, or damage diagnostic logs.
- Reserved-bit damage: generated masks expose named fields but do not identify all reserved bits or write constraints. Writes should preserve unrelated fields and follow PCIe/NBIO programming sequences.

## Test Signals

Useful validation signals for work touching this chunk include:

- AMDGPU builds that include `nbio_v7_9.c` and `amdgpu_ras_nbio_v7_9.c` with no missing, renamed, or duplicate NBIO 7.9.0 macros.
- Mechanical checks that every field has a matching shift/mask pair after adjacent chunk reconciliation, accounting for the two expected local boundary partials.
- Cross-checks against `nbio_7_9_0_offset.h` so every register family here has the expected generated address macro and base index.
- Hardware or emulator PCI config-space dumps for NBIO 7.9 devices decode expected `DEV0_EPF1` and `DEV0_RC0` capability chains, including PM, PCIe, MSI/MSI-X, AER, ACS, PASID, ARI, and vendor-specific capability headers.
- SR-IOV or GPU IOV validation confirms UVD/VCN and GFX schedule registers, engine command-complete events, self-recovered hang events, hang-needs-FLR events, and VM-busy-transition events report and clear as expected.
- PCIe stress tests show no new completion timeout, malformed TLP, ECRC, unsupported request, receiver overflow, surprise-down, or root-port PME anomalies.
- Interrupt tests verify MSI/MSI-X delivery, masking, pending-bit accounting, and root/endpoint message address/data programming.
- Reset coverage, including FLR, GPU reset, hot reset, suspend/resume, and runtime power transitions, confirms PCIe control, AER status/mask/severity, MSI/MSI-X, ACS/PASID/ARI, and GPU IOV event state are restored or intentionally reset.
