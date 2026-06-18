# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h

## Purpose
`dcn42_mpc.h` is the DCN 4.2 Multiple Plane/Pixel Combiner register-contract header. It extends the DCN 4.01 MPC definitions with the register lists, field masks, shift structures, and public function prototypes needed to program MPCC blending, output color-space conversion, output gamma, movable color-management blocks, and the newer RMCM shaper/3D LUT/gamut-remap path.

## Important APIs, types, and functions
The key type is `struct dcn42_mpc`, which embeds `struct mpc` and stores MPCC use tracking, MPCC/RMU counts, and pointers to register, shift, and mask tables. `struct dcn42_mpc_registers`, `struct dcn42_mpc_shift`, and `struct dcn42_mpc_mask` are generated from large macro lists. Construction and MPCC setup are declared through `dcn42_mpc_construct()` and `mpc42_init_mpcc()`. RMCM programming APIs include shaper LUT programming/configuration, 3D LUT power and fast-load selection, LUT read/write control, LUT mode, 3D LUT size, fast-load bias/scale, bit-depth programming, and `mpc42_set_fl_config()`. State/readback hooks include `mpc42_read_mpcc_state()` and `mpc42_update_blending()`.

## Control flow
This header has no executable control flow, but it defines the metadata consumed by the DCN42 MPC implementation. Driver initialization supplies register arrays and field metadata to `dcn42_mpc_construct()`. Runtime MPC operations use the macros to resolve per-instance MPCC, MCM, OCSC, OGAM, DWB mux, flow-control, and RMCM registers before issuing `REG_*` helper writes. The RMCM functions form a typical sequence of powering memory, programming shaper/3D LUT region parameters and LUT data, selecting banks, enabling fast load, and enabling the active LUT mode.

## State and persistence behavior
All state is volatile display-driver and hardware-register state. The header describes software-side fields such as `mpcc_in_use_mask`, `num_mpcc`, and `num_rmu`, plus hardware register addresses and bitfields. It persists nothing across driver unload, suspend, or reboot; correctness depends on initialization and mode-set paths repopulating hardware state.

## Dependencies and integration points
The file depends on `dcn401/dcn401_mpc.h`, the AMD DC register macro system (`SF`, `SRII`, `MPC_REG_*`), `struct dc_context`, `struct mpcc`, `struct pwl_params`, `struct pwl_result_data`, color-management LUT types, and common MPC/MPCC abstractions. It integrates with resource construction, color-management programming, plane blending, display writeback muxing, and DCN42-specific fast 3D LUT load paths.

## Risks and edge cases
Most risk is hardware ABI drift: field names, instance arrays, and mask/shift declarations must match generated register headers. The repeated RAMA/RAMB region lists and MCM/RMCM field blocks are easy to desynchronize. `MAX_MPCC`-sized arrays assume the implementation never indexes beyond hardware MPCC count. Fast-load status/underflow fields require careful sequencing so partial 3D LUT updates do not become visible. The TODO in the RMCM register list notes possible missing 3D LUT registers.

## Test signals
Useful signals include DCN42 build coverage, display bring-up with multiple planes, MPCC blend and background-color tests, output CSC/OGAM/MCM/RMCM color-management validation, RMCM shaper and 3D LUT programming with both banks, fast-load completion and underflow checks, DWB mux validation, and suspend/resume or hotplug mode-set tests that force reconstruction.
