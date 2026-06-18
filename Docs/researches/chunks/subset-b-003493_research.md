# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h lines 20396-22764

## Scope And Purpose

This chunk is the closing 2,369-line section of AMD's generated Navi10 enum header. It contains C enum typedefs and two scalar `#define` constants used as compile-time numeric names for Navi10 hardware register fields, packet fields, surface descriptors, interrupt-handler controls, semaphore performance counters, UVD/EFC formats, and a USB-PD revision constant. It defines no functions, structs with storage, global variables, branches, allocation paths, locks, MMIO accessors, or persistence logic.

The path is under a `ceph-client` source mirror, but the content is AMDGPU hardware metadata, not Ceph filesystem logic. Runtime behavior comes from DRM/AMDGPU code that includes this header or matching generated enum headers and writes the numeric values into packet/register fields described by other generated register-definition headers.

## Important APIs, Types, And Constants

The exported API is the enum namespace itself. Most enum values are direct hardware encodings and must remain synchronized with the ASIC register database:

- Render/depth/color encodings: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `SurfaceNumber`, `SurfaceSwap`, and `RoundMode`. These cover DCC color transforms, depth/stencil compare modes and formats, color buffer formats, CMASK clear/fragment states, pixel export formats, numeric interpretation, channel swapping, and rounding.
- Surface/tile layout encodings: `IMG_NUM_FORMAT_FMASK`, `IMG_NUM_FORMAT_N_IN_16`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `SeEnable`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, and `SampleSplitBytes`. These describe color/depth tiling, micro/macro tile shape, tile split size, sample split, pipe/bank topology, shader-engine enablement, row size, and bank-swap/sample-split byte encodings.
- Buffer and image format tables: `BUF_FMT` has 128 entries, `IMG_FMT` has 430 declared entries in this chunk, `BUF_DATA_FORMAT` has 16, `IMG_DATA_FORMAT` has 117, `BUF_NUM_FORMAT` has 8, and `IMG_NUM_FORMAT` has 16. The tables cover UNORM/SNORM/scaled/integer/float variants, SRGB, packed 10/11/11 and 10/10/10/2 layouts, 32-bit through 128-bit vector formats, depth/stencil-packed forms, GB/GR and BG/RG formats, FMASK encodings, BC1-BC7 compressed formats, multimedia `MM_*` layouts, and reserved holes up to the encoded field width.
- Interrupt-handler enums: `IH_PERF_SEL` is the largest enum in this chunk with 718 performance selector values. It starts with cycle/idle and client/storm/cookie/buffer events, then includes memory-client events, 64 BIF selections, per-client selections for client 0-31, and ring-buffer event selectors for RB0/RB1/RB2 including write pointers, full flags, overflow flags, read pointers, and load-read-pointer selectors across PF/VF variants. `IH_CLIENT_TYPE`, `IH_RING_ID`, `IH_VF_RB_SELECT`, and `IH_INTERFACE_TYPE` define interrupt client grouping, interrupt/request/translation rings, virtual-function ring-buffer selection policy, and legacy versus register-write interrupt interface mode.
- Semaphore/performance-monitor enums: `SEM_PERF_SEL` has 175 selectors for SEM cycle/idle, request-signal and request-wait events from SDMA, UVD, VCE, ACP, ISP, VP8, CPG, CPC immediate engines, CPC offline engines 0-31 for CPC1/CPC2, poll-wait variants, MC read/write request/return events, ATC request/return/XNACK/invalidation events, and ATC VM invalidation.
- Firmware/video/display constants: `ROM_SIGNATURE` is `0x0000aa55`. `EFC_SURFACE_PIXEL_FORMAT` lists endian/channel-ordered RGB, RGBA, ARGB, YCrCb/CrYCb, planar 4:2:0, packed 4:2:2, fixed/float RGB111110/BGR101111, and monochrome pixel formats for the UVD EFC path. `UVDFirmwareCommand` defines UVD firmware command IDs for fence/trap, decoded and macroblock addresses, IT/display buffers, end-of-decode, display pitch/tiling, bitstream address, and bitstream size. `IP_USB_PD_REVISION_ID` is `0x00000000`.

## Control Flow And Runtime Behavior

There is no local control flow. The header is consumed as a generated numeric contract:

1. Navi10 register, packet, and descriptor programming code includes this header or a related ASIC enum header.
2. Driver logic maps DRM/KMS, GEM/TTM, command submission, display, UVD, interrupt, or power-management decisions onto these enum values.
3. Those values are packed into register fields, command processor packets, image/buffer descriptors, interrupt-handler controls, or performance-counter select fields using companion address and shift/mask headers.
4. The hardware interprets the packed numeric value, not the C enum name.

Because the enum values are simple constants, C type checking gives limited protection. In many call sites the effective API is an integer field in a descriptor or register, so wrong enum values can compile successfully and fail only as incorrect hardware behavior.

## State And Persistence Behavior

The file stores no software state and persists nothing. The enum values describe stateful hardware-visible encodings. Once a consumer writes one of these values into a register or descriptor, the resulting state may live in GPU registers, ring packets, memory-backed image/buffer descriptors, interrupt rings, firmware command buffers, or performance-monitor configuration until it is overwritten, reset, invalidated, or lost across power management transitions.

The state represented by this chunk includes render target/depth/stencil formats, compression metadata interpretation, tiling geometry, swizzle/channel order, numeric conversion behavior, buffer and image descriptor format fields, IH ring and virtualization selection, IH/SEM performance-counter selections, UVD/EFC surface formats, UVD firmware command slots, and ROM/USB-PD signature/revision constants.

## Dependencies And Integration Points

This chunk depends on the rest of `navi10_enum.h` for the complete generated namespace and on companion Navi10 headers that define register addresses and bitfields. Typical integration points are AMDGPU display, GFX, GMC, interrupt-handler, UVD/video, and power/performance-monitor code paths that need stable hardware encodings.

Nearby generated headers in this tree expose overlapping enum contracts for other ASIC generations, including `soc21_enum.h`, `soc24_enum.h`, `asic_reg/smu/smu_7_1_*_enum.h`, and `asic_reg/gca/gfx_*_enum.h`. Those files are useful parity references but are not substitutes for Navi10-specific values because reserved holes and later-generation additions can differ.

The format enums integrate with buffer/image descriptor setup and surface programming. The tiling enums integrate with address-library or mode-setting decisions that choose displayable versus non-displayable layouts, bank/pipe geometry, FMASK, CMASK, and depth layouts. The IH enums integrate with interrupt ring setup, SR-IOV/PF/VF ring selection, interrupt-client classification, and IH performance counters. The SEM enum integrates with semaphore/performance monitor programming across SDMA, media, command processor, memory controller, and ATC paths. The UVD/EFC enums integrate with firmware command buffers and video/display format handling.

## Risks And Edge Cases

- Generated-header drift is the main risk. A numeric change in these enums can compile cleanly while programming the wrong hardware value.
- The chunk starts at a comment boundary for `ColorTransform` and ends at the file guard close, so it is self-contained for the listed enums but not for the full `navi10_enum.h` namespace.
- `BUF_FMT`, `IMG_FMT`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` contain many reserved holes. Treating reserved values as usable can produce descriptor faults, corrupted rendering, unsupported texture sampling, or undefined hardware behavior.
- Format families with similar names are not interchangeable. For example `SurfaceFormat`, `BUF_FMT`, `IMG_FMT`, data-format enums, and numeric-format enums encode related concepts at different abstraction levels and field widths.
- Tiling values affect memory addressing. Incorrect pipe, bank, row, split, or macro-tile settings can cause visible corruption, page faults, or failures that depend on resolution, sample count, compression, or displayability.
- Depth/stencil, CMASK, FMASK, and color-export encodings interact with compression and render backend behavior. Off-by-one values may appear only under MSAA, DCC, depth testing, fast clears, or specific export formats.
- IH selectors are highly repetitive across RB0/RB1/RB2, PF/VF, and client indices. Copy/paste or generated-order mistakes can misattribute interrupt performance events or break virtualization-specific interrupt routing diagnostics.
- SEM selectors are similarly repetitive across CPC immediate/offline engines and poll-wait variants. Incorrect selector values can make performance counters misleading without affecting normal functional execution.
- UVD firmware command enum values are protocol identifiers. Reordering or using the wrong command ID can make firmware parse a command buffer incorrectly even though the host-side structure compiles.
- `ROM_SIGNATURE` and `IP_USB_PD_REVISION_ID` are fixed constants; using them as mutable state or assuming they validate all ROM/USB-PD behavior would be misleading.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU/Navi10 code that includes `navi10_enum.h` so enum typedefs, duplicate names, and file-guard closure are compile-checked.
- Mechanically compare this line range with the authoritative generated Navi10 register database and with adjacent generated ASIC enum headers where parity is expected.
- Verify enum counts and boundary values for the large tables: `BUF_FMT` 128 entries, `IMG_FMT` 430 declared entries ending at `IMG_FMT_RESERVED_511`, `IMG_DATA_FORMAT` ending at `IMG_DATA_FORMAT_RESERVED_127`, `IH_PERF_SEL` ending at `IH_PERF_SEL_RB2_LOAD_RPTR_VF30`, and `SEM_PERF_SEL` ending at `SEM_PERF_SEL_ATC_VM_INVALIDATION`.
- Exercise runtime paths that create color/depth/stencil targets, compressed textures, BC formats, SRGB formats, FMASK/CMASK/MSAA resources, displayable and non-displayable tiling, and multimedia image formats.
- Validate interrupt handling and diagnostics under PF/VF or SR-IOV configurations, especially IH RB0/RB1/RB2 selector programming and ring selection policy.
- Validate SEM/IH performance counter programming by checking that selected events increment under the corresponding SDMA, UVD/VCE, command processor, memory controller, ATC, interrupt-ring, and virtualization workloads.
- Exercise UVD firmware command submission and EFC surface formats with planar 4:2:0, packed 4:2:2, RGB/RGBA, high-bit-depth, float/fixed, and monochrome surfaces.
- Watch for GPU page faults, descriptor validation errors, corrupted render targets, incorrect texture sampling, failed fast clears, interrupt storms or missed interrupts, bogus performance counter readings, and UVD firmware command failures.

## Cross-Chunk Notes

The merge lane should combine this with earlier `navi10_enum.h` chunks before making complete statements about the file. This chunk closes the header with `#endif /*_navi10_ENUM_HEADER*/`, so there is no following enum content in this source file after line 22764.
