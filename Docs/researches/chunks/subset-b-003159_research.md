# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 31261-31871

## Purpose

This chunk is the final generated AMD NBIO 7.2.0 offset-map slice for device 2 endpoint functions in the BIF PCI configuration decode space. It starts in the middle of the `BIF_CFG_DEV2_EPF1_1` PCIe Advanced Error Reporting log area, completes the remaining `EPF1_1` enhanced-capability offsets, then defines the complete `BIF_CFG_DEV2_EPF2_1` endpoint configuration-space register offsets through the end of the header.

The file contains no executable driver logic. Its public surface is a set of C preprocessor constants that name hardware register offsets and their register-access base indices. AMDGPU and display code include this header so generated register names can be passed to the AMD register access macros for NBIO 7.2 hardware.

## Public Surface In This Chunk

The exported API is 603 `#define` constants in the generated offset-header pattern:

- `regBIF_CFG_DEV2_EPFx_1_<REGISTER>` gives the encoded MMIO/register address for a PCI/PCIe configuration register.
- `regBIF_CFG_DEV2_EPFx_1_<REGISTER>_BASE_IDX` gives the register access base index, which is consistently `5` throughout this chunk.

The `EPF1_1` portion continues from the previous chunk. It starts with `PCIE_HDR_LOG1_BASE_IDX`, then covers AER header log registers 2-3, TLP prefix logs 0-3, BAR enhanced capability registers for BAR1-BAR6, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, TPH requester capability/control, and TPH steering table entries 0-63.

The `EPF2_1` block starts at the generated marker `addressBlock: nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`. It defines standard endpoint PCI configuration header registers, PCI power-management capability registers, USB-related capability bytes such as `SBRN`, `FLADJ`, and `DBESL_DBESLD`, PCIe device/link capability and control registers, MSI/MSI-X registers, vendor-specific enhanced capability registers, AER registers and logs, BAR enhanced capability registers, power budgeting, DPA, ACS, PASID, ARI, TPH requester registers, and TPH steering table entries 0-63. The chunk then closes the header guard.

## Important Register Families

The `EPF1_1` tail is entirely PCIe enhanced-capability addressing. AER log offsets identify the captured header and TLP prefix fields associated with PCIe errors. BAR enhanced capability offsets describe the capability/control pairs for endpoint BAR1 through BAR6. Power budgeting registers expose the data selector, data, and capability slots used by software to inspect advertised power budget information.

The DPA group defines capability, latency indicator, status/control, and eight substate power allocation offsets. Several DPA names intentionally share offsets: `PCIE_DPA_STATUS` and `PCIE_DPA_CNTL` both resolve to `0x3fff80900497`, while substate allocation entries 0-3 share `0x3fff80900498` and entries 4-7 share `0x3fff80900499`; field-level access is supplied by the companion shift/mask headers. ACS, PASID, and ARI expose address translation/isolation and function-numbering capability/control registers. The TPH requester group includes the capability/control registers and 64 steering table logical entries, with pairs of table entries sharing each 32-bit register address.

The `EPF2_1` standard PCI header block maps endpoint identity, command/status, class code, cache/latency/header/BIST bytes, six BARs, CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and latency grant fields. Its PM capability group includes capability list, capability, and status/control offsets. The PCIe capability group covers device and link capability/control/status registers, including PCIe 2.0 device/link capability and control/status offsets.

The `EPF2_1` interrupt groups define both MSI and MSI-X address/data/table/PBA locations, including 32-bit and 64-bit MSI data, mask, and pending locations. The AER group maps uncorrectable and correctable error status/mask/severity, capability/control, four header log registers, and four TLP prefix logs. The final enhanced-capability groups mirror the `EPF1_1` tail: BAR enhanced capability, power budgeting, DPA, ACS, PASID, ARI, TPH requester, and TPH steering table entries 0-63.

## Control Flow And State

There is no runtime control flow, branching, allocation, locking, or function dispatch in this header slice. The effective flow is compile-time substitution:

1. A translation unit includes `nbio_7_2_0_offset.h`.
2. The caller references a `regBIF_CFG_DEV2_EPF1_1_*` or `regBIF_CFG_DEV2_EPF2_1_*` macro.
3. AMDGPU register helper macros use the offset plus the `BASE_IDX` to reach the intended NBIO register aperture.
4. Field interpretation, masking, and composition are performed with companion shift/mask headers, not in this offset header.

This chunk stores no software state and has no persistence layer. The persistent and side-effectful state lives in the GPU's NBIO PCI/PCIe configuration registers. External callers decide when those registers are read, written, or cleared; this header only binds symbolic names to addresses.

## Dependencies And Integration Points

The mechanical dependency is the AMD generated register-header convention. This offset header must stay in sync with the companion NBIO 7.2.0 shift/mask and default headers, and with the ASIC register generator that produced the `reg...` and `_BASE_IDX` names. Shared offsets in the DPA and TPH groups depend on field masks from the corresponding `_sh_mask` file to distinguish logical fields within the same 32-bit register.

Direct inclusion points in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and display resource files under `drivers/gpu/drm/amd/display/dc/resource/dcn301/` and `dcn31/`. Those consumers do not get behavior from the header by itself; they use it as a register-address namespace for NBIO setup, feature discovery, link/power handling, and display resource code that needs NBIO 7.2 register definitions.

The semantic dependencies are the PCI and PCI Express configuration-space specifications: standard endpoint headers, PM capability, PCIe capability, MSI, MSI-X, vendor-specific enhanced capabilities, AER, enhanced BAR capability, power budgeting, DPA, ACS, PASID, ARI, and TPH requester/steering-table layout. The generated names encode those specifications but do not enforce valid programming sequences.

## Risks And Maintenance Notes

- The chunk begins mid-register-family: `EPF1_1_PCIE_HDR_LOG1_BASE_IDX` appears without its paired offset macro in this slice because the offset is in the previous chunk. The merged per-file report must reconcile adjacent chunks for a complete `EPF1_1` view.
- Every `_BASE_IDX` in this chunk is `5`; if the ASIC register generator or access macros expect a different base for a future NBIO variant, stale constants would route reads or writes to the wrong aperture.
- Repeated logical entries share physical offsets in DPA substate allocations and TPH steering tables. Callers must use the correct shift/mask definitions and avoid treating each logical name as an independent 32-bit register.
- AER status/log registers, MSI/MSI-X state, ACS/PASID/ARI controls, DPA controls, and TPH controls can affect interrupt delivery, isolation, error reporting, endpoint power behavior, and PCIe transaction handling. The presence of an offset macro does not imply that blind read-modify-write is safe.
- The `EPF2_1` block is highly repetitive relative to neighboring endpoint-function blocks and NBIO generations. Review drift is easy to miss because many names differ only by function prefix or table index.
- This header ends immediately after `EPF2_1_PCIE_TPH_ST_TABLE_63`; there are no trailing generated blocks after the header guard close. Any expected later capability for this endpoint must be verified against the hardware spec or regenerated headers.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for translation units that include `nbio_7_2_0_offset.h`, especially `amdgpu/nbio_v7_2.c` and the DCN 3.01/3.1 display resource files.
- Static generation checks that every non-partial register offset in the chunk has a matching `_BASE_IDX`, and that all base indices remain `5`.
- Cross-header checks that `EPF1_1` and `EPF2_1` register names here have corresponding field definitions in the NBIO 7.2.0 shift/mask header where the registers are not full-width raw values.
- Hardware or register-dump validation on NBIO 7.2 systems comparing decoded `EPF2_1` vendor/device/class fields, BARs, PM/PCIe capabilities, MSI/MSI-X tables, AER status/logs, ACS/PASID/ARI state, DPA state, and TPH steering table locations against PCI config dumps such as `lspci -vvxxx` and AMDGPU debug register reads.
- Error-path testing that observes or injects AER conditions and confirms that the header log and TLP prefix log offsets identify the intended captured error data.
- Power and transaction-path tests around power budgeting, DPA substate allocation, PASID/ARI exposure, ACS isolation settings, and TPH steering behavior, with special attention to registers where multiple logical names share one physical offset.
