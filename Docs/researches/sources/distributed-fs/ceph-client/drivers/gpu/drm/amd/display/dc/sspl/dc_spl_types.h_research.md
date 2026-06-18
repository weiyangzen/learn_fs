# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_types.h

Purpose: this header is the central SPL data model for scaler calculation and hardware programming. It defines geometry, ratios, taps, input policy, output register payloads, EASF/iSharp register fields, callbacks, and debug knobs used by AMD Display Core scaler code.

Important types: simple geometry and scaler primitives include `spl_size`, `spl_rect`, `spl_ratios`, `spl_inits`, `spl_taps`, and `spl_scaler_data`. Hardware-facing outputs are concentrated in `dscl_prog_data`, which contains recout, MPC size, DSCL mode, black color, ratios, init values, taps, raw filter pointers, EASF register fields, iSharp registers, blur-scale filters, and `sharpness_level`. Public calculation boundaries are `spl_in`, `spl_out`, and `spl_scratch`. Policy enums cover pixel formats, 3D view mode, rotation, color space, transfer functions, chroma cositing, sharpness behavior, and linear-light scaling preference.

Control flow and state: the header itself has no functions, but it describes the state flow used by SPL. Callers provide `spl_in` basic input/output properties and policy flags; SPL fills `spl_scratch.scl_data`; final hardware-ready results are written through `spl_out.dscl_prog_data`. Pointers inside `dscl_prog_data` refer to static coefficient tables supplied by filter modules.

Dependencies and integration: it includes debug, OS type, fixed-point, and custom-float helpers. It is consumed broadly by `dc_spl.c`, filter selection modules, iSharp support, and any hardware sequencer code translating `dscl_prog_data` to registers.

Risks and tests: this is a wide ABI-style header; field ordering and meaning matter to every scaler path. Many fields are raw register values with no local validation, so tests should verify SPL fills all relevant fields for RGB/YUV, 4:2:0 chroma, rotations, scaling/bypass modes, EASF/iSharp enable policies, fullscreen/HDR policy, and ODM/MPC slicing. Pointer lifetime assumptions for coefficient arrays should be checked by integration tests rather than unit-only coverage.
