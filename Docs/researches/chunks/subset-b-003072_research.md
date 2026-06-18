# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 9886-12358

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask header. It describes bitfield geometry for PCI/PCIe configuration-space registers exposed by the NBIO/BIF configuration decoder, primarily for `BIF_CFG_DEV0_EPF6_0`, `BIF_CFG_DEV0_EPF7_0`, and the beginning of `BIF_CFG_DEV1_EPF0_0`. The chunk also contains the tail of `BIF_CFG_DEV0_EPF5_0` PCIe advanced error reporting and extended capability definitions.

The file is hardware metadata rather than executable code. Each field is exported as a preprocessor pair:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`: the already-shifted mask for the field.

The range contains 2,131 `#define` entries over 336 commented blocks. There are 1,065 `__SHIFT` definitions and 1,066 `_MASK` definitions. The one-mask imbalance is intentional for this line range: it starts at the last four masks for `BIF_CFG_DEV0_EPF5_0_PCIE_UNCORR_ERR_SEVERITY`, whose matching shifts are in the previous chunk. The range ends at line 12358 in the middle of `BIF_CFG_DEV1_EPF0_0_DEVICE_CNTL2`; the last three masks for `LTR_EN`, `OBFF_EN`, and `END_END_TLP_PREFIX_BLOCKING` are in the next chunk.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or typedefs in this chunk. Its API is the generated macro namespace consumed by AMDGPU register access helpers.

The main register groups are:

- `BIF_CFG_DEV0_EPF5_0_PCIE_*`: the tail of endpoint/function 5 PCIe advanced error reporting and extended capabilities. The chunk begins with uncorrectable-error severity masks for internal errors, memory-controller blocked TLPs, AtomicOp egress blocking, and TLP prefix blocking. It then covers correctable error status/mask bits, advanced error capability/control, TLP header and prefix logs, BAR enhanced capability controls for BAR1 through BAR6, power-budget capability/data fields, dynamic power allocation (`DPA`) fields, access control services (`ACS`) capability/control, and alternative routing-ID interpretation (`ARI`) capability/control.
- `BIF_CFG_DEV0_EPF6_0_*`: a complete PCI configuration-space field set for device 0, endpoint/function 6. It includes vendor/device IDs, PCI command/status, revision/class/header/BIST fields, BAR1-BAR6, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, vendor capability, power-management capability/status, USB-style `SBRN`, `FLADJ`, `DBESL_DBESLD`, PCIe capability and link/device controls, MSI/MSI-X capability tables, SATA capability/index/data fields, vendor-specific enhanced capability fields, PCIe AER status/mask/severity/log fields, BAR enhanced capability controls, power budget, DPA, ACS, and ARI.
- `BIF_CFG_DEV0_EPF7_0_*`: a second complete PCI configuration-space field set for device 0, endpoint/function 7. Its layout mirrors EPF6 in this chunk: identity, command/status, BARs, power management, PCIe device/link capability and control, MSI/MSI-X, SATA, vendor-specific extended capability, AER, BAR enhanced capability, power budget, DPA, ACS, and ARI.
- `BIF_CFG_DEV1_EPF0_0_*`: the beginning of device 1, endpoint/function 0 configuration-space definitions. This chunk covers identity, PCI command/status, class/header/BIST, BARs, adapter ID, ROM base, capability pointer, interrupt metadata, vendor and power-management capabilities, PCIe capability, device/link capability and control, device/link status, Device Capability 2, and most of Device Control 2.

Important field families include:

- PCI command and status bits: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`, target/master abort state, parity/system-error state, capability-list presence, and interrupt status.
- BAR and ROM mapping fields: `BASE_ADDR` for BAR1-BAR6 and ROM base, plus enhanced BAR capability/control fields such as `BAR_SIZE_SUPPORTED`, `BAR_INDEX`, `BAR_TOTAL_NUM`, and `BAR_SIZE`.
- PCIe device/link controls: max payload/read-request sizes, relaxed ordering, no-snoop, extended tag, FLR initiation, link disable/retrain, common clock, extended sync, clock power management, hardware autonomous width/speed disable, and bandwidth interrupt enables/status.
- PCIe Device Capability 2 and Device Control 2 fields: completion timeout support/value/disable, ARI forwarding, AtomicOp request/routing/completion support, ID-based ordering request/completion enables, LTR, OBFF, TPH completer support, extended format, end-to-end TLP prefix support/blocking, and max TLP prefixes.
- MSI/MSI-X fields for EPF6 and EPF7: capability IDs, message control, address/data registers, per-vector masking, pending bits, table BIR/offset, and PBA BIR/offset.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity for DLP, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, memory-controller blocked TLP, AtomicOp egress block, and TLP prefix block. Correctable error fields include receiver error, bad TLP/DLLP, replay rollover/timeout, advisory nonfatal, correctable internal error, and header-log overflow.
- Error log and extended capability fields: AER header logs, TLP prefix logs, first-error pointer, ECRC generation/check capabilities and enables, multi-header receive controls, and TLP prefix log presence.
- Power and topology fields: power-management capability/status/control, PCIe power-budget data selection/data/capability, dynamic power allocation substates and transition latency, ACS source validation/translation/blocking/redirect/completion controls, and ARI next-function/function-group controls.
- SATA and vendor-specific fields on EPF6/EPF7: `SATA_CAP_0`, `SATA_CAP_1`, indirect index/data pairs, vendor-specific capability ID/version/next-pointer/header, and two vendor-specific payload registers.

These macros are normally used with address macros from `nbio_7_0_offset.h`, defaults from `nbio_7_0_default.h`, and AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and indexed PCIe/NBIO accessors.

## Control Flow and Runtime Behavior

This chunk has no direct control flow. Inclusion of the header only makes constants available for compile-time expansion. Runtime behavior occurs in AMDGPU code that reads a register, extracts a field with its mask and shift, or modifies a field in a read/modify/write sequence.

The represented hardware behavior is PCIe configuration and capability behavior. Device/function identity and class fields are read by PCI enumeration and driver bring-up. Command/status fields govern whether the function accepts I/O, memory, and bus-mastering transactions and report legacy PCI error state. BAR and ROM fields represent address apertures advertised to the PCI core or internally decoded by NBIO. Capability-list and enhanced-capability next-pointer fields define how software walks the PCI/PCIe capability chains.

PCIe link and device fields participate in link configuration and error recovery. `DEVICE_CNTL` and `LINK_CNTL` settings can change payload size, read-request size, ordering behavior, FLR, link retraining, common clock configuration, clock power management, and bandwidth notifications. The matching `DEVICE_STATUS`, `LINK_STATUS`, `DEVICE_CAP2`, and `LINK_CAP` fields provide readback for negotiated link width/speed, training state, data-link active state, pending transactions, and optional PCIe features.

The AER groups define how hardware reports and classifies PCIe errors. Status registers latch error causes, mask registers suppress selected reporting, severity registers classify uncorrectable conditions as fatal or nonfatal, and log registers capture TLP headers or prefixes associated with faults. Driver-visible error handling depends on these bit positions being correct because a single wrong shift can misclassify link errors or hide actionable AER state.

MSI/MSI-X fields describe interrupt-message capability layout for EPF6 and EPF7. Message-control bits advertise 64-bit address support, per-vector masking, enabled vectors, table size, and MSI-X enable/function-mask state. Table and PBA fields carry BIR and offset values used to locate MSI-X resources.

Power-management, DPA, ACS, and ARI fields represent optional PCIe capabilities. Power-management control selects D-states and PME behavior. DPA fields describe substate count, transition latency, power-allocation scaling, selected substate, and enable/status. ACS bits determine request validation, peer-to-peer redirect/blocking, upstream forwarding, egress control, and direct translated peer-to-peer support. ARI bits expose next-function and function-group routing controls.

## State and Persistence

The header itself owns no state, allocates no memory, performs no I/O, and persists nothing. The state described by these macros lives in NBIO/PCIe hardware registers and in any software state that caches or interprets those registers.

State categories in this chunk include:

- Configuration state: PCI command enables, BAR/ROM address fields, MSI/MSI-X enables and table/PBA locations, PCIe device/link controls, Device Control 2 settings, power-management state, DPA enable/substate controls, ACS controls, and ARI forwarding/group controls.
- Capability/read-only identity state: vendor/device IDs, revision/class codes, header type, BIST capability, subsystem IDs, capability IDs, capability versions, capability next pointers, supported link speed/width, supported payload/read-request features, and optional PCIe feature support bits.
- Runtime status state: PCI status bits, interrupt status, PMI/PME status and data, device error status, link training and bandwidth status, data-link active state, AER correctable/uncorrectable status, first-error pointer, TLP header/prefix logs, DPA status, and MSI pending bits.
- Error-classification and masking state: AER uncorrectable masks, correctable masks, and severity fields. These settings determine which hardware errors become visible to operating-system AER handling and whether uncorrectable errors are reported as fatal.
- Reserved or opaque fields: several capability and status registers include reserved masks. The generated layout documents bit occupation, but runtime code should generally preserve reserved bits unless the hardware specification or firmware flow requires a specific value.

Reset values and persistence across GPU reset, function-level reset, suspend/resume, and power-gating are not encoded here. They come from ASIC defaults, firmware initialization, PCIe reset semantics, and companion `nbio_7_0_default.h` definitions. A wrong generated mask persists as a software ABI problem: every compiled caller using the macro will read or write the wrong hardware bits until the header is regenerated or corrected.

## Dependencies and Integration Points

Direct companion generated files are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`, which provides matching register address macros such as `cfgBIF_CFG_DEV0_EPF6_0_VENDOR_ID`, `cfgBIF_CFG_DEV0_EPF6_0_PCIE_UNCORR_ERR_STATUS`, `cfgBIF_CFG_DEV0_EPF7_0_VENDOR_ID`, and `cfgBIF_CFG_DEV1_EPF0_0_VENDOR_ID`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`, which provides reset/default macros for the same generated register namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`, which is included with this header by NBIO v7.0 driver code for SMN-level register access.

In-tree consumers of `nbio_7_0_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, the main NBIO v7.0 implementation. It includes the offset/default/shift-mask headers and uses SOC15 register helpers for NBIO programming, including read/modify/write field operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`, which includes the same generated NBIO v7.0 mask header as part of SOC15 ASIC integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, which includes the header through the power-management stack.

This exact chunk is most relevant to PCIe enumeration, NBIO function configuration, SR-IOV or multi-function exposure, PCIe error handling, interrupt capability setup, link management, power management, ACS/ARI routing, and low-level ASIC bring-up. Because the chunk covers endpoint/function replicas, name alignment across EPF5, EPF6, EPF7, and DEV1/EPF0 is an important integration contract.

## Risks

- Generated-header drift is the primary risk. If any `_MASK` or `__SHIFT` differs from the ASIC register database, all users compile successfully but manipulate the wrong bit positions.
- The chunk starts and ends inside register blocks. The first four `EPF5` severity masks depend on shifts in the prior chunk, and the `DEV1_EPF0_DEVICE_CNTL2` block is missing its final three masks until the next chunk. Whole-file reconciliation must join adjacent chunks before pair-completeness checks.
- PCIe AER bit errors have high diagnostic impact. A wrong status, mask, or severity macro can hide correctable errors, misreport fatal/nonfatal state, or make captured TLP header/prefix logs appear unrelated to the actual fault.
- PCI command, BAR, ROM, and bus-mastering masks affect address decoding and DMA enablement. Incorrect use can break enumeration, expose the wrong aperture, or leave a function unable to access memory.
- Device/link control masks are sequencing-sensitive. Bad shifts for FLR, retrain, common-clock configuration, payload size, read-request size, LTR, OBFF, ARI, AtomicOp, or TLP-prefix controls can cause intermittent link failures or interoperability issues that only appear on specific platforms or switches.
- MSI/MSI-X field errors can misplace table or PBA resources or leave interrupts masked/enabled incorrectly, producing lost interrupts or spurious interrupt behavior.
- ACS and ARI fields affect request routing and isolation. Incorrect masks can weaken peer-to-peer isolation, break virtual function/function-group discovery, or route completions through the wrong path.
- Several blocks are duplicated across EPF6 and EPF7. Copy/generation skew between functions may not be noticed by builds because the macro names remain valid.
- Reserved fields should not be used as ordinary writable controls. Callers assembling raw register values without preserving reserved bits can trigger undocumented hardware behavior.

## Test and Validation Signals

Useful validation combines generated-header consistency, build coverage, and hardware behavior checks:

- Build AMDGPU paths that include `nbio_7_0_sh_mask.h`, especially `nbio_v7_0.c`, `soc15.c`, and the SMU10 PowerPlay include path, to catch syntax or missing-name regressions.
- Run static checks over the complete `nbio_7_0_sh_mask.h` file, not just this chunk, to verify every field has both `__SHIFT` and `_MASK`, masks are compatible with shifts, and masks are contiguous for ordinary scalar fields.
- Cross-check register names against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so each `BIF_CFG_DEV0_EPF6_0_*`, `BIF_CFG_DEV0_EPF7_0_*`, and `BIF_CFG_DEV1_EPF0_0_*` field block has a matching address/default where expected.
- Compare EPF6 and EPF7 duplicated layouts mechanically to detect unintended field or mask drift between endpoint functions.
- Exercise PCIe enumeration and configuration on NBIO 7.0 hardware: BAR sizing, ROM base handling, bus mastering, memory access enablement, FLR, payload/read-request sizing, and link retraining.
- Validate interrupt paths that depend on these capability layouts by testing MSI and MSI-X enable/disable, vector masking, pending bits, and table/PBA decoding for the affected functions.
- Trigger or inspect PCIe AER paths where available: correctable errors, completion timeout, unsupported request, ECRC, malformed TLP, ACS violation, and header/prefix log capture.
- Exercise suspend/resume, GPU reset, runtime power management, and SR-IOV or multi-function configurations if supported, because these flows stress power-management, DPA, ACS, ARI, and function-level reset fields.
