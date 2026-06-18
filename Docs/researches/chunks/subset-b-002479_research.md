# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 7649-10057

## Scope

This chunk is a generated AMDGPU GC 10.3.0 shader-mask header segment. It contains C preprocessor constants only: each register field has a `__SHIFT` constant and a matching `MASK` constant. The paired register-address definitions live in the corresponding GC offset headers, while driver code consumes these names through helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and golden-register table initializers.

The range starts in the primitive assembly/scanner (`PA_SC`) binner event/control area, then covers full register-field maps for the `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and most of `gc_rbdec` address blocks, ending at the first part of `CB_HW_CONTROL_4`.

## Purpose

The purpose of this header slice is to make GC 10.3.0 register bit layouts available to the AMDGPU kernel driver without hand-coded numeric shifts at every call site. These masks let runtime code extract hardware topology from registers, apply ASIC-specific golden settings, program diagnostics such as thread trace and watchpoints, and decode or control low-level GPU blocks.

Important consumers are in the GC 10 driver path, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`. That file includes the GC 10.1 header directly but also defines/adapts GC 10.3 aliases, uses the same field-name contract, and programs many registers represented by this chunk. For GC 10.3 ASICs, `gfx_v10_0_gpu_early_init()` reads `mmGB_ADDR_CONFIG` and derives `adev->gfx.config.gb_addr_config_fields` with `REG_GET_FIELD(..., GB_ADDR_CONFIG, NUM_PKRS/NUM_PIPES/MAX_COMPRESSED_FRAGS/NUM_RB_PER_SE/NUM_SHADER_ENGINES/PIPE_INTERLEAVE_SIZE)`. The same source carries GC 10.3 golden settings for `mmPA_SC_BINNER_TIMEOUT_COUNTER`, `mmPA_SC_ENHANCE_2`, `mmLDS_CONFIG`, `mmSQ_CONFIG`, `mmSPI_CONFIG_CNTL_1`, `mmDB_DEBUG3`, `mmDB_DEBUG4`, `mmDB_EXCEPTION_CONTROL`, `mmGB_ADDR_CONFIG`, and `mmCB_HW_CONTROL_4`, all of which depend on the register-field definitions remaining aligned with hardware.

## Register Families Covered

The PA/SC portion covers binner event, batching, clock-gating, FIFO, steering, and enhancement controls. It includes `PA_SC_BINNER_TIMEOUT_COUNTER`, `PA_SC_BINNER_PERF_CNTL_0..3`, `PA_SC_ENHANCE_2`, `PA_SC_BINNER_CNTL_OVERRIDE`, `PA_SC_PBB_OVERRIDE_FLAG`, `PA_PH_INTERFACE_FIFO_SIZE`, `PA_PH_ENHANCE`, `PA_SC_BC_WAVE_BREAK`, `PA_SC_ENHANCE_3`, `PA_SC_FIFO_SIZE`, `PA_SC_IF_FIFO_SIZE`, `PA_SC_PKR_WAVE_TABLE_CNTL`, `PA_SIDEBAND_REQUEST_DELAYS`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_DSM_CNTL`, and `PA_SC_TILE_STEERING_CREST_OVERRIDE`. These fields tune primitive batch breaking, persistent state thresholds, PBB behavior, SC/DB/BCI/SPI interface gating, FIFO depths, timeout thresholds, and tile steering override. In `gfx_v10_0.c`, GC 10.3 golden settings repeatedly program `mmPA_SC_BINNER_TIMEOUT_COUNTER` to `0x00000800` and `mmPA_SC_ENHANCE_2` with ASIC-specific masks/values, so drift in these definitions can surface as hangs or incorrect primitive binning behavior.

The `gc_sqdec` block maps shader core and shader-cache registers. It includes `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQG_STATUS`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, `SQ_RUNTIME_CONFIG`, `SH_MEM_BASES`, `SP_CONFIG`, `SQ_ARB_CONFIG`, `SH_MEM_CONFIG`, shader trap addresses (`SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`), SQC UTCL0 instruction/data cache control and status, `SQG_CONFIG`, shader-rate config, interrupt masking/message control, watchpoint registers `SQ_WATCH0..3`, SQ thread-trace buffer/mask/token/control/status/counter registers, indirect index/data access, `SQ_CMD`, time registers, load-balancer counters, EDC counters, and WREXEC address fields. These definitions back shader dispatch behavior, memory aperture defaults, per-VMID cache invalidation, thread trace capture, debugger watchpoints, and error-reporting controls.

The `gc_shsdec` block maps shader processor input/export controls. It includes `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_CONFIG_CNTL`, `SPI_WAVE_LIMIT_CNTL`, `SPI_CONFIG_CNTL_2`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_PS_CU_EN`, wavefront lifetime control/limit/status registers, SPI load-balancer counters, static WGP masks, `SPI_GDS_CREDITS`, SX export and scoreboard buffer sizes, CSQ wavefront active counters, per-WGP active wave counters, and trap screen base/mask/minimum GPR registers for pipes 0 and 1. `gfx_v10_0.c` programs `mmSPI_CONFIG_CNTL_1` and remaps `mmSPI_CONFIG_CNTL_REMAP` to the proper `mmSPI_CONFIG_CNTL` offset on some GC 10.3 ASICs, so these masks are part of the user-mode register-remap and golden-setting boundary.

The `gc_tpdec` block covers texture pipe status and diagnostics: `TD_STATUS`, `TD_DSM_CNTL`, `TD_DSM_CNTL2`, `TD_SCRATCH`, `TA_CNTL`, `TA_RESERVED_010C`, `TA_STATUS`, and `TA_SCRATCH`. Fields expose busy bits, FIFO empty/busy status, DSM single-write/error-injection controls, and TA/TD credit tuning. These are low-level debug and bring-up surfaces rather than normal filesystem or memory-management code paths.

The `gc_gdsdec` block covers global data share state. It includes `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, protection fault registers (`GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`), EDC counters, physical and pipe open-address counters, DSM controls, and `GDS_WD_GDS_CSB`. These fields are used for GDS/GWS/OA arbitration, VMID fault reporting, address/counter diagnostics, and EDC/FUE accounting. Any KFD or compute path that enables GDS/GWS/OA resources relies on these field meanings for fault attribution and debug visibility.

The `gc_rbdec` block covers depth-buffer, render-backend, graphics-block topology, and the beginning of color-buffer controls. It includes `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, multiple stutter controls, credit and watermark registers, subtile/cacheline/FIFO controls, burst/ring/RMI/cache/exception controls, DFSM configuration/status/watchdog/flush controls, DB fine-grain clock-gating SRAM/interface overrides, `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, `GB_ADDR_CONFIG_READ`, and the first `CB_HW_CONTROL_4` fields. This block is especially important because `GB_ADDR_CONFIG` fields are persisted into `adev->gfx.config` during early init and drive downstream tile-pipe, RB, SE, compressed-fragment, and pipe-interleave assumptions.

## Important APIs, Types, and Macros

This file defines no functions, structs, or runtime storage. Its API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift for a field within a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit field mask.
- Register-group comments such as `// addressBlock: gc_sqdec` and `//GB_ADDR_CONFIG` provide the hardware grouping used by generated register headers and review tools.

The main external helper contract is that AMDGPU macros concatenate register and field names. For example, `REG_GET_FIELD(gb_addr_config, GB_ADDR_CONFIG, NUM_PKRS)` expands using `GB_ADDR_CONFIG__NUM_PKRS_MASK` and `GB_ADDR_CONFIG__NUM_PKRS__SHIFT`. `REG_SET_FIELD` and golden-setting macros use the same convention when constructing masked writes. This makes field-name stability an ABI-like source contract inside the driver: changing a macro spelling or numeric value breaks compile-time expansion or silently targets the wrong hardware bits.

## Control Flow

There is no executable control flow in this header. Control flow appears at the integration points:

- During GPU early init, `gfx_v10_0_gpu_early_init()` reads `mmGB_ADDR_CONFIG`, extracts fields via this register-field convention, and stores derived values in `adev->gfx.config`.
- During golden-register initialization, GC 10.3 tables in `gfx_v10_0.c` apply masked writes to many registers covered here. These writes happen as part of ASIC initialization and resume paths.
- During user-mode register remapping, `gfx_v10_0.c` writes `mmGRBM_CAM_DATA` entries so UMD-facing register aliases map to hardware registers such as `mmSPI_CONFIG_CNTL`; the field masks in this header document the target register layout.
- Diagnostic or debug paths can read status/fault/thread-trace/watchpoint fields after hardware events. The masks define how raw register dumps are decoded.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile GPU state, usually reset or reprogrammed during GPU initialization, suspend/resume, and reset recovery.

Some decoded values become persistent driver state for the life of an initialized device. `GB_ADDR_CONFIG` is the clearest example: `gfx_v10_0_gpu_early_init()` saves the raw register value in `adev->gfx.config.gb_addr_config` and derives `num_pipes`, `max_tile_pipes`, `max_compress_frags`, `num_rb_per_se`, `num_se`, `pipe_interleave_size`, and, for GC 10.3, `num_pkrs`. Those values feed later memory-layout, tiling, and render-backend decisions. Incorrect masks here can persist as wrong topology even if the raw register read was correct.

Other fields describe diagnostic state that persists only until cleared or reset, such as SQ/GDS/DB EDC counters, GDS protection fault latches, thread-trace write pointers/status, SPI lifetime interrupt status, and DB DFSM watchdog/flush state. Golden-setting writes persist in hardware until overwritten, GPU reset, or power-management transitions reapply them.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register ecosystem:

- Matching offset headers provide `mm*` or `reg*` addresses for the same register names.
- `amdgpu` SOC15 register helpers perform raw MMIO reads/writes using those offsets.
- Register helper macros in the AMDGPU codebase compose the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names defined here.
- ASIC-specific code in `gfx_v10_0.c` chooses which golden-setting table applies to IP versions such as GC 10.3.0, 10.3.2, 10.3.3, 10.3.4, 10.3.5, 10.3.6, and 10.3.7.
- KFD/compute, debugfs, perf/trace, RAS/EDC, and GPU-reset tooling can indirectly depend on these bit layouts when they inspect shader, GDS, DB/RB, or thread-trace state.

Notable cross-block integration:

- `PA_SC_*`, `DB_*`, `CB_*`, and `GB_*` fields jointly affect graphics frontend/binning, depth/color backend, and render-backend topology.
- `SQ_*`, `SQC_*`, `SPI_*`, and `SX_*` fields jointly affect shader wave scheduling, cache behavior, thread trace, trap handling, and export buffering.
- `GDS_*` and `SPI_GDS_CREDITS` connect shader dispatch with shared data-store resource flow.
- `GB_ADDR_CONFIG` and `CC_RB_*` connect topology discovery with RB disable/redundancy and backend mapping.

## Risks

The main risk is silent hardware misprogramming. These are all numeric constants; a one-bit shift or mask error can compile cleanly but make the driver program the wrong feature, decode the wrong topology, or miss a fault/status bit.

High-risk fields in this chunk include `GB_ADDR_CONFIG` and `GB_ADDR_CONFIG_READ`, because they drive persistent topology in `adev->gfx.config`; `PA_SC_ENHANCE_2`, `LDS_CONFIG`, `SQ_CONFIG`, `SPI_CONFIG_CNTL_1`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_EXCEPTION_CONTROL`, and `CB_HW_CONTROL_4`, because GC 10.3 golden settings write them during initialization; SQC UTCL0 invalidation fields, because cache-invalidation and VMID handling failures can cause stale instruction/data fetches; SQ thread trace and watchpoint fields, because debug tooling depends on precise buffer, VMID, and mask semantics; and GDS protection-fault fields, because fault attribution depends on correct VMID, address, CU/SIMD/wave, TMZ, GWS, and OA decoding.

The chunk also contains reserved, unused, and diagnostic/error-injection fields. Accidentally enabling DSM/error-injection bits or reserved clock-gating overrides can create hangs that are difficult to tie back to a header-only change. Conversely, overzealous cleanup of apparently unused fields can break out-of-tree tooling, register dump decoders, or future ASIC-specific workarounds.

Because this is generated source, hand edits are risky. Regeneration from the authoritative AMD register database should preserve ordering, names, and values; if manual patches are unavoidable, they should be reviewed against the matching offset header and hardware documentation.

## Test Signals

Useful compile-time signals are straightforward: AMDGPU builds must continue to compile anywhere `REG_GET_FIELD`, `REG_SET_FIELD`, or golden settings reference these names. Missing or renamed macros fail at compile time.

Runtime validation needs hardware or register-emulation coverage. Strong signals include successful boot/probe of GC 10.3 ASICs, correct `adev->gfx.config` topology values from `GB_ADDR_CONFIG`, no regressions in GPU reset and suspend/resume, no graphics or compute hangs during golden-register application, and stable rendering/compute under workloads that stress binning, DB/CB paths, shader waves, and GDS.

Debug and diagnostic signals include sane register dumps for `SQ_THREAD_TRACE_*`, working SQ watchpoints/thread trace, expected EDC/fault counter behavior, correct GDS protection-fault attribution, and no unexpected DB DFSM watchdog or exception-control events. For changes near `CB_HW_CONTROL_4`, render correctness and cache/scoreboard behavior under color/depth-heavy workloads are important. For changes near cache invalidation fields, VM and shader-cache stress tests should show no stale-data or stale-instruction symptoms.
