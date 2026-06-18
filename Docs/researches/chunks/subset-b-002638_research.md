# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 14605-17204

## Purpose

This chunk is generated AMD GC 9.1 register field metadata. It contains no executable driver logic; it publishes C preprocessor constants for hardware register bit positions and masks used by AMDGPU code when constructing, updating, or decoding Graphics Core MMIO register values.

The requested line range spans several GC hardware decode areas:

- The tail of GC-level EDC/DIDT and CAC metadata, beginning mid-`GC_EDC_CTRL` and then covering EDC thresholds/status/overflow, DIDT and EDC droop controls, GC/SE CAC indirect index/data registers, and SE CAC clock-gating timing.
- `addressBlock: gc_tcpdec`, covering TCP watchpoint address/control registers, GATCL1/UTCL1 controls and status, and TCP perf-counter filter fields.
- `addressBlock: gc_gdspdec`, covering GDS per-VMID base/size windows, GWS/OA per-VMID ownership, GWS/OA reset controls, compute max wave ID, GDS enhance/restore bits, and compute/graphics context-switch status/counters.
- `addressBlock: gc_rasdec`, covering RAS signature controls and signature readback registers for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- The beginning of `addressBlock: gc_gfxdec0`, covering DB depth/stencil/render state, PA scissor/clip/window/viewport state, CB target/shader masks and blend constants, CP context identifiers, VGT reset index, DCC/stencil state, viewport transforms, user clip planes, and `SPI_PS_INPUT_CNTL_0` through the first fields of `SPI_PS_INPUT_CNTL_14`.

The chunk has more than 2,100 `#define` lines. The line boundaries are artificial: line 14605 starts after the `GC_EDC_CTRL` shift and low mask fields, and line 17204 stops before the remaining `SPI_PS_INPUT_CNTL_14` masks. Adjacent chunks are required for complete per-register coverage at both edges.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU kernel-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: mask used to extract, clear, or set that field.

These constants are intended to be paired with the matching address macros in `gc_9_1_offset.h`, then consumed through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_GET_FIELD`, `REG_SET_FIELD`, and lower-level CGS accessors.

Representative register groups in this chunk:

- `GC_EDC_*`, `GC_DIDT_DROOP_CTRL`, `GC_EDC_DROOP_CTRL`, `GC_CAC_IND_*`, and `SE_CAC_*`: power droop, electrical-design-current throttling/status, CAC indirect access, and SE CAC clock-gating fields.
- `TCP_WATCH{0..3}_ADDR_{H,L}` and `TCP_WATCH{0..3}_CNTL`: TCP address watchpoint comparators with address, mask, VMID, ATC, mode, and valid fields.
- `TCP_GATCL1_CNTL`, `TCP_UTCL1_CNTL1`, `TCP_UTCL1_CNTL2`, and `TCP_UTCL1_STATUS`: texture cache and L1 translation/cache behavior, invalidation, fault response, snooping, force-miss, FIFO/cache-depth reduction, and status fields.
- `TCP_PERFCOUNTER_FILTER` and `_EN`: per-event perf-counter selection and enable fields for texture-cache-related counters.
- `GDS_VMID{0..15}_BASE` and `GDS_VMID{0..15}_SIZE`: per-VMID GDS address-window base and size fields.
- `GDS_GWS_VMID{0..15}` and `GDS_OA_VMID{0..15}`: per-VMID ownership/resource fields for global wave sync and ordered append.
- `GDS_GWS_RESET*`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET`: reset masks and reset triggers for GDS-managed resources.
- `GDS_*_CTXSW_*`: context-switch status and counters for compute shader, graphics shader, VS, PS0-PS7, and GS activity.
- `RAS_*_SIGNATURE*`: signature-control and per-block signature readback fields used for RAS/diagnostic comparison.
- `DB_*`: depth/stencil render control, depth view, render override, htile base, depth/stencil clear values, Z/stencil info and base addresses, and DFSM controls.
- `PA_SC_*`, `PA_SU_*`, and `PA_CL_*`: screen/window/generic/viewport scissors, clip-rect rules, edge rules, hardware screen offset, raster config, tile steering, viewport transforms, and user clip planes.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_BLEND_*`, and `CB_DCC_CONTROL`: color-buffer write masks, shader export masks, blend constants, and DCC behavior.
- `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`: command processor context identification and perfmon context fields.
- `VGT_MULTI_PRIM_IB_RESET_INDX`: primitive restart index for indexed draws.
- `SPI_PS_INPUT_CNTL_{0..14}`: pixel-shader interpolator input metadata fields such as attribute offset, default values, flat shade, cylindrical wrap, point-sprite texture selection, duplication, FP16 interpolation mode, and attribute-valid bits.

## Control Flow

This header has no local control flow. It participates in runtime behavior only through macro expansion in code that reads, modifies, and writes registers.

Common usage follows a read-modify-write pattern:

1. Runtime code reads a register value from the GC address space or an indirect index/data pair.
2. It clears a field with `~<REGISTER>__<FIELD>_MASK`.
3. It shifts a desired value by `<REGISTER>__<FIELD>__SHIFT` and masks it back into place.
4. It writes the resulting register value, or extracts a field with the same mask/shift pair for status decisions.

For the GC EDC/DIDT fields, power-management code uses table-driven configuration entries containing an offset, mask, shift, and value. The local Vega10 PowerTune implementation demonstrates the pattern for same-named GC EDC fields: `vega10_program_gc_didt_config_registers()` reads a register, clears the configured mask, ORs `(value << shift) & mask`, and writes the value back; `vega10_enable_psm_gc_edc_config()` wraps related programming with RLC safe-mode entry/exit and shader-engine selection.

For DB/PA/CB/VGT/SPI state, the control flow is normally driven by command submission and graphics pipeline setup rather than ordinary CPU-side loops in this header. User-mode or kernel command builders emit register writes for draw state; hardware then consumes these fields during depth/stencil testing, rasterization, clipping, viewport transform, color export, interpolation, and primitive restart handling.

GDS and TCP fields sit on compute and memory/cache control paths. GDS base/size/ownership/reset fields are relevant to queue setup, context switching, and resource isolation by VMID. TCP watchpoints, UTCL1 invalidation, and perf-counter filters are diagnostic, cache-control, or performance-measurement surfaces; correct sequencing is imposed by the relevant cache, VM, or profiling code rather than by this generated file.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state.

EDC/DIDT/CAC registers hold power-management configuration and status. Control fields can enable throttling, reset logic, select droop levels, configure thresholds, or select indirect CAC addresses; status fields expose throttle levels, rolling droop/power deltas, overflow conditions, and similar hardware-maintained values.

TCP registers hold watchpoint, translation/cache, invalidation, and perf-counter state. Watchpoint `VALID`, `VMID`, `ATC`, `MODE`, address, and mask fields persist in hardware until overwritten or reset. UTCL1 invalidation and force-miss/force-snoop controls may be transient or side-effect-sensitive depending on the hardware programming sequence.

GDS registers hold VMID-scoped resource allocation and context-switch accounting state. Base/size and GWS/OA ownership fields define resource partitioning. Reset fields can clear resources, while context-switch counters/status reflect hardware-maintained activity and may be sticky until reset or overwritten by hardware.

RAS signature registers are diagnostic state. Signature control/mask fields configure collection or comparison, and signature registers expose block-specific values that are meaningful only under the selected RAS/test mode.

DB/PA/CB/VGT/SPI registers are graphics pipeline state. They persist in the GPU context until command streams, context switches, suspend/resume, reset, or driver reinitialization replace them. Many of these fields are part of user-visible rendering correctness: scissor bounds, viewport transforms, depth/stencil base addresses, target masks, shader export masks, and pixel-shader input controls directly affect draws.

The header does not encode read-only, write-one-to-clear, self-clearing, sticky, privilege, or reserved-bit semantics. Those properties are hardware-defined and must be respected by the code that uses the masks.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`, which supplies matching register offsets and base-index symbols. This shift/mask header must remain synchronized with that offset header and AMD's GC 9.1 register database.

Other nearby integration surfaces include:

- AMDGPU SOC15 access helpers and field helpers used to read/write GC registers.
- PowerPlay/PowerTune DIDT and EDC code paths that use offset/mask/shift/value tables to program GC power-management registers.
- GFX/RLC safe-mode and GRBM index selection when programming per-SE or per-instance graphics state.
- KFD and graphics queue setup paths that depend on GDS partitioning, VMID resource ownership, and context-switch state.
- Command submission and graphics pipeline state programming paths that consume DB, PA, CB, VGT, and SPI field layouts.
- RAS and diagnostics paths that read signature registers or set signature controls.
- Perf/debug paths that configure TCP perf filters, watchpoints, or register dumps.

In this tree, direct textual inclusion of `gc_9_1_sh_mask.h` was not observed in the C files searched; `gc_9_1_offset.h` is included by `psp_v10_0.c`, and same-named GC EDC/DIDT field macros are used by `pm/powerplay/hwmgr/vega10_powertune.c` through that platform's include stack. The exact generated generation selected at compile time is ASIC-specific, so users must pair GC 9.1 offsets and masks rather than mixing them with GC 9.0, GC 10, or later headers that may share names but differ in bit layout.

## Risks And Edge Cases

- These macros are untyped numeric constants. A wrong mask or shift compiles cleanly but can program the wrong hardware bits.
- The chunk contains many repeated per-VMID, per-viewport, per-pixel-shader-input, and per-pipeline-stage register families. A generation or copy error can affect only one VMID, viewport, PS input slot, or shader stage, making failures sparse and workload-specific.
- The range starts and ends mid-register. Research consumers must merge adjacent chunks before making complete claims about `GC_EDC_CTRL` or `SPI_PS_INPUT_CNTL_14`.
- Reserved and `UNUSED` masks are present. Blindly writing full register values can corrupt reserved fields unless hardware documentation explicitly requires it.
- EDC/DIDT fields affect throttling, droop handling, clock override, and force-stall behavior. Bad programming can create power, stability, or performance failures that only appear under load, thermal pressure, or power-management transitions.
- TCP watchpoint and UTCL1 invalidation fields are VMID- and address-sensitive. Incorrect `VMID`, `ATC`, address, mask, or invalidation fields can miss debug events, disrupt translation behavior, or create cache-coherency symptoms.
- GDS VMID base/size and GWS/OA ownership fields are isolation-sensitive. Wrong masks can overlap VMID resources or reset the wrong GDS allocation.
- DB depth/stencil and base-address fields are memory-safety-sensitive. Bad masks can point hardware at the wrong depth, stencil, or htile memory or misconfigure compressed/decompressed layout fields.
- PA scissor, clip, viewport, and user clip-plane fields are rendering-correctness-sensitive. Off-by-one or sign/width mistakes usually show up as clipped, missing, or overdrawn pixels rather than immediate driver errors.
- `SPI_PS_INPUT_CNTL_*` fields define interpolation and attribute validity. A wrong attribute offset, default, point-sprite, FP16 interpolation, or valid bit can produce shader input corruption that varies by pipeline state.

## Test Signals

Useful validation is mostly integration and hardware oriented:

- Kernel build coverage with AMDGPU, PowerPlay, GFX, KFD, RAS, and debug/perf code enabled catches missing or renamed macros.
- Static checks should verify that GC 9.1 offset and shift/mask headers are regenerated together and that same-named fields are not accidentally mixed across GC generations.
- Power-management validation should exercise DIDT/EDC enable, disable, reset, forced-stall, load, idle, suspend/resume, and thermal/power-limit transitions while monitoring for ring timeouts, throttling anomalies, and unstable clocks.
- TCP and UTCL1 validation should cover VMID-specific watchpoints, address masks, invalidation paths, perf-counter filters, and fault-response modes.
- GDS validation should run compute workloads using multiple queues/VMIDs and verify that GDS, GWS, and OA resources remain isolated across context switches and resets.
- RAS/debug validation should confirm that signature controls and signature readbacks change predictably under the selected diagnostic mode and do not report stale values after reset.
- Graphics validation should include depth/stencil, DCC, scissor/clip/window, viewport arrays, primitive restart, blend constants, target/shader masks, and pixel-shader interpolation tests.
- Register tracing around read-modify-write sequences should confirm that only intended field masks change and reserved bits are preserved.
