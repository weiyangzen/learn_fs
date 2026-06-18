# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_display_cfg_types.h

## Purpose
`dml_top_display_cfg_types.h` defines the public DML21 display configuration input model. It describes planes, streams, surface layout, timing, link output, writeback, overrides, and MCache configuration descriptors used by the DML top layer, PMO, DPMM, and core calculation code. It is the primary caller-facing structure for "what display mode should DML validate and program?"

## Important APIs, Types, And Data Shapes
The header establishes fixed maxima with `DML2_MAX_PLANES`, `DML2_MAX_DCN_PIPES`, `DML2_MAX_MCACHES`, and `DML2_MAX_WRITEBACK`. Enumerations classify input tiling (`dml2_swizzle_mode`), pixel/source format (`dml2_source_format_class`), chroma siting (`dml2_sample_positioning`), rotation, output format, encoder type, DP link rate, p-state type, UCLK strategy, SubVP and MALL overrides, ODM/MSO modes, scaling transform, DSC policy, TDLUT mode, and Twait budgeting policy.

`struct dml2_surface_cfg` describes plane0/plane1 dimensions, pitch, tiling, and optional DCC pitch/rate metadata. `struct dml2_composition_cfg` describes rotation, mirroring, output scaling intent, viewport rectangles for plane0/plane1, stationary behavior, and scaler/tap ratios including EASF, ISHARP, and UPSP controls. `struct dml2_timing_cfg` captures timing totals, active area, blanking, sync widths, pixel clock, bits per component, DSC overrides, interlace, DRR flags, and nominal vblank.

`struct dml2_plane_parameters` binds a plane to a stream and combines pixel format, surface, composition, metadata, cursor, TDLUT, immediate flip, and per-plane policy/HW overrides. `struct dml2_stream_parameters` holds timing, link output, writeback configuration, and stream-level ODM/SubVP/Twait overrides. `struct dml2_display_cfg` is the top-level input: VM mode flags, page-table levels, plane and stream descriptor arrays, counts, DET reallocation policy, and global overrides for HW forcing, power management, synchronization, SubVP implicit PMO, blanking, and DML debug knobs.

The MCache descriptors at the end, `dml2_pipe_configuration_descriptor` and `dml2_plane_mcache_configuration_descriptor`, are used by MCache programming to map calculated per-plane allocation onto actual pipe viewport slices.

## Control Flow And Integration
There are no functions here, but these types drive almost every DML21 pass. `dml21_translation_helper.c` builds `dml2_display_cfg` from DC state. `dml2_top_soc15.c` copies and mutates it during mode support and programming. `dml2_pmo_*` optimizers consume the same structure to choose p-state, SubVP, DRR, and ODM strategies. `dml2_core_dcn4.c` may copy the input, expand implicit SubVP into phantom streams and planes, and pass the expanded config to `dml2_core_calcs_mode_support_ex()` and `dml2_core_calcs_mode_programming_ex()`.

The config also feeds generated register extraction: `dml2_core_dcn4_calcs.c` reads surface, composition, timing, VM, cursor, DCC, DSC, writeback, and override fields to calculate support, bandwidth, register values, and informative diagnostics.

## State And Persistence Behavior
`dml2_display_cfg` is copied by value through many layers. It has no internal allocation and no ownership pointers, which makes `memcpy()` the dominant persistence pattern inside a single validation/programming pass. The top context stores a current display config, but the data is runtime state, not persistent storage. Counts such as `num_planes`, `num_streams`, `active_writebacks_per_stream`, and `num_cursors` are critical bounds for fixed-size arrays.

## Dependencies
The file includes `dml2_external_lib_deps.h` for standard types. It is included by `dml_top_types.h` and referenced by core, PMO, DPMM, wrapper, translation helper, and generated calculation files. Some fields are closely coupled to DC hardware concepts, such as DET, DCC, DSC, ODM, DRR, SubVP, MALL, TDLUT, VM page tables, and writeback.

## Risks And Edge Cases
Array bounds depend on callers honoring `DML2_MAX_PLANES`, `DML2_MAX_DCN_PIPES`, `DML2_MAX_MCACHES`, and `DML2_MAX_WRITEBACK`; invalid counts can cause later loops to overrun fixed arrays. Pixel format semantics determine whether plane1 is used, so incorrect format translation can distort chroma bandwidth, viewport, and MCache allocation. Overrides are powerful and bypass normal policy; debug forcing for unbounded requests, DET size, clocks, PTE buffer mode, and SubVP can create hardware-programming results that are valid for simulation but unsafe for production if leaked. Several fields combine units in kHz, MHz, us, ns, pixels, lines, bytes, and elements, so translation tests are important.

## Test Signals
Strong test signals include round-trip translation tests from DC state to `dml2_display_cfg`, mode-support coverage for RGB, planar YUV, mono, DCC, cursor, TDLUT, writeback, DSC, DRR, ODM, and SubVP inputs, and negative tests for viewport exceeding surface, pitch alignment, unsupported scaling/taps, and invalid link rates. Boundary tests should exercise maximum planes/streams, no-output or writeback-only streams, hostvm/gpuvm enablement, forced hardware overrides, and synchronized timing policy.
