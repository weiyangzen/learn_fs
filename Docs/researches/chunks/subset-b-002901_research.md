# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h lines 7707-10473

## Chunk Scope

This chunk is a generated register-offset slice from AMDGPU's NBIO 2.3 ASIC register header. It covers 2,187 preprocessor definitions from the middle of the `VF26` virtual-function register block through the start of the `SWDS1` PCI bridge configuration block. The content is data, not executable logic: C code includes this header to name NBIO, BIF, RCC, PCIe, MSI-X, doorbell, mailbox, HDP flush, and PCI configuration register addresses without embedding numeric constants at call sites.

The mapped source range begins inside `nbio_nbif0_bif_bx_dev0_epf0_vf26_BIFPFVFDEC1`, at `mmBIF_BX_DEV0_EPF0_VF26_GPU_HDP_FLUSH_REQ_BASE_IDX`, and ends inside `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp`, at `cfgBIF_CFG_DEV0_SWDS1_SLOT_CAP`. Because this is a chunk of a larger generated header, both ends have cross-chunk continuity: earlier lines define the first half of VF26, and later lines continue the SWDS1 bridge capability table.

## Purpose

The chunk supplies symbolic register names for NBIO/BIF PCIe virtualization plumbing on AMD GPUs. It has two related address forms:

- `mm*` macros define register offsets and matching `*_BASE_IDX` selector values. These are typically consumed by AMDGPU register access macros that combine a block base index with an offset.
- `cfg*` macros define absolute configuration-space addresses for PCIe/NBIO configuration registers, including per-virtual-function windows and higher-level PCIe capability structures.

Most of the chunk is a repeated per-VF template. Virtual functions expose the same register names at different bases, so the generator emits families such as `VF0` through `VF30` with predictable address strides. That regularity is important for SR-IOV and virtualization code that may address individual VFs explicitly.

## Important Macro Families

The chunk contains these major groups:

- `mmBIF_BX_DEV0_EPF0_VF26` through `mmBIF_BX_DEV0_EPF0_VF30`: offset-based definitions for late virtual functions. Each VF has indirect MMIO index/data registers, RCC error and doorbell/config status registers, BIF bus-master/atomic/doorbell/HDP/mailbox registers, and a four-vector GFX MSI-X table plus PBA.
- `cfgBIF_BX_DEV0_EPF0_VF0` through `cfgBIF_BX_DEV0_EPF0_VF30`: absolute configuration addresses for per-VF BIF register windows. Each VF base advances by `0x80000`, from `0xd0000000` for `VF0` through `0xd0f00000` for `VF30`.
- `cfgRCC_DEV0_EPF0_VF*`: absolute addresses for RCC-side VF registers such as `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`, and each VF's GFX MSI-X vectors.
- `cfgPSWUSCFG0_1_*`: PCIe upstream switch/root-port style configuration registers at base `0xfffe00000000`. This includes conventional PCI config header fields, power-management capability, MSI, PCIe device/link/slot capabilities, SR-IOV, ATS, PASID, PRI, ARI, L1 PM substate, ESM, data-link feature, 16 GT/s PHY, margining, and CCIX capability registers.
- `cfgBIF_BX_PF0_*` and `cfgSUM_*`: a small physical-function indirect-index block and summary index/data registers.
- `cfgBIF_CFG_DEV0_SWDS1_*`: the start of a downstream bridge/device configuration block at `0xfffe10100000`, covering the conventional PCI header and initial PCIe capability registers through `SLOT_CAP` in this chunk.

Representative per-VF register categories include:

- indirect access: `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`;
- error/status: `RCC_ERR_LOG`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `BIF_TRANS_PENDING`;
- aperture and address control: `RCC_DOORBELL_APER_EN`, `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `DOORBELL_SELFRING_GPA_APER_BASE_LOW`, `DOORBELL_SELFRING_GPA_APER_CNTL`, `NBIF_GFX_ADDR_LUT_BYPASS`;
- coherency and flushing: `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`;
- virtualization mailbox: `MAILBOX_MSGBUF_TRN_DW0` through `DW3`, `MAILBOX_MSGBUF_RCV_DW0` through `DW3`, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, `BIF_VMHV_MAILBOX`;
- interrupts: `GFXMSIX_VECT0` through `GFXMSIX_VECT3` address/data/control registers and `GFXMSIX_PBA`.

## APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this range. The public interface is the macro namespace itself. Consumers depend on these names being present at compile time and on the numeric values matching the hardware register map.

The `*_BASE_IDX` macros for `mm*` definitions are part of the access contract. In this chunk the MMIO index registers use base index `0`, the BIF/RCC VF functional registers use base index `2`, and GFX MSI-X registers use base index `3`. Driver code that uses AMDGPU's generated register accessor macros must pair the offset macro with the correct base-index macro; mixing base indices can target the wrong register block even when the offset looks valid.

## Control Flow

This header has no local control flow. Its control-flow effect is indirect:

- compile-time preprocessing substitutes symbolic register names into AMDGPU C code;
- call sites choose runtime ordering for operations such as writing mailbox transmit dwords, enabling doorbell apertures, requesting HDP flushes, polling `GPU_HDP_FLUSH_DONE` or `BIF_TRANS_PENDING`, and programming MSI-X vectors;
- SR-IOV or virtual-function management code can choose the target VF by selecting the macro family for a specific `VF<n>`.

For the per-VF families, the generated layout is intentionally uniform. The same semantic operation on a different VF is represented by the same suffix under another `VF<n>` prefix.

## State And Persistence

The file itself stores no runtime state. The macros identify hardware registers whose state is owned by the GPU/NBIO block and, for config-space registers, by PCIe configuration mechanisms. Persistence and reset behavior are therefore hardware-defined:

- doorbell aperture registers and GPA base registers control per-VF doorbell exposure;
- HDP coherency and flush registers coordinate CPU/GPU-visible memory ordering;
- mailbox registers carry VM/hypervisor or PF/VF control messages;
- MSI-X table/PBA and PCIe capability registers affect interrupt routing and PCIe feature negotiation;
- status/error registers retain hardware-observed conditions until cleared according to register-specific semantics from the corresponding mask/shift headers and hardware documentation.

Because this chunk contains offsets only, bit definitions, clear-on-read behavior, reset values, and access restrictions must be obtained from companion headers or register specs.

## Dependencies And Integration Points

This header is integrated by AMDGPU ASIC-specific code under the DRM driver tree. It is normally included with related generated NBIO 2.3 headers that provide masks, shifts, and possibly block base arrays. The macros in this chunk depend on:

- AMDGPU register access helpers that understand the `mm*` plus `*_BASE_IDX` convention;
- PCIe/NBIO initialization and SR-IOV paths that configure per-VF doorbells, mailboxes, BAR/config windows, MSI-X, and PCIe capabilities;
- interrupt setup code that programs `GFXMSIX_VECT*` and observes `GFXMSIX_PBA`;
- memory-management and synchronization code that requests/polls HDP flush registers;
- virtualization control paths that use mailbox and `RCC_IOV_FUNC_IDENTIFIER` registers to coordinate PF/VF or VM/hypervisor behavior.

The `cfgPSWUSCFG0_1_*` and `cfgBIF_CFG_DEV0_SWDS1_*` tables align with PCI/PCIe configuration-space layouts. They are likely consumed by low-level NBIO/PCIe code rather than generic Linux PCI core helpers, because the constants are GPU-internal config aperture addresses rather than normal bus/device/function offsets.

## Risks And Edge Cases

- The chunk starts and ends inside generated address blocks. Any human review or merge step must avoid treating this chunk as a complete standalone register map.
- The `VF*` definitions are repetitive but not disposable. A single wrong digit in a VF number, stride, or suffix would silently point code at another function's register window.
- `mm*` offset constants and `cfg*` absolute address constants have different units and access paths. Using a `cfg*` address with an accessor expecting an `mm*` offset, or vice versa, would be a serious register access bug.
- `*_BASE_IDX` values are as important as offsets for MMIO access. Copying only the offset macro can lose the register block selector.
- Some PCIe configuration entries are byte- or word-sized fields at odd offsets, while many GPU register accesses are dword-oriented. Consumers must use access widths compatible with the register field, especially for config header fields such as revision, class code bytes, status/control words, and MSI/PCIe capability fields.
- The `cfgBIF_CFG_DEV0_SWDS1_MSI_MSG_DATA` address is outside this mapped range's end but visible just after the boundary and shares an address with `MSI_MSG_ADDR_HI`; this is a common 32-bit versus 64-bit MSI layout ambiguity and should be handled by capability format, not by assuming every macro maps to a unique dword.
- Hardware availability may depend on ASIC revision, fusing, SR-IOV mode, and virtualization enablement. The header's presence does not prove every register is valid in every runtime configuration.

## Test Signals

Useful validation signals for changes touching this generated map include:

- build coverage for AMDGPU with NBIO 2.3 headers included, catching missing or renamed macros;
- generated-header consistency checks against AMD's source register database, especially per-VF stride checks from `VF0` to `VF30`;
- static checks that every `mm*` macro with a `*_BASE_IDX` suffix has the expected paired offset macro and base index;
- SR-IOV smoke tests that create or manage VFs and exercise mailbox, doorbell aperture, BME status, and VF identification paths;
- interrupt tests that program and deliver MSI-X vectors through the GFX MSI-X table;
- HDP flush tests that write `GPU_HDP_FLUSH_REQ`, observe `GPU_HDP_FLUSH_DONE`, and ensure no hangs while `BIF_TRANS_PENDING` is active;
- PCIe link capability/status validation for the `cfgPSWUSCFG0_1_*` block, including L1 PM substate, link speed capability, margining, ARI/SR-IOV/PASID/PRI/ATS exposure, and CCIX/ESM capability presence when supported.

## Cross-Chunk Notes

The preceding chunk is needed for the beginning of `VF26` offset definitions and earlier VF offset families. The following chunk is needed for the continuation of `cfgBIF_CFG_DEV0_SWDS1_*` after `SLOT_CAP` and any remaining PCIe downstream-device capability definitions. The final per-file research report should merge this chunk with neighboring chunks to present the complete generated register namespace for `nbio_2_3_offset.h`.
