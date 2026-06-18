# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 4911-7345

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 register-offset header. It provides preprocessor constants for PCIe/NBIF configuration-space windows in the `nbio_nbif0` block, covering the end of device 1 endpoint-function 1, the device 2 root-complex function, device 2 endpoint functions 0 through 6, and the beginning of the RCC endpoint control block for device 0.

The constants map symbolic register names to dword offsets plus a companion `_BASE_IDX` value. In this range every `_BASE_IDX` is `5`, which tells AMDGPU's generated register-access layer which register base array entry to use when translating a symbolic register into an MMIO/config-space access. The source is hardware metadata rather than executable logic; it lets C code refer to PCIe capability, error-reporting, BAR, MSI/MSI-X, DPA, ACS, PASID, ARI, lane-training, and endpoint-control registers without hard-coding raw offsets.

## Important APIs, Types, and Macros

There are no C functions, structs, typedefs, or enums in this range. The public interface is the generated macro pattern:

- `reg<block/register>`: the register offset used by AMDGPU register helper macros.
- `reg<block/register>_BASE_IDX`: the generated base-index selector, consistently `5` in this chunk.

The chunk contains 2,399 `#define` lines. The address blocks inside the assigned line range are:

- Tail of `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`: only the final VF resizable-BAR registers for BAR2 through BAR6 and the RTR enhanced-capability/data registers remain in this chunk.
- `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp`, base address `0x10102000`: device 2 root-complex configuration registers. It includes standard PCI configuration header aliases, bridge bus/window registers, PMI/PCIe/MSI/SSID/MSI-map capability registers, vendor-specific and VC capability registers, AER status/mask/severity/header-log registers, PCIe link/equalization and lane margining registers for lanes 0 through 15, and RTR capability/data registers.
- `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base address `0x10150000`: device 2 endpoint function 0. EPF0 is the broadest endpoint block in this chunk, including base PCI header/BAR registers, vendor and adapter IDs, MSI/MSI-X, SATA capability/IDP registers, VC resources, AER status/masks/logs, BAR enhanced capability registers, power-budgeting, DPA, ACS, PASID, LTR, ARI, 16 GT/s parity mismatch status, lane margining, and RTR registers.
- `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, base address `0x10151000`.
- `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`, base address `0x10152000`.
- `nbio_nbif0_bif_cfg_dev2_epf3_bifcfgdecp`, base address `0x10153000`.
- `nbio_nbif0_bif_cfg_dev2_epf4_bifcfgdecp`, base address `0x10154000`.
- `nbio_nbif0_bif_cfg_dev2_epf5_bifcfgdecp`, base address `0x10155000`.
- `nbio_nbif0_bif_cfg_dev2_epf6_bifcfgdecp`, base address `0x10156000`.
- `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`, base address `0x10131000`: the beginning of an RCC endpoint port-control decode block. This chunk includes scratch, endpoint PCIe control, interrupt control/status, RX/bus/config controls, TX LTR control, function 0 DPA capability/control/status, and DPA substate power-allocation registers 0 through 7.

The endpoint-function blocks use a repeated schema. EPF0 has extra VC, LTR, parity mismatch, and lane-margining coverage. EPF1, EPF3, and EPF4 each have 256 macro lines in this range, while EPF2, EPF5, and EPF6 have 250 macro lines. Those smaller endpoint chunks omit a few registers present in the neighboring functions, so consumers should use the exact function-specific symbol rather than assuming all EPFs expose identical offsets.

Key register families are:

- Standard PCI configuration header aliases: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_*`, `CAP_PTR`, `ROM_BASE_ADDR`, and interrupt-line/pin fields.
- Root-complex bridge state: device 2 RC0 includes bus-number/latency, I/O base/limit, memory base/limit, prefetchable base/limit, upper window registers, bridge interrupt control, extended bridge control, slot/root capability/control/status registers, and secondary status.
- PCIe capability state: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and the corresponding `*2` registers where present.
- MSI/MSI-X state: MSI message control, address, data, 64-bit data, mask, and pending registers, plus MSI-X table and PBA registers on endpoint functions.
- PCIe advanced error reporting: enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability control, header logs 0 through 3, and TLP prefix logs where present.
- Capability-extension blocks: vendor-specific capability, virtual-channel capability/resources, BAR enhanced capability controls, power-budgeting, dynamic power allocation, ACS, PASID, ARI, LTR, lane margining, and RTR registers.
- Low-level endpoint controls in the RCC block: `EP_PCIE_SCRATCH`, `EP_PCIE_CNTL`, `EP_PCIE_INT_CNTL`, `EP_PCIE_INT_STATUS`, `EP_PCIE_RX_CNTL2`, `EP_PCIE_BUS_CNTL`, `EP_PCIE_CFG_CNTL`, and `EP_PCIE_TX_LTR_CNTL`.

These macros are normally consumed through AMDGPU register helpers and SOC15/NBIO accessors that combine register offsets, base indices, instance selection, and field masks from companion headers.

## Control Flow and Runtime Behavior

This header chunk has no runtime control flow. It is included at compile time and contributes integer constants to later read, write, and read-modify-write operations in AMDGPU's NBIO/PCIe code.

The implied runtime flows are:

1. Device discovery and initialization code can read standard PCI header and capability-list registers for the device 2 root-complex and endpoint-function windows using these symbolic offsets.
2. PCIe setup code can program command/status, BARs, bridge windows, link control, slot/root control, MSI/MSI-X, and vendor-specific controls by pairing these offsets with the matching shift/mask definitions and access wrappers.
3. Error-handling paths can inspect AER uncorrectable/correctable status and logs, then mask or classify errors through the corresponding mask and severity registers.
4. Power and latency-management paths can access DPA, power-budgeting, LTR, and endpoint TX LTR controls. DPA state is split into capability/status/control registers plus repeated substate power-allocation entries.
5. I/O virtualization and isolation paths can use ACS, PASID, ARI, BAR enhanced capability, and the tail of the VF resizable-BAR registers to configure routing, function addressing, and BAR sizing behavior.
6. Link validation or debug code can use RC0 and EPF0 lane-equalization/lane-margining registers for lanes 0 through 15, plus parity mismatch status at 16 GT/s where defined.
7. RCC endpoint control paths can use the final block to adjust endpoint-specific PCIe control, interrupt routing/status, RX behavior, bus/config behavior, and LTR transmission controls.

The header does not prescribe sequencing. Any required ordering, polling, write-one-to-clear behavior, lock protection, reset handling, or firmware coordination must be implemented by the driver code that uses these constants and by the underlying hardware specification.

## State and Persistence

The file itself owns no mutable state, performs no I/O, allocates no memory, and persists nothing. The represented state lives in NBIO 7.11.0 hardware registers.

State represented by this chunk includes:

- PCI identity and configuration state for root-complex and endpoint functions, including command/status, BARs, bus windows, bridge controls, capability pointers, and interrupt descriptors.
- Interrupt-delivery state in MSI and MSI-X capability registers, including message address/data, mask, pending, table, and PBA offsets.
- PCIe link and topology state through device/link/slot/root capability, control, and status registers; RC0-specific bridge-window registers; VC resources; MSI map state; RTR data; and lane-specific equalization/margining registers.
- Error-observation and error-policy state through AER status/mask/severity, header-log, and TLP-prefix-log registers.
- Power-management state through PMI, power-budget, LTR, DPA capability/control/status, and DPA substate power-allocation registers.
- Isolation and multi-function state through ACS, PASID, ARI, vendor-specific, BAR enhanced-capability, and VF resizable-BAR registers.
- Endpoint-local RCC state through scratch/control/status registers and function 0 DPA/LTR controls.

Retention across GPU reset, FLR, BACO, suspend/resume, runtime power transitions, or PCIe link reset is not specified by the generated header. Callers must rely on NBIO hardware behavior and AMDGPU reinitialization paths to restore any policy registers that are not retained.

## Dependencies and Integration Points

Primary dependencies are the adjacent generated NBIO 7.11.0 headers:

- `nbio_7_11_0_sh_mask.h` supplies bit positions and masks for fields inside many of these registers.
- `nbio_7_11_0_default.h` supplies reset/default values where generated.
- `nbio_7_11_0_smn.h` supplies SMN-addressed registers for the same IP generation.
- Other chunks of this same offset header supply the earlier parts of device 1 endpoint function 1, the continuation of the RCC endpoint block after line 7345, and the surrounding NBIO address blocks.

Likely AMDGPU integration points include:

- NBIO 7.11 initialization and low-level access code that selects the generated NBIO register tables for this ASIC generation.
- SOC15-era register macros that use `reg...` and `reg..._BASE_IDX` names to construct MMIO/config-space accesses.
- PCIe link setup, ASPM/LTR/power-management, BAR sizing, bridge-window programming, and capability enumeration code.
- RAS and PCIe error paths that read AER status, masks, severity, header logs, TLP prefix logs, parity mismatch status, and endpoint interrupt status.
- SR-IOV, VF BAR sizing, PASID, ACS, and ARI paths that need function-specific offsets for isolation and function-addressing controls.
- Debug, bring-up, and validation paths that read lane equalization, lane margining, RTR, scratch, and RCC endpoint control/status registers.

The integration contract is purely symbolic. A consumer must include the NBIO 7.11.0 header that matches the ASIC/IP block it is programming; offsets from earlier NBIO generations may have similar names but are not interchangeable.

## Risks

- A wrong offset or base index can route a register access to the wrong NBIO window. Since most macros use the same `_BASE_IDX` value, simple compile-time type checking will not catch a symbol selected for the wrong device/function.
- The endpoint-function blocks are highly repetitive but not identical. Copying an EPF0 register name into EPF1-EPF6 code, or assuming all functions carry EPF0's VC/LTR/lane-margining/parity registers, can create build failures or incorrect hardware accesses.
- Many logical PCI registers share the same dword offset because they are subfields in one PCI configuration register, for example command/status, class-code bytes, link control/status, DPA status/control, ACS capability/control, and PASID capability/control. Offset-only users must pair the offset with the correct shift/mask header definitions.
- Root-complex and endpoint functions have similar AER and capability names but different address windows. Misclassifying RC0 versus EPF* can produce misleading error diagnosis or mask the wrong PCIe error source.
- MSI/MSI-X and BAR capability registers affect interrupt delivery and address decoding. Incorrect programming can break interrupt routing, expose unexpected BAR sizing, or disrupt virtual-function resource assignment.
- Error-reporting, DPA, LTR, ACS, PASID, ARI, and RTR registers can affect link behavior, isolation, power management, and recovery. Bad writes may have system-visible consequences beyond a single driver operation.
- The work item starts and ends mid-file. It begins after the start of device 1 endpoint-function 1 and ends after only the beginning of the RCC endpoint block, so merge/reconciliation must not treat missing neighboring registers as absent from the complete source.
- Generated headers are easy to validate mechanically but hard to validate semantically without ASIC documentation or hardware. A value can look structurally consistent while still being wrong for the hardware revision.

## Test and Validation Signals

Useful validation signals are a mix of generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU configurations that include NBIO 7.11.0 generated headers to catch malformed macro names, duplicate incompatible definitions, or missing symbols referenced by driver code.
- Run mechanical checks that every non-`_BASE_IDX` register macro in this chunk has the expected companion `_BASE_IDX` macro and that each companion value is `5`.
- Cross-check repeated endpoint-function sequences across EPF1 through EPF6 and separately compare EPF0, which intentionally has additional VC/LTR/parity/lane-margining coverage.
- Validate address-block boundaries: RC0 offsets should sit under base `0x10102000`, EPF0-EPF6 under `0x10150000` through `0x10156000`, and the RCC endpoint block under `0x10131000`.
- Cross-check register names against `nbio_7_11_0_sh_mask.h` and `nbio_7_11_0_default.h` so field masks/defaults exist where expected and absent masks are understood as whole-register or externally specified accesses.
- On hardware, read stable identity/capability registers such as vendor/device IDs, PCIe capability headers, MSI/MSI-X capability headers, AER capability headers, and lane-margining capability headers to confirm offsets land in plausible configuration-space locations.
- Exercise controlled PCIe error paths and confirm AER status, masks, severity registers, header logs, and TLP prefix logs are read from the expected RC0 or EPF window.
- Exercise suspend/resume, reset, and link retrain paths to confirm driver initialization restores command, BAR, interrupt, power-management, and link-policy registers that are expected to be programmed from these symbols.
- For SR-IOV or virtualization scenarios, validate VF BAR sizing, ACS/PASID/ARI behavior, MSI/MSI-X routing, and isolation with the function-specific symbols rather than shared offsets.

## Chunk Boundary Notes

Line 4911 starts in the middle of the previous `DEV1_EPF1` endpoint-function block. Only VF resizable-BAR entries for BAR2 through BAR6 and RTR entries are visible before the `DEV2_RC0` block begins at line 4938.

Line 7345 ends in the middle of `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`. This work item includes the RCC scratch/control/interrupt/RX/bus/config/TX-LTR and initial function 0 DPA substate power-allocation offsets, but the rest of the RCC endpoint block continues in a later chunk.
