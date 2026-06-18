# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params.h

## Purpose
Defines the host-side ISP parameter aggregate for the AtomISP CSS pipeline and declares helpers for storing host parameter data and shared GDC lookup tables. It is the central header for stream, pipe, and stage parameter state consumed by SP/ISP staging code such as `sh_css_sp.c` and parameter-copy code.

## Important APIs, Types, and Functions
The main type is `struct ia_css_isp_parameters`, which stores UDS parameters per stage, stream optical-black config, FPN/motion/morphing/shading tables, gamma/CTC/MACC/XNR tables, many public `ia_css_*_config` blocks, DVS coefficients, change flags, per-pipe DDR pointer maps, and an `isp_parameters_id`. Declared APIs include `ia_css_params_store_ia_css_host_data()`, `ia_css_params_store_sctbl()`, `ia_css_params_alloc_convert_sctbl()`, `sh_css_pipe_isp_config_get()`, default GDC LUT map/free/get helpers, and `sh_css_pipe_get_pp_gdc_lut()`.

## Control Flow
The header has no runtime flow, but it defines the object that parameter setters populate and that pipeline initialization copies to CSS/DDR. `sh_css_sp.c` calls `sh_css_params_ddr_address_map()` and later copies binary memory interfaces to DDR, while GDC LUT access feeds SP pipeline setup.

## State and Persistence Behavior
Most fields persist across frames until their corresponding changed bit is consumed. Per-pipe/per-stage memory-change arrays drive selective parameter uploads. Pointer fields such as morph, shading, and DVS tables require strict lifetime ownership by the surrounding CSS code.

## Dependencies and Integration Points
Depends on AtomISP public type/config headers, binary/pipeline definitions, UDS/crop parameter types, and `sh_css_defs.h`. Integrates with ISP kernels generated from parameter metadata and with the SP stage serialization path.

## Risks
The struct is broad and ABI-like inside the driver: changing field names, array dimensions, or changed-bit semantics can silently desynchronize host parameter updates from firmware expectations. Pointer table ownership is easy to misuse because several fields are borrowed rather than embedded.

## Test Signals
Useful signals are successful pipeline start with changed ISP parameters, per-frame `isp_parameters_id` tracking, shading/morph/DVS table upload, default GDC LUT allocation/free, and no stale parameters after pipe/stage switches.
