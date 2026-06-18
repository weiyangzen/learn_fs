# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 36660-39092

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It contains register-field geometry for NBIF/BIF PCIe configuration-space registers, not executable driver logic. The constants let NBIO 7.4 code combine matching register offsets from `nbio_7_4_offset.h` with bit shifts and masks from this file when decoding or programming hardware registers.

The range starts at the tail of `BIF_CFG_DEV0_EPF0_VF7_0`, covers complete `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, `vf9_bifcfgdecp`, and `vf10_bifcfgdecp` address blocks, then enters `vf11_bifcfgdecp` and stops after `BIF_CFG_DEV0_EPF0_VF11_0_LINK_STATUS2`. These are virtual-function PCI configuration images for device 0, endpoint PF0, virtual functions 8 through 11, plus the final ATS/ARI definitions for VF7.

## Public Surface

The public surface in this slice is generated C preprocessor macros only. There are 2,139 `#define` entries in 282 commented register groups: 1,072 `__SHIFT` constants and 1,067 canonical `_MASK` constants. A broader text search sees additional `_MASK` strings because some hardware fields are themselves named `MASK`, producing valid names such as `MSI_MASK__MSI_MASK_MASK`.

Macro names follow the established AMDGPU generated-register convention:

- `BIF_CFG_DEV0_EPF0_VF8_0_<REGISTER>__<FIELD>__SHIFT` gives the zero-based field bit position.
- `BIF_CFG_DEV0_EPF0_VF8_0_<REGISTER>__<FIELD>_MASK` gives the pre-shifted field mask.
- `VF9_0`, `VF10_0`, and `VF11_0` prefixes repeat the same layout for different virtual-function config images.

There are no functions, structs, typedefs, enums, locks, allocations, or runtime APIs in this chunk. The API contract is exact macro spelling plus numeric shift/mask value.

## Register Coverage

The VF7 tail contains the end of its advanced PCIe capability chain:

- TLP prefix log dwords 0-3.
- ATS enhanced capability list, ATS capability, and ATS control fields, including invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.
- ARI enhanced capability list, ARI capability, and ARI control fields, including next function number, function-group capabilities, and function-group enables.

The VF8, VF9, and VF10 blocks are complete in this chunk. Each block covers the same virtual-function PCI configuration shape:

- Conventional PCI header fields: vendor ID, device ID, command, status, revision/class-code bytes, cache-line size, latency timer, header type, BIST, six BAR dwords, adapter/subsystem ID, ROM BAR, capability pointer, and interrupt line/pin.
- PCIe capability fields: capability-list header, PCIe capability header, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and reserved slot capability/control/status 2 fields.
- Interrupt capabilities: MSI capability-list/header fields, MSI enable/multi-message/64-bit/per-vector-mask controls, MSI message address/data, MSI mask and pending registers, and MSI-X capability, table, and PBA fields.
- Vendor-specific enhanced capability: VSEC capability-list metadata, VSEC header, and two full-width scratch registers.
- Advanced Error Reporting: AER capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, TLP header logs 0-3, and TLP prefix logs 0-3.
- Translation and routing capabilities: ATS enhanced capability/capability/control and ARI enhanced capability/capability/control.

The VF11 block begins the same layout and reaches through PCIe link status 2:

- PCI identity/header/BAR/capability-pointer fields.
- PCIe device and link capability/control/status groups through `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI, MSI-X, VSEC, AER, ATS, and ARI groups for VF11 are outside this chunk and must be supplied by the next chunk.

## Field Semantics

The command and status fields expose standard PCI control and observation bits: I/O enable, memory enable, bus mastering, SERR, interrupt disable, capability-list presence, abort/error indicators, parity reporting, and interrupt status. The BAR and ROM BAR masks are full-width address payload fields; actual sizing, decode enablement, and access permissions are determined by PCI config semantics and surrounding driver or firmware policy.

The PCIe capability fields describe per-VF protocol support and policy. `DEVICE_CAP` advertises maximum payload, phantom function, extended tag, acceptable latencies, role-based error reporting, slot power fields, and FLR capability. `DEVICE_CNTL` controls error enables, relaxed ordering, payload size, extended tag, no-snoop, read request size, and FLR initiation. `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe and control link speed, width, ASPM/PM, retrain/disable, common clock, clock power management, bandwidth-management interrupts, current speed/width, training state, slot clock configuration, and data-link active state.

The capability 2 fields expose newer PCIe behavior: completion timeout policy, ARI forwarding, atomic operation routing/completion support, ID-based ordering, LTR, TPH completer support, ten-bit tags, OBFF, extended format and end-to-end TLP prefix support, emergency power reduction, target link speed, compliance controls, de-emphasis, 8 GT/s equalization status, crosslink state, RTM presence detection, and downstream component presence.

The interrupt sections model MSI and MSI-X config-space structures. MSI fields cover enablement, multiple-message capability/enables, 64-bit message addressing, per-vector masking, address/data payloads, vector masks, and pending bits. MSI-X fields expose table size, function mask, enable bit, and table/PBA BIR and offset fields. These constants only describe bit layout; actual interrupt programming and masking are performed by PCI core, AMDGPU, firmware, or virtualization code elsewhere.

The AER groups expose error-observation and error-policy fields for data link protocol errors, surprise-down, poisoned TLPs, flow-control protocol errors, completion timeout/abort, unexpected completions, receiver overflow, malformed TLPs, ECRC, unsupported requests, ACS violations, internal errors, multicast blocked TLPs, atomic egress blocking, and TLP prefix blocking. Status, mask, and severity registers intentionally share most field names, so the register prefix is critical.

ATS and ARI fields are virtualization and IOMMU relevant. ATS capability/control fields describe invalidation queue depth, page alignment and global invalidate support, smallest translation unit, and ATC enable. ARI fields describe next-function routing and multifunction/ACS function grouping. For these VF-prefixed blocks, misuse can affect virtual function enumeration, request routing, or translated DMA behavior.

## Control Flow and State

There is no control flow in this header. The practical compile-time flow is:

1. An NBIO 7.4 include site includes this generated shift/mask header together with the matching offset header.
2. Driver code chooses a `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` address macro from `nbio_7_4_offset.h`.
3. It uses the corresponding `BIF_CFG_DEV0_EPF0_VF*_0_*__FIELD__SHIFT` and `_MASK` macros with AMDGPU register helpers or direct bit operations.
4. The actual read, write, read-modify-write, polling, or error decode occurs outside this header.

This file stores no software state and persists nothing. The represented state lives in NBIO/BIF PCI configuration-space hardware. Some fields are read-only capability or identity fields, some are writable configuration policy, some are hardware-updated status bits, and some are sticky error/log/pending fields whose clearing rules are defined by PCIe and AMD hardware specifications. Persistence across FLR, VF reset, GPU reset, suspend/resume, BACO, or power-gating transitions is not encoded here.

## Dependencies and Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`. For example, this chunk's `BIF_CFG_DEV0_EPF0_VF8_0_VENDOR_ID__VENDOR_ID_MASK` pairs with `cfgBIF_CFG_DEV0_EPF0_VF8_0_VENDOR_ID`, and the VF11 link-status-2 masks pair with `cfgBIF_CFG_DEV0_EPF0_VF11_0_LINK_STATUS2`. Default-value headers for neighboring NBIO versions show the same generated register family, but this chunk must remain synchronized with the NBIO 7.4 offset map.

In-tree include sites for `nbio_7_4_sh_mask.h` include `amdgpu/nbio_v7_4.c`, SMU power-management files for Arcturus, Aldebaran, and SMU 13.0.6, plus Vega20 PowerPlay/HWMgr code. The specific VF8-VF11 constants may be consumed indirectly through common generated-register helpers, debug/register dump paths, virtualization setup, PCIe error handling, interrupt setup, IOMMU/ATS coordination, or firmware-mediated NBIO programming.

External semantic dependencies are the PCI and PCI Express configuration-space specifications plus MSI, MSI-X, AER, ATS, ARI, LTR, OBFF, atomic operations, ten-bit tags, TLP prefixing, FLR, and AMD NBIO/GPU virtualization register definitions. The macros do not encode access width, reset value, read/write permission, write-one-to-clear behavior, required sequencing, or firmware ownership.

## Risks and Maintenance Notes

- The chunk starts mid-block. VF7 identity, PCIe, MSI/MSI-X, VSEC, and most AER definitions are in the previous chunk; this chunk only contains VF7's TLP prefix log tail plus ATS/ARI.
- The chunk ends mid-block. VF11 is only covered through link status 2; its MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions continue in the next chunk.
- VF8, VF9, and VF10 are intentionally near-identical. Copying a mask from one VF prefix while using another VF's offset can compile cleanly while decoding or programming the wrong config image.
- AER `STATUS`, `MASK`, and `SEVERITY` groups have very similar fields. Confusing them can suppress errors, over-report errors, or misclassify severity.
- MSI/MSI-X mask and pending field names produce generated symbols with repeated `MASK` text. Tooling must preserve those names exactly.
- Link-control and capability-2 fields can affect link stability and performance if used for writes: target speed, retrain, link disable, autonomous speed/width behavior, ASPM, compliance, de-emphasis, LTR, OBFF, atomic operations, and TLP prefix policy are not interchangeable diagnostics.
- ATS and ARI fields affect IOMMU translation, request routing, and VF enumeration. Incorrect masks or wrong-prefix usage can break isolation or guest behavior.
- Full-width `0xFFFFFFFFL` masks for BARs, logs, scratch registers, message addresses, and payload registers should not be interpreted as permission to write arbitrary all-ones values.
- Generated `L`-suffixed masks should be used with normal register-width-aware unsigned operations to avoid host integer width or sign-extension surprises in composed values.

## Test and Validation Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware or simulator coverage:

- Build AMDGPU configurations that include NBIO 7.4 headers, especially `amdgpu/nbio_v7_4.c`, Arcturus/Aldebaran/SMU 13.0.6 power-management code, and Vega20 PowerPlay code.
- Cross-check every visible `BIF_CFG_DEV0_EPF0_VF8_0`, `VF9_0`, `VF10_0`, and partial `VF11_0` register group against matching `cfgBIF_CFG_DEV0_EPF0_*` offsets in `nbio_7_4_offset.h`.
- Run mechanical pair checks after adjacent chunks are merged: each complete field should have both `__SHIFT` and `_MASK`, with expected exceptions at the VF7 start boundary and VF11 end boundary.
- Compare this generated header slice against AMD's authoritative NBIO 7.4 register database, especially AER status/mask/severity, MSI/MSI-X table/PBA fields, ATS control, ARI routing, and link capability/control/status 2 fields.
- Decode PCI config-space dumps for VF8, VF9, VF10, and VF11 on NBIO 7.4 hardware or simulation and compare vendor/device/class, BAR, capability chain, PCIe device/link fields, MSI/MSI-X, AER, ATS, and ARI values.
- Exercise SR-IOV or mediated virtualization flows that expose these VFs, checking VF enumeration, BAR sizing, FLR capability, MSI/MSI-X delivery, ATS enablement, ARI routing, and absence of cross-VF leakage.
- Inject or observe PCIe AER events and verify uncorrectable/correctable status, masks, severity, first-error pointer, header logs, and TLP prefix logs decode to the expected fields.
- Exercise PCIe link training and recovery paths while observing current speed/width, training state, DL active, bandwidth-management status, target speed, compliance, de-emphasis, and 8 GT/s equalization indicators.

## Chunk Boundary Notes

Lines 36660-36716 finish the `BIF_CFG_DEV0_EPF0_VF7_0` capability chain with TLP prefix log, ATS, and ARI fields. Lines 36717-37400 cover complete `BIF_CFG_DEV0_EPF0_VF8_0` definitions. Lines 37401-38084 cover complete `BIF_CFG_DEV0_EPF0_VF9_0` definitions. Lines 38085-38768 cover complete `BIF_CFG_DEV0_EPF0_VF10_0` definitions. Lines 38769-39092 begin `BIF_CFG_DEV0_EPF0_VF11_0` and stop at `LINK_STATUS2`; the next chunk is required for the rest of VF11.
