# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 2479-4910

## Scope

This chunk is a generated AMDGPU NBIO 7.11 register-offset header segment. It contains C preprocessor constants only: no functions, structs, enums, variables, allocations, locks, branches, loops, or direct hardware reads/writes. The exported data maps NBIF/BIF PCI configuration-space register names to 32-bit register offsets and emits a matching `<register>_BASE_IDX` constant for AMDGPU's SOC15 register access layer.

The range contains 2,400 `#define` entries: 1,200 register-offset symbols and 1,200 `_BASE_IDX` symbols. All `_BASE_IDX` values in this slice are `5`. The first line is a chunk-boundary tail for `regBIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL_BASE_IDX`; then the slice closes the `DEV0_EPF2` routing-tail registers with `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. It then covers full Type 0 endpoint-function config images for `DEV0_EPF3_0` through `DEV0_EPF7_0`, a Type 1/root-complex config image for `DEV1_RC0`, a richer endpoint/root-port-like `DEV1_EPF0_0` image, and the first part of `DEV1_EPF1_0` through `PCIE_VF_RESIZE_BAR2_CAP`.

Although the repository tree is under `sources/distributed-fs/ceph-client`, this file is AMD GPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_offset.h` gives AMDGPU compile-time names for NBIO 7.11 registers. This chunk focuses on NBIF/BIF PCI configuration-space decode blocks. Driver code pairs these `reg...` offsets with matching field shifts and masks from `nbio_7_11_0_sh_mask.h`, then reads or writes hardware through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

The constants here describe where NBIO exposes PCI/PCIe configuration words for multiple device/function views. These include standard PCI identity and resource registers, PCIe capability and link state, MSI/MSI-X capability state, vendor-specific enhanced capability payloads, Advanced Error Reporting, BAR resize/power-budget/dynamic-power-allocation capabilities, ACS/PASID/ARI/SR-IOV capabilities, 16 GT/s physical-layer capability/status/equalization registers, lane margining, and routing-table capability data. The header supplies addresses only; field layout, reset values, side effects, and access policy live in companion generated files and the hardware specification.

## Address Blocks And Macro Families

The opening fragment belongs to the previous `DEV0_EPF2_0` block. Line 2479 is the `_BASE_IDX` for `PCIE_ARI_CNTL`, and lines 2480-2485 define the routing-table enhanced capability list and two routing data registers at offsets `0x1095c` through `0x1095e`.

`nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` through `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp` are complete, repeated endpoint-function images. Their base addresses are `0x10143000`, `0x10144000`, `0x10145000`, `0x10146000`, and `0x10147000`; their register offsets run from `0x10c00` to `0x10d5e`, `0x11000` to `0x1115e`, `0x11400` to `0x1155e`, `0x11800` to `0x1195e`, and `0x11c00` to `0x11d5e`. Each block has 128 register offsets plus 128 base-index macros. The repeated families include `VENDOR_ID`/`DEVICE_ID`, `COMMAND`/`STATUS`, revision/class/header/BIST, `BASE_ADDR_1` through `BASE_ADDR_6`, adapter and ROM base registers, capability pointers, interrupt-line/pin/min-grant/max-latency aliases, PMI, PCIe device/link capability and control/status registers, MSI/MSI-X, SATA IDP registers, vendor-specific enhanced capabilities, AER status/mask/severity/logs, resizable BAR registers, power-budget and DPA registers, ACS, PASID, ARI, and routing-table registers.

`nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` starts at base address `0x10101000` and maps a Type 1/root-complex style PCIe configuration image at offsets `0x0400` through `0x055e`. It has 188 register offsets and 188 base-index macros. Unlike the Type 0 endpoint blocks, this block includes bridge-oriented registers such as `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, prefetchable base/limit and upper registers, `IO_BASE_LIMIT_HI`, IRQ and extended bridge control, slot/root capability-control-status registers, MSI map and SSID capability registers, virtual-channel capability/resource registers, device serial number, root error command/status/source ID, secondary PCIe capability, lane error status, per-lane equalization for lanes 0-15, ACS, Data Link Feature, 16 GT/s PHY capability/status/equalization, and per-lane margining control/status. It closes with the same routing-table capability registers at `0x055c`-`0x055e`.

`nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` starts at base address `0x10148000` and maps offsets `0x12000` through `0x1215e`. It has 221 register offsets and 221 base-index macros. The early portion resembles the Type 0 endpoint blocks, but the extended capability chain is richer: it includes VC registers, lane equalization, ACS/PASID/LTR/ARI, Data Link Feature, 16 GT/s PHY registers, and lane margining before the routing-table registers. This makes it closer to a physical endpoint/root-port-facing function than the simpler `DEV0_EPF3`-`EPF7` endpoint images.

`nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` starts at base address `0x10149000`. This chunk covers offsets `0x12400` through `0x12533`, with 148 register-offset macros and 147 matching `_BASE_IDX` macros inside the requested line range because `regBIF_CFG_DEV1_EPF1_0_PCIE_VF_RESIZE_BAR2_CAP_BASE_IDX` is on the next line after the chunk. The covered part includes the standard Type 0 config header, PCIe device/link capability and status, MSI/MSI-X, SATA IDP, vendor-specific enhanced capability, AER logs, BAR resize, power budget, DPA, ACS, PASID, ARI, SR-IOV capability registers, VF BAR base registers, and the start of VF resizable BAR capability/control registers.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `regBIF_CFG_DEV*_...` symbols encode register offsets.
- `regBIF_CFG_DEV*_..._BASE_IDX` symbols encode the SOC15 base index used by AMDGPU register helpers.

The numeric values are untyped preprocessor integer literals. Some symbolic names alias the same offset because PCI config words pack multiple fields into one 32-bit register: for example vendor and device ID share offset `0x10c00` in `DEV0_EPF3_0`, command and status share `0x10c01`, and several MSI 32-bit/64-bit variants alias adjacent message-data, mask, or pending registers. Consumers must use the matching shift/mask macros to address subfields safely.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs in including AMDGPU code:

1. The NBIO 7.11 implementation or a PCIe/NBIO helper selects a generated `reg...` offset.
2. The code converts it through `SOC15_REG_OFFSET` or uses a PCIe/SOC15 read/write helper.
3. It applies matching `nbio_7_11_0_sh_mask.h` field masks and shifts when a subfield is needed.
4. The resulting read or write observes status, programs controls, configures resources, clears or masks errors, enables interrupt capabilities, or drives virtualization and PCIe-link policy.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` includes both this offset header and `nbio_7_11_0_sh_mask.h`. The visible NBIO 7.11 implementation uses the generated register database for revision ID reads, framebuffer access enablement, doorbell aperture/range programming, interrupt control, HDP flush offsets, PCIe index/data offsets, clock-gating controls, light-sleep controls, and register remapping. The specific BIF config symbols in this chunk are hardware metadata for PCIe config images and are most likely consumed by generic register access, diagnostics, display/resource include paths, virtualization/SR-IOV paths, or future/adjacent code rather than by a tight loop inside this header.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware-backed PCI/PCIe configuration-space state exposed through NBIO/NBIF register windows. Persistence, reset behavior, ownership, and side effects are governed by PCIe semantics, GPU reset domains, firmware initialization, Linux PCI resource management, SR-IOV lifecycle, suspend/resume save-restore, function-level reset, and AMDGPU call-site policy.

Represented state includes identity/class registers, command/status bits, BAR/ROM/resource windows, bridge bus and memory windows, capability-list pointers, PCIe device/link controls and status, MSI/MSI-X message and mask state, AER status/mask/severity/header logs, virtual-channel and data-link-feature state, ACS/PASID/LTR/ARI controls, SR-IOV VF counts/stride/device IDs/page sizes/VF BAR bases, resizable BAR controls, DPA and power-budget information, 16 GT/s equalization status, lane margining controls/status, and routing-table data. Some registers are read-only capabilities, some are software-programmed controls, some are hardware-updated live status, and some diagnostic/error bits may be sticky or write-one-to-clear in the underlying hardware.

## Dependencies And Integration Points

The main dependency is consistency across the generated NBIO 7.11 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h` supplies the matching field shifts and masks.
- Other generated NBIO 7.11 headers provide adjacent offsets, SMN addresses, and reset/default data where present.
- AMDGPU SOC15 and PCIe register helpers combine base index, register offset, and field masks to access the hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` is the primary NBIO 7.11 include user.
- `amdgpu_discovery.c` selects `nbio_v7_11_funcs` for NBIO IP versions 7.11.0 through 7.11.3, and `soc21.c`/`nbif_v6_3_1.c` contain NBIO 7.11 generation integration paths.
- Display resource files for DCN 3.5 and 3.5.1 include `nbio_7_11_0_offset.h`, so display bring-up may also depend on selected register offsets.

The hardware integration surfaces are PCIe enumeration, endpoint and root-complex config access, bridge window setup, MSI/MSI-X interrupt routing, PCIe AER diagnostics, VC/data-link features, ACS/PASID/ARI/IOMMU-related behavior, SR-IOV VF exposure, resizable BAR sizing, power-budget/DPA policy, 16 GT/s equalization, lane margining diagnostics, routing-table access, reset/FLR, and suspend/resume.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line is a `_BASE_IDX` for an earlier `DEV0_EPF2` register, and the final line defines `regBIF_CFG_DEV1_EPF1_0_PCIE_VF_RESIZE_BAR2_CAP` without its `_BASE_IDX`, which appears immediately after the requested range.
- Generated offset drift can compile cleanly while steering reads or writes to the wrong hardware register. This is especially risky because many register names alias the same dword by design, so accidental aliasing can look plausible.
- The repeated endpoint-function blocks are mechanically similar. A generation or copy error in only `DEV0_EPF3`, `EPF4`, `EPF5`, `EPF6`, or `EPF7` could affect one exposed function while other functions continue to work.
- Applying a Type 0 endpoint offset pattern to the `DEV1_RC0` Type 1/root-complex block would corrupt bridge, slot, root-error, lane, or link-training state rather than endpoint BAR/MSI state.
- PCI command, BAR, bridge memory-window, ROM, SR-IOV VF BAR, and resizable BAR registers directly affect MMIO decode, DMA visibility, and resource sizing.
- MSI/MSI-X register offsets affect interrupt delivery. Wrong offsets can cause lost, duplicated, masked, or misrouted interrupts.
- AER status, severity, mask, root-error, header-log, and TLP-prefix-log registers may have sticky or write-one-to-clear semantics. Incorrect read/modify/write handling can erase diagnostic evidence or leave errors uncleared.
- ACS, PASID, ARI, and SR-IOV registers are isolation-sensitive. Offset mistakes can affect VF enumeration, function routing, IOMMU behavior, and peer-to-peer access policy.
- 16 GT/s equalization and lane-margining registers are PCIe link-sensitive. Wrong register access can destabilize link training, margining diagnostics, or recovery behavior.
- `_BASE_IDX` value `5` is part of the SOC15 addressing contract. A mismatch between offset and base index would be as damaging as a wrong offset, even if the symbolic register name is correct.

## Test And Validation Signals

- Build AMDGPU with NBIO 7.11 support and display DCN 3.5/3.5.1 paths enabled. Missing or renamed macros should surface through `nbio_v7_11.c`, display resource includes, and related NBIF code.
- Run generated-header consistency checks that pair every non-`_BASE_IDX` register offset with a matching `_BASE_IDX`, allowing for this chunk's first-line and last-line boundary exceptions during whole-file reconciliation.
- Cross-check `nbio_7_11_0_offset.h` against `nbio_7_11_0_sh_mask.h` so every field mask has a valid register offset and every offset family has expected field definitions.
- Compare repeated `DEV0_EPF3_0` through `DEV0_EPF7_0` layouts for identical relative offsets, differing only by the function's offset window.
- On NBIO 7.11 hardware, validate PCIe enumeration, vendor/device/class fields, BAR sizing, command-bit transitions, capability-list traversal, MSI/MSI-X interrupt delivery, AER logging/clearing, ACS/PASID/ARI state, SR-IOV VF creation/removal where applicable, and resizable BAR behavior.
- Exercise suspend/resume, runtime power transitions, reset/FLR, and PCIe link retraining while monitoring link speed/width/status, AER events, 16 GT/s equalization status, and lane margining diagnostics.
- For bridge/root-complex paths, verify bus numbering, I/O and memory windows, root-error status/source IDs, slot/root status, and downstream device accessibility.

## Chunk Notes

- Lines 2479-2485: boundary tail for `DEV0_EPF2_0`, ending its ARI/routing-table capability offsets.
- Lines 2488-3787: complete repeated `DEV0_EPF3_0` through `DEV0_EPF7_0` endpoint-function config images.
- Lines 3788-4167: complete `DEV1_RC0` Type 1/root-complex config image with bridge, root, lane, 16 GT/s, margining, and routing registers.
- Lines 4168-4613: complete `DEV1_EPF0_0` extended endpoint/function image.
- Lines 4614-4910: partial `DEV1_EPF1_0` image, ending at the start of the VF resizable BAR capability family.
