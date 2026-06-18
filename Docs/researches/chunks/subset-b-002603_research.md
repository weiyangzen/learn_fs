# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 27637-30183

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `_MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the middle of the hull-shader resource programming family, immediately after earlier `SPI_SHADER_PGM_RSRC1_HS` shifts, and continue through hull-shader resource/user-data fields, SPI request/arbitration/debug/DIDT controls, TCP watchpoint fields, and a large graphics-decoder block for depth buffer, stencil, scissor, viewport, clip, VRS, color blend, and pixel-shader interpolation/input state. The chunk ends at the opening comment for `SPI_PS_INPUT_CNTL_23`, before that register's fields are emitted in the next chunk.

Although the repository path is nested under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 registers. Driver code pairs these field macros with register address symbols from the matching GC 12.1.0 offset header and, where available, generated default/reset-value headers. Consumers normally use these constants through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so hardware register values can be packed or decoded without hard-coded bit positions.

This slice covers several graphics-programming surfaces:

- Hull/LS-HS shader state: `SPI_SHADER_PGM_RSRC1_HS`, `SPI_SHADER_PGM_RSRC2_HS`, 32 `SPI_SHADER_USER_DATA_HS_*` payload registers, `SPI_SHADER_REQ_CTRL_LSHS`, and four `SPI_SHADER_USER_ACCUM_LSHS_*` contribution registers.
- SPI scheduler and debug controls: time-slot arbitration, WCL pipe percentage controls for graphics, HP3D, and compute queues, per-VMID user-accum/debug controls, compute queue reset, wavefront context-save status, DIDT throttle controls, and DIDT type masks.
- TCP watchpoints: four watch address/control triplets with 48-bit-style high/low address fields, VMID matching, mask, mode, valid, and attach bits.
- DB/depth/stencil render state: render control/override, depth view and size, Z/stencil metadata/base addresses, GL1/cache temporal policy, depth bounds, count/viewport controls, VRS center location, shader/depth/stencil controls, EQAA, alpha-to-mask, stencil refs/op values/read masks/write masks, and TA border-color base address.
- PA/SC/CL viewport and clipping state: screen/window/generic/viewport scissors, clip rectangles and extensions, edge rules, hardware screen offsets, user clip planes, guard-band adjust registers, raster/tile steering controls, 16 viewport transform sets, and 16 Z min/max ranges.
- VRS and color state: VRS override, feedback/rate surface bases and sizes, VRS info, color-buffer GL2 cache policy, and constant blend color components.
- Pixel-shader input/interpolation state: `SPI_PS_IN_CONTROL`, interpolation control, shader index/position/Z/color export format, barycentric control, PS input enable/address masks, and `SPI_PS_INPUT_CNTL_0` through the start of `SPI_PS_INPUT_CNTL_23`.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.
- Register-address symbols are expected in the companion `gc_12_1_0_offset.h` header, commonly with `mm...` names matching these register names.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, MMIO read/write helpers, command-packet register programming, debug/perf dump decoders, reset/recovery code, virtualization handling, and shader/pipeline state setup.

Important macro families in this slice include:

- `SPI_SHADER_PGM_RSRC1_HS` and `SPI_SHADER_PGM_RSRC2_HS`: hull-shader VGPR/SGPR counts, priority, float mode, privilege/debug/perf controls, forward progress, WGP mode, LS VGPR component count, FP16 overflow, scratch enable, user SGPR count, trap/OC LDS/threadgroup-size controls, exception enables, LDS size, and shared VGPR count.
- `SPI_SHADER_USER_DATA_HS_0..31`: full-width data payload registers used to pass shader user-data SGPR values to the hull-shader stage.
- `SPI_SHADER_REQ_CTRL_LSHS` and `SPI_SHADER_USER_ACCUM_LSHS_0..3`: LS-HS soft grouping, request count, allocation timeout, hard-lock thresholds, producer lockout, global scanning, allocation-rate throttling, and user-accum contribution fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0`, and `SPI_ARB_CYCLES_1`: SPI pipe time-slot ordering, duration multipliers, and per-time-slot cycle durations.
- `SPI_WCL_PIPE_PERCENT_GFX`, `SPI_WCL_PIPE_PERCENT_HP3D`, and `SPI_WCL_PIPE_PERCENT_CS0..7`: wavefront control/launch percentage fields for graphics, HP3D, and compute pipe groups.
- `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_COMPUTE_WF_CTX_SAVE`, `SPI_SAVE_RESTORE_STATUS`, `SPI_CONFIG_DIDT_CNTL`, and `SPI_CONFIG_DIDT_TYPEMASK`: VMID-scoped accumulation/debug control, compute queue reset, wavefront context-save address/status, and dynamic instruction/data throttling configuration.
- `TCP_WATCH0..3_{ADDR_L,ADDR_H,CNTL}`: texture/cache watchpoint address and control fields with VMID, address mask, mode, valid, and attach behavior.
- `DB_RENDER_CONTROL`, `DB_DEPTH_VIEW`, `DB_DEPTH_VIEW1`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_DEPTH_SIZE_XY`, `DB_Z_INFO`, `DB_STENCIL_INFO`, and DB base-address pairs: depth/stencil surface layout, compression/decompression, HiZ/HiS, HTILE, Z-range precision, read/write base addresses, sample controls, and render override modes.
- `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_STENCIL_CONTROL`, `DB_EQAA`, and `DB_ALPHA_TO_MASK`: depth/stencil test state, shader export/depth ordering, sample/overrasterization behavior, alpha-to-mask offsets, and conservative/ordered pixel-shader controls.
- `SC_MEM_TEMPORAL`, `SC_MEM_SPEC_READ`, `PA_SC_*`, `PA_CL_*`, and `PA_SU_*`: cache temporal/speculative-read policy, viewport/scissor bounds, window offsets, clip rectangles, edge rules, raster config, tile steering, user clip planes, guard-band clip/discard adjust values, and viewport transforms.
- `PA_SC_VRS_*`: variable-rate shading override, rate/feedback surface addresses and dimensions, and VRS software mode fields.
- `CB_RMI_GL2_CACHE_CONTROL` and `CB_BLEND_*`: color-buffer GL2 read/write cache policy and full-width floating-point blend constant components.
- `SPI_PS_IN_CONTROL`, `SPI_INTERP_CONTROL_0`, `SPI_SHADER_*_FORMAT`, `SPI_BARYC_CNTL`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, and `SPI_PS_INPUT_CNTL_0..22`: pixel-shader interpolation mode, export format, barycentric enable/control, input enable/address bitmaps, and per-attribute interpolation controls. Attributes 0 through 19 include point-sprite texture fields; attributes 20 through 22 omit the point-sprite texture bits in this range.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 12.1.0 register metadata for the active ASIC generation.
2. Choose the matching register address from `gc_12_1_0_offset.h`.
3. Read an existing register value or construct a command-packet/MMIO register value.
4. Use the `__SHIFT`/`_MASK` pairs, usually through generated register helpers, to pack field values or extract status bits.
5. Apply the resulting value during shader setup, graphics draw state programming, VRS setup, depth/stencil/color state setup, TCP debug watchpoint programming, SPI scheduling/debug control, queue reset/recovery, or hang/perf diagnostics.

For shader setup, graphics pipeline code writes hull-shader resource registers, user-data registers, LS-HS request controls, and pixel-shader interpolation/input registers before dispatching draws. For render state, command submission programs DB/PA/SC/CL/CB state from API pipeline state: depth/stencil formats and bases, stencil refs/masks, viewport transforms, scissor rectangles, clip planes, blend constants, VRS rate images, and pixel-shader input mappings. For debug and recovery, code may program TCP watchpoints, decode SPI save/restore state, reset compute queues, inspect context-save wavefront status, or tune/disable SPI/DIDT behavior.

This generated header does not encode ordering requirements, polling loops, clear-on-read semantics, sticky bits, reserved-bit preservation rules, address alignment units, cache coherency sequences, or side-effect timing. Those rules live in AMDGPU engine code, firmware interfaces, command-stream validation, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, and AMDGPU runtime programming.

Shader resource and user-data fields persist as context state until replaced by later command-stream writes, reset, preemption/context restore, or power-transition reinitialization. Incorrect VGPR/SGPR, LDS, scratch, trap, exception, user SGPR, or WGP-mode masks can make hull shaders launch with invalid resources, wrong trap behavior, or broken scratch/LDS accounting. Pixel-shader input and interpolation state similarly persists as draw state and must match compiled shader expectations; bad attribute offsets, defaults, flat-shade flags, validity bits, or barycentric controls can corrupt interpolation or make shaders read unintended attributes.

DB/PA/SC/CL/CB registers are active graphics pipeline state. Depth/stencil base addresses, metadata/compression modes, stencil refs/masks, depth bounds, viewport/scissor rectangles, clip planes, VRS surfaces, blend constants, and color/depth cache policy remain relevant across draws until reprogrammed. Split base address fields and `BASE_256B` VRS fields imply address-unit and alignment constraints outside this header. Full-register writes around dense render override and shader control registers must preserve reserved bits unless the hardware sequence explicitly defines them.

SPI scheduler, WCL, debug, DIDT, compute reset, and context-save status fields include privileged or side-effecting controls. Queue reset, wavefront save/restore, debug-per-VMID, and DIDT throttling can alter execution behavior or recovery state; they should not be treated as passive status. TCP watchpoint registers are persistent debug state and can affect memory/debug behavior for selected VMIDs and address windows until disabled.

Viewport, scissor, clip, and VRS arrays are heavily repeated state. Off-by-one index mistakes, partial programming of multi-register families, or mismatched top-left/bottom-right pairs can create rendering clipping errors that are hard to diagnose from register dumps alone.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register family staying internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` should provide matching register address macros.
- Any matching GC 12.1.0 default/reset header should remain consistent with these masks.
- AMDGPU register helpers provide the actual field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU GFX, shader pipeline setup, graphics command submission, KFD/compute queue recovery, CP/SPI debug, VRS, DB/CB/PA/SC state emission, reset/suspend/resume, SR-IOV/virtualization, debugfs, perf, and hang-dump paths are likely consumers.

Integration points include hull-shader program resource emission, shader user-data upload, LS-HS scheduling controls, SPI pipe arbitration and WCL throttling, VMID-scoped debug/accumulation, compute queue reset and wavefront context-save handling, TCP watchpoint setup, depth/stencil surface programming, Z/stencil compression metadata, GL1/GL2 cache policy selection, stencil/depth tests, EQAA and alpha-to-mask behavior, screen/window/viewport scissors, clip rectangles and user clip planes, raster/tile steering, VRS rate/feedback images, blend constants, and pixel-shader attribute interpolation.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- This chunk starts and ends mid-family. `SPI_SHADER_PGM_RSRC1_HS` began before line 27637, and `SPI_PS_INPUT_CNTL_23` continues after line 30183; adjacent chunks are required for complete family-level conclusions.
- Many fields are repeated arrays with only index changes: 32 hull-shader user-data registers, 16 viewports, 16 viewport scissor pairs, 16 viewport transform/Z ranges, 6 user clip planes, 4 clip rectangles, 4 TCP watchpoints, and 23 visible pixel-shader input controls. Generator or copy mistakes can be isolated to one index and produce index-specific render/debug faults.
- Address fields use different units and widths. DB Z/stencil and TA base pairs, TCP high/low watch addresses, and VRS `BASE_256B` surfaces require correct split-address and alignment handling outside the mask definitions.
- Dense DB render override/control fields can carry side effects for compression, decompression, HiZ/HiS, sample counts, ReZ, VRS center selection, conservative/ordered pixel shader, and depth-before-shader behavior. Full-register writes are risky without reserved-bit preservation.
- Pixel-shader input controls are similar but not uniform. Attributes 0 through 19 expose point-sprite texture fields, while 20 through 22 in this range omit those fields; assuming a single template for all 32 inputs can encode nonexistent bits.
- Stencil and depth state contains front/back-face variants. Swapping `_BF` masks or default values can cause one-sided rendering failures that are not obvious in simple tests.
- Viewport/scissor fields mix 16-bit, 15-bit, 13-bit, 12-bit, and full-width data fields. Treating them as a uniform coordinate format can truncate or sign/extend incorrectly.
- VRS rate and feedback surfaces are stateful memory references. Wrong base, size, mode, or override fields can cause invalid shading rates, corrupt feedback, or memory faults.
- SPI compute reset, wavefront context-save, debug, TCP watchpoint, and DIDT controls are not harmless decode fields. Incorrect writes can reset queues, disturb debug sessions, change throttling, or mask execution problems.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and graphics/runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GFX pipeline state, shader setup, DB/CB/PA/SC emission, VRS, debug/hang dump, reset, and queue recovery paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `_MASK` value in this line range.
- Cross-checks that every register in this chunk has matching address macros in `gc_12_1_0_offset.h` and expected defaults in the matching generated default header where applicable.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, split base-address masks should match documented widths, repeated indexed families should remain structurally consistent where hardware intends, and fields should not overlap unless documented.
- Shader pipeline tests that validate HS resource programming, user-data SGPR layout, LS-HS request controls, pixel-shader input enable/address masks, interpolation defaults, flat shading, FP16 interpolation mode, barycentric controls, and export format selection.
- Render-state tests covering depth/stencil enable/write/compare modes, stencil front/back refs/op values/read/write masks, depth bounds, EQAA, alpha-to-mask, shader depth export/kill behavior, sample counts, and DB render override paths.
- Surface/address tests that program Z/stencil read/write bases, TA border-color base, and VRS rate/feedback bases with known aligned addresses and verify correct high/low or `BASE_256B` packing.
- Viewport/scissor/clip tests that exercise all 16 viewport rectangles, viewport scissors, viewport transforms, Z min/max ranges, screen/window/generic scissors, clip rectangles, clip rectangle extensions, edge rules, user clip planes, and guard-band adjustments.
- VRS tests that vary override rate, combiners, rate-surface enablement, feedback writeback, surface sizes, and software mode fields under controlled draws.
- TCP/debug tests that program watchpoints for each watch index and VMID, verify address match/mask behavior, and ensure disabling clears debug effects.
- SPI scheduling/recovery tests that cover WCL percentages, arbitration durations, user-accum VMID controls, compute queue reset, wavefront context-save status, and DIDT type masks without unexpected hangs or performance regressions.
- Runtime warning signals include HS launch failures, shader input/interpolation corruption, missing or wrong point-sprite attributes, depth/stencil one-sided failures, bad clipping/scissor behavior, invalid VRS rates or feedback writes, cache/compression anomalies, stuck compute queue reset, unexpected wavefront context-save state, TCP watchpoints firing on the wrong VMID/address, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002603`. It covers lines 27637-30183 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `SPI_SHADER_PGM_RSRC1_HS` and `SPI_PS_INPUT_CNTL_23` families and to place these SPI, TCP, DB, PA/SC/CL, VRS, CB, and pixel-shader input definitions in the full GC 12.1.0 register map.
